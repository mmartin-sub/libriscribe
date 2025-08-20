# src/libriscribe2/cli.py
"""
LibriScribe2 - Modern book creation CLI with rich output and type safety.

Usage Examples:
    # Create a book with all generation steps (NON-INTERACTIVE - RECOMMENDED)
    hatch run python src/libriscribe2/cli.py create-book \
        --title "My Awesome Book" \
        --genre fantasy \
        --description "A tale of epic proportions about 2 kids living in Lausanne called Eva and Justine" \
        --category fiction \
        --characters 3 \
        --worldbuilding \
        --all

    # Create just the concept and outline (NON-INTERACTIVE - RECOMMENDED)
    hatch run python src/libriscribe2/cli.py create-book \
        --title "My Book" \
        --genre mystery \
        --generate-concept \
        --generate-outline

    # Start interactive mode (ADVANCED - NOT FULLY SUPPORTED)
    hatch run python src/libriscribe2/cli.py start

    # Check book statistics (NON-INTERACTIVE - RECOMMENDED)
    hatch run python src/libriscribe2/cli.py book-stats --project-name my_book

    # Check book statistics with recent log entries
    hatch run python src/libriscribe2/cli.py book-stats --project-name my_book --show-logs

Requirements:
    - Python 3.12+
    - Use 'hatch run' to ensure correct Python version and dependencies
    - Set up configuration file with API keys or use --config-file
"""

import asyncio
import datetime
import logging
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel

# Create application log file
from .utils.timestamp_utils import format_timestamp_for_filename

# Add better error handling for imports
try:
    from libriscribe2.agents.project_manager import ProjectManagerAgent
    from libriscribe2.settings import Settings
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("💡 This might be due to:")
    print("   - Missing dependencies (run 'hatch run pip install -e .')")
    print("   - Python version mismatch (this project requires Python 3.12+)")
    print("   - Incorrect PYTHONPATH")
    print(f"   - Current Python version: {sys.version}")
    print("💡 Try running with hatch:")
    print("   hatch run python src/libriscribe2/main.py --help")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error during import: {e}")
    print(f"💡 Python version: {sys.version}")
    print("💡 Try running with hatch:")
    print("   hatch run python src/libriscribe2/main.py --help")
    sys.exit(1)

# Configure logging with reduced console verbosity
# Only configure console logging, don't interfere with file handlers
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))
console_handler.setLevel(logging.CRITICAL)  # Only show critical errors in console

# Get root logger and add console handler without clearing existing handlers
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
# Set root logger level to DEBUG to allow all messages to pass through to handlers
root_logger.setLevel(logging.DEBUG)


# Set up application-level logging
def setup_application_logging() -> Path:
    """Set up application-level logging before any project is created."""
    from pathlib import Path

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = format_timestamp_for_filename()
    app_log_file = logs_dir / f"libriscribe_{timestamp}.log"

    # Configure file handler for application logs
    file_handler = logging.FileHandler(app_log_file, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    file_handler.setLevel(logging.DEBUG)  # Capture all levels in file

    # Add file handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    return app_log_file


# Initialize application logging
app_log_file = setup_application_logging()

# Suppress traceback output to console


# Override sys.excepthook to suppress tracebacks
def suppress_traceback(exc_type: type[BaseException], exc_value: BaseException, _exc_traceback: Any) -> None:
    """Suppress traceback output to console."""
    # Only log the error message, not the full traceback
    if exc_type is not KeyboardInterrupt:
        # Log to file with full traceback
        logging.getLogger().exception("Unhandled exception", exc_info=(exc_type, exc_value, _exc_traceback))
        # Print minimal error to console
        print(f"❌ Error: {exc_value}", file=sys.stderr)


# sys.excepthook = suppress_traceback

console = Console()


# app = typer.Typer(callback=main_callback)
def custom_help() -> None:
    """Display custom help with Rich formatting."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    console = Console()

    # Title
    title = Text("LibriScribe2", style="bold blue")
    title.append(" - Modern book creation CLI", style="default")
    console.print(title)
    console.print()

    # Recommended Commands Table
    recommended_table = Table(title="🟢 NON-INTERACTIVE (RECOMMENDED)", show_header=True, header_style="bold green")
    recommended_table.add_column("Command", style="bold")
    recommended_table.add_column("Description", style="default")

    recommended_table.add_row("create-book", "Create books with command-line arguments")
    recommended_table.add_row("book-stats", "View book statistics (non-interactive)")
    recommended_table.add_row("format", "Format existing books")

    console.print(recommended_table)
    console.print()

    # Advanced Commands Table
    advanced_table = Table(title="🟡 INTERACTIVE (ADVANCED)", show_header=True, header_style="bold yellow")
    advanced_table.add_column("Command", style="bold")
    advanced_table.add_column("Description", style="default")

    advanced_table.add_row("start", "Interactive book creation")
    advanced_table.add_row("concept", "Generate concept for existing project")
    advanced_table.add_row("outline", "Generate outline for existing project")
    advanced_table.add_row("characters", "Generate characters for existing project")
    advanced_table.add_row("worldbuilding", "Generate worldbuilding for existing project")
    advanced_table.add_row("write", "Write specific chapter")
    advanced_table.add_row("edit", "Edit specific chapter")
    advanced_table.add_row("research", "Research functionality")
    advanced_table.add_row("resume", "Resume existing project")

    console.print(advanced_table)
    console.print()

    # Usage recommendation
    usage_panel = Panel(
        "Use 'create-book' for most use cases. It's fully implemented and supports\n"
        "all generation steps with comprehensive configuration options.",
        title="RECOMMENDED USAGE",
        border_style="green",
    )
    console.print(usage_panel)
    console.print()


def version_callback(
    _ctx: typer.Context, version: bool = typer.Option(None, "--version", "-v", help="Show version and exit")
) -> None:
    """Show version and exit."""
    if version:
        from libriscribe2 import __version__

        console.print(f"LibriScribe2 version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    help="LibriScribe2 - Modern book creation CLI",
    rich_markup_mode="rich",
    callback=version_callback,
    invoke_without_command=True,
)


# project_manager = ProjectManagerAgent()  # Initialize ProjectManager

logger = logging.getLogger(__name__)

# Global project manager variable
project_manager: ProjectManagerAgent


# Log the current date, time, and program arguments (only for actual commands, not help)
def log_command_start() -> None:
    """Log the start of a command execution."""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    program_arguments = " ".join(sys.argv)
    logger.info(f"--- Log started on {current_time} with arguments: {program_arguments} ---")


@app.command()
def start(
    env_file: str = typer.Option(None, "--env-file", help="Path to a custom .env file"),
    config_file: str = typer.Option(None, "--config-file", help="Path to a custom JSON/YAML config file"),
) -> None:
    """Starts the interactive book creation process (ADVANCED - NOT FULLY SUPPORTED)."""
    # Log command start
    log_command_start()

    settings = Settings(env_file=env_file, config_file=config_file)
    global project_manager
    project_manager = ProjectManagerAgent(settings=settings)
    # interactive_create is not implemented
    console.print("[red]ERROR: Interactive creation is not implemented. See .kiro/TODO.md[#interactive_create].")


@app.command(name="create-book")
def create_book(
    title: str = typer.Option(
        None, "--title", "-t", help="Book title (optional - use --auto-title to generate based on content)"
    ),
    project_name: str = typer.Option(
        None, "--project-name", "-p", help="Custom project folder name (spaces allowed, must be empty or non-existent)"
    ),
    auto_title: bool = typer.Option(
        False, "--auto-title", help="Auto-generate title based on content (skipped if title is provided)"
    ),
    category: str = typer.Option("Fiction", "--category", "-c", help="Book category [default: Fiction]"),
    project_type: str = typer.Option(
        "novel", "--project-type", help="Project type: short_story, novella, book, novel, epic [default: novel]"
    ),
    genre: str = typer.Option(None, "--genre", "-g", help="Book genre (e.g., fantasy, mystery, romance)"),
    description: str = typer.Option(None, "--description", "-d", help="Book description or synopsis"),
    language: str = typer.Option(None, "--language", "-l", help="Book language"),
    chapters: str = typer.Option(
        None, "--chapters", help="Number of chapters to generate (e.g., 10, 8-12) (overrides project-type)"
    ),
    characters: str = typer.Option(None, "--characters", help="Number of characters to create (e.g., 5, 3-7, 5+)"),
    scenes_per_chapter: str = typer.Option(
        None, "--scenes-per-chapter", help="Scene range per chapter (e.g., 3-6, 4-8, 5) (overrides project-type)"
    ),
    target_audience: str = typer.Option(
        "General",
        "--target-audience",
        help="Target audience (e.g., General, Young Adult, Adult, Children) [default: General]",
    ),
    worldbuilding: bool = typer.Option(False, "--worldbuilding", help="Enable worldbuilding for the book"),
    config_file: str = typer.Option(
        None, "--config-file", help="Path to configuration file (.env, .yaml, .yml, or .json)"
    ),
    log_file: str = typer.Option(None, "--log-file", help="Path to log file"),
    log_level: str = typer.Option(
        "INFO", "--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) [default: INFO]"
    ),
    mock: bool = typer.Option(False, "--mock", help="Use mock LLM provider for testing"),
    skip_error: bool = typer.Option(False, "--skip-error", help="Continue execution even if an error occurs"),
    generate_concept: bool = typer.Option(False, "--generate-concept", help="Generate book concept"),
    generate_outline: bool = typer.Option(False, "--generate-outline", help="Generate book outline"),
    generate_characters: bool = typer.Option(False, "--generate-characters", help="Generate character profiles"),
    generate_worldbuilding: bool = typer.Option(
        False, "--generate-worldbuilding", help="Generate worldbuilding details (requires --worldbuilding)"
    ),
    write_chapters: bool = typer.Option(False, "--write-chapters", help="Write all chapters"),
    format_book: bool = typer.Option(False, "--format-book", help="Format the book into final output"),
    user: str | None = typer.Option(None, "--user", help="User identifier for LiteLLM tags (spaces allowed)"),
    all: bool = typer.Option(
        False,
        "--all",
        help="Perform all generation steps (concept, outline, characters, worldbuilding, chapters, formatting)",
    ),
) -> int:
    """Create a new book using command-line arguments without interactive prompts.

    EXAMPLES:
        # Create a short story with auto-generated title (using mock for testing)
        create-book --project-type=short_story --genre=fantasy --all --auto-title --mock

        # Create a novella with auto-generated title (using mock for testing)
        create-book --project-type=novella --genre=mystery --all --auto-title --mock

        # Create a book with auto-generated title (using mock for testing)
        create-book --project-type=book --genre=fantasy --all --auto-title --mock

        # Create a novel with auto-generated title (using mock for testing)
        create-book --project-type=novel --genre=fantasy --all --auto-title --mock

        # Create an epic novel with auto-generated title (using mock for testing)
        create-book --project-type=epic --genre=fantasy --all --auto-title --mock

        # Create with manual chapter override (using mock for testing)
        create-book --project-type=novel --chapters=15 --genre=fantasy --all --auto-title --mock

        # Create with custom scene range override (using mock for testing)
        create-book --project-type=novel --scenes-per-chapter=5-8 --genre=fantasy --all --auto-title --mock

        # Create with specific title (auto-title will be skipped) (using mock for testing)
        create-book --title="My Fantasy Novel" --project-type=novel --genre=fantasy --all --mock --user="user-123"

        # Create with project name containing spaces (using mock for testing)
        create-book --project-name="my custom project" --project-type=novel --all --auto-title --mock

        # Create with custom configuration (using mock for testing)
        create-book --config-file=config-example.json --project-type=novel --all --auto-title --mock

    NOTE: Use --mock flag for testing without API keys. For production use, provide a configuration file with your API keys.
    """
    from libriscribe2.services.book_creator import BookCreatorService

    # Log command start
    log_command_start()

    try:
        # Create the book creator service with configuration
        book_creator = BookCreatorService(
            config_file=config_file,
            mock=mock,
            log_file=log_file,
            log_level=log_level,
        )

        # Prepare arguments for book creation
        args = {
            "title": title,
            "project_name": project_name,
            "auto_title": auto_title,
            "category": category,
            "project_type": project_type,
            "genre": genre,
            "description": description,
            "language": language,
            "chapters": chapters,
            "characters": characters,
            "target_audience": target_audience,
            "worldbuilding": worldbuilding,
            "generate_concept": generate_concept,
            "generate_outline": generate_outline,
            "generate_characters": generate_characters,
            "generate_worldbuilding": generate_worldbuilding,
            "write_chapters": write_chapters,
            "format_book": format_book,
            "scenes_per_chapter": scenes_per_chapter,
            "user": user,
            "all": all,
        }

        # Create the book using the async method
        import asyncio

        result = asyncio.run(book_creator.create_book_from_cli(args))
        if result:
            console.print("[green]Book created successfully![/green]")
            return 0
        else:
            console.print("[red]Failed to create book.[/red]")
            return 5

    except OSError as e:
        console.print(f"[red]❌ File Error: {e!s}[/red]")
        if not skip_error:
            console.print("[yellow]Execution halted. Use --skip-error to continue on file errors.[/yellow]")
            return 1
        console.print("[yellow]--skip-error is enabled, continuing execution...[/yellow]")
        return 0  # Continue execution
    except ValueError as e:
        console.print(f"[red]❌ Invalid input: {e!s}[/red]")
        console.print("💡 Check your command line arguments and try again.")
        return 2
    except ImportError as e:
        console.print(f"[red]❌ Import Error: {e!s}[/red]")
        console.print("💡 This might be due to missing dependencies.")
        console.print("   Try: hatch run pip install -e .")
        return 3
    except RuntimeError as e:
        console.print(f"[red]{e!s}[/red]")
        return 1
    except Exception as e:
        # Log the full traceback for debugging to file only
        logger.exception("Unexpected error during book creation")
        console.print(f"[red]❌ Unexpected error: {e!s}[/red]")
        console.print("💡 Check the logs for more details.")
        return 1


# Not sure if it is the proper way to do it
@app.command()
async def concept(project_name: str = typer.Option(..., prompt="Project name")) -> None:
    """Generates a book concept (ADVANCED - NOT FULLY SUPPORTED)."""
    from libriscribe2.services.book_creator import BookCreatorService

    service = BookCreatorService()
    await service.generate_concept(project_name)


@app.command()
async def outline(project_name: str = typer.Option(..., prompt="Project name")) -> None:
    """Generates a book outline (ADVANCED - NOT FULLY SUPPORTED)."""
    from libriscribe2.services.book_creator import BookCreatorService

    service = BookCreatorService()
    await service.generate_outline(project_name)


@app.command()
async def characters(project_name: str = typer.Option(..., prompt="Project name")) -> None:
    """Generates character profiles (ADVANCED - NOT FULLY SUPPORTED)."""
    from libriscribe2.services.book_creator import BookCreatorService

    service = BookCreatorService()
    await service.generate_characters(project_name)


@app.command()
async def worldbuilding(project_name: str = typer.Option(..., prompt="Project name")) -> None:
    """Generates worldbuilding details (ADVANCED - NOT FULLY SUPPORTED)."""
    from libriscribe2.services.book_creator import BookCreatorService

    service = BookCreatorService()
    await service.generate_worldbuilding(project_name)


@app.command()
async def write(
    project_name: str = typer.Option(..., prompt="Project name"),
    chapter_number: int = typer.Option(..., prompt="Chapter number"),
) -> None:
    """Writes a specific chapter, with review process (ADVANCED - NOT FULLY SUPPORTED)."""
    from libriscribe2.services.book_creator import BookCreatorService

    service = BookCreatorService()
    await service.write_chapter(project_name, chapter_number)


@app.command()
async def edit(
    project_name: str = typer.Option(..., prompt="Project name"),
    chapter_number: int = typer.Option(..., prompt="Chapter number to edit"),
) -> None:
    """Edits and refines a specific chapter (ADVANCED - NOT FULLY SUPPORTED)"""
    from libriscribe2.services.book_creator import BookCreatorService

    service = BookCreatorService()
    await service.edit_chapter(project_name, chapter_number)


@app.command()
async def format(
    project_name: str = typer.Option(..., prompt="Project name"),
    _output_format: str = typer.Option(None, "--output-format", help="Output format (md or pdf)"),
) -> None:
    """Formats the entire book into a single Markdown or PDF file (ADVANCED - NOT FULLY SUPPORTED)."""
    from libriscribe2.services.book_creator import BookCreatorService

    service = BookCreatorService()
    await service.format_book(project_name)


@app.command()
async def research(query: str = typer.Option(..., prompt="Research query")) -> None:
    """Performs web research on a given query (ADVANCED - NOT FULLY SUPPORTED)."""
    from libriscribe2.services.book_creator import BookCreatorService

    service = BookCreatorService()
    await service.research_topic(query)


@app.command(name="book-stats")
def book_stats(
    project_name: str = typer.Option(..., "--project-name", help="Project name to display statistics for"),
    show_logs: bool = typer.Option(False, "--show-logs", help="Display the last 20 lines of the log file"),
) -> None:
    """Displays statistics for a book project (NON-INTERACTIVE - RECOMMENDED)."""
    # Log command start
    log_command_start()

    try:
        # Initialize project manager with settings and load project data
        settings = Settings()
        pm = ProjectManagerAgent(settings=settings)
        pm.load_project_data(project_name)

        kb = pm.project_knowledge_base
        if not kb:
            console.print(f"[red]Error: Could not load knowledge base for '{project_name}'.[/red]")
            return

        if not pm.project_dir:
            console.print("[red]Error: Project directory not set[/red]")
            return

        # Set up project-specific logging
        project_log_file = pm.project_dir / "book_creation.log"

        # Create log file if it doesn't exist
        if not project_log_file.exists():
            project_log_file.touch()
            console.print(f"[yellow]Created log file: {project_log_file}[/yellow]")

        # Set up project logger
        project_logger = logging.getLogger(f"project.{project_name}")
        project_logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        for handler in project_logger.handlers[:]:
            project_logger.removeHandler(handler)

        # Add file handler for project logging
        file_handler = logging.FileHandler(project_log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        project_logger.addHandler(file_handler)

        # Prepare statistics data
        stats_data = {
            "project_name": kb.project_name,
            "title": kb.title,
            "genre": kb.genre,
            "language": kb.language,
            "category": kb.category,
            "book_length": kb.book_length,
            "num_characters": kb.num_characters,
            "num_chapters": kb.num_chapters,
            "worldbuilding_needed": kb.worldbuilding_needed,
            "review_preference": kb.review_preference,
            "description": kb.description,
        }

        # Log statistics to project log file
        project_logger.info("=== BOOK STATISTICS REPORT ===")
        project_logger.info(f"Statistics generated for project: {kb.project_name}")
        for key, value in stats_data.items():
            if key == "description" and value and isinstance(value, str) and len(value) > 100:
                project_logger.info(f"{key.replace('_', ' ').title()}: {value[:100]}...")
            else:
                project_logger.info(f"{key.replace('_', ' ').title()}: {value}")

        # Log dynamic questions and answers
        if kb.dynamic_questions:
            project_logger.info("--- Dynamic Questions & Answers ---")
            for q_id, answer in kb.dynamic_questions.items():
                project_logger.info(f"{q_id}: {answer}")

        # Log chapter status
        chapter_stats = []
        if kb.chapters:
            project_logger.info("--- Chapter Status ---")
            for chapter_number, chapter in kb.chapters.items():
                chapter_path = pm.project_dir / f"chapter_{chapter_number}.md"
                status = "Exists" if chapter_path.exists() else "Missing"
                chapter_info = f"Chapter {chapter_number}: {chapter.title} - {status}"
                project_logger.info(chapter_info)
                chapter_stats.append((chapter_number, chapter.title, status))
        else:
            project_logger.info("No chapters recorded yet.")

        # Log file links
        project_logger.info("--- Associated Log Files ---")
        project_logger.info(f"Main application log: {app_log_file.resolve()}")

        # Find the latest llm_output log
        llm_logs_dir = pm.project_dir
        llm_log_files = list(llm_logs_dir.glob("llm_output_*.log"))
        if llm_log_files:
            latest_llm_log = max(llm_log_files, key=lambda f: f.stat().st_mtime)
            project_logger.info(f"Latest LLM output log: {latest_llm_log.resolve()}")
        else:
            project_logger.info("No LLM output logs found in the project directory.")

        project_logger.info("=== END STATISTICS REPORT ===")

        # Display statistics to console
        console.print(
            Panel(
                f"[bold blue]Statistics for '{kb.project_name}'[/bold blue]",
                expand=False,
            )
        )
        console.print(f"  [bold]Title:[/bold] {kb.title}")
        console.print(f"  [bold]Genre:[/bold] {kb.genre}")
        console.print(f"  [bold]Language:[/bold] {kb.language}")
        console.print(f"  [bold]Category:[/bold] {kb.category}")
        console.print(f"  [bold]Book Length:[/bold] {kb.book_length}")
        console.print(f"  [bold]Number of Characters:[/bold] {kb.num_characters}")
        console.print(f"  [bold]Number of Chapters:[/bold] {kb.num_chapters}")
        console.print(f"  [bold]Worldbuilding Needed:[/bold] {kb.worldbuilding_needed}")
        console.print(f"  [bold]Review Preference:[/bold] {kb.review_preference}")
        console.print(f"  [bold]Description:[/bold] {kb.description[:100] if kb.description else 'N/A'}...")

        # Display dynamic questions and answers
        if kb.dynamic_questions:
            console.print(Panel("[bold blue]Dynamic Questions & Answers[/bold blue]", expand=False))
            for q_id, answer in kb.dynamic_questions.items():
                console.print(f"  [bold]{q_id}:[/bold] {answer}")

        # Display chapter status
        if kb.chapters:
            console.print(Panel("[bold blue]Chapter Status[/bold blue]", expand=False))
            for chapter_number, chapter in kb.chapters.items():
                chapter_path = pm.project_dir / f"chapter_{chapter_number}.md"
                status = "[green]Exists[/green]" if chapter_path.exists() else "[red]Missing[/red]"
                console.print(f"  Chapter {chapter_number}: {chapter.title} - {status}")
        else:
            console.print("[yellow]No chapters recorded yet.[/yellow]")

        # Log file information
        console.print(
            Panel(
                f"[bold blue]Log File: {project_log_file.name}[/bold blue]",
                expand=False,
            )
        )
        console.print(f"  [bold]Location:[/bold] {project_log_file}")
        console.print("  [bold]Statistics logged:[/bold] [green]Yes[/green]")

        # Show logs if requested
        if show_logs and project_log_file.exists():
            console.print(Panel("[bold blue]Recent Log Entries (Last 20 lines)[/bold blue]", expand=False))
            with open(project_log_file, encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-20:]:  # Display last 20 lines
                    console.print(line.strip())
        elif not show_logs:
            console.print("  [dim]Use --show-logs to view recent log entries[/dim]")

        # Clean up logger handlers
        for handler in project_logger.handlers[:]:
            handler.close()
            project_logger.removeHandler(handler)

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        logger.exception(f"Error in book-stats command for project {project_name}")


@app.command()
def resume(
    project_name: str = typer.Option(..., prompt="Project name to resume"),
) -> None:
    """Resumes a project from the last checkpoint (ADVANCED - NOT FULLY SUPPORTED)."""
    from libriscribe2.services.book_creator import BookCreatorService

    service = BookCreatorService()
    asyncio.run(service.resume_project(project_name))


@app.command()
def generate_title(
    project_name: str = typer.Option(..., prompt="Project name"),
    config_file: str = typer.Option(None, "--config-file", help="Path to configuration file"),
    mock: bool = typer.Option(False, "--mock", help="Use mock LLM provider for testing"),
    user: str | None = typer.Option(None, "--user", help="User identifier for LiteLLM tags (spaces allowed)"),
) -> None:
    """Generate a better title for an existing project based on its content."""
    # Log command start
    log_command_start()

    try:
        from libriscribe2.services.book_creator import BookCreatorService

        # Load settings and initialize service
        settings = Settings(config_file=config_file)
        book_creator = BookCreatorService(
            config_file=config_file,
            mock=mock,
        )

        # Load the project
        project_dir = Path(settings.projects_dir) / project_name
        if not project_dir.exists():
            print(f"❌ Project '{project_name}' not found in {settings.projects_dir}")
            return

        # Load project knowledge base
        project_data_path = project_dir / settings.project_data_filename
        if not project_data_path.exists():
            print(f"❌ Project data not found at {project_data_path}")
            return

        from libriscribe2.knowledge_base import ProjectKnowledgeBase

        kb = ProjectKnowledgeBase.load_from_file(str(project_data_path))
        if not kb:
            print(f"❌ Failed to load project data from {project_data_path}")
            return

        print(f"📚 Project '{project_name}' loaded. Current title: '{kb.title}'")

        # Initialize project manager
        book_creator.project_manager = ProjectManagerAgent(settings=settings, model_config=book_creator.model_config)

        # Initialize LLM client (always use OpenAI)
        llm_provider = "mock" if mock else "openai"
        book_creator.project_manager.initialize_llm_client(llm_provider, user)

        # Set up the project
        book_creator.project_manager.create_project_from_kb(kb, str(project_dir))

        # Check if title generation is needed
        if book_creator.project_manager.needs_title_generation():
            print("🎯 Generating better title based on content...")
            try:
                success = asyncio.run(book_creator.project_manager.generate_project_title())
                if success:
                    if book_creator.project_manager.project_knowledge_base:
                        new_title = book_creator.project_manager.project_knowledge_base.title
                        print("✅ Title generated successfully!")
                        print(f"📖 New title: '{new_title}'")
                        print(f"💾 Updated project data saved to {project_data_path}")
                    else:
                        print("⚠️ Title generated but project knowledge base is not available")
                else:
                    print("⚠️ Failed to generate title")
            except Exception as e:
                print(f"❌ Failed to generate title: {e}")
        else:
            # Check why title generation is not needed
            if not kb.auto_title:
                print("ℹ️ Auto-title not enabled for this project")
                print("💡 To enable title generation, you can:")
                print("   1. Edit the project_data.json file and set 'auto_title': true")
                print("   2. Or recreate the project with --auto-title flag")
            elif kb.title != "Untitled" and kb.title != "Untitled Book":
                print(f"ℹ️ Project already has a title: '{kb.title}'")
                print("💡 To generate a new title anyway, edit project_data.json and set 'auto_title': true")
            else:
                print("ℹ️ Insufficient content available for title generation")
                print("💡 Title generation works best with:")
                print("   - Chapters (--write-chapters)")
                print("   - Characters (--generate-characters)")
                print("   - Outline (--generate-outline)")
                print("   - Or use --all to generate all content")

    except FileNotFoundError:
        print(f"❌ Project '{project_name}' not found.")
    except ValueError as e:
        print(f"❌ Error loading project data: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Check if --help is used and no subcommand is specified
    if "--help" in sys.argv and len(sys.argv) == 2:
        custom_help()
        sys.exit(0)
    else:
        app()
