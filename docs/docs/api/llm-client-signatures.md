# LLM Client - Function and Class Signatures

## Overview

This document provides a comprehensive reference of all function and class signatures in the `src/libriscribe2/utils/llm_client.py` module.

## Type Aliases

```python
ModelType = str
PromptType = str
ResponseType = str | dict[str, Any]
```

## Protocols

### LLMProviderProtocol

```python
class LLMProviderProtocol(Protocol):
    """Protocol for LLM providers using Python 3.12 features."""

    async def generate_content(self, prompt: str, **kwargs: Any) -> str:
        """Generate content from a prompt."""
        ...

    async def generate_streaming_content(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Generate streaming content from a prompt."""
        ...
```

## Exception Classes

### LLMClientError

```python
class LLMClientError(Exception):
    """Exception for LLM client errors with improved error messages."""

    def __init__(
        self,
        message: str,
        provider: str,
        context: dict[str, Any] | None = None
    ) -> None:
        """Initialize LLM client error with context."""
```

**Attributes:**
- `provider` (str): The LLM provider that caused the error
- `context` (dict[str, Any] | None): Additional error context

## Main Classes

### LLMClient

```python
class LLMClient:
    """LLM Client using Python 3.12 features."""

    def __init__(
        self,
        provider: str,
        model_config: dict[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        environment: str = DEFAULT_ENVIRONMENT,
        project_name: str = "",
        user: str | None = None,
    ) -> None:
        """Initialize LLM client with configuration."""
```

#### Public Methods

##### Core Generation Methods

```python
async def generate_content(
    self,
    prompt: str,
    prompt_type: str = "general",
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int | None = None,
    **kwargs: Any,
) -> str:
    """Generate content with improved error handling and timeout."""

async def generate_streaming_content(
    self,
    prompt: str,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int | None = None,
    **kwargs: Any
) -> AsyncIterator[str]:
    """Generate streaming content with improved async iteration."""

async def generate_content_with_timing(
    self,
    prompt: str,
    **kwargs: Any
) -> tuple[str, float]:
    """Generate content with timing information."""

async def generate_content_with_fallback(
    self,
    primary_prompt: str,
    fallback_prompt: str | None = None,
    **kwargs: Any
) -> str:
    """Generate content with fallback support."""

async def generate_content_with_content_filtering_fallback(
    self,
    primary_prompt: str,
    fallback_prompt: str | None = None,
    prompt_type: str = "general",
    temperature: float = DEFAULT_TEMPERATURE,
    max_retries: int = 2,
    **kwargs: Any,
) -> str | None:
    """Generate content with fallback for content filtering issues."""
```

##### Utility Methods

```python
def get_model_for_prompt_type(self, prompt_type: str) -> str:
    """Gets the specific model for a given prompt type, falling back to default."""

def validate_prompt(self, prompt: Any) -> bool:
    """Validate prompt using Python 3.12 features."""

def get_client_config(self) -> dict[str, Any]:
    """Get client configuration using Python 3.12 features."""
```

##### Context Manager Methods

```python
@asynccontextmanager
async def client_session(self):
    """Async context manager for LLM client sessions."""

async def __aenter__(self):
    """Async context manager entry."""

async def __aexit__(self, exc_type, _exc_val, _exc_tb):
    """Async context manager exit."""

async def initialize_session(self) -> None:
    """Initialize client session."""

async def cleanup_session(self) -> None:
    """Cleanup client session."""
```

#### Private Methods

##### Configuration and Validation

```python
def _validate_configuration(self) -> None:
    """Validate client configuration using Python 3.12 features."""

def _analyze_content_filtering_triggers(self, prompt: Any) -> list[str]:
    """Analyze prompt for potential content filtering triggers."""

def _create_simplified_prompt(self, original_prompt: str, prompt_type: str) -> str:
    """Create a simplified version of the prompt to avoid content filtering."""
```

##### Provider-Specific Implementation

```python
async def _generate_openai_content(
    self,
    prompt: str,
    temperature: float,
    max_tokens: int | None,
    model: str = OPENAI_DEFAULT_MODEL,
    **kwargs: Any
) -> str:
    """Generate content using OpenAI."""

async def _generate_mock_content(
    self,
    prompt: str,
    temperature: float,
    **kwargs: Any
) -> str:
    """Generate mock content for testing."""

async def _generate_openai_streaming(
    self,
    prompt: str,
    temperature: float,
    max_tokens: int | None,
    **kwargs: Any
) -> AsyncIterator[str]:
    """Generate streaming content using OpenAI."""

async def _generate_mock_streaming(
    self,
    prompt: str,
    temperature: float,
    **kwargs: Any
) -> AsyncIterator[str]:
    """Generate mock streaming content for testing."""
```

## Constants and Defaults

```python
# Type aliases
T = TypeVar("T")
ModelType = str
PromptType = str
ResponseType = str | dict[str, Any]

# Default values from settings
DEFAULT_TIMEOUT: float = 300.0
DEFAULT_TEMPERATURE: float = 0.7
DEFAULT_MAX_TOKENS: int = 100000
DEFAULT_ENVIRONMENT: str = "production"
FALLBACK_MODEL: str = "gpt-4o-mini"
OPENAI_DEFAULT_MODEL: str = "gpt-4o-mini"
OPENAI_BASE_URL: str = "https://api.openai.com/v1"
CLIENT_VERSION: str = "1.0.0"
```

## Usage Patterns

### Basic Initialization

```python
# Minimal initialization
client = LLMClient("openai")

# Full initialization
client = LLMClient(
    provider="openai",
    model_config={"creative": "gpt-4o", "general": "gpt-4o-mini"},
    timeout=300.0,
    environment="production",
    project_name="my-book-project",
    user="author@example.com"
)
```

### Content Generation Patterns

```python
# Basic generation
content: str = await client.generate_content("Write a story")

# With prompt type
content: str = await client.generate_content(
    "Write a creative story",
    prompt_type="creative"
)

# With all parameters
content: str = await client.generate_content(
    prompt="Write a story",
    prompt_type="creative",
    temperature=0.8,
    max_tokens=1000
)

# With timing
content: str
duration: float
content, duration = await client.generate_content_with_timing("Write a story")

# With fallback
content: str = await client.generate_content_with_fallback(
    primary_prompt="Complex prompt",
    fallback_prompt="Simple prompt"
)

# With content filtering fallback
content: str | None = await client.generate_content_with_content_filtering_fallback(
    primary_prompt="Potentially filtered prompt",
    fallback_prompt="Safe prompt",
    max_retries=3
)
```

### Streaming Generation Patterns

```python
# Basic streaming
async for chunk in client.generate_streaming_content("Tell a story"):
    chunk: str
    print(chunk, end="")

# Streaming with parameters
async for chunk in client.generate_streaming_content(
    prompt="Tell a story",
    temperature=0.7,
    max_tokens=1000
):
    chunk: str
    process_chunk(chunk)
```

### Context Manager Patterns

```python
# Session context manager
async with client.client_session():
    content = await client.generate_content("Write content")

# Full context manager
async with LLMClient("openai") as client:
    content = await client.generate_content("Write content")
```

### Error Handling Patterns

```python
# Basic error handling
try:
    content = await client.generate_content("Write content")
except LLMClientError as e:
    print(f"Provider: {e.provider}")
    print(f"Context: {e.context}")
    print(f"Error: {str(e)}")

# Specific error handling
try:
    content = await client.generate_content("Write content")
except LLMClientError as e:
    if "timeout" in str(e).lower():
        # Handle timeout
        pass
    elif "content filtering" in str(e).lower():
        # Handle content filtering
        pass
    else:
        # Handle other errors
        pass
```

### Configuration Patterns

```python
# Get model for prompt type
model: str = client.get_model_for_prompt_type("creative")

# Validate prompt
is_valid: bool = client.validate_prompt("Some prompt text")

# Get client configuration
config: dict[str, Any] = client.get_client_config()
```

## Return Type Specifications

### Method Return Types

```python
# Synchronous methods
get_model_for_prompt_type(str) -> str
validate_prompt(Any) -> bool
get_client_config() -> dict[str, Any]

# Asynchronous methods
generate_content(...) -> str
generate_streaming_content(...) -> AsyncIterator[str]
generate_content_with_timing(...) -> tuple[str, float]
generate_content_with_fallback(...) -> str
generate_content_with_content_filtering_fallback(...) -> str | None
initialize_session() -> None
cleanup_session() -> None

# Context manager methods
__aenter__() -> LLMClient
__aexit__(...) -> None
client_session() -> AsyncContextManager[LLMClient]
```

### Exception Types

```python
# Raised exceptions
LLMClientError: Exception with provider and context information
TimeoutError: When operations exceed timeout
ValueError: For invalid configuration or parameters
```

## Parameter Type Specifications

### Common Parameter Types

```python
# String parameters
provider: str                    # Required, non-empty
prompt: str                     # Required, non-empty
prompt_type: str               # Optional, defaults to "general"
environment: str               # Optional, defaults to "production"
project_name: str              # Optional, defaults to ""
model: str                     # Optional, provider-specific default

# Numeric parameters
temperature: float             # 0.0 to 1.0, defaults to 0.7
timeout: float                 # Positive number, defaults to 300.0
max_tokens: int | None         # Positive integer or None
max_retries: int              # Non-negative integer, defaults to 2

# Optional parameters
user: str | None              # Optional user identifier
fallback_prompt: str | None   # Optional fallback prompt
model_config: dict[str, str] | None  # Optional model configuration
context: dict[str, Any] | None       # Optional error context

# Complex parameters
**kwargs: Any                 # Provider-specific additional parameters
```

### Model Configuration Structure

```python
model_config: dict[str, str] = {
    "general": "gpt-4o-mini",
    "creative": "gpt-4o",
    "analysis": "gpt-4o",
    "title_generation": "gpt-4o-mini",
    "character_generation": "gpt-4o",
    "outline_generation": "gpt-4o",
    "chapter_writing": "gpt-4o",
    "worldbuilding": "gpt-4o",
    "review": "gpt-4o",
}
```

## Import Requirements

```python
import asyncio
import logging
import os
import re
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Protocol, TypeVar

import aiohttp

from ..settings import (
    CLIENT_VERSION,
    DEFAULT_ENVIRONMENT,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL_CONFIG,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    FALLBACK_MODEL,
    OPENAI_BASE_URL,
    OPENAI_DEFAULT_MODEL,
)
from .validation_mixin import ValidationMixin
```

## Complete Method Signature Summary

```python
class LLMClient:
    # Constructor
    def __init__(self, provider: str, model_config: dict[str, str] | None = None,
                 timeout: float = DEFAULT_TIMEOUT, environment: str = DEFAULT_ENVIRONMENT,
                 project_name: str = "", user: str | None = None) -> None

    # Core generation methods
    async def generate_content(self, prompt: str, prompt_type: str = "general",
                              temperature: float = DEFAULT_TEMPERATURE,
                              max_tokens: int | None = None, **kwargs: Any) -> str

    async def generate_streaming_content(self, prompt: str,
                                        temperature: float = DEFAULT_TEMPERATURE,
                                        max_tokens: int | None = None,
                                        **kwargs: Any) -> AsyncIterator[str]

    async def generate_content_with_timing(self, prompt: str, **kwargs: Any) -> tuple[str, float]

    async def generate_content_with_fallback(self, primary_prompt: str,
                                            fallback_prompt: str | None = None,
                                            **kwargs: Any) -> str

    async def generate_content_with_content_filtering_fallback(
        self, primary_prompt: str, fallback_prompt: str | None = None,
        prompt_type: str = "general", temperature: float = DEFAULT_TEMPERATURE,
        max_retries: int = 2, **kwargs: Any) -> str | None

    # Utility methods
    def get_model_for_prompt_type(self, prompt_type: str) -> str
    def validate_prompt(self, prompt: Any) -> bool
    def get_client_config(self) -> dict[str, Any]

    # Context manager methods
    async def __aenter__(self) -> LLMClient
    async def __aexit__(self, exc_type, _exc_val, _exc_tb) -> None
    async def initialize_session(self) -> None
    async def cleanup_session(self) -> None

    @asynccontextmanager
    async def client_session(self) -> AsyncIterator[LLMClient]

    # Private methods
    def _validate_configuration(self) -> None
    def _analyze_content_filtering_triggers(self, prompt: Any) -> list[str]
    def _create_simplified_prompt(self, original_prompt: str, prompt_type: str) -> str

    async def _generate_openai_content(self, prompt: str, temperature: float,
                                      max_tokens: int | None,
                                      model: str = OPENAI_DEFAULT_MODEL,
                                      **kwargs: Any) -> str

    async def _generate_mock_content(self, prompt: str, temperature: float,
                                    **kwargs: Any) -> str

    async def _generate_openai_streaming(self, prompt: str, temperature: float,
                                        max_tokens: int | None,
                                        **kwargs: Any) -> AsyncIterator[str]

    async def _generate_mock_streaming(self, prompt: str, temperature: float,
                                      **kwargs: Any) -> AsyncIterator[str]
```

## See Also

- [LLM Client API Documentation](llm-client-api.md)
- [Settings Configuration](../user-guide/configuration.md)
