# LLM Client API Documentation

## Overview

The `LLMClient` class provides a unified interface for interacting with Large Language Models (LLMs) in LibriScribe2. It supports multiple providers (OpenAI, mock) with advanced features like content filtering fallback, streaming generation, and comprehensive error handling.

## Key Features

- **Multi-Provider Support**: OpenAI and mock providers
- **Model Configuration**: Per-prompt-type model selection
- **Content Filtering Fallback**: Automatic retry with simplified prompts
- **Streaming Generation**: Real-time content streaming
- **Comprehensive Error Handling**: Detailed error context and recovery
- **LiteLLM Integration**: Full support for LiteLLM proxy with metadata
- **Performance Monitoring**: Built-in timing and metrics
- **Python 3.12 Features**: Modern async/await patterns and type hints

## Class Definition

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
    )
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `provider` | `str` | Required | LLM provider ("openai", "mock") |
| `model_config` | `dict[str, str] \| None` | `None` | Model mapping for different prompt types |
| `timeout` | `float` | `300.0` | Request timeout in seconds |
| `environment` | `str` | `"production"` | Environment tag for LiteLLM |
| `project_name` | `str` | `""` | Project name for LiteLLM metadata |
| `user` | `str \| None` | `None` | User identifier for LiteLLM |

## Core Methods

### generate_content()

Generate content with comprehensive error handling and model selection.

```python
async def generate_content(
    self,
    prompt: str,
    prompt_type: str = "general",
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int | None = None,
    **kwargs: Any,
) -> str
```

**Parameters:**
- `prompt` (str): The input prompt text
- `prompt_type` (str): Type of prompt for model selection ("general", "creative", "analysis", etc.)
- `temperature` (float): Sampling temperature (0.0-1.0)
- `max_tokens` (int | None): Maximum tokens to generate
- `**kwargs`: Additional provider-specific parameters

**Returns:**
- `str`: Generated content

**Raises:**
- `LLMClientError`: On generation failure with detailed context

**Example:**
```python
client = LLMClient("openai", model_config={"creative": "gpt-4o", "general": "gpt-4o-mini"})

# Generate creative content
content = await client.generate_content(
    "Write a fantasy story opening",
    prompt_type="creative",
    temperature=0.8
)

# Generate analytical content
analysis = await client.generate_content(
    "Analyze this text for themes",
    prompt_type="analysis",
    temperature=0.3
)
```

### generate_streaming_content()

Generate content with real-time streaming.

```python
async def generate_streaming_content(
    self,
    prompt: str,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int | None = None,
    **kwargs: Any
) -> AsyncIterator[str]
```

**Parameters:**
- `prompt` (str): The input prompt text
- `temperature` (float): Sampling temperature
- `max_tokens` (int | None): Maximum tokens to generate
- `**kwargs`: Additional parameters

**Returns:**
- `AsyncIterator[str]`: Stream of content chunks

**Example:**
```python
async for chunk in client.generate_streaming_content("Tell me a story"):
    print(chunk, end="", flush=True)
```

### generate_content_with_content_filtering_fallback()

Generate content with automatic fallback for content filtering issues.

```python
async def generate_content_with_content_filtering_fallback(
    self,
    primary_prompt: str,
    fallback_prompt: str | None = None,
    prompt_type: str = "general",
    temperature: float = DEFAULT_TEMPERATURE,
    max_retries: int = 2,
    **kwargs: Any,
) -> str | None
```

**Parameters:**
- `primary_prompt` (str): Primary prompt to try first
- `fallback_prompt` (str | None): Optional fallback prompt
- `prompt_type` (str): Type of prompt for model selection
- `temperature` (float): Sampling temperature
- `max_retries` (int): Maximum retry attempts
- `**kwargs`: Additional parameters

**Returns:**
- `str | None`: Generated content or None if all attempts fail

**Example:**
```python
content = await client.generate_content_with_content_filtering_fallback(
    primary_prompt="Complex prompt with potential filtering issues",
    fallback_prompt="Simple alternative prompt",
    prompt_type="creative",
    max_retries=3
)
```

### generate_content_with_timing()

Generate content with performance timing information.

```python
async def generate_content_with_timing(
    self,
    prompt: str,
    **kwargs: Any
) -> tuple[str, float]
```

**Parameters:**
- `prompt` (str): The input prompt text
- `**kwargs`: Additional parameters

**Returns:**
- `tuple[str, float]`: Generated content and execution time in seconds

**Example:**
```python
content, duration = await client.generate_content_with_timing("Generate a summary")
print(f"Generated {len(content)} characters in {duration:.2f} seconds")
```

### generate_content_with_fallback()

Generate content with fallback prompt support.

```python
async def generate_content_with_fallback(
    self,
    primary_prompt: str,
    fallback_prompt: str | None = None,
    **kwargs: Any
) -> str
```

**Parameters:**
- `primary_prompt` (str): Primary prompt to try first
- `fallback_prompt` (str | None): Fallback prompt if primary fails
- `**kwargs`: Additional parameters

**Returns:**
- `str`: Generated content

**Example:**
```python
content = await client.generate_content_with_fallback(
    primary_prompt="Complex technical prompt",
    fallback_prompt="Simplified version of the prompt"
)
```

## Utility Methods

### get_model_for_prompt_type()

Get the appropriate model for a specific prompt type.

```python
def get_model_for_prompt_type(self, prompt_type: str) -> str
```

**Parameters:**
- `prompt_type` (str): The prompt type

**Returns:**
- `str`: Model name for the prompt type

**Example:**
```python
model = client.get_model_for_prompt_type("creative")  # Returns "gpt-4o"
```

### validate_prompt()

Validate a prompt before processing.

```python
def validate_prompt(self, prompt: Any) -> bool
```

**Parameters:**
- `prompt` (Any): Prompt to validate

**Returns:**
- `bool`: True if prompt is valid

**Example:**
```python
if client.validate_prompt(user_input):
    content = await client.generate_content(user_input)
```

### get_client_config()

Get current client configuration.

```python
def get_client_config(self) -> dict[str, Any]
```

**Returns:**
- `dict[str, Any]`: Client configuration dictionary

**Example:**
```python
config = client.get_client_config()
print(f"Provider: {config['provider']}")
print(f"Timeout: {config['timeout']}")
```

## Context Manager Support

The LLMClient supports async context manager usage for resource management.

```python
async def client_session(self):
    """Async context manager for LLM client sessions."""

async def __aenter__(self):
    """Async context manager entry."""

async def __aexit__(self, exc_type, _exc_val, _exc_tb):
    """Async context manager exit."""
```

**Example:**
```python
async with LLMClient("openai") as client:
    content = await client.generate_content("Generate content")
    # Client automatically cleaned up
```

## Error Handling

### LLMClientError

Custom exception class with enhanced error information.

```python
class LLMClientError(Exception):
    """Exception for LLM client errors with improved error messages."""

    def __init__(
        self,
        message: str,
        provider: str,
        context: dict[str, Any] | None = None
    ) -> None
```

**Attributes:**
- `provider` (str): The LLM provider that caused the error
- `context` (dict): Additional error context information

**Example:**
```python
try:
    content = await client.generate_content("Invalid prompt")
except LLMClientError as e:
    print(f"Provider: {e.provider}")
    print(f"Context: {e.context}")
    print(f"Message: {str(e)}")
```

## Model Configuration

The client supports flexible model configuration for different prompt types:

```python
model_config = {
    "general": "gpt-4o-mini",      # General purpose
    "creative": "gpt-4o",          # Creative writing
    "analysis": "gpt-4o",          # Text analysis
    "title_generation": "gpt-4o-mini",  # Title generation
    "character_generation": "gpt-4o",   # Character creation
    "outline_generation": "gpt-4o",     # Outline creation
    "chapter_writing": "gpt-4o",        # Chapter writing
    "worldbuilding": "gpt-4o",          # World building
    "review": "gpt-4o",                 # Content review
}

client = LLMClient("openai", model_config=model_config)
```

## LiteLLM Integration

The client fully supports LiteLLM proxy with metadata tagging:

```python
client = LLMClient(
    provider="openai",
    environment="production",
    project_name="my-book-project",
    user="author@example.com"
)

# Headers automatically include:
# X-Litellm-Tag-Environment: production
# X-Litellm-Tag-Project: my-book-project
# X-Litellm-Tag-User: author@example.com
```

## Content Filtering Analysis

The client includes sophisticated content filtering analysis:

```python
def _analyze_content_filtering_triggers(self, prompt: Any) -> list[str]
```

Detects potential triggers:
- Unicode escape sequences
- HTML-like tags
- JavaScript injection patterns
- URLs and email patterns
- IP addresses
- Non-ASCII characters
- Very long prompts
- Repeated patterns

## Provider-Specific Implementation

### OpenAI Provider

- Full OpenAI API compatibility
- LiteLLM proxy support
- Comprehensive error handling
- Content filtering detection
- Request/response validation

### Mock Provider

- Deterministic responses for testing
- Language-specific content generation
- Configurable content length
- JSON response simulation
- No API costs

## Usage Examples

### Basic Usage

```python
from libriscribe2.utils.llm_client import LLMClient

# Initialize client
client = LLMClient(
    provider="openai",
    model_config={"creative": "gpt-4o", "general": "gpt-4o-mini"},
    timeout=300.0,
    project_name="my-book"
)

# Generate content
content = await client.generate_content(
    "Write a compelling book opening",
    prompt_type="creative",
    temperature=0.8
)
```

### Advanced Usage with Error Handling

```python
from libriscribe2.utils.llm_client import LLMClient, LLMClientError

client = LLMClient("openai")

try:
    # Try with content filtering fallback
    content = await client.generate_content_with_content_filtering_fallback(
        primary_prompt="Complex prompt that might trigger filtering",
        fallback_prompt="Simple alternative prompt",
        prompt_type="creative",
        max_retries=3
    )

    if content:
        print(f"Generated: {content}")
    else:
        print("All generation attempts failed")

except LLMClientError as e:
    print(f"Error from {e.provider}: {e}")
    if e.context:
        print(f"Context: {e.context}")
```

### Streaming Generation

```python
print("Generating story...")
async for chunk in client.generate_streaming_content(
    "Tell me an adventure story",
    temperature=0.7
):
    print(chunk, end="", flush=True)
print("\nDone!")
```

### Performance Monitoring

```python
content, duration = await client.generate_content_with_timing(
    "Analyze this text for themes and motifs"
)

print(f"Analysis completed in {duration:.2f} seconds")
print(f"Generated {len(content)} characters")
print(f"Rate: {len(content)/duration:.1f} chars/second")
```

### Context Manager Usage

```python
async with LLMClient("openai", project_name="my-book") as client:
    # Generate multiple pieces of content
    title = await client.generate_content("Generate a book title", "title_generation")
    outline = await client.generate_content("Create a chapter outline", "outline_generation")

    # Client automatically cleaned up
```

## Configuration Integration

The LLMClient integrates with LibriScribe2's settings system:

```python
from libriscribe2.settings import Settings

settings = Settings()
client = LLMClient(
    provider=settings.default_llm,
    timeout=settings.llm_timeout,
    environment=settings.environment
)
```

## Best Practices

1. **Use appropriate prompt types** for optimal model selection
2. **Handle LLMClientError exceptions** with proper error context
3. **Use content filtering fallback** for prompts that might trigger filtering
4. **Monitor performance** with timing methods for optimization
5. **Use context managers** for proper resource cleanup
6. **Configure models per prompt type** for cost optimization
7. **Set appropriate timeouts** based on expected generation time
8. **Use mock provider** for testing to avoid API costs

## Thread Safety

The LLMClient is designed to be thread-safe for concurrent usage:

- No shared mutable state between requests
- Each request uses independent HTTP sessions
- Error handling is request-specific
- Logging is thread-safe

## Performance Considerations

- **Model Selection**: Use smaller models (gpt-4o-mini) for simple tasks
- **Timeout Configuration**: Set appropriate timeouts based on content length
- **Content Filtering**: Use fallback methods to avoid retry delays
- **Streaming**: Use streaming for long-form content generation
- **Connection Pooling**: HTTP sessions are automatically managed

## Migration Guide

### From Previous Versions

The new LLMClient includes breaking changes:

1. **Constructor changes**: New parameters for environment and project metadata
2. **Error handling**: New LLMClientError with enhanced context
3. **Model configuration**: Per-prompt-type model selection
4. **Async context manager**: New resource management patterns

### Updating Code

```python
# Old usage
client = LLMClient("openai")
content = await client.generate_content("prompt")

# New usage
client = LLMClient(
    provider="openai",
    model_config={"general": "gpt-4o-mini"},
    project_name="my-project"
)
content = await client.generate_content("prompt", prompt_type="general")
```

## See Also

- [Settings Configuration](../user-guide/configuration.md)
- [Mock LLM Client](mock-llm-client-api.md)
- [Error Handling Guide](../development/error-handling.md)
- [Performance Optimization](../development/performance.md)
