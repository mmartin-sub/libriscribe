# LibriScribe2 CLI - Complete Function Signatures

## Overview

This document provides complete function signatures for all functions and classes in the LibriScribe2 CLI module (`src/libriscribe2/cli.py`).

## Module-Level Variables

```python
console: Console = Console()
project_manager: ProjectManagerAgent
app_log_file: Path
```

## Application Setup

```python
app: typer.Typer = typer.Typer(
    help="LibriScribe2 - Modern book creation CLI",
    rich_markup_mode="rich",
    callback=version_callback,
    invoke_without_command=True,
)
```

## Utility Functions

### setup_application_logging()

```python
def setup_application_logging() -> Path:
    """Set up application-level logging before any project is created.

    Returns:
        Path: Path to the created log file (logs/libriscribe_{timestamp}.log)

    Side Effects:
        - Creates logs/ directory if it doesn't exist
        - Creates timestamped log file with UTF-8 encoding
        - Configures file handler with DEBUG level logging
        - Adds file handler to root logger

    Example:
        >>> app_log_file = setup_application_logging()
        >>> print(f"Logging to: {app_log_file}")
        Logging to: logs/libriscribe_20250815_143022.log
    """
```

### custom_help()

```python
def custom_help() -> None:
    """Display custom help with Rich formatting.

    Features:
        - Colored tables showing command categories
        - Usage recommendations
        - Command descriptions
        - Rich console formatting with panels and tables

    Output:
        Displays formatted help to console with:
        - Title and description
        - Recommended commands table (green)
        - Advanced commands table (yellow)
        - Usage recommendation panel

    Example:
        >>> custom_help()
        LibriScribe2 - Modern book creation CLI

        🟢 NON-INTERACTIVE (RECOMMENDED)
        ┌─────────────┬─────────────────────────────────────┐
        │ Command     │ Description                         │
        ├─────────────┼─────────────────────────────────────┤
        │ create-book │ Create books with command-line args │
        │ book-stats  │ View book statistics                │
        └─────────────┴─────────────────────────────────────┘
    """
```

### version_callback()

```python
def version_callback(
    _ctx: typer.Context,
    version: bool = typer.Option(None, "--version", "-v", help="Show version and exit")
) -> None:
    """Show version and exit.

    Args:
        _ctx (typer.Context): Typer context (unused)
        version (bool): Whether to show version information

    Raises:
        typer.Exit: Always exits after showing version if version=True

    Example:
        >>> version_callback(ctx, True)
        LibriScribe2 version 1.0.0
        # Exits with code 0
    """
```

### log_command_start()

```python
def log_command_start() -> None:
    """Log the start of a command execution.

    Logs:
        - Current timestamp in YYYY-MM-DD HH:MM:SS format
        - Complete program arguments from sys.argv
        - Command execution start marker

    Side Effects:
        - Writes to application log file
        - Uses INFO level logging

    Example:
        >>> log_command_start()
        # Logs: "--- Log started on 2025-08-15 14:30:22 with arguments: python -m libriscribe2.cli create-book --title Test ---"
    """
```

### suppress_traceback()

```python
def suppress_traceback(
    exc_type: type[BaseException],
    exc_value: BaseException,
    _exc_traceback: Any
) -> None:
    """Suppress traceback output to console.

    Args:
        exc_type (type[BaseException]): Exception type
        exc_value (BaseException): Exception instance
        _exc_traceback (Any): Traceback object (unused)

    Behavior:
        - Logs full traceback to file with exception details
        - Shows minimal error message to console
        - Ignores KeyboardInterrupt exceptions
        - Uses logger.exception() for complete traceback logging

    Example:
        >>> suppress_traceback(ValueError, ValueError("Invalid input"), None)
        # Console: ❌ Error: Invalid input
        # Log file: Full traceback with stack trace
    """
```

## Command Functions

### start()

```python
@app.command()
def start(
    env_file: str = typer.Option(None, "--env-file", help="Path to a custom .env file"),
    config_file: str = typer.Option(None, "--config-file", help="Path to a custom JSON/YAML config file"),
) -> None:
    """Starts the interactive book creation process (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        env_file (str, optional): Path to custom .env file for environment variables
        config_file (str, optional): Path to custom JSON/YAML configuration file

    Status:
        NOT IMPLEMENTED - Shows error message and exits

    Side Effects:
        - Logs command start
        - Creates Settings instance
        - Shows error message about implementation status

    Example:
        >>> start(env_file=".env.custom", config_file="config.json")
        ERROR: Interactive creation is not implemented. See .kiro/TODO.md[#interactive_create].
    """
```

### create_book()

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

    Args:
        title (str, optional): Book title. If None and auto_title=True, generates title from content
        project_name (str, optional): Custom project folder name. Supports spaces. Must be empty/non-existent
        auto_title (bool): Auto-generate title based on content. Skipped if title is provided
        category (str): Book category. Default "Fiction"
        project_type (str): Project type preset. Default "novel". Options: short_story, novella, book, novel, epic
        genre (str, optional): Book genre (fantasy, mystery, romance, sci-fi, horror, etc.)
        description (str, optional): Book description or synopsis
        language (str): Book language. Default "English"
        chapters (str, optional): Number of chapters (e.g., "10", "8-12"). Overrides project_type defaults
        characters (str, optional): Number of characters (e.g., "5", "3-7", "5+")
        scenes_per_chapter (str, optional): Scene range per chapter (e.g., "3-6", "4-8", "5"). Overrides project_type
        target_audience (str): Target audience. Default "General". Options: General, Young Adult, Adult, Children
        worldbuilding (bool): Enable worldbuilding generation for fantasy/sci-fi genres
        config_file (str, optional): Path to configuration file (.env, .yaml, .yml, or .json)
        log_file (str, optional): Custom log file path
        log_level (str): Logging level. Default "INFO". Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
        mock (bool): Use mock LLM provider for testing without API consumption
        generate_concept (bool): Generate book concept step
        generate_outline (bool): Generate book outline step
        generate_characters (bool): Generate character profiles step
        generate_worldbuilding (bool): Generate worldbuilding details step (requires worldbuilding=True)
        write_chapters (bool): Write all chapters step
        format_book (bool): Format book into final output step
        user (str, optional): User identifier for LiteLLM tracking and tagging
        all (bool): Perform all generation steps (equivalent to enabling all generate_* and write_chapters and format_book)

    Returns:
        int: Exit code
            0: Success
            1: Runtime error or unexpected error
            2: Invalid input (ValueError)
            3: Import error (missing dependencies)
            5: Book creation failed

    Raises:
        ValueError: Invalid input parameters
        ImportError: Missing dependencies
        RuntimeError: Runtime errors during book creation

    Project Types:
        - short_story: 1-3 chapters, 1-3 characters, 1-2 scenes per chapter
        - novella: 4-8 chapters, 2-5 characters, 2-4 scenes per chapter
        - book: 8-15 chapters, 3-8 characters, 3-5 scenes per chapter
        - novel: 15-25 chapters, 5-12 characters, 3-6 scenes per chapter
        - epic: 25+ chapters, 8+ characters, 4-8 scenes per chapter

    Side Effects:
        - Creates project directory structure
        - Generates content files (concept, outline, characters, etc.)
        - Creates project log file
        - Updates project_data.json
        - Logs all operations to application and project log files

    Example:
        >>> create_book(
        ...     title="My Fantasy Novel",
        ...     genre="fantasy",
        ...     project_type="novel",
        ...     worldbuilding=True,
        ...     characters="5",
        ...     all=True
        ... )
        0  # Success
    """
```

### book_stats()

```python
@app.command(name="book-stats")
def book_stats(
    project_name: str = typer.Option(..., "--project-name", help="Project name to display statistics for"),
    show_logs: bool = typer.Option(False, "--show-logs", help="Display the last 20 lines of the log file"),
) -> None:
    """Displays statistics for a book project (NON-INTERACTIVE - RECOMMENDED).

    Args:
        project_name (str): Name of the project to analyze. Required parameter
        show_logs (bool): Whether to display the last 20 lines of the project log file

    Features:
        - Non-interactive operation suitable for automation
        - Automatic log file creation if missing
        - Comprehensive project metadata display
        - Chapter status overview (exists vs. missing files)
        - Dynamic questions and answers display
        - Optional log file viewing with --show-logs
        - Timestamped logging of all statistics to project log

    Display Information:
        - Project metadata: title, genre, language, category
        - Content metrics: book length, character count, chapter count
        - Configuration: worldbuilding status, review preferences
        - Chapter status: file existence for each chapter
        - Log file information and location
        - Recent log entries (if --show-logs is used)

    Logging:
        - Automatically creates project log file if missing
        - Logs complete statistics report with timestamp
        - Uses structured format for easy parsing
        - Includes all project metadata and chapter status

    Side Effects:
        - Creates book_creation.log in project directory if missing
        - Logs statistics report to project log file
        - Displays formatted output to console
        - Sets up project-specific logger

    Raises:
        FileNotFoundError: When project directory or project_data.json is not found
        ValueError: When project data is corrupted or invalid JSON
        Exception: For other unexpected errors during processing

    Example:
        >>> book_stats(project_name="my-fantasy-novel", show_logs=True)
        # Displays:
        # ╭─────────────────────────────────╮
        # │ Statistics for 'my-fantasy-novel' │
        # ╰─────────────────────────────────╯
        #   Title: The Dragon's Quest
        #   Genre: fantasy
        #   ...
        #   Chapter 1: The Beginning - Exists
        #   Chapter 2: The Journey - Missing
        #   ...
        #   Recent Log Entries (Last 20 lines)
        #   2025-08-15 11:19:29 - INFO - === BOOK STATISTICS REPORT ===
    """
```

### generate_title()

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
        project_name (str): Name of the existing project. Required with prompt if not provided
        config_file (str, optional): Path to configuration file (.env, .yaml, .yml, or .json)
        mock (bool): Whether to use mock LLM provider for testing
        user (str, optional): User identifier for LiteLLM tracking and tagging

    Requirements:
        - Project must exist with valid project_data.json file
        - Auto-title must be enabled (auto_title: true) OR title must be "Untitled" or "Untitled Book"
        - Sufficient content must be available for analysis:
          - Chapters (preferred for best results)
          - Characters (good for character-driven titles)
          - Outline (good for plot-driven titles)
          - At least one of the above must exist

    Process:
        1. Loads existing project data from project_data.json
        2. Validates title generation requirements
        3. Analyzes available content (chapters, characters, outline)
        4. Generates new title using LLM based on content analysis
        5. Updates project_data.json with new title
        6. Provides detailed feedback on success/failure

    Content Analysis:
        - Chapter content: themes, plot points, character development
        - Character profiles: main characters, relationships, roles
        - Outline structure: story arc, major events, climax
        - Genre and tone: maintains consistency with original intent
        - Target audience: ensures age-appropriate title

    Side Effects:
        - Updates project_data.json with new title
        - Logs title generation process
        - Creates/updates project log file
        - Initializes LLM client with specified configuration

    Raises:
        FileNotFoundError: When project directory or project_data.json is not found
        ValueError: When project data is corrupted or requirements not met
        RuntimeError: When title generation fails or LLM errors occur

    Example:
        >>> generate_title(project_name="my-project", mock=True)
        🎯 Generating better title based on content...
        ✅ Title generated successfully!
        📖 New title: 'The Chronicles of Aethermoor'
        💾 Updated project data saved to projects/my-project/project_data.json

        # Or if requirements not met:
        ℹ️ Auto-title not enabled for this project
        💡 To enable title generation, you can:
           1. Edit the project_data.json file and set 'auto_title': true
           2. Or recreate the project with --auto-title flag
    """
```

### resume()

```python
@app.command()
def resume(
    project_name: str = typer.Option(..., prompt="Project name to resume"),
) -> None:
    """Resumes a project from the last checkpoint (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name (str): Name of the project to resume. Required with prompt if not provided

    Process:
        1. Loads existing project data from project_data.json
        2. Checks for missing content in dependency order:
           - Outline (outline.md)
           - Characters (characters.md, if num_characters > 0)
           - Worldbuilding (worldbuilding.md, if worldbuilding_needed = true)
        3. Generates missing content using async operations
        4. Continues writing chapters from last checkpoint
        5. Formats book if all chapters exist
        6. Generates title if auto-title is enabled and conditions are met

    Content Generation Order:
        1. Outline generation (if missing)
        2. Character generation (if needed and missing)
        3. Worldbuilding generation (if needed and missing)
        4. Chapter writing (continues from last written chapter)
        5. Book formatting (if all chapters complete)
        6. Title generation (if auto-title enabled)

    Status:
        PARTIALLY IMPLEMENTED - Basic functionality available
        - Outline generation: ✅ Implemented
        - Character generation: ✅ Implemented
        - Worldbuilding generation: ✅ Implemented
        - Chapter writing: ⚠️ Partially implemented
        - Book formatting: ⚠️ Partially implemented
        - Title generation: ✅ Implemented

    Side Effects:
        - Generates missing content files
        - Updates project_data.json with progress
        - Creates checkpoint saves after each major step
        - Logs all operations to project log file
        - Uses async operations for content generation

    Raises:
        FileNotFoundError: When project directory or project_data.json is not found
        ValueError: When project data is corrupted or invalid
        RuntimeError: When content generation fails

    Example:
        >>> resume(project_name="incomplete-project")
        Project 'incomplete-project' loaded. Resuming...
        Outline already exists. Skipping outline generation.
        Characters already generated or not needed. Skipping.
        Worldbuilding already generated or not needed. Skipping.
        Continuing chapter writing from chapter 3...
        # Generates remaining chapters and formats book
    """
```

## Async Command Functions (Placeholder)

### concept()

```python
@app.command()
async def concept(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None:
    """Generates a book concept (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name (str): Name of the project. Required with prompt if not provided

    Status:
        NOT IMPLEMENTED - Placeholder function
        Shows message about implementation status

    Intended Functionality:
        - Load existing project data
        - Generate book concept using ProjectManagerAgent
        - Save concept to project files
        - Update project status

    Example:
        >>> await concept(project_name="my-project")
        Project 'my-project' loaded. Generating concept...
        # Would generate concept if implemented
    """
```

### outline()

```python
@app.command()
async def outline(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None:
    """Generates a book outline (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name (str): Name of the project. Required with prompt if not provided

    Status:
        NOT IMPLEMENTED - Placeholder function
        Shows message about implementation status

    Intended Functionality:
        - Load existing project data
        - Generate book outline using ProjectManagerAgent
        - Save outline to outline.md
        - Update project status

    Example:
        >>> await outline(project_name="my-project")
        Project 'my-project' loaded. Generating outline...
        # Would generate outline if implemented
    """
```

### characters()

```python
@app.command()
async def characters(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None:
    """Generates character profiles (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name (str): Name of the project. Required with prompt if not provided

    Status:
        NOT IMPLEMENTED - Placeholder function
        Shows message about implementation status

    Intended Functionality:
        - Load existing project data
        - Generate character profiles using ProjectManagerAgent
        - Save characters to characters.md
        - Update project status

    Example:
        >>> await characters(project_name="my-project")
        Project 'my-project' loaded. Generating characters...
        # Would generate characters if implemented
    """
```

### worldbuilding()

```python
@app.command()
async def worldbuilding(
    project_name: str = typer.Option(..., prompt="Project name")
) -> None:
    """Generates worldbuilding details (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name (str): Name of the project. Required with prompt if not provided

    Status:
        NOT IMPLEMENTED - Placeholder function
        Shows message about implementation status

    Intended Functionality:
        - Load existing project data
        - Generate worldbuilding details using ProjectManagerAgent
        - Save worldbuilding to worldbuilding.md
        - Update project status

    Example:
        >>> await worldbuilding(project_name="my-project")
        Project 'my-project' loaded. Generating worldbuilding...
        # Would generate worldbuilding if implemented
    """
```

### write()

```python
@app.command()
async def write(
    project_name: str = typer.Option(..., prompt="Project name"),
    chapter_number: int = typer.Option(..., prompt="Chapter number"),
) -> None:
    """Writes a specific chapter, with review process (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name (str): Name of the project. Required with prompt if not provided
        chapter_number (int): Chapter number to write. Required with prompt if not provided

    Status:
        NOT IMPLEMENTED - Placeholder function
        Shows message about implementation status

    Intended Functionality:
        - Load existing project data
        - Write specific chapter using ProjectManagerAgent
        - Include review process for quality control
        - Save chapter to chapter_{number}.md
        - Update project status

    Example:
        >>> await write(project_name="my-project", chapter_number=1)
        Project 'my-project' loaded. Writing chapter 1...
        # Would write and review chapter if implemented
    """
```

### edit()

```python
@app.command()
async def edit(
    project_name: str = typer.Option(..., prompt="Project name"),
    chapter_number: int = typer.Option(..., prompt="Chapter number to edit"),
) -> None:
    """Edits and refines a specific chapter (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        project_name (str): Name of the project. Required with prompt if not provided
        chapter_number (int): Chapter number to edit. Required with prompt if not provided

    Status:
        NOT IMPLEMENTED - Placeholder function
        Shows message about implementation status

    Intended Functionality:
        - Load existing project data
        - Load existing chapter content
        - Edit and refine chapter using ProjectManagerAgent
        - Save updated chapter
        - Update project status

    Example:
        >>> await edit(project_name="my-project", chapter_number=1)
        Project 'my-project' loaded. Editing chapter 1...
        # Would edit chapter if implemented
    """
```

### format()

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
        project_name (str): Name of the project. Required with prompt if not provided
        _output_format (str, optional): Output format. Currently unused parameter

    Status:
        PARTIALLY IMPLEMENTED - Basic formatting available
        - Markdown formatting: ✅ Available
        - PDF formatting: ❌ Not implemented

    Functionality:
        - Load existing project data
        - Format book using ProjectManagerAgent.format_book()
        - Generate manuscript.md with all chapters
        - Create formatted output

    Side Effects:
        - Creates manuscript.md in project directory
        - Updates project status
        - Logs formatting operations

    Example:
        >>> await format(project_name="my-project")
        Project 'my-project' loaded. Formatting book...
        # Formats book to manuscript.md
    """
```

### research()

```python
@app.command()
async def research(
    query: str = typer.Option(..., prompt="Research query")
) -> None:
    """Performs web research on a given query (ADVANCED - NOT FULLY SUPPORTED).

    Args:
        query (str): Research query string. Required with prompt if not provided

    Status:
        NOT IMPLEMENTED - Placeholder function
        Shows message about implementation status

    Intended Functionality:
        - Perform web research using ProjectManagerAgent
        - Gather relevant information for book writing
        - Save research results
        - Integrate with book content generation

    Example:
        >>> await research(query="medieval castle architecture")
        # Would perform research if implemented
    """
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

**Behavior:**
- Shows custom help if `--help` is the only argument
- Otherwise runs the Typer app normally
- Allows for custom help formatting while maintaining standard Typer functionality

## Type Annotations Summary

### Parameter Types

```python
# String parameters
title: str
project_name: str
config_file: str
genre: str
description: str

# Optional string parameters
title: str = typer.Option(None, ...)
config_file: str = typer.Option(None, ...)
user: str | None = typer.Option(None, ...)

# Boolean parameters
auto_title: bool = typer.Option(False, ...)
worldbuilding: bool = typer.Option(False, ...)
mock: bool = typer.Option(False, ...)
show_logs: bool = typer.Option(False, ...)

# String parameters with defaults
category: str = typer.Option("Fiction", ...)
language: str = typer.Option("English", ...)
log_level: str = typer.Option("INFO", ...)

# Required parameters with prompts
project_name: str = typer.Option(..., prompt="Project name")
chapter_number: int = typer.Option(..., prompt="Chapter number")

# Integer parameters
chapter_number: int = typer.Option(..., prompt="Chapter number")
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
FileNotFoundError: When files/directories are not found
ValueError: When input parameters are invalid
ImportError: When required modules cannot be imported
RuntimeError: When runtime errors occur during execution

# Typer exceptions
typer.Exit: When version callback exits
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
from libriscribe2.services.book_creator import BookCreatorService
from libriscribe2.settings import MANUSCRIPT_MD_FILENAME, Settings
from libriscribe2.utils.timestamp_utils import format_timestamp_for_filename
```

## Usage Patterns

### Command Registration

```python
@app.command()
def sync_command():
    """Synchronous command."""
    pass

@app.command()
async def async_command():
    """Asynchronous command."""
    pass

@app.command(name="custom-name")
def function_name():
    """Command with custom name."""
    pass
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
except RuntimeError as e:
    console.print(f"[red]{e}[/red]")
    return 1  # Runtime error
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

## See Also

- [CLI API Documentation](cli-api.md)
- [CLI Comprehensive Documentation](cli-comprehensive.md)
- [CLI Usage Examples](../../examples/cli_usage_examples.md)
- [BookCreator Service API](book-creator-api.md)
- [ProjectManager API](project-manager-api.md)
