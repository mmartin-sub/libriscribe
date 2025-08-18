# AutoGen Best Practices for LibriScribe

This document outlines the best practices for using Microsoft AutoGen with LibriScribe, including security guidelines, performance optimization, and integration patterns.

## Table of Contents

1. [Overview](#overview)
2. [Security Best Practices](#security-best-practices)
3. [Performance Optimization](#performance-optimization)
4. [Agent Configuration](#agent-configuration)
5. [Error Handling](#error-handling)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Integration Patterns](#integration-patterns)
8. [Testing Strategies](#testing-strategies)

## Overview

AutoGen provides a powerful framework for multi-agent coordination. When integrated with LibriScribe, it enables:

- **Coordinated Workflows**: Multiple agents working together on book creation
- **Conversation Management**: Structured conversations between specialized agents
- **Error Recovery**: Built-in mechanisms for handling failures
- **Scalability**: Easy addition of new agents and capabilities

## Security Best Practices

### 1. API Key Management

```python
# ✅ Good: Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ❌ Bad: Hardcode API keys
api_key = "sk-123"  <!-- pragma: allowlist secret -->
```

### 2. Input Validation

```python
# ✅ Good: Validate all inputs
def validate_project_data(project_kb: ProjectKnowledgeBase) -> bool:
    if not project_kb.title or len(project_kb.title.strip()) == 0:
        raise ValueError("Title cannot be empty")

    if project_kb.title not in ALLOWED_CHARACTERS:
        raise ValueError("Title contains invalid characters")

    return True
```

### 3. Rate Limiting

```python
# ✅ Good: Implement rate limiting
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def make_api_call_with_retry(prompt: str):
    # Add delay between calls
    await asyncio.sleep(1)
    return await llm_client.generate_content(prompt)
```

### 4. Sensitive Data Handling

```python
# ✅ Good: Sanitize logs
def sanitize_for_logging(message: str) -> str:
    """Remove sensitive data from log messages."""
    import re

    # Remove API keys
    message = re.sub(r'sk-[a-zA-Z0-9]{20,}', '[API_KEY]', message)

    # Remove other sensitive patterns
    message = re.sub(r'password\s*=\s*[^\s]+', 'password=[REDACTED]', message)

    return message
```

## Performance Optimization

### 1. Async/Await Usage

```python
# ✅ Good: Use async/await for I/O operations
async def create_book_with_autogen(project_kb: ProjectKnowledgeBase):
    chat_manager = await setup_autogen_team()

    for step in workflow_steps:
        await execute_step(chat_manager, step)
        await asyncio.sleep(1)  # Rate limiting
```

### 2. Caching

```python
# ✅ Good: Implement caching for repeated requests
import functools
from typing import Dict, Any

class ConversationCache:
    def __init__(self):
        self.cache: Dict[str, Any] = {}

    def get_cached_response(self, prompt_hash: str) -> Optional[str]:
        return self.cache.get(prompt_hash)

    def cache_response(self, prompt_hash: str, response: str):
        self.cache[prompt_hash] = response
```

### 3. Batch Processing

```python
# ✅ Good: Batch similar operations
async def batch_process_chapters(chapters: List[str]):
    tasks = []
    for chapter in chapters:
        task = process_chapter(chapter)
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 4. Model Selection

```python
# ✅ Good: Use appropriate models for tasks
def get_optimal_model(task_type: str) -> str:
    model_mapping = {
        "creative_writing": "gpt-4",
        "fact_checking": "gpt-4-turbo",
        "summarization": "gpt-3.5-turbo",
        "research": "gpt-4"
    }
    return model_mapping.get(task_type, "gpt-4")
```

## Agent Configuration

### 1. System Messages

```python
# ✅ Good: Specific, detailed system messages
concept_generator_system = """You are a book concept generator specializing in:
- Market analysis and positioning
- Genre-specific conventions
- Target audience identification
- Compelling title creation
- Logline development

Your responses must be:
- Structured in JSON format
- Market-oriented
- Original and creative
- Suitable for the specified genre"""
```

### 2. LLM Configuration

```python
# ✅ Good: Task-specific configurations
def get_llm_config(task_type: str) -> Dict[str, Any]:
    configs = {
        "creative": {
            "temperature": 0.8,
            "max_tokens": 4000,
            "top_p": 0.9
        },
        "analytical": {
            "temperature": 0.2,
            "max_tokens": 2000,
            "top_p": 0.7
        },
        "factual": {
            "temperature": 0.1,
            "max_tokens": 1500,
            "top_p": 0.5
        }
    }
    return configs.get(task_type, configs["creative"])
```

### 3. Conversation Flow

```python
# ✅ Good: Structured conversation flow
class BookCreationWorkflow:
    def __init__(self):
        self.steps = [
            "concept_generation",
            "outline_creation",
            "character_development",
            "worldbuilding",
            "chapter_writing",
            "content_review",
            "editing"
        ]

    async def execute_workflow(self, project_kb: ProjectKnowledgeBase):
        for step in self.steps:
            try:
                await self.execute_step(step, project_kb)
                await self.validate_step_result(step)
            except Exception as e:
                await self.handle_step_error(step, e)
```

## Error Handling

### 1. Graceful Degradation

```python
# ✅ Good: Handle failures gracefully
async def execute_with_fallback(primary_method, fallback_method):
    try:
        return await primary_method()
    except Exception as e:
        logger.warning(f"Primary method failed: {e}")
        try:
            return await fallback_method()
        except Exception as fallback_error:
            logger.error(f"Fallback method also failed: {fallback_error}")
            raise
```

### 2. Retry Logic

```python
# ✅ Good: Implement retry with exponential backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
async def reliable_api_call(prompt: str):
    return await llm_client.generate_content(prompt)
```

### 3. Timeout Handling

```python
# ✅ Good: Implement timeouts
import asyncio

async def execute_with_timeout(coro, timeout_seconds: int = 300):
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error(f"Operation timed out after {timeout_seconds} seconds")
        raise
```

## Monitoring and Logging

### 1. Structured Logging

```python
# ✅ Good: Use structured logging
import logging
import json
from datetime import datetime

class AutoGenLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def log_conversation_step(self, step: str, message: str, duration: float):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "step": step,
            "message_length": len(message),
            "duration_seconds": duration,
            "status": "success"
        }
        self.logger.info(json.dumps(log_entry))
```

### 2. Performance Metrics

```python
# ✅ Good: Track performance metrics
class PerformanceTracker:
    def __init__(self):
        self.metrics = {
            "total_conversations": 0,
            "average_duration": 0.0,
            "success_rate": 1.0,
            "api_calls": 0
        }

    def record_conversation(self, duration: float, success: bool):
        self.metrics["total_conversations"] += 1
        self.metrics["average_duration"] = (
            (self.metrics["average_duration"] * (self.metrics["total_conversations"] - 1) + duration)
            / self.metrics["total_conversations"]
        )

        if not success:
            self.metrics["success_rate"] = (
                (self.metrics["success_rate"] * (self.metrics["total_conversations"] - 1))
                / self.metrics["total_conversations"]
            )
```

## Integration Patterns

### 1. Hybrid Approach

```python
# ✅ Good: Combine AutoGen coordination with LibriScribe execution
class HybridBookCreator:
    def __init__(self, autogen_service: AutoGenService, libriscribe_agents: Dict):
        self.autogen_service = autogen_service
        self.libriscribe_agents = libriscribe_agents

    async def create_book(self, project_kb: ProjectKnowledgeBase):
        # Use AutoGen for high-level coordination
        plan = await self.autogen_service.create_plan(project_kb)

        # Use LibriScribe agents for execution
        for step in plan.steps:
            agent = self.libriscribe_agents[step.agent_type]
            await agent.execute(step.parameters)
```

### 2. Conversation Management

```python
# ✅ Good: Manage conversation state
class ConversationManager:
    def __init__(self):
        self.conversation_history = []
        self.current_context = {}

    def add_message(self, sender: str, message: str, metadata: Dict = None):
        entry = {
            "timestamp": datetime.utcnow(),
            "sender": sender,
            "message": message,
            "metadata": metadata or {}
        }
        self.conversation_history.append(entry)

    def get_context_summary(self) -> str:
        # Create a summary of the conversation for context
        recent_messages = self.conversation_history[-5:]
        return "\n".join([f"{msg['sender']}: {msg['message']}" for msg in recent_messages])
```

## Testing Strategies

### 1. Mock Testing

```python
# ✅ Good: Use mocks for testing
import unittest
from unittest.mock import Mock, AsyncMock

class TestAutoGenIntegration(unittest.TestCase):
    def setUp(self):
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate_content = AsyncMock(return_value="Mock response")

    async def test_concept_generation(self):
        autogen_service = AutoGenService(self.mock_llm_client)
        result = await autogen_service.create_concept("Test Book")
        self.assertTrue(result)
```

### 2. Integration Testing

```python
# ✅ Good: Test the full workflow
class TestBookCreationWorkflow(unittest.TestCase):
    async def test_full_book_creation(self):
        project_kb = ProjectKnowledgeBase(
            title="Test Book",
            category="Fiction",
            genre="Fantasy"
        )

        autogen_service = AutoGenService(self.llm_client)
        result = await autogen_service.create_book_with_autogen_team(project_kb)

        self.assertTrue(result)
        self.assertIsNotNone(project_kb.concept)
        self.assertIsNotNone(project_kb.outline)
```

### 3. Performance Testing

```python
# ✅ Good: Test performance characteristics
import time
import asyncio

async def performance_test():
    start_time = time.time()

    autogen_service = AutoGenService(llm_client)
    result = await autogen_service.create_book_with_autogen_team(project_kb)

    duration = time.time() - start_time

    # Assert performance requirements
    assert duration < 300  # Should complete within 5 minutes
    assert result is True
```

## Best Practices Summary

### Do's ✅

1. **Use environment variables for sensitive data**
2. **Implement proper error handling and retry logic**
3. **Use async/await for I/O operations**
4. **Implement caching for repeated requests**
5. **Use structured logging with proper sanitization**
6. **Validate all inputs before processing**
7. **Implement rate limiting and timeouts**
8. **Use appropriate models for specific tasks**
9. **Test thoroughly with mocks and integration tests**
10. **Monitor performance and costs**

### Don'ts ❌

1. **Don't hardcode API keys or sensitive data**
2. **Don't ignore error handling**
3. **Don't use synchronous calls for I/O operations**
4. **Don't make unnecessary API calls**
5. **Don't log sensitive information**
6. **Don't trust user input without validation**
7. **Don't exceed API rate limits**
8. **Don't use inappropriate models for tasks**
9. **Don't skip testing**
10. **Don't ignore monitoring and analytics**

## Conclusion

Following these best practices will ensure that your AutoGen integration with LibriScribe is secure, performant, and maintainable. The key is to balance the power of multi-agent coordination with proper engineering practices for production systems.
