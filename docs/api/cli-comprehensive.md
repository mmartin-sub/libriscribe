# LibriScribe2 CLI - Comprehensive Documentation

## Overview

The LibriScribe2 CLI (`src/libriscribe2/cli.py`) provides a modern, type-safe command-line interface for creating, managing, and analyzing book projects. Built with Typer and Rich, it offers enhanced user experience with colored output, comprehensive error handling, and both interactive and non-interactive modes.

## Architecture

### Module Structure

```python
# src/libriscribe2/cli.py
"""
LibriScribe2 - Modern book creation CLI with rich output and type safety.
"""
```

### Key Components

1. **Application Setup**: Typer app with Rich formatting
2. **Logging System**: Multi-level logging with file and console handlers
3. **Error Handling**: Comprehensive error handling with specific exit codes
4. **Command Categories**: Recommended (non-interactive) and advanced (interactive) commands
5. **Global State**: Project manager and console instances

### Dependencies

```python
import asyncio
import datetime
import logging
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel

from libriscribe2.agents.project_manager import ProjectManagerAgent
from libriscribe2.services.book_creator import BookCreatorService
from libriscribe2.settings import MANUSCRIPT_MD_FILENAME, Settings
from libriscribe2.utils.timestamp_utils import format_timestamp_for_filename
```

## Application Configuration

### Typer App Setup

```python
app = typer.Typer(
    help="LibriScribe2 - Modern book creation CLI",
    rich_markup_mode="rich",
    callback=version_callback,
    invoke_without_command=True,
)
```

### Global Variables

```python
console: Console = Console()  # Rich console for formatted output
project_manager: ProjectManagerAgent  # Global project manager instance
app_log_file: Path  # Application log file path
```

## Logging System

### Application Logging Setup

```python
def setup_application_logging() -> Path:
    """Set up application-level logging before any project is created.

    Returns:
        Path: Path to the created log file

    Creates:
        - logs/ directory if it doesn't exist
        - Timestamped log file: logs/libriscribe_{timestamp}.log
        - File handler with DEBUG level logging
        - Adds file handler to root logger
    """
```

**Features:**
- Creates `logs/` directory automatically
- Generates timestamped log files: `logs/libriscribe_{timestamp}.log`
- DEBUG level file logging (captures all messages)
- CRITICAL level console logging (minimal console output)
- UTF-8 encoding support

### Logging Configuration

```python
# Console handler - minimal output
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))
console_handler.setLevel(logging.CRITICAL)

# File handler - comprehensive logging
file_handler = logging.FileHandler(app_log_file, mode="a", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
file_handler.setLevel(logging.DEBUG)
```

## Error Handling

### Traceback Suppression

```python
def suppress_traceback(
    exc_type: type[BaseException],
    exc_value: BaseException,
    _exc_traceback: Any
) -> None:
    """Suppress traceback output to console.

    Args:
        exc_type: Exception type
        exc_value: Exception instance
        _exc_traceback: Traceback object (unused)

    Behavior:
        - Logs full traceback to file
        - Shows minimal error message to console
        - Ignores KeyboardInterrupt
    """
```

### Exit Codes

The CLI uses specific exit codes for workflow integration:

- **0**: Success
- **1**: Runtime error or unexpected error
- **2**: Invalid input (ValueError)
- **3**: Import error (missing dependencies)
- **5**: Book creation failed

## Command Categories

### 🟢 NON-INTERACTIVE (RECOMMENDED)

Fully implemented, production-ready commands:

| Command | Description | Status |
|---------|-------------|--------|
| `create-book` | Create books with command-line arguments | ✅ Fully Implemented |
| `book-stats` | View book statistics | ✅ Fully Implemented |
| `generate-title` | Generate titles for existing projects | ✅ Fully Implemented |
| `resume` | Resume existing project | ⚠️ Partially Implemented |

### 🟡 INTERACTIVE (ADVANCED)

Experimental or partially implemented commands:

| Command | Description | Status |
|---------|-------------|--------|
| `start` | Interactive book creation | ❌ Not Implemented |
| `concept` | Generate concept for existing project | ❌ Not Implemented |
| `outline` | Generate outline for existing project | ❌ Not Implemented |
| `characters` | Generate characters for existing project | ❌ Not Implemented |
| `worldbuilding` | Generate worldbuilding for existing project | ❌ Not Implemented |
| `write` | Write specific chapter | ❌ Not Implemented |
| `edit` | Edit specific chapter | ❌ Not Implemented |
| `format` | Format book into final output | ⚠️ Partially Implemented |
| `research` | Research functionality | ❌ Not Implemented |

## Core Functions

### Utility Functions

#### setup_application_logging()

```python
def setup_application_logging() -> Path
```

Sets up application-level logging with timestamped files and multi-level handlers.

**Returns:**
- `Path`: Path to the created log file

**Side Effects:**
- Creates `logs/` directory
- Creates timestamped log file
- Configures file and console handlers
- Adds handlers to root logger

#### custom_help()

```python
def custom_help() -> None
```

Displays custom help with Rich formatting, showing command categories and usage recommendations.

**Features:**
- Colored tables for command categories
- Usage recommendations
- Command descriptions
- Rich console formatting

#### version_callback()

```python
def version_callback(
    _ctx: typer.Context,
    version: bool = typer.Option(None, "--version", "-v", help="Show version and exit")
) -> None
```

Shows version information and exits.

**Parameters:**
- `_ctx`: Typer context (unused)
- `version`: Whether to show version

**Raises:**
- `typer.Exit`: Always exits after showing version

#### log_command_start()

```python
def log_command_start() -> None
```

Logs command execution start with timestamp and arguments.

**Logs:**
- Current timestamp
- Program arguments
- Command execution marker

## Command Functions

### create_book()

The primary command for book creation with comprehensive options.

```python
@app.command(name="create-book")
def create_book(
    title: str = typer.Option(None, "--title", "-t", help="Book title"),
    project_name: str = typer.Option(None, "--project-name", "-p", help="Custom project folder name"),
    auto_title: bool = typer.Option(False, "--auto-title", help="Auto-generate title based on content"),
    category: str = typer.Option("Fiction", "--category", "-c", help="Book category"),
    project_type: str = typer.Option("novel", "--project-type", help="Project type"),
    genre: str = typer.Option(None, "--genre", "-g", help="Book genre"),
    description: str = typer.Option(None, "--description", "-d", help="Book description"),
    language: str = typer.Option("English", "--language", "-l", help="Book language"),
    chapters: str = typer.Option(None, "--chapters", help="Number of chapters"),
    characters: str = typer.Option(None, "--characters", help="Number of characters"),
    scenes_per_chapter: str = typer.Option(None, "--scenes-per-chapter", help="Scene range per chapter"),
    target_audience: str = typer.Option("General", "--target-audience", help="Target audience"),
    worldbuilding: bool = typer.Option(False, "--worldbuilding", help="Enable worldbuilding"),
    config_file: str = typer.Option(None, "--config-file", help="Configuration file path"),
    log_file: str = typer.Option(None, "--log-file", help="Log file path"),
    log_level: str = typer.Option("INFO", "--log-level", help="Log level"),
    mock: bool = typer.Option(False, "--mock", help="Use mock LLM provider"),
    generate_concept: bool = typer.Option(False, "--generate-concept", help="Generate book concept"),
    generate_outline: bool = typer.Option(False, "--generate-outline", help="Generate book outline"),
    generate_characters: bool = typer.Option(False, "--generate-characters", help="Generate character profiles"),
    generate_worldbuilding: bool = typer.Option(False, "--generate-worldbuilding", help="Generate worldbuilding"),
    write_chapters: bool = typer.Option(False, "--write-chapters", help="Write all chapters"),
    format_book: bool = typer.Option(False, "--format-book", help="Format book into final output"),
    user: str | None = typer.Option(None, "--user", help="User identifier for LiteLLM tags"),
    all: bool = typer.Option(False, "--all", help="Perform all generation steps"),
) -> int
```

**Key Features:**
- Comprehensive book configuration options
- Project type presets (short_story, novella, book, novel, epic)
- Flexible chapter and character count specifications
- Auto-title generation based on content
- Mock mode for testing without API consumption
- Granular control over generation steps
- User identification for LiteLLM tracking

**Project Types:**
- `short_story`: 1-3 chapters, 1-3 characters, 1-2 scenes per chapter
- `novella`: 4-8 chapters, 2-5 characters, 2-4 scenes per chapter
- `book`: 8-15 chapters, 3-8 characters, 3-5 scenes per chapter
- `novel`: 15-25 chapters, 5-12 characters, 3-6 scenes per chapter
- `epic`: 25+ chapters, 8+ characters, 4-8 scenes per chapter

**Usage Examples:**

```bash
# Create a complete novel with auto-generated title
create-book --project-type=novel --genre=fantasy --all --auto-title --mock

# Create with specific title and custom configuration
create-book --title="My Fantasy Novel" --config-file=config.json --all

# Create with custom project name (spaces allowed)
create-book --project-name="my custom project" --all --auto-title --mock

# Create with manual overrides
create-book --project-type=novel --chapters=20 --scenes-per-chapter=4-6 --all
```

### book_stats()

Displays comprehensive project statistics with automatic logging.

```python
@app.command(name="book-stats")
def book_stats(
    project_name: str = typer.Option(..., "--project-name", help="Project name to display statistics for"),
    show_logs: bool = typer.Option(False, "--show-logs", help="Display the last 20 lines of the log file"),
) -> None
```

**Features:**
- Non-interactive operation (suitable for automation)
- Automatic log file creation and management
- Comprehensive project metadata display
- Chapter status overview (exists vs. missing)
- Dynamic questions and answers display
- Optional log file viewing (last 20 lines)
- Timestamped logging of all statistics

**Display Information:**
- Project metadata (title, genre, language, category)
- Content metrics (chapters, characters, book length)
- Configuration settings (worldbuilding, review preferences)
- Chapter status (file existence)
- Log file information and location

**Logging Format:**
```
2025-08-15 11:19:29,107 - INFO - === BOOK STATISTICS REPORT ===
2025-08-15 11:19:29,107 - INFO - Statistics generated for project: my-project
2025-08-15 11:19:29,108 - INFO - Project Name: my-project
2025-08-15 11:19:29,109 - INFO - Title: My Book Title
...
2025-08-15 11:19:29,117 - INFO - === END STATISTICS REPORT ===
```

### generate_title()

Generates improved titles for existing projects based on their content.

```python
@app.command()
def generate_title(
    project_name: str = typer.Option(..., prompt="Project name"),
    config_file: str = typer.Option(None, "--config-file", help="Configuration file path"),
    mock: bool = typer.Option(False, "--mock", help="Use mock LLM provider"),
    user: str | None = typer.Option(None, "--user", help="User identifier for LiteLLM tags"),
) -> None
```

**Requirements:**
- Project must exist with `project_data.json`
- Auto-title must be enabled OR title must be "Untitled"
- Sufficient content must be available (chapters, characters, or outline)

**Process:**
1. Loads existing project data
2. Validates title generation requirements
3. Analyzes available content (chapters, characters, outline)
4. Generates new title using LLM
5. Updates project data file
6. Provides feedback on success/failure

**Content Analysis:**
- Chapter content and themes
- Character profiles and relationships
- Outline structure and plot points
- Genre and tone consistency

### resume()

Resumes incomplete projects from the last checkpoint.

```python
@app.command()
def resume(
    project_name: str = typer.Option(..., prompt="Project name to resume"),
) -> None
```

**Process:**
1. Loads existing project data
2. Checks for missing content (outline, characters, worldbuilding)
3. Generates missing content in dependency order
4. Continues writing chapters from last checkpoint
5. Formats book if all chapters exist
6. Generates title if auto-title is enabled

**Status:** Partially implemented - basic functionality available

## Async Command Functions

### Placeholder Commands

The following commands are defined but not fully implemented:

#### concept()
```python
@app.command()
async def concept(project_name: str = typer.Option(..., prompt="Project name")) -> None
```

#### outline()
```python
@app.command()
async def outline(project_name: str = typer.Option(..., prompt="Project name")) -> None
```

#### characters()
```python
@app.command()
async def characters(project_name: str = typer.Option(..., prompt="Project name")) -> None
```

#### worldbuilding()
```python
@app.command()
async def worldbuilding(project_name: str = typer.Option(..., prompt="Project name")) -> None
```

#### write()
```python
@app.command()
async def write(
    project_name: str = typer.Option(..., prompt="Project name"),
    chapter_number: int = typer.Option(..., prompt="Chapter number"),
) -> None
```

#### edit()
```python
@app.command()
async def edit(
    project_name: str = typer.Option(..., prompt="Project name"),
    chapter_number: int = typer.Option(..., prompt="Chapter number to edit"),
) -> None
```

#### format()
```python
@app.command()
async def format(
    project_name: str = typer.Option(..., prompt="Project name"),
    _output_format: str = typer.Option(None, "--output-format", help="Output format (md or pdf)"),
) -> None
```

#### research()
```python
@app.command()
async def research(query: str = typer.Option(..., prompt="Research query")) -> None
```

**Status:** All placeholder commands show "NOT IMPLEMENTED" or "NOT FULLY SUPPORTED" messages.

## Usage Examples

### Complete Book Creation Workflow

```bash
# 1. Create a complete book with all steps
hatch run python -m libriscribe2.cli create-book \
    --title="The Dragon's Quest" \
    --genre=fantasy \
    --description="An epic fantasy adventure" \
    --category=fiction \
    --characters=5 \
    --worldbuilding \
    --all

# 2. Check project statistics
hatch run python -m libriscribe2.cli book-stats \
    --project-name="the-dragons-quest" \
    --show-logs

# 3. Generate a better title based on content
hatch run python -m libriscribe2.cli generate-title \
    --project-name="the-dragons-quest"

# 4. Resume if interrupted
hatch run python -m libriscribe2.cli resume \
    --project-name="the-dragons-quest"
```

### Testing and Development

```bash
# Use mock mode for testing without API consumption
hatch run python -m libriscribe2.cli create-book \
    --project-type=short_story \
    --genre=mystery \
    --auto-title \
    --mock \
    --all

# Custom configuration for development
hatch run python -m libriscribe2.cli create-book \
    --config-file=config-dev.json \
    --log-level=DEBUG \
    --title="Development Test" \
    --all
```

### Automation and Scripting

```bash
# Batch processing multiple projects
for project_type in short_story novella novel; do
    hatch run python -m libriscribe2.cli create-book \
        --project-type="$project_type" \
        --genre=fantasy \
        --auto-title \
        --mock \
        --all
done

# CI/CD integration with exit code checking
if hatch run python -m libriscribe2.cli create-book --title="CI Test" --mock --all; then
    echo "Book creation successful"
    hatch run python -m libriscribe2.cli book-stats --project-name="ci-test"
else
    echo "Book creation failed with exit code $?"
    exit 1
fi
```

## Configuration Integration

### Configuration File Support

The CLI supports multiple configuration formats:

```bash
# JSON configuration
--config-file=config.json

# YAML configuration
--config-file=config.yaml

# Environment file
--config-file=.env
```

### Mock Mode

Mock mode enables testing without API consumption:

```bash
# Enable mock mode
--mock

# Mock mode with user identification
--mock --user="test-user-123"
```

### LiteLLM Integration

User identification for LiteLLM tracking:

```bash
# Add user identifier for tracking
--user="user-123"

# User identifier with spaces
--user="John Doe - Project Alpha"
```

## Error Handling and Recovery

### Comprehensive Error Handling

```python
try:
    # Command logic
    return 0  # Success
except ValueError as e:
    console.print(f"[red]❌ Invalid input: {e}[/red]")
    return 2  # Invalid input
except ImportError as e:
    console.print(f"[red]❌ Import Error: {e}[/red]")
    return 3  # Missing dependencies
except RuntimeError as e:
    console.print(f"[red]{e}[/red]")
    return 1  # Runtime error
except Exception as e:
    logger.exception("Unexpected error")
    console.print(f"[red]❌ Unexpected error: {e}[/red]")
    return 1  # General error
```

### Error Recovery Guidance

The CLI provides specific guidance for common errors:

```bash
# Missing dependencies
❌ Import Error: No module named 'libriscribe2'
💡 This might be due to:
   - Missing dependencies (run 'hatch run pip install -e .')
   - Python version mismatch (this project requires Python 3.12+)
   - Incorrect PYTHONPATH

# Invalid input
❌ Invalid input: Invalid project type 'invalid'
💡 Check your command line arguments and try again.

# Runtime errors
❌ Failed to create book.
💡 Check the logs for more details.
```

## Performance and Optimization

### Async Support

Commands that perform I/O intensive operations use async/await:

```python
@app.command()
async def async_command():
    """Async command for I/O intensive operations."""
    result = await some_async_operation()
    return result
```

### Resource Management

- Automatic cleanup of temporary resources
- Proper file handle management
- Memory-efficient processing for large projects

### Logging Optimization

- Minimal console output (CRITICAL level only)
- Comprehensive file logging (DEBUG level)
- Efficient log rotation and management

## Integration Points

### BookCreatorService Integration

```python
from libriscribe2.services.book_creator import BookCreatorService

book_creator = BookCreatorService(
    config_file=config_file,
    mock=mock,
    log_file=log_file,
    log_level=log_level,
)

result = asyncio.run(book_creator.acreate_book(args))
```

### ProjectManagerAgent Integration

```python
from libriscribe2.agents.project_manager import ProjectManagerAgent

settings = Settings(env_file=env_file, config_file=config_file)
project_manager = ProjectManagerAgent(settings=settings)
```

### Settings Integration

```python
from libriscribe2.settings import Settings

settings = Settings()  # Loads from default locations
settings = Settings(config_file=config_file)  # Custom config
```

## Best Practices

### Command Usage

1. **Use NON-INTERACTIVE commands** for production workflows
2. **Use --mock flag** for testing without API consumption
3. **Specify --config-file** for consistent configuration
4. **Use --all flag** for complete book generation
5. **Check exit codes** in automated workflows

### Error Handling

1. **Check return codes** for workflow integration
2. **Review log files** for detailed error information
3. **Use appropriate log levels** for debugging
4. **Handle missing dependencies** gracefully

### Performance

1. **Use async commands** for I/O intensive operations
2. **Configure appropriate timeouts** for LLM calls
3. **Monitor resource usage** during book generation
4. **Use parallel processing** where available

## Future Enhancements

### Planned Features

1. **Interactive Mode Implementation**: Full implementation of interactive commands
2. **Advanced Formatting Options**: PDF generation, custom templates
3. **Research Integration**: Web research and fact-checking
4. **Collaboration Features**: Multi-user project support
5. **Plugin System**: Extensible command system

### API Improvements

1. **RESTful API**: HTTP API for web integration
2. **WebSocket Support**: Real-time updates
3. **GraphQL Interface**: Flexible data querying
4. **Webhook Integration**: Event-driven workflows

## See Also

- [BookCreator Service API](book-creator-api.md)
- [ProjectManager API](project-manager-api.md)
- [Settings Configuration](../user-guide/configuration.md)
- [Installation Guide](../../INSTALL.md)
- [CLI Usage Examples](../../examples/cli_usage_examples.md)
