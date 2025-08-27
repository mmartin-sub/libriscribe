# Configuration

LibriScribe2 uses a flexible configuration system that allows you to customize various aspects of the application, including model selection for different types of content generation.

## Configuration Files

The application supports multiple configuration file formats:

- **JSON**: `config-example.json` (copy and rename to `config.json`)
- **YAML**: `config.yaml` or `config.yml`

## Model Configuration

The model configuration allows you to specify which AI model to use for different types of content generation. This is configured through the `models` section in your configuration file.

### Default Models

Default model configurations are stored in `src/libriscribe2/settings.py` and include:

- **Default fallback model**: `gpt-4o-mini` (used when no specific model is configured)
- **Complete default configuration**: All model types have sensible defaults

### Available Model Types

| Model Type | Description | Default Model |
|------------|-------------|---------------|
| `default` | Default model when none specified | `gpt-4o-mini` |
| `concept` | For generating book concepts | `gpt-4o-mini` |
| `outline` | For generating book outlines | `gpt-4o` |
| `character` | For character generation | `gpt-4o` |
| `worldbuilding` | For worldbuilding content | `gpt-4o` |
| `scene_outline` | For generating scene outlines | `gpt-4o-mini` |
| `scene` | For writing individual scenes | `gpt-4o-mini` |
| `chapter` | For writing chapters | `gpt-4o-mini` |
| `editor` | For editing and revision | `gpt-4o` |
| `formatting` | For formatting tasks | `gpt-4o` |
| `keyword_generation` | For generating keywords | `gpt-4o-mini` |
| `research` | For research tasks | `gpt-4o-mini` |
| `title_generation` | For generating alternative titles | `gpt-4o-mini` |

### Configuration Example

```json
{
  "openai_api_key": "your-openai-api-key-here",
  "openai_base_url": "https://api.openai.com/v1",
  "openai_default_model": "gpt-4o-mini",
  "default_llm": "openai",
  "llm_timeout": 360,
  "environment": "production",
  "projects_dir": "./projects",
  "models": {
    "default": "gpt-4o-mini",
    "concept": "gpt-4o-mini",
    "outline": "gpt-4o",
    "character": "gpt-4o",
    "worldbuilding": "gpt-4o",
    "scene_outline": "gpt-4o-mini",
    "scene": "gpt-4o-mini",
    "chapter": "gpt-4o-mini",
    "editor": "gpt-4o",
    "formatting": "gpt-4o",
    "keyword_generation": "gpt-4o-mini",
    "research": "gpt-4o-mini",
    "title_generation": "gpt-4o-mini"
  }
}
```

### YAML Configuration Example

```yaml
# LibriScribe Configuration File
openai_api_key: "your-openai-api-key-here"
openai_base_url: "https://api.openai.com/v1"
openai_default_model: "gpt-4o-mini"
default_llm: "openai"
llm_timeout: 360
environment: "production"
projects_dir: "./projects"

# Model Configuration
models:
  default: "gpt-4o-mini"
  concept: "gpt-4o-mini"
  outline: "gpt-4o"
  character: "gpt-4o"
  worldbuilding: "gpt-4o"
  scene_outline: "gpt-4o-mini"
  scene: "gpt-4o-mini"
  chapter: "gpt-4o-mini"
  editor: "gpt-4o"
  formatting: "gpt-4o"
  keyword_generation: "gpt-4o-mini"
  research: "gpt-4o-mini"
  title_generation: "gpt-4o-mini"
```

## Model Selection Strategy

The application automatically selects the appropriate model based on the type of content being generated:

1. **Look for specific model**: First checks if a model is configured for the specific prompt type
2. **Fall back to default**: If no specific model is found, uses the `"default"` model from configuration
3. **Hardcoded fallback**: If no `"default"` is configured, uses `gpt-4o-mini` as the final fallback

### Model Complexity Guidelines

- **High-complexity tasks** (outlines, worldbuilding, editing) use more powerful models like `gpt-4o`
- **Medium-complexity tasks** (chapters, concepts, research) use balanced models like `gpt-4o-mini`
- **Simple tasks** (scene outlines, keywords) use faster models like `gpt-4o-mini`

## Environment Variables

You can also configure the application using environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_BASE_URL`: OpenAI API base URL (default: https://api.openai.com/v1)
- `OPENAI_DEFAULT_MODEL`: Default model name
- `DEFAULT_LLM`: Default LLM provider
- `LLM_TIMEOUT`: Timeout in seconds
- `ENVIRONMENT`: Environment for LiteLLM tags (e.g., "production", "staging", "testing")
- `PROJECTS_DIR`: Directory for project files

## Configuration Loading Order

The application loads configuration in the following order:

1. Environment variables
2. `.env` file (if present)
3. Configuration file (`config.json` or `config.yaml`)
4. Default values

**Note**: Copy `config-example.json` to `config.json` and customize it with your settings.

Later sources override earlier ones, allowing for flexible configuration management.

## LiteLLM Tags

LibriScribe supports LiteLLM tags for better tracking and monitoring of LLM calls. The following tags are automatically included in all LLM requests:

- **X-Litellm-Tag-Environment**: Set from the `environment` field in your configuration file
- **X-Litellm-Tag-Project**: Set to the project folder name where book content is stored
- **X-Litellm-Tag-User**: Set from the `--user` CLI parameter (optional, spaces allowed)

### Usage Examples

```bash
# With user identifier
create-book --genre=fantasy --all --mock --user="user-123"

# With user identifier containing spaces
create-book --genre=fantasy --all --mock --user="user-123 x"

# Without user identifier (only environment and project tags will be set)
create-book --genre=fantasy --all --mock
```

### Environment Values

Common environment values include:
- `production`: For live/production environments
- `staging`: For staging/testing environments
- `testing`: For development/testing environments
- `development`: For local development

### Scene Configuration

LibriScribe supports configurable scene ranges per chapter to create more dynamic and varied books:

#### Scene Range Format

- **Single number**: `"5"` - Always generates exactly 5 scenes per chapter
- **Range**: `"3-6"` - Generates a random number between 3 and 6 scenes per chapter
- **Wide range**: `"4-8"` - Generates a random number between 4 and 8 scenes per chapter

#### Examples

```bash
# Use default scene range (3-6)
create-book --genre=fantasy --all --mock

# Custom scene range
create-book --genre=fantasy --scenes-per-chapter=4-8 --all --mock

# Fixed scene count
create-book --genre=mystery --scenes-per-chapter=5 --all --mock
```

#### Configuration

Add to your config file:
```json
{
  "scenes_per_chapter": "3-6"
}
```

## Auto-Title Generation

LibriScribe supports automatic title generation based on book content. The auto-title feature works as follows:

### When Auto-Title is Used

- **No title provided**: If no `--title` is specified, a temporary title "Untitled Book" is used for project creation
- **Auto-title enabled**: Use `--auto-title` flag to generate a title based on content
- **Title provided**: If a title is provided, auto-title generation is skipped (even if `--auto-title` is used)

### Title Generation Requirements

Auto-title generation works best when you have:
- **Chapters** (`--write-chapters` or `--all`)
- **Characters** (`--generate-characters`)
- **Outline** (`--generate-outline`)
- **Concept** (`--generate-concept`)

### Examples

```bash
# Generate title based on full manuscript
create-book --genre=fantasy --all --auto-title --mock

# Generate title based on concept and outline
create-book --genre=mystery --generate-concept --generate-outline --auto-title --mock

# Skip title generation (title provided)
create-book --title="My Book" --genre=fantasy --all --auto-title --mock

# Generate better title for existing book
generate-title my-fantasy-project --mock
```

## Test Configuration

For testing purposes, LibriScribe uses a separate configuration that isolates test projects from user projects:

### Test Output Directory

Test projects are automatically created in `tests/output/` to prevent confusion with user-created books. This directory is:
- Automatically cleaned up after tests
- Ignored by git
- Used for debugging when needed

### Test Settings

Tests use modified settings for faster execution:
- **Projects directory**: `tests/output/`
- **Chapters**: 3 (reduced from 15)
- **Scenes per chapter**: 2-4 (reduced from 3-6)
- **Environment**: "testing"
- **LLM timeout**: 30 seconds (reduced from 360)
- **Mock mode**: Enabled by default

### Test Project Cleanup

To move existing test projects from the main projects directory:

```bash
# List test projects
python scripts/cleanup_test_projects.py list

# Move test projects to tests/output
python scripts/cleanup_test_projects.py move
```

## Model Configuration Migration

The model configuration system has been updated to use a centralized approach. Previously, model selections were hardcoded in the `prompts_context.py` file. Now, all model selections are managed through the configuration file and default values are stored in `settings.py`, making it easier to customize and maintain.

### Default Configuration Location

Default model configurations are now stored in `src/libriscribe2/settings.py`:

- `DEFAULT_MODEL_CONFIG`: Complete default configuration for all model types
- `FALLBACK_MODEL`: Hardcoded fallback model (`gpt-4o-mini`)

### Removed Variables

The following variables have been removed from `prompts_context.py` as they are now handled by the configuration system:

- `SCENE_OUTLINE_PROMPT_MODEL`
- `OUTLINE_PROMPT_MODEL`
- `CHARACTER_PROMPT_MODEL`
- `WORLDBUILDING_PROMPT_MODEL`
- `EDITOR_PROMPT_MODEL`
- `RESEARCH_PROMPT_MODEL`
- `FORMATTING_PROMPT_MODEL`
- `SCENE_PROMPT_MODEL`
- `KEYWORD_GENERATION_PROMPT_MODEL`
- `DEF_MODEL_OUTPUT_S_CONTEXT_S`
- `DEF_MODEL_OUTPUT_M_CONTEXT_M`
- `DEF_MODEL_OUTPUT_L_CONTEXT_L`

## Best Practices

1. **Use appropriate models**: Match model complexity to task complexity
2. **Monitor costs**: More powerful models cost more per token
3. **Test configurations**: Validate your configuration before running large projects
4. **Version control**: Keep your configuration files in version control
5. **Environment separation**: Use different configurations for development and production

## Troubleshooting

### Common Issues

1. **Model not found**: Ensure the model name is correct and available in your OpenAI account
2. **Configuration not loaded**: Check file paths and permissions
3. **Timeout errors**: Increase `llm_timeout` for complex tasks
4. **API errors**: Verify your API key and base URL

### Debugging

Enable debug logging to see which models are being selected:

```bash
export LOG_LEVEL=DEBUG
libriscribe2 your-command
```

This will show you which model is being used for each prompt type.
