# LibriScribe2 CLI - Function Signatures

## Complete API Reference

### Module-Level Functions

#### setup_application_logging()

```python
def setup_application_logging() -> Path
```

Set up application-level logging before any project is created.

**Returns:**
- `Path`: Path to the created log file

**Side Effects:**
- Creates `logs/` directory if it doesn't exist
- Creates timestamped log file: `logs/libriscribe_{timestamp}.log`
- Configures file handler with DEBUG level logging
- Adds file handler to root logger

#### custom_help()

```python
def custom_help() -> None
```

Display custom help with Rich formatting.

**Features:**
- Colored tables showing command categories
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

Show version and exit.

**Parameters:**
- `_ctx` (typer.Context): Typer context (unused)
- `version` (bool): Whether to show version

**Raises:**
- `typer.Exit`: Always exits after showing version

#### log_command_start()

```python
def log_command_start() -> None
```

Log the start of a command execution.

**Logs:**
- Current timestamp
- Program arguments
- Command execution start marker

#### suppress_traceback()

```python
def suppress_traceback(
    exc_type: type[BaseException],
    exc_value: BaseException,
    _exc_traceback: Any
) -> None
```

Suppress traceback output to console.

**Parameters:**
- `exc_type` (type[BaseException]): Exception type
- `exc_value` (BaseException): Exception instance
- `_exc_traceback` (Any): Traceback object (unused)

**Behavior:**
- Logs full traceback to file
- Shows minimal error message to console
- Ignores KeyboardInterrupt

### Command Functions

#### start()

```python
@app.command()
def start(
    env_file: str = typer.Option(None, "--env-file", help="Path to a custom .env file"),
    config_file: str = typer.Option(None, "--config-file", help="Path to a custom JSON/YAML config file"),
) -> None
```

Starts the interactive book creation process (ADVANCED - NOT FULLY SUPPORTED).

**Parameters:**
- `env_file` (str, optional): Path to custom .env file
- `config_file` (str, optional): Path to custom JSON/YAML config file

**Status:** NOT IMPLEMENTED - Shows error message

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
) -> int
```

Create a new book using command-line arguments without interactive prompts.

**Parameters:**
- `title` (str, optional): Book title
- `project_name` (str, optional): Custom project folder name
- `auto_title` (bool): Auto-generate title based on content
- `category` (str): Book category, default "Fiction"
- `project_type` (str): Project type, default "novel"
- `genre` (str, optional): Book genre
- `description` (str, optional): Book description or synopsis
- `language` (str): Book language, default "English"
- `chapters` (str, optional): Number of chapters to generate
- `characters` (str, optional): Number of characters to create
- `scenes_per_chapter` (str, optional): Scene range per chapter
- `target_audience` (str): Target audience, default "General"
- `worldbuilding` (bool): Enable worldbuilding
- `config_file` (str, optional): Path to configuration file
- `log_file` (str, optional): Path to log file
- `log_level` (str): Log level, default "INFO"
- `mock` (bool): Use mock LLM provider
- `generate_concept` (bool): Generate book concept
- `generate_outline` (bool): Generate book outline
- `generate_characters` (bool): Generate character profiles
- `generate_worldbuilding` (bool): Generate worldbuilding details
- `write_chapters` (bool): Write all chapters
- `format_book` (bool): Format the book into final output
- `user` (str, optional): User identifier for LiteLLM tags
- `all` (bool): Perform all generation steps

**Returns:**
- `int`: Exit code (0 = success, >0 = error)

**Exit Codes:**
- `0`: Success
- `1`: Runtime error or unexpected error
- `2`: Invalid input (ValueError)
- `3`: Import error (missing dependencies)
- `5`: Book creation failed

#### book_stats()

```python
@app.command(name="book-stats")
def book_stats(
    project_name: str = typer.Option(..., "--project-name", help="Project name to display statistics for"),
    show_logs: bool = typer.Option(False, "--show-logs", help="Display the last 20 lines of the log file"),
) -> None
```

Displays statistics for a book project (NON-INTERACTIVE - RECOMMENDED).

**Parameters:**
- `project_name` (str): Name of the project to analyze
- `show_logs` (bool): Whether to display recent log entries

**Features:**
- Project metadata display
- Chapter status overview
- Dynamic questions and answers
- Automatic log file creation and logging
- Optional log file viewing (last 20 lines)
- Error handling for missing projects

**Logging:**
- Automatically logs all statistics to project log file
- Creates log file if it doesn't exist
- Timestamped entries for tracking

**Raises:**
- `FileNotFoundError`: When project is not found
- `ValueError`: When project data is invalid

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
) -> None
```

Generate a better title for an existing project based on its content.

**Parameters:**
- `project_name` (str): Name of the existing project
- `config_file` (str, optional): Path to configuration file
- `mock` (bool): Whether to use mock LLM provider
- `user` (str, optional): User identifier for LiteLLM tags

**Requirements:**
- Project must exist with project_data.json
- Auto-title must be enabled or title must be "Untitled"
- Sufficient content must be available (chapters, characters, or outline)

**Raises:**
- `FileNotFoundError`: When project is not found
- `ValueError`: When project data is invalid

#### resume()

```python
@app.command()
def resume(
    project_name: str = typer.Option(..., prompt="Project name to resume"),
) -> None
```

Resumes a project from the last checkpoint (ADVANCED - NOT FULLY SUPPORTED).

**Parameters:**
- `project_name` (str): Name of the project to resume

**Process:**
1. Loads existing project data
2. Checks for missing content (outline, characters, worldbuilding)
3. Generates missing content in order
4. Continues writing chapters from last checkpoint
5. Formats book if all chapters exist
6. Generates title if auto-title is enabled

**Status:** PARTIALLY IMPLEMENTED - Basic functionality available

**Raises:**
- `FileNotFoundError`: When project is not found
- `ValueError`: When project data is invalid

### Async Command Functions

#### concept()

```python
@app.command()
async def concept(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None
```

Generates a book concept (ADVANCED - NOT FULLY SUPPORTED).

**Parameters:**
- `project_name` (str): Name of the project

**Status:** NOT IMPLEMENTED - Placeholder function

#### outline()

```python
@app.command()
async def outline(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None
```

Generates a book outline (ADVANCED - NOT FULLY SUPPORTED).

**Parameters:**
- `project_name` (str): Name of the project

**Status:** NOT IMPLEMENTED - Placeholder function

#### characters()

```python
@app.command()
async def characters(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None
```

Generates character profiles (ADVANCED - NOT FULLY SUPPORTED).

**Parameters:**
- `project_name` (str): Name of the project

**Status:** NOT IMPLEMENTED - Placeholder function

#### worldbuilding()

```python
@app.command()
async def worldbuilding(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None
```

Generates worldbuilding details (ADVANCED - NOT FULLY SUPPORTED).

**Parameters:**
- `project_name` (str): Name of the project

**Status:** NOT IMPLEMENTED - Placeholder function

#### write()

```python
@app.command()
async def write(
    project_name: str = typer.Option(..., prompt="Project name"),
    chapter_number: int = typer.Option(..., prompt="Chapter number"),
) -> None
```

Writes a specific chapter, with review process (ADVANCED - NOT FULLY SUPPORTED).

**Parameters:**
- `project_name` (str): Name of the project
- `chapter_number` (int): Chapter number to write

**Status:** NOT IMPLEMENTED - Placeholder function

#### edit()

```python
@app.command()
async def edit(
    project_name: str = typer.Option(..., prompt="Project name"),
    chapter_number: int = typer.Option(..., prompt="Chapter number to edit"),
) -> None
```

Edits and refines a specific chapter (ADVANCED - NOT FULLY SUPPORTED).

**Parameters:**
- `project_name` (str): Name of the project
- `chapter_number` (int): Chapter number to edit

**Status:** NOT IMPLEMENTED - Placeholder function

#### format()

```python
@app.command()
async def format(
    project_name: str = typer.Option(..., prompt="Project name"),
    _output_format: str = typer.Option(
        None, "--output-format",
        help="Output format (md or pdf)"
    ),
) -> None
```

Formats the entire book into a single Markdown or PDF file (ADVANCED - NOT FULLY SUPPORTED).

**Parameters:**
- `project_name` (str): Name of the project
- `_output_format` (str, optional): Output format (currently unused)

**Status:** PARTIALLY IMPLEMENTED - Basic formatting available

#### research()

```python
@app.command()
async def research(
    query: str = typer.Option(..., prompt="Research query")
) -> None
```

Performs web research on a given query (ADVANCED - NOT FULLY SUPPORTED).

**Parameters:**
- `query` (str): Research query string

**Status:** NOT IMPLEMENTED - Placeholder function

## Global Variables

### console

```python
console: Console
```

Rich console instance for formatted output.

**Type:** `rich.console.Console`

**Usage:**
- Colored output
- Progress bars
- Tables and panels
- Error messages

### project_manager

```python
project_manager: ProjectManagerAgent
```

Global project manager instance.

**Type:** `libriscribe2.agents.project_manager.ProjectManagerAgent`

**Usage:**
- Project creation and management
- Content generation coordination
- State management

### app_log_file

```python
app_log_file: Path
```

Path to the application log file.

**Type:** `pathlib.Path`

**Format:** `logs/libriscribe_{timestamp}.log`

## Type Annotations Summary

### Common Parameter Types

```python
# String parameters
title: str
project_name: str
config_file: str
log_file: str
genre: str
description: str
language: str

# Optional string parameters
title: str = typer.Option(None, ...)
config_file: str = typer.Option(None, ...)
user: str | None = typer.Option(None, ...)

# Boolean parameters
auto_title: bool = typer.Option(False, ...)
worldbuilding: bool = typer.Option(False, ...)
mock: bool = typer.Option(False, ...)

# String parameters with defaults
category: str = typer.Option("Fiction", ...)
language: str = typer.Option("English", ...)
log_level: str = typer.Option("INFO", ...)

# Required parameters with prompts
project_name: str = typer.Option(..., prompt="Project name")
```

### Return Types

```python
# Void functions
-> None

# Exit code functions
-> int

# Path functions
-> Path
```

### Exception Types

```python
# Standard exceptions
FileNotFoundError
ValueError
ImportError
RuntimeError

# Typer exceptions
typer.Exit
```

## Usage Patterns

### Basic Command Structure

```python
@app.command()
def command_name(
    param: str = typer.Option(default, "--flag", help="Description")
) -> ReturnType:
    """Command description."""
    # Implementation
```

### Async Command Structure

```python
@app.command()
async def async_command(
    param: str = typer.Option(..., prompt="Prompt text")
) -> None:
    """Async command description."""
    # Async implementation
```

### Error Handling Pattern

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
except Exception as e:
    logger.exception("Unexpected error")
    console.print(f"[red]❌ Unexpected error: {e}[/red]")
    return 1  # General error
```

### Logging Pattern

```python
def command_function():
    """Command with logging."""
    log_command_start()  # Log command execution start

    try:
        # Command logic
        logger.info("Command completed successfully")
    except Exception as e:
        logger.exception("Command failed")
        raise
```

## Import Requirements

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

## Command Registration

```python
# Create Typer app
app = typer.Typer(
    help="LibriScribe2 - Modern book creation CLI",
    rich_markup_mode="rich",
    callback=version_callback,
    invoke_without_command=True,
)

# Register commands with decorators
@app.command()
def command_name():
    pass

@app.command(name="custom-name")
def function_name():
    pass
```

## Entry Point

```python
if __name__ == "__main__":
    # Check if --help is used and no subcommand is specified
    if "--help" in sys.argv and len(sys.argv) == 2:
        custom_help()
        sys.exit(0)
    else:
        app()
```
