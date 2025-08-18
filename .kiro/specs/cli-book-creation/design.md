# Design Document: CLI Book Creation

## Overview

The CLI Book Creation feature will extend LibriScribe's functionality by providing a command-line interface for creating books without requiring interactive input. This design document outlines the architecture, components, and implementation details for this feature.

The feature will allow users to:

1. Create books using command-line arguments with no interactive input
2. Specify book metadata via CLI parameters
3. Control which parts of the book generation process to execute
4. Use different environment configurations for testing
5. Support both live and mock LLM providers
6. Generate detailed logs and statistics for monitoring and debugging

This CLI mode will exist alongside the current interactive mode, providing a clear separation between interactive and non-interactive usage patterns.

## Architecture

The CLI Book Creation feature will build upon the existing LibriScribe architecture, extending the current command-line interface with new commands and options. The architecture will follow these principles:

1. **Separation of Concerns**: Separate the CLI interface from the core book creation logic
2. **Code Reuse**: Leverage existing functionality in the ProjectManagerAgent and other agents
3. **Testability**: Design for easy testing with both live and mock LLM providers
4. **Extensibility**: Allow for future expansion of CLI capabilities

### High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  CLI Interface  │────▶│  Book Creator   │────▶│  Project Mgr    │
│  (Typer App)    │     │  Service        │     │  & Agents       │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  CLI Args       │     │  Environment    │     │  LLM Client     │
│  Parser         │     │  Config         │     │  (Real/Mock)    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Components and Interfaces

### 1. CLI Interface

The CLI interface will be implemented using the Typer library, extending the existing CLI commands in `main.py`. The interface will include:

- A new `create-book` command with various options
- Parameter validation and help text
- Error handling for invalid inputs

```python
@app.command()
def create_book(
    title: str = typer.Option(..., "--title", "-t", help="Book title"),
    output_dir: str = typer.Option(None, "--output-dir", "-o", help="Output directory for the book project"),
    category: str = typer.Option("Fiction", "--category", "-c", help="Book category"),
    genre: str = typer.Option(None, "--genre", "-g", help="Book genre"),
    description: str = typer.Option(None, "--description", "-d", help="Book description"),
    language: str = typer.Option("English", "--language", "-l", help="Book language"),
    chapters: int = typer.Option(None, "--chapters", help="Number of chapters"),
    characters: int = typer.Option(None, "--characters", help="Number of characters"),
    worldbuilding: bool = typer.Option(False, "--worldbuilding", help="Enable worldbuilding"),
    llm: str = typer.Option(None, "--llm", help="LLM provider to use"),
    model_config: str = typer.Option(None, "--model-config", help="Path to model configuration file"),
    default_model: str = typer.Option(None, "--default-model", help="Default model to use when not specified"),
    env_file: str = typer.Option(None, "--env-file", help="Path to .env file"),
    config_file: str = typer.Option(None, "--config-file", help="Path to configuration file"),
    log_file: str = typer.Option(None, "--log-file", help="Path to log file"),
    mock: bool = typer.Option(False, "--mock", help="Use mock LLM provider"),
    generate_concept: bool = typer.Option(False, "--generate-concept", help="Generate book concept"),
    generate_outline: bool = typer.Option(False, "--generate-outline", help="Generate book outline"),
    generate_characters: bool = typer.Option(False, "--generate-characters", help="Generate character profiles"),
    generate_worldbuilding: bool = typer.Option(False, "--generate-worldbuilding", help="Generate worldbuilding details"),
    write_chapters: bool = typer.Option(False, "--write-chapters", help="Write all chapters"),
    format_book: bool = typer.Option(False, "--format-book", help="Format the book"),
    all: bool = typer.Option(False, "--all", help="Perform all generation steps"),
):
    """Create a new book using command-line arguments without interactive prompts."""
    # Implementation
```

### 2. Book Creator Service

A new service layer will be introduced to handle the book creation process based on CLI arguments. This service will:

- Parse and validate CLI arguments
- Create a ProjectKnowledgeBase object
- Initialize the ProjectManagerAgent
- Execute the requested book generation steps
- Generate unique project folder names
- Configure book-specific logging

```python
class BookCreatorService:
    def __init__(self,
                 env_file: Optional[str] = None,
                 config_file: Optional[str] = None,
                 model_config: Optional[str] = None,
                 default_model: Optional[str] = None,
                 mock: bool = False,
                 log_file: Optional[str] = None):
        self.settings = Settings(env_file=env_file)
        self.config = self._load_config(config_file)
        self.model_config = self._load_model_config(model_config)
        self.default_model = default_model
        self.mock = mock
        self.project_manager = None
        self.log_file = log_file

    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file."""
        # Implementation

    def _load_model_config(self, model_config: Optional[str]) -> Dict[str, str]:
        """Load model configuration from file.

        The model configuration file should be a JSON file with the following structure:
        {
            "default": "gpt-4o-mini",
            "outline": "gpt-4o",
            "worldbuilding": "gpt-4o",
            "chapter": "gpt-4o-mini",
            "formatting": "gpt-4o"
        }
        """
        # Implementation

    def _generate_unique_folder_name(self, title: str) -> str:
        """Generate a unique folder name based on title, date, and hash."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        title_slug = self._slugify(title)
        unique_hash = hashlib.md5(f"{title}{timestamp}".encode()).hexdigest()[:8]
        return f"{title_slug}-{timestamp}-{unique_hash}"

    def create_book(self, args: Dict[str, Any]) -> bool:
        """Create a book based on the provided arguments."""
        # Implementation

    def setup_logging(self, project_dir: Path) -> None:
        """Set up logging for this book project."""
        if self.log_file:
            log_path = Path(self.log_file)
        else:
            log_path = project_dir / "book_creation.log"

        # Configure logging to write to the specified log file
        # Implementation
```

### 3. Environment Configuration

The environment configuration component will handle loading environment variables from custom configuration files and configuring the system for testing:

- Load environment variables from a specified .env file
- Support additional configuration from a separate config file (not just .env)
- Configure the system to use mock LLM providers when requested
- Set up appropriate logging for testing with configurable log file locations

```python
def load_environment(env_file: Optional[str] = None, config_file: Optional[str] = None) -> None:
    """Load environment variables and configuration."""
    # Load from .env file
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file, override=True)

    # Load additional configuration from config file
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            # Apply configuration settings
            return config
    return {}
```

### 4. Mock LLM Client

A mock implementation of the LLMClient will be created for testing purposes:

- Implement the same interface as the real LLMClient
- Return deterministic responses for testing
- Support model-specific responses
- Log interactions for verification

```python
class MockLLMClient(LLMClient):
    def __init__(self, provider: str = "mock", model_config: Optional[Dict[str, str]] = None):
        super().__init__(provider)
        self.responses = self._load_mock_responses()
        self.model_config = model_config or {}

    def generate_content(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """Generate content using mock responses based on prompt type and model."""
        # Determine which model to use
        model_to_use = model or self.model

        # Get response based on prompt type and model
        response = self._get_response_for_prompt_and_model(prompt, model_to_use)

        # Log the interaction
        self._log_interaction(prompt, response, model_to_use)

        return response
```

## Data Models

The CLI Book Creation feature will use the existing data models in LibriScribe, particularly:

1. **ProjectKnowledgeBase**: Stores all book metadata and content
2. **Settings**: Stores application configuration

No new data models are required for this feature.

## Error Handling

The CLI Book Creation feature will implement comprehensive error handling:

1. **Input Validation**: Validate all CLI arguments before processing
2. **No Interactive Fallback**: CLI mode will not fall back to interactive mode for missing parameters, instead it will fail with appropriate exit codes
3. **Clear Error Messages**: Provide clear error messages for invalid inputs
4. **Logging**: Log errors to a book-specific log file for debugging purposes
5. **Standardized Exit Codes**: Use standardized exit codes to indicate different types of failures

### Exit Codes

The CLI will use the following standardized exit codes:

| Exit Code | Description |
|-----------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid command-line arguments |
| 3 | Environment configuration error |
| 4 | LLM initialization error |
| 5 | Book creation error |
| 6 | File system error |
| 7 | Network/API error |

Error handling will be implemented at multiple levels:

```python
try:
    # Attempt to create book
    result = book_creator.create_book(args)
    if result:
        console.print("[green]Book created successfully![/green]")
        return 0
    else:
        console.print("[red]Failed to create book.[/red]")
        return 5
except ValueError as e:
    console.print(f"[red]Invalid input: {str(e)}[/red]")
    return 2
except EnvironmentError as e:
    console.print(f"[red]Environment error: {str(e)}[/red]")
    return 3
except Exception as e:
    console.print(f"[red]Error: {str(e)}[/red]")
    logger.exception("Unexpected error during book creation")
    return 1
```

## Testing Strategy

The testing strategy for the CLI Book Creation feature will include:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test the interaction between components
3. **End-to-End Tests**: Test the complete book creation process

Tests will be implemented using pytest and will leverage the mock LLM client for deterministic testing.

### Unit Tests

Unit tests will focus on testing individual components:

- CLI argument parsing
- Environment configuration
- Book creator service methods

### Integration Tests

Integration tests will focus on testing the interaction between components:

- CLI interface to book creator service
- Book creator service to project manager
- Environment configuration to LLM client

### End-to-End Tests

End-to-end tests will test the complete book creation process:

- Create a book with minimal parameters
- Create a book with all parameters
- Create a book with mock LLM provider

## Implementation Plan

The implementation of the CLI Book Creation feature will be divided into the following phases:

1. **Phase 1**: Implement the CLI interface and argument parsing
2. **Phase 2**: Implement the book creator service
3. **Phase 3**: Implement environment configuration and mock LLM client
4. **Phase 4**: Implement testing infrastructure
5. **Phase 5**: Write tests and documentation

## Design Decisions and Rationales

### 1. Using Typer for CLI Interface

Typer is already used in the project and provides a clean, type-annotated interface for building CLI applications. It handles argument parsing, help text generation, and error reporting.

### 2. Introducing a Service Layer

A service layer is introduced to separate the CLI interface from the book creation logic. This improves testability and allows for future extensions (e.g., a REST API).

### 3. Configurable Model Selection

The design allows for configuring different models for different prompt types, either through a configuration file or command-line arguments. This provides flexibility for users to optimize the model selection based on their needs and budget.

### 4. Mock LLM Client for Testing

A mock LLM client is introduced to enable testing without making actual API calls to external LLM services. This improves test reliability and reduces costs. The mock client supports the same model configuration approach as the real client for consistent behavior.

### 5. Reusing Existing Components

The design reuses existing components (ProjectManagerAgent, ProjectKnowledgeBase) to maintain consistency and reduce duplication.

## Additional Features

### Statistics and Diagnostics

The CLI Book Creation feature will include a statistics and diagnostics component to help users monitor and debug the book creation process:

```python
@app.command()
def book_stats(
    project_path: str = typer.Argument(..., help="Path to the book project"),
    show_logs: bool = typer.Option(False, "--logs", "-l", help="Show recent log entries"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed statistics"),
):
    """Show statistics and diagnostics for a book project."""
    # Implementation
```

This command will:

1. Check which files have been created
2. Show the current stage of the book creation process
3. Display the last few lines of the log file
4. Show error information if the process failed
5. Provide suggestions for resolving issues

## Limitations and Future Improvements

### Limitations

1. The CLI interface may not support all features available in the interactive mode
2. Mock responses may not perfectly match real LLM responses
3. Some complex book configurations may require additional configuration files

### Future Improvements

1. Support for loading book configuration from a YAML or JSON file
2. Support for custom templates and themes
3. Support for batch processing multiple books
4. Support for more advanced LLM configuration options
5. Interactive debugging mode for troubleshooting failed book creation attempts
