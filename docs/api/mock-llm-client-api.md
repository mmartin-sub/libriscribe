# Mock LLM Client API Documentation

## Overview

The `MockLLMClient` class provides a testing-focused implementation of the LLM interface that generates deterministic responses without making actual API calls. It's designed for development, testing, and demonstration purposes, offering realistic content generation with configurable parameters.

## Key Features

- **Deterministic Responses**: Consistent output for testing
- **Multi-Language Support**: French, Spanish, and English content
- **Configurable Content Length**: Adjustable word counts for different content types
- **Realistic Content Generation**: Lorem ipsum with language-specific vocabulary
- **JSON Response Simulation**: Structured responses for different prompt types
- **No API Costs**: Free testing without external API calls
- **LiteLLM Metadata Support**: Compatible with LiteLLM tagging system

## Class Definition

```python
class MockLLMClient:
    """A mock LLM client for testing purposes."""

    def __init__(
        self,
        llm_provider: str = "mock",
        model_config: dict[str, str] | None = None,
        environment: str = DEFAULT_ENVIRONMENT,
        project_name: str = "",
        user: str | None = None,
        mock_config: MockConfig | None = None,
    )
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm_provider` | `str` | `"mock"` | Provider identifier |
| `model_config` | `dict[str, str] \| None` | `None` | Model mapping for prompt types |
| `environment` | `str` | `"production"` | Environment tag |
| `project_name` | `str` | `""` | Project name for metadata |
| `user` | `str \| None` | `None` | User identifier |
| `mock_config` | `MockConfig \| None` | `None` | Custom mock configuration |

## Mock Configuration

The `MockConfig` TypedDict defines configurable parameters:

```python
class MockConfig(TypedDict):
    scene_length: dict[str, int]
    chapter_length: dict[str, int]
    lorem_ipsum_words: list[str]
```

### Default Configuration

```python
MOCK_CONFIG: MockConfig = {
    "scene_length": {
        "min_words": 150,
        "max_words": 300,
    },
    "chapter_length": {
        "min_words": 800,
        "max_words": 1500,
    },
    "lorem_ipsum_words": [
        "lorem", "ipsum", "dolor", "sit", "amet",
        # ... extensive word list
    ],
}
```

## Core Methods

### generate_content()

Generate mock content based on prompt type and language.

```python
def generate_content(
    self,
    prompt: str,
    prompt_type: str = "default",
    temperature: float = DEFAULT_TEMPERATURE,
    language: str = "English",
    timeout: int | None = None,
) -> str
```

**Parameters:**
- `prompt` (str): Input prompt (used for context)
- `prompt_type` (str): Type of content to generate
- `temperature` (float): Temperature parameter (affects randomness)
- `language` (str): Target language ("English", "French", "Spanish")
- `timeout` (int | None): Timeout parameter (ignored in mock)

**Returns:**
- `str`: Generated mock content

**Supported Prompt Types:**
- `"questions"`: JSON formatted questions
- `"concept"`: Book concept with title, logline, description
- `"outline"`: Chapter and scene outline
- `"scene_outline"`: Detailed scene breakdown
- `"character"`: Character profiles in JSON format
- `"worldbuilding"`: World building elements
- `"chapter"`: Full chapter content
- `"scene"`: Scene content
- `"formatting"`: Formatted book content
- `"critique"`: Content critique
- `"refine"`: Refined concept
- `"keywords"`: SEO keywords
- `"plagiarism_check"`: Plagiarism analysis
- `"fact_check"`: Fact checking results
- `"content_review"`: Content review

**Example:**
```python
mock_client = MockLLMClient()

# Generate English character
character = mock_client.generate_content(
    "Create a fantasy character",
    prompt_type="character",
    language="English"
)

# Generate French chapter
chapter = mock_client.generate_content(
    "Write a chapter",
    prompt_type="chapter",
    language="French"
)
```

### generate_content_with_json_repair()

Generate content with simulated JSON repair functionality.

```python
def generate_content_with_json_repair(
    self,
    original_prompt: str,
    prompt_type: str = "default",
    temperature: float = DEFAULT_TEMPERATURE,
) -> str
```

**Parameters:**
- `original_prompt` (str): Original prompt text
- `prompt_type` (str): Type of content to generate
- `temperature` (float): Temperature parameter

**Returns:**
- `str`: Generated content (always valid JSON for applicable types)

**Example:**
```python
content = mock_client.generate_content_with_json_repair(
    "Generate character data",
    prompt_type="character"
)
```

### get_model_for_prompt_type()

Get the model name for a specific prompt type.

```python
def get_model_for_prompt_type(self, prompt_type: str) -> str
```

**Parameters:**
- `prompt_type` (str): The prompt type

**Returns:**
- `str`: Model name (from model_config or default)

**Example:**
```python
model = mock_client.get_model_for_prompt_type("creative")
```

## Configuration Methods

### update_mock_config()

Update mock configuration settings.

```python
def update_mock_config(self, new_config: MockConfig) -> None
```

**Parameters:**
- `new_config` (MockConfig): New configuration to merge

**Example:**
```python
new_config = {
    "scene_length": {"min_words": 200, "max_words": 400},
    "chapter_length": {"min_words": 1000, "max_words": 2000}
}
mock_client.update_mock_config(new_config)
```

### get_mock_config()

Get current mock configuration.

```python
def get_mock_config(self) -> MockConfig
```

**Returns:**
- `MockConfig`: Copy of current configuration

**Example:**
```python
config = mock_client.get_mock_config()
print(f"Scene length: {config['scene_length']}")
```

## Language-Specific Content Generation

The MockLLMClient supports multiple languages with appropriate vocabulary:

### English Content
- Standard lorem ipsum with English words
- Realistic character names and descriptions
- English worldbuilding terminology

### French Content
- French vocabulary and grammar patterns
- French character names (Pierre Dubois, Marie Laurent)
- French worldbuilding terms

### Spanish Content
- Spanish vocabulary and grammar patterns
- Spanish character names (Carlos Mendoza, María González)
- Spanish worldbuilding terms

## Content Type Examples

### Character Generation

**English:**
```json
[
    {
        "name": "Mock Character 1",
        "age": "25",
        "physical_description": "A brave mock character with brown hair and green eyes.",
        "personality_traits": "Brave, Loyal, Impulsive, Intelligent, Compassionate",
        "background": "Born in a modest family, always dreamed of adventure.",
        "motivations": "Protect family and discover new horizons.",
        "relationships": "Faithful friend and mentor to young adventurers.",
        "role": "Main protagonist",
        "internal_conflicts": "Doubt between family safety and adventure call.",
        "external_conflicts": "Faces mysterious forces threatening his village.",
        "character_arc": "Evolves from timid young man to confident hero."
    }
]
```

**French:**
```json
[
    {
        "name": "Pierre Dubois",
        "age": "25",
        "physical_description": "Un jeune homme aux cheveux bruns et aux yeux verts.",
        "personality_traits": "Courageux, Loyal, Impulsif, Intelligent, Compatissant",
        "background": "Né dans une famille modeste, Pierre a toujours rêvé d'aventure.",
        "motivations": "Protéger sa famille et découvrir de nouveaux horizons.",
        "relationships": "Fidèle ami de Marie et mentor de jeunes aventuriers.",
        "role": "Protagoniste principal"
    }
]
```

### Concept Generation

```json
{
    "title": "Mock Concept Title",
    "logline": "A mock logline for a mock book.",
    "description": "This is a mock description of a mock book concept, generated by the mock LLM client."
}
```

### Outline Generation

```markdown
# Mock Outline
## Chapter 1: The Beginning
- Scene 1.1: Mock opening
- Scene 1.2: Mock conflict introduction
## Chapter 2: The Middle
- Scene 2.1: Mock rising action
- Scene 2.2: Mock climax
## Chapter 3: The End
- Scene 3.1: Mock falling action
- Scene 3.2: Mock resolution
```

### Worldbuilding Generation

**English:**
```json
{
    "geography": "Mock mountains and rivers.",
    "culture_and_society": "Mock traditions and customs."
}
```

**French:**
```json
{
    "geography": "Montagnes majestueuses et rivières sinueuses traversent ce paysage fantastique.",
    "culture_and_society": "Traditions ancestrales et coutumes mystérieuses rythment la vie quotidienne."
}
```

## Lorem Ipsum Generation

The client includes sophisticated lorem ipsum generators for different languages:

### _generate_lorem_ipsum()

Generate English lorem ipsum text.

```python
def _generate_lorem_ipsum(self, min_words: int, max_words: int) -> str
```

### _generate_french_lorem_ipsum()

Generate French lorem ipsum text.

```python
def _generate_french_lorem_ipsum(self, min_words: int, max_words: int) -> str
```

### _generate_spanish_lorem_ipsum()

Generate Spanish lorem ipsum text.

```python
def _generate_spanish_lorem_ipsum(self, min_words: int, max_words: int) -> str
```

**Features:**
- Cryptographically secure random word selection
- Realistic paragraph structure (20-50 words per paragraph)
- Proper capitalization and punctuation
- Language-appropriate vocabulary
- Configurable length ranges

## Usage Examples

### Basic Usage

```python
from libriscribe2.utils.mock_llm_client import MockLLMClient

# Initialize mock client
mock_client = MockLLMClient(
    environment="testing",
    project_name="test-book"
)

# Generate different types of content
concept = mock_client.generate_content("Create a book concept", "concept")
characters = mock_client.generate_content("Generate characters", "character")
chapter = mock_client.generate_content("Write a chapter", "chapter")
```

### Multi-Language Usage

```python
# Generate content in different languages
english_char = mock_client.generate_content(
    "Create a character",
    "character",
    language="English"
)

french_char = mock_client.generate_content(
    "Créer un personnage",
    "character",
    language="French"
)

spanish_char = mock_client.generate_content(
    "Crear un personaje",
    "character",
    language="Spanish"
)
```

### Custom Configuration

```python
# Create custom configuration
custom_config = {
    "scene_length": {"min_words": 100, "max_words": 200},
    "chapter_length": {"min_words": 500, "max_words": 1000},
    "lorem_ipsum_words": ["custom", "word", "list"]
}

mock_client = MockLLMClient(mock_config=custom_config)

# Update configuration later
mock_client.update_mock_config({
    "scene_length": {"min_words": 300, "max_words": 500}
})
```

### Testing Integration

```python
import pytest
from libriscribe2.utils.mock_llm_client import MockLLMClient

@pytest.fixture
def mock_llm():
    return MockLLMClient(environment="testing")

def test_character_generation(mock_llm):
    character = mock_llm.generate_content("Generate character", "character")
    assert "Mock Character" in character
    assert "name" in character
    assert "age" in character

def test_multilingual_support(mock_llm):
    french_content = mock_llm.generate_content("Test", "character", language="French")
    assert "Pierre" in french_content or "Marie" in french_content

    spanish_content = mock_llm.generate_content("Test", "character", language="Spanish")
    assert "Carlos" in spanish_content or "María" in spanish_content
```

### Performance Testing

```python
import time

mock_client = MockLLMClient()

# Test generation speed
start_time = time.time()
for i in range(100):
    content = mock_client.generate_content(f"Test {i}", "chapter")
duration = time.time() - start_time

print(f"Generated 100 chapters in {duration:.2f} seconds")
print(f"Average: {duration/100:.4f} seconds per chapter")
```

## Integration with LLMClient

The MockLLMClient is designed to be used seamlessly with the main LLMClient:

```python
from libriscribe2.utils.llm_client import LLMClient

# Use mock provider
client = LLMClient(
    provider="mock",
    model_config={"creative": "mock-gpt-4", "general": "mock-gpt-3.5"},
    project_name="test-project"
)

# Generate content (uses MockLLMClient internally)
content = await client.generate_content(
    "Write a story",
    prompt_type="creative"
)
```

## Security Features

- **Input Sanitization**: Provider name sanitization to prevent log injection
- **Cryptographically Secure Random**: Uses `secrets` module for random generation
- **Safe Logging**: Prevents sensitive data exposure in logs
- **Memory Safety**: No persistent state between requests

## Best Practices

1. **Use for Testing**: Ideal for unit tests and integration tests
2. **Language Testing**: Test multi-language functionality without API costs
3. **Performance Benchmarking**: Measure application performance without network latency
4. **Development**: Develop features without consuming API quotas
5. **Configuration Testing**: Test different content lengths and formats
6. **Deterministic Testing**: Rely on consistent outputs for test assertions

## Limitations

- **Not Real AI**: Generates template-based content, not intelligent responses
- **Limited Creativity**: Responses follow predefined patterns
- **No Learning**: Cannot adapt or improve based on feedback
- **Template-Based**: Content quality depends on predefined templates
- **Language Support**: Limited to three languages (English, French, Spanish)

## Extending the Mock Client

### Adding New Prompt Types

```python
# In generate_content method, add new case:
elif prompt_type == "new_type":
    return "Mock response for new type"
```

### Adding New Languages

```python
def _generate_italian_lorem_ipsum(self, min_words: int, max_words: int) -> str:
    italian_words = ["ciao", "mondo", "bella", "vita", ...]
    # Implementation similar to other language generators
```

### Custom Response Templates

```python
def generate_custom_response(self, prompt_type: str, **kwargs) -> str:
    templates = {
        "custom_type": "Custom template with {variable}",
    }
    return templates.get(prompt_type, "Default response").format(**kwargs)
```

## See Also

- [LLM Client API](llm-client-api.md)
- [Testing Guide](../development/testing.md)
- [Multi-Language Support](../user-guide/internationalization.md)
- [Configuration Guide](../user-guide/configuration.md)
