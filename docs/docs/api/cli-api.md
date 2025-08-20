# LibriScribe2 CLI API Documentation

## Overview

The LibriScribe2 CLI provides a comprehensive command-line interface for creating, managing, and analyzing book projects. The CLI is built using Typer and Rich for enhanced user experience with colored output and interactive prompts.

## Module Structure

```python
# src/libriscribe2/cli.py
"""
LibriScribe2 - Modern book creation CLI with rich output and type safety.
"""
```

## Core Components

### Application Setup

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
console: Console  # Rich console for formatted output
project_manager: ProjectManagerAgent  # Global project manager instance
app_log_file: Path  # Application log file path
```

## Command Categories

### 🟢 NON-INTERACTIVE (RECOMMENDED)

These commands are fully implemented and production-ready:

- `create-book` - Create books with command-line arguments
- `book-stats` - View book statistics
- `format` - Format existing books
- `generate-title` - Generate titles for existing projects

### 🟡 INTERACTIVE (ADVANCED)

These commands are partially implemented or experimental:

- `start` - Interactive book creation
- `concept` - Generate concept for existing project
- `outline` - Generate outline for existing project
- `characters` - Generate characters for existing project
- `worldbuilding` - Generate worldbuilding for existing project
- `write` - Write specific chapter
- `edit` - Edit specific chapter
- `research` - Research functionality
- `resume` - Resume existing project

## Function Signatures

### Utility Functions

#### setup_application_logging()

```python
def setup_application_logging() -> Path:
    """Set up application-level logging before any project is created.

    Returns:
        Path: Path to the created log file

    Creates:
        - logs/ directory if it doesn't exist
        - Timestamped log file: logs/libriscribe_{timestamp}.log
        - File handler with DEBUG level logging
    """
```

#### custom_help()

```python
def custom_help() -> None:
    """Display custom help with Rich formatting.

    Features:
        - Colored tables showing command categories
        - Usage recommendations
        - Command descriptions
    """
```

#### version_callback()

```python
def version_callback(
    _ctx: typer.Context,
    version: bool = typer.Option(None, "--version", "-v", help="Show version and exit")
) -> None:
    """Show version and exit.

    Args:
        _ctx: Typer context (unused)
        version: Whether to show version

    Raises:
        typer.Exit: Always exits after showing version
    """
```

#### log_command_start()

```python
def log_command_start() -> None:
    """Log the start of a command execution.

    Logs:
        - Current timestamp
        - Program arguments
        - Command execution start marker
    """
```

#### suppress_traceback()

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

### Command Functions

#### start()

```python
@app.command()
def start(
    env_file: str = typer.Option(None, "--env-file", help="Path to a custom .env file"),
    config_file: str = typer.Option(None, "--config-file", help="Path to a custom JSON/YAML config file"),
) -> None:
    """Starts the interactive book creation process (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        env_file: Path to custom .env file
        config_file: Path to custom JSON/YAML config file

    Status:
        NOT IMPLEMENTED - Shows error message
    """
```

#### create_book()

```python
@app.command(name="create-book")
def create_book(
    title: str = typer.Option(
        None, "--title", "-t",
        help="Book title (optional - use --auto-title to generate based on content)"
    ),
    project_name: str = typer.Option(
        None, "--project-name", "-p",
        help="Custom project folder name (spaces allowed, must be empty or non-existent)"
    ),
    auto_title: bool = typer.Option(
        False, "--auto-title",
        help="Auto-generate title based on content (skipped if title is provided)"
    ),
    category: str = typer.Option(
        "Fiction", "--category", "-c",
        help="Book category [default: Fiction]"
    ),
    project_type: str = typer.Option(
        "novel", "--project-type",
        help="Project type: short_story, novella, book, novel, epic [default: novel]"
    ),
    genre: str = typer.Option(
        None, "--genre", "-g",
        help="Book genre (e.g., fantasy, mystery, romance)"
    ),
    description: str = typer.Option(
        None, "--description", "-d",
        help="Book description or synopsis"
    ),
    language: str = typer.Option(
        "English", "--language", "-l",
        help="Book language [default: English]"
    ),
    chapters: str = typer.Option(
        None, "--chapters",
        help="Number of chapters to generate (e.g., 10, 8-12) (overrides project-type)"
    ),
    characters: str = typer.Option(
        None, "--characters",
        help="Number of characters to create (e.g., 5, 3-7, 5+)"
    ),
    scenes_per_chapter: str = typer.Option(
        None, "--scenes-per-chapter",
        help="Scene range per chapter (e.g., 3-6, 4-8, 5) (overrides project-type)"
    ),
    target_audience: str = typer.Option(
        "General", "--target-audience",
        help="Target audience (e.g., General, Young Adult, Adult, Children) [default: General]",
    ),
    worldbuilding: bool = typer.Option(
        False, "--worldbuilding",
        help="Enable worldbuilding for the book"
    ),
    config_file: str = typer.Option(
        None, "--config-file",
        help="Path to configuration file (.env, .yaml, .yml, or .json)"
    ),
    log_file: str = typer.Option(
        None, "--log-file",
        help="Path to log file"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level",
        help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) [default: INFO]"
    ),
    mock: bool = typer.Option(
        False, "--mock",
        help="Use mock LLM provider for testing"
    ),
    generate_concept: bool = typer.Option(
        False, "--generate-concept",
        help="Generate book concept"
    ),
    generate_outline: bool = typer.Option(
        False, "--generate-outline",
        help="Generate book outline"
    ),
    generate_characters: bool = typer.Option(
        False, "--generate-characters",
        help="Generate character profiles"
    ),
    generate_worldbuilding: bool = typer.Option(
        False, "--generate-worldbuilding",
        help="Generate worldbuilding details (requires --worldbuilding)"
    ),
    write_chapters: bool = typer.Option(
        False, "--write-chapters",
        help="Write all chapters"
    ),
    format_book: bool = typer.Option(
        False, "--format-book",
        help="Format the book into final output"
    ),
    user: str | None = typer.Option(
        None, "--user",
        help="User identifier for LiteLLM tags (spaces allowed)"
    ),
    all: bool = typer.Option(
        False, "--all",
        help="Perform all generation steps (concept, outline, characters, worldbuilding, chapters, formatting)",
    ),
) -> int:
    """Create a new book using command-line arguments without interactive prompts.

    Returns:
        int: Exit code (0 = success, >0 = error)

    Exit Codes:
        0: Success
        1: Runtime error or unexpected error
        2: Invalid input (ValueError)
        3: Import error (missing dependencies)
        5: Book creation failed

    Examples:
        # Create a short story with auto-generated title (using mock for testing)
        create-book --project-type=short_story --genre=fantasy --all --auto-title --mock

        # Create a novel with specific title
        create-book --title="My Fantasy Novel" --project-type=novel --genre=fantasy --all --mock

        # Create with custom configuration
        create-book --config-file=config-example.json --project-type=novel --all --auto-title --mock
    """
```

#### book_stats()

```python
@app.command(name="book-stats")
def book_stats(
    project_name: str = typer.Option(..., "--project-name", help="Project name to display statistics for"),
    show_logs: bool = typer.Option(False, "--show-logs", help="Display the last 20 lines of the log file"),
) -> None:
    """Displays statistics for a book project (NON-INTERACTIVE - RECOMMENDED).

    Args:
        project_name: Name of the project to analyze
        show_logs: Whether to display recent log entries

    Features:
        - Project metadata display
        - Chapter status overview
        - Dynamic questions and answers
        - Automatic log file creation and logging
        - Optional log file viewing (last 20 lines)
        - Error handling for missing projects

    Displays:
        - Title, genre, language, category
        - Book length and character count
        - Chapter count and worldbuilding status
        - Review preferences
        - Chapter existence status
        - Log file information and contents (optional)

    Logging:
        - Automatically logs all statistics to project log file
        - Creates log file if it doesn't exist
        - Timestamped entries for tracking
    """
```

#### generate_title()

```python
@app.command()
def generate_title(
    project_name: str = typer.Option(..., prompt="Project name"),
    config_file: str = typer.Option(
        None, "--config-file",
        help="Path to configuration file"
    ),
    mock: bool = typer.Option(
        False, "--mock",
        help="Use mock LLM provider for testing"
    ),
    user: str | None = typer.Option(
        None, "--user",
        help="User identifier for LiteLLM tags (spaces allowed)"
    ),
) -> None:
    """Generate a better title for an existing project based on its content.

    Args:
        project_name: Name of the existing project
        config_file: Path to configuration file
        mock: Whether to use mock LLM provider
        user: User identifier for LiteLLM tags

    Requirements:
        - Project must exist with project_data.json
        - Auto-title must be enabled or title must be "Untitled"
        - Sufficient content must be available (chapters, characters, or outline)

    Process:
        1. Loads existing project
        2. Checks if title generation is needed
        3. Generates new title based on content
        4. Updates project data file
        5. Provides feedback on success/failure
    """
```

#### resume()

```python
@app.command()
def resume(
    project_name: str = typer.Option(..., prompt="Project name to resume"),
) -> None:
    """Resumes a project from the last checkpoint (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name: Name of the project to resume

    Process:
        1. Loads existing project data
        2. Checks for missing content (outline, characters, worldbuilding)
        3. Generates missing content in order
        4. Continues writing chapters from last checkpoint
        5. Formats book if all chapters exist
        6. Generates title if auto-title is enabled

    Status:
        PARTIALLY IMPLEMENTED - Basic functionality available
    """
```

### Async Command Functions

#### concept()

```python
@app.command()
async def concept(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None:
    """Generates a book concept (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name: Name of the project

    Status:
        NOT IMPLEMENTED - Placeholder function
    """
```

#### outline()

```python
@app.command()
async def outline(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None:
    """Generates a book outline (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name: Name of the project

    Status:
        NOT IMPLEMENTED - Placeholder function
    """
```

#### characters()

```python
@app.command()
async def characters(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None:
    """Generates character profiles (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name: Name of the project

    Status:
        NOT IMPLEMENTED - Placeholder function
    """
```

#### worldbuilding()

```python
@app.command()
async def worldbuilding(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None:
    """Generates worldbuilding details (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name: Name of the project

    Status:
        NOT IMPLEMENTED - Placeholder function
    """
```

#### write()

```python
@app.command()
async def write(
    project_name: str = typer.Option(..., prompt="Project name"),
    chapter_number: int = typer.Option(..., prompt="Chapter number"),
) -> None:
    """Writes a specific chapter, with review process (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name: Name of the project
        chapter_number: Chapter number to write

    Status:
        NOT IMPLEMENTED - Placeholder function
    """
```

#### edit()

```python
@app.command()
async def edit(
    project_name: str = typer.Option(..., prompt="Project name"),
    chapter_number: int = typer.Option(..., prompt="Chapter number to edit"),
) -> None:
    """Edits and refines a specific chapter (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name: Name of the project
        chapter_number: Chapter number to edit

    Status:
        NOT IMPLEMENTED - Placeholder function
    """
```

#### format()

```python
@app.command()
async def format(
    project_name: str = typer.Option(..., prompt="Project name"),
    _output_format: str = typer.Option(
        None, "--output-format",
        help="Output format (md or pdf)"
    ),
) -> None:
    """Formats the entire book into a single Markdown or PDF file (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name: Name of the project
        _output_format: Output format (currently unused)

    Status:
        PARTIALLY IMPLEMENTED - Basic formatting available
    """
```

#### research()

```python
@app.command()
async def research(
    query: str = typer.Option(..., prompt="Research query")
) -> None:
    """Performs web research on a given query (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        query: Research query string

    Status:
        NOT IMPLEMENTED - Placeholder function
    """
```

## Usage Examples

### Basic Book Creation

```bash
# Create a complete book with all steps
hatch run python -m libriscribe2.main create-book \
    --title="My Awesome Book" \
    --genre=fantasy \
    --description="A tale of epic proportions" \
    --category=fiction \
    --characters=3 \
    --worldbuilding \
    --all

# Create with auto-generated title
hatch run python -m libriscribe2.main create-book \
    --project-type=novel \
    --genre=mystery \
    --auto-title \
    --all \
    --mock

# Create with custom project name
hatch run python -m libriscribe2.main create-book \
    --title="My Book" \
    --project-name="my custom project" \
    --all
```

### Project Management

```bash
# View book statistics
hatch run python -m libriscribe2.main book-stats --project-name my_book

# Generate title for existing project
hatch run python -m libriscribe2.main generate-title --project-name my_book

# Resume incomplete project
hatch run python -m libriscribe2.main resume --project-name my_book
```

### Configuration Options

```bash
# Use custom configuration file
hatch run python -m libriscribe2.main create-book \
    --config-file=config-example.json \
    --title="My Book" \
    --all

# Use mock mode for testing
hatch run python -m libriscribe2.main create-book \
    --title="Test Book" \
    --mock \
    --all

# Set custom log level
hatch run python -m libriscribe2.main create-book \
    --title="My Book" \
    --log-level=DEBUG \
    --all
```

## Error Handling

The CLI implements comprehensive error handling with specific exit codes:

- **Exit Code 0**: Success
- **Exit Code 1**: Runtime error or unexpected error
- **Exit Code 2**: Invalid input (ValueError)
- **Exit Code 3**: Import error (missing dependencies)
- **Exit Code 5**: Book creation failed

### Error Recovery

```python
# Errors are logged to file with full traceback
# Console shows minimal error message
# Specific error codes allow workflow integration
```

## Logging

### Application Logging

- **File**: `logs/libriscribe_{timestamp}.log`
- **Level**: DEBUG (all messages captured)
- **Format**: `%(asctime)s %(levelname)s %(name)s %(message)s`

### Console Logging

- **Level**: CRITICAL (minimal console output)
- **Format**: `%(message)s`
- **Traceback**: Suppressed (logged to file only)

## Integration

### Workflow Integration

The CLI is designed for integration with external workflows:

```bash
# Check exit code for workflow decisions
if hatch run python -m libriscribe2.main create-book --title="Test" --all; then
    echo "Book creation successful"
else
    echo "Book creation failed with exit code $?"
fi
```

### Configuration Files

Supports multiple configuration formats:

- `.env` files
- JSON configuration files
- YAML configuration files

## Dependencies

### Required Imports

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
from libriscribe2.settings import MANUSCRIPT_MD_FILENAME, Settings
from libriscribe2.utils.timestamp_utils import format_timestamp_for_filename
```

### External Dependencies

- **typer**: CLI framework
- **rich**: Enhanced console output
- **asyncio**: Async command support
- **pathlib**: Path handling
- **logging**: Comprehensive logging

## Recent Changes

### Log File Path Display Enhancement

**Change**: Updated error message in `book_stats()` command to show the actual log file path when no log file is found.

**Before**:
```python
console.print(f"[yellow]No log file found for '{project_name}'.[/yellow]")
```

**After**:
```python
console.print(f"[yellow]No log file found at {project_log_file}.[/yellow]")
```

**Impact**: Provides more specific information to users about where the system expected to find the log file, improving debugging and user experience.

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

## See Also

- [ProjectManager API](project-manager-api.md)
- [Settings Configuration](../user-guide/configuration.md)
