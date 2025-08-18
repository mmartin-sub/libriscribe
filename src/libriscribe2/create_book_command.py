"""
Create Book Command

This module provides the command-line interface for creating books.
"""

import asyncio
import hashlib
import logging
import os
import re
from pathlib import Path

import typer
from rich.console import Console

from libriscribe2.agents.project_manager import ProjectManagerAgent
from libriscribe2.knowledge_base import Chapter, ProjectKnowledgeBase
from libriscribe2.settings import MANUSCRIPT_MD_FILENAME, Settings
from libriscribe2.utils.language import normalize_language

# Initialize console and logger
console = Console()
logger = logging.getLogger(__name__)

# Define exit codes
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_INVALID_ARGS = 2
EXIT_ENV_CONFIG_ERROR = 3
EXIT_LLM_INIT_ERROR = 4
EXIT_BOOK_CREATION_ERROR = 5
EXIT_FILE_SYSTEM_ERROR = 6
EXIT_NETWORK_ERROR = 7

# Initialize app
app = typer.Typer()

# Initialize project manager
settings = Settings()
project_manager = ProjectManagerAgent(settings=settings, llm_client=None)


def validate_title(title: str) -> str:
    """Validate the book title."""
    if not title or len(title.strip()) == 0:
        raise ValueError("Book title cannot be empty")
    return title.strip()


def validate_output_dir(output_dir: str | None) -> str | None:
    """Validate the output directory if provided."""
    if output_dir:
        path = Path(output_dir)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")
            except Exception as e:
                raise ValueError(f"Could not create output directory: {e}") from e
        elif not path.is_dir():
            raise ValueError(f"Output path exists but is not a directory: {output_dir}")
        elif not os.access(output_dir, os.W_OK):
            raise ValueError(f"Output directory is not writable: {output_dir}")
    return output_dir


def validate_category(category: str) -> str:
    """Validate the book category."""
    valid_categories = ["Fiction", "Non-Fiction", "Business", "Research Paper"]
    if category and category not in valid_categories:
        logger.warning(f"Non-standard category provided: {category}")
    return category


def validate_genre(genre: str | None) -> str:
    """Validate the book genre."""
    if genre is None:
        return "General"
    return genre.strip()


def validate_language(language: str) -> str:
    """Validate the book language."""
    if not language or len(language.strip()) == 0:
        raise ValueError("Book language cannot be empty")
    return language.strip()


def validate_description(description: str | None) -> str | None:
    """Validate the book description."""
    if description is not None and len(description.strip()) == 0:
        raise ValueError("Book description cannot be empty if provided")
    return description


def validate_chapters(chapters: str | int | None) -> int | tuple[int, int] | None:
    """Validate the number of chapters."""
    if chapters is None:
        return None

    if isinstance(chapters, str):
        try:
            if "-" in chapters:
                min_chapters, max_chapters = map(int, chapters.split("-"))
                if min_chapters < 1 or max_chapters < min_chapters:
                    raise ValueError(f"Invalid chapter range: {chapters}")
                return (min_chapters, max_chapters)
            else:
                chapter_count = int(chapters)
                if chapter_count < 1:
                    raise ValueError(f"Invalid chapter count: {chapters}")
                return chapter_count
        except ValueError as e:
            raise ValueError(f"Invalid chapter format '{chapters}': {e}")
    elif isinstance(chapters, int):
        if chapters < 1:
            raise ValueError("Number of chapters must be greater than 0")
        return chapters
    else:
        raise ValueError(f"Invalid chapter type: {type(chapters)}")


def validate_characters(characters: int | None) -> int | None:
    """Validate the number of characters."""
    if characters is not None and characters < 0:
        raise ValueError("Number of characters cannot be negative")
    return characters


def validate_env_file(env_file: str | None) -> str | None:
    """Validate the environment file if provided."""
    if env_file and not Path(env_file).exists():
        raise ValueError(f"Environment file not found: {env_file}")
    return env_file


def validate_model_config(model_config: str | None) -> str | None:
    """Validate the model configuration file if provided."""
    if model_config and not Path(model_config).exists():
        raise ValueError(f"Model configuration file not found: {model_config}")
    return model_config


def validate_default_model(default_model: str | None) -> str | None:
    """Validate the default model if provided."""
    if default_model is not None and len(default_model.strip()) == 0:
        raise ValueError("Default model cannot be empty if provided")
    return default_model


def validate_config_file(config_file: str | None) -> str | None:
    """Validate the configuration file if provided."""
    if config_file and not Path(config_file).exists():
        raise ValueError(f"Configuration file not found: {config_file}")
    return config_file


def validate_log_file_path(log_file: str | None) -> str | None:
    """Validate the log file path if provided."""
    if log_file:
        log_path = Path(log_file)
        if log_path.exists() and not log_path.is_file():
            raise ValueError(f"Log file path exists but is not a file: {log_file}")
        try:
            # Check if directory is writable
            log_dir = log_path.parent
            if not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)
            # Test write access
            if not os.access(str(log_dir), os.W_OK):
                raise ValueError(f"Log file directory is not writable: {log_dir}")
        except Exception as e:
            raise ValueError(f"Invalid log file path: {e}") from e
    return log_file


def validate_llm_provider(llm: str | None) -> str | None:
    """Validate the LLM provider if provided."""
    if llm is not None:
        if len(llm.strip()) == 0:
            raise ValueError("LLM provider cannot be empty if provided")
        # List of supported providers could be expanded in the future
        supported_providers = ["openai", "mock"]
        if llm.lower() not in supported_providers:
            logger.info(f"Non-standard LLM provider specified: {llm}")
    return llm


def validate_generation_flags(all_flag: bool, **flags) -> dict[str, bool]:
    """Validate generation flags."""
    # If all flag is set, override all other flags
    if all_flag:
        return {
            "generate_concept": True,
            "generate_outline": True,
            "generate_characters": True,
            "generate_worldbuilding": True,
            "write_chapters": True,
            "format_book": True,
        }

    # Otherwise use provided flags
    result = {
        "generate_concept": flags.get("generate_concept", False),
        "generate_outline": flags.get("generate_outline", False),
        "generate_characters": flags.get("generate_characters", False),
        "generate_worldbuilding": flags.get("generate_worldbuilding", False),
        "write_chapters": flags.get("write_chapters", False),
        "format_book": flags.get("format_book", False),
    }

    # Check if at least one generation flag is set
    if not any(result.values()):
        logger.info("No generation flags set. Book will be created but no content will be generated.")

    return result


def check_required_parameters(params):
    """
    Check if all required parameters are provided and prompt for missing ones.

    Args:
        params: Dictionary of parameters

    Returns:
        Updated parameters with any missing values filled in
    """
    updated_params = params.copy()

    # Check for required parameters
    if not updated_params.get("title"):
        try:
            updated_params["title"] = typer.prompt("Book title")
        except typer.Abort:
            raise ValueError("Book title is required") from None

    # Check for optional parameters with prompts
    if updated_params.get("generate_characters", False) and updated_params.get("characters") is None:
        try:
            updated_params["characters"] = int(typer.prompt("Number of characters", default="3"))
        except (ValueError, typer.Abort):
            updated_params["characters"] = 3
            logger.info("Invalid input for number of characters. Using default: 3")

    if updated_params.get("write_chapters", False) and updated_params.get("chapters") is None:
        try:
            updated_params["chapters"] = int(typer.prompt("Number of chapters", default="5"))
        except (ValueError, typer.Abort):
            updated_params["chapters"] = 5
            logger.info("Invalid input for number of chapters. Using default: 5")

    return updated_params


def generate_unique_folder_name(title: str) -> str:
    """Generate a unique folder name based on title, date, and hash."""
    from .utils.timestamp_utils import format_timestamp_for_folder_name_with_microseconds

    timestamp = format_timestamp_for_folder_name_with_microseconds()
    title_slug = re.sub(r"[^\w\s-]", "", title.lower())
    title_slug = re.sub(r"[-\s]+", "-", title_slug).strip("-")
    unique_hash = hashlib.sha256(f"{title}{timestamp}".encode()).hexdigest()[:8]
    return f"{title_slug}-{timestamp}-{unique_hash}"


@app.command()
async def create_book(
    title: str | None = typer.Option(None, "--title", "-t", help="Book title"),
    output_dir: str | None = typer.Option(None, "--output-dir", "-o", help="Output directory for the book project"),
    category: str = typer.Option("Fiction", "--category", "-c", help="Book category"),
    genre: str | None = typer.Option(None, "--genre", "-g", help="Book genre"),
    description: str | None = typer.Option(None, "--description", "-d", help="Book description"),
    language: str = typer.Option("English", "--language", "-l", help="Book language"),
    chapters: str | None = typer.Option(None, "--chapters", help="Number of chapters (e.g., 10, 8-12)"),
    characters: int | None = typer.Option(None, "--characters", help="Number of characters"),
    worldbuilding: bool = typer.Option(False, "--worldbuilding", help="Enable worldbuilding"),
    llm: str | None = typer.Option(None, "--llm", help="LLM provider to use"),
    model_config: str | None = typer.Option(None, "--model-config", help="Path to model configuration file"),
    default_model: str | None = typer.Option(None, "--default-model", help="Default model to use when not specified"),
    env_file: str | None = typer.Option(None, "--env-file", help="Path to .env file"),
    config_file: str | None = typer.Option(None, "--config-file", help="Path to configuration file"),
    log_file: str | None = typer.Option(None, "--log-file", help="Path to log file"),
    mock: bool = typer.Option(False, "--mock", help="Use mock LLM provider"),
    generate_concept: bool = typer.Option(False, "--generate-concept", help="Generate book concept"),
    generate_outline: bool = typer.Option(False, "--generate-outline", help="Generate book outline"),
    generate_characters: bool = typer.Option(False, "--generate-characters", help="Generate character profiles"),
    generate_worldbuilding: bool = typer.Option(
        False, "--generate-worldbuilding", help="Generate worldbuilding details"
    ),
    write_chapters: bool = typer.Option(False, "--write-chapters", help="Write all chapters"),
    format_book_flag: bool = typer.Option(False, "--format-book", help="Format the book"),
    user: str | None = typer.Option(None, "--user", help="User identifier for LiteLLM tags (spaces allowed)"),
    all: bool = typer.Option(False, "--all", help="Perform all generation steps"),
):
    """Create a new book using command-line arguments without interactive prompts."""
    try:
        # Check for required parameters and prompt for missing ones
        params = {
            "title": title,
            "output_dir": output_dir,
            "category": category,
            "genre": genre,
            "description": description,
            "language": language,
            "chapters": chapters,
            "characters": characters,
            "worldbuilding": worldbuilding,
            "llm": llm,
            "model_config": model_config,
            "default_model": default_model,
            "env_file": env_file,
            "config_file": config_file,
            "log_file": log_file,
            "mock": mock,
            "generate_concept": generate_concept,
            "generate_outline": generate_outline,
            "generate_characters": generate_characters,
            "generate_worldbuilding": generate_worldbuilding,
            "write_chapters": write_chapters,
            "format_book_flag": format_book_flag,
            "user": user,
            "all": all,
        }

        try:
            params = check_required_parameters(params)
        except ValueError as e:
            console.print(f"[red]Error: {e!s}[/red]")
            return EXIT_INVALID_ARGS
        except typer.Abort:
            console.print("[red]Error: Book title is required[/red]")
            return EXIT_INVALID_ARGS

        # Update local variables from params with proper type casting
        # Handle OptionInfo objects (when called directly vs through typer)
        def safe_convert(value, converter):
            if value is None:
                return None
            # Check if it's an OptionInfo object
            if hasattr(value, "default"):
                if value.default is None:
                    return None
                return converter(value.default)
            return converter(value)

        title = safe_convert(params["title"], str)
        output_dir = safe_convert(params["output_dir"], str)
        category_val = safe_convert(params["category"], str)
        genre = safe_convert(params["genre"], str)
        description = safe_convert(params["description"], str)
        language_val = safe_convert(params["language"], str)
        chapters = safe_convert(params["chapters"], str)
        characters = safe_convert(params["characters"], int)
        worldbuilding_val = safe_convert(params["worldbuilding"], bool) or False
        llm = safe_convert(params["llm"], str)
        model_config = safe_convert(params["model_config"], str)
        default_model = safe_convert(params["default_model"], str)
        env_file = safe_convert(params["env_file"], str)
        config_file = safe_convert(params["config_file"], str)
        log_file = safe_convert(params["log_file"], str)
        mock_val = safe_convert(params["mock"], bool) or False
        generate_concept = safe_convert(params["generate_concept"], bool) or False
        generate_outline = safe_convert(params["generate_outline"], bool) or False
        generate_characters = safe_convert(params["generate_characters"], bool) or False
        generate_worldbuilding = safe_convert(params["generate_worldbuilding"], bool) or False
        write_chapters = safe_convert(params["write_chapters"], bool) or False
        format_book_flag = safe_convert(params["format_book_flag"], bool) or False
        all_val = safe_convert(params["all"], bool) or False
        # Validate all parameters
        try:
            if title is None:
                raise ValueError("Book title is required")
            title = validate_title(title)
            output_dir = validate_output_dir(output_dir)
            category = validate_category(category_val or "Fiction")
            genre = validate_genre(genre)
            description = validate_description(description)
            language = validate_language(language_val or "English")  # Only check for empty
            language = normalize_language(language)  # Normalize to BCP 47
            validated_chapters = validate_chapters(chapters)
            characters = validate_characters(characters)
            env_file = validate_env_file(env_file)
            model_config = validate_model_config(model_config)
            config_file = validate_config_file(config_file)
            log_file = validate_log_file_path(log_file)
            llm = validate_llm_provider(llm)
            default_model = validate_default_model(default_model)
            worldbuilding = worldbuilding_val or False
            mock = mock_val or False
            all = all_val or False

            # Validate generation flags
            generation_flags = validate_generation_flags(
                all,
                generate_concept=generate_concept or False,
                generate_outline=generate_outline or False,
                generate_characters=generate_characters or False,
                generate_worldbuilding=generate_worldbuilding or False,
                write_chapters=write_chapters or False,
                format_book=format_book_flag or False,
            )
        except ValueError as e:
            console.print(f"[red]Error in command arguments: {e!s}[/red]")
            return EXIT_INVALID_ARGS

        # Load environment configuration
        try:
            settings = Settings(env_file=env_file, config_file=config_file)

            # Load model configuration
            model_config_dict = settings.get_model_config(model_config)
            if model_config_dict:
                console.print(f"[cyan]📋 Loaded model configuration with {len(model_config_dict)} entries[/cyan]")
                logger.info(f"Model configuration: {model_config_dict}")

        except Exception as e:
            console.print(f"[red]Error loading environment configuration: {e!s}[/red]")
            return EXIT_ENV_CONFIG_ERROR

        # Generate a project name from the title
        project_name = generate_unique_folder_name(title)

        # Create the project knowledge base
        project_knowledge_base = ProjectKnowledgeBase(project_name=project_name, title=title)
        project_knowledge_base.set("category", category)
        project_knowledge_base.set("genre", genre)
        project_knowledge_base.set("description", description or f"A {genre or 'general'} {category} book.")
        project_knowledge_base.set("language", language)

        # Set optional parameters if provided
        if validated_chapters is not None:
            project_knowledge_base.set("num_chapters", validated_chapters)
        if characters is not None:
            project_knowledge_base.set("num_characters", characters)
        project_knowledge_base.set("worldbuilding_needed", worldbuilding)
        project_knowledge_base.set("review_preference", "AI")  # Always use AI review in non-interactive mode

        # Set config file name
        config_file_name = Path(config_file).name if config_file else "config.json"
        project_knowledge_base.set("config_file", config_file_name)

        # Initialize LLM client (always use OpenAI)
        try:
            project_manager.initialize_llm_client("openai", user)
        except Exception as e:
            console.print(f"[red]Error initializing LLM client: {e!s}[/red]")
            return EXIT_LLM_INIT_ERROR

        # Initialize project
        project_manager.create_project_from_kb(project_knowledge_base, str(output_dir) if output_dir else "")

        # Execute the requested steps
        if generation_flags["generate_concept"]:
            console.print("\n[cyan]✨ Generating book concept...[/cyan]")
            await project_manager.generate_concept()
            project_manager.checkpoint()
            console.print("[green]✅ Concept generated![/green]")

        if generation_flags["generate_outline"]:
            console.print("\n[cyan]📝 Generating book outline...[/cyan]")
            await project_manager.generate_outline()
            project_manager.checkpoint()
            console.print("[green]✅ Outline generated![/green]")

        if generation_flags["generate_characters"]:
            if project_knowledge_base.get("num_characters", 0) > 0:
                console.print("\n[cyan]👥 Generating character profiles...[/cyan]")
                await project_manager.generate_characters()
                project_manager.checkpoint()
                console.print("[green]✅ Character profiles generated![/green]")
            else:
                console.print("[yellow]⚠️ Skipping character generation (num_characters is 0 or not set)[/yellow]")

        if generation_flags["generate_worldbuilding"]:
            if project_knowledge_base.get("worldbuilding_needed", False):
                console.print("\n[cyan]🏔️ Creating worldbuilding details...[/cyan]")
                await project_manager.generate_worldbuilding()
                project_manager.checkpoint()
                console.print("[green]✅ Worldbuilding details generated![/green]")
            else:
                console.print("[yellow]⚠️ Skipping worldbuilding (worldbuilding_needed is False)[/yellow]")

        if generation_flags["write_chapters"]:
            num_chapters = project_knowledge_base.get("num_chapters", 1)
            if isinstance(num_chapters, tuple):
                num_chapters = num_chapters[1]

            console.print(f"\n[cyan]📝 Writing {num_chapters} chapters...[/cyan]")

            for i in range(1, num_chapters + 1):
                chapter = project_knowledge_base.get_chapter(i)
                if chapter is None:
                    console.print(
                        f"[yellow]WARNING: Chapter {i} not found in outline. Creating basic structure...[/yellow]"
                    )
                    chapter = Chapter(
                        chapter_number=i,
                        title=f"Chapter {i}",
                        summary="To be written",
                    )
                    project_knowledge_base.add_chapter(chapter)

                console.print(f"[cyan]Writing Chapter {i}: {chapter.title}[/cyan]")

                await project_manager.write_and_review_chapter(i)
                project_manager.checkpoint()
                console.print(f"[green]✅ Chapter {i} completed successfully[/green]")

            console.print("[green]✅ All chapters written![/green]")

        if generation_flags["format_book"]:
            console.print("\n[cyan]📘 Formatting book...[/cyan]")
            if project_manager.project_dir:
                output_path = str(project_manager.project_dir / MANUSCRIPT_MD_FILENAME)
            else:
                console.print("[red]Error: Project directory not set[/red]")
                return EXIT_BOOK_CREATION_ERROR
            await project_manager.format_book()
            console.print(f"[green]✅ Book formatted and saved to: {output_path}[/green]")

        # Only show success message if all steps completed successfully
        console.print("\n[green]🎉 Book creation process complete![/green]")
        console.print(f"[cyan]Project directory: {project_manager.project_dir}[/cyan]")
        return EXIT_SUCCESS

    except ConnectionError as e:
        console.print(f"[red]Network error during book creation: {e!s}[/red]")
        logger.exception("Network error in book creation process")
        return EXIT_NETWORK_ERROR
    except Exception as e:
        console.print(f"[red]ERROR: {e!s}[/red]")
        logger.exception("Error in book creation process")
        return EXIT_GENERAL_ERROR


async def main():
    try:
        typer.run(create_book)
    except Exception as e:
        # This is to prevent the application from crashing silently
        # and to ensure that the exit code is non-zero.
        logger.error(f"Unhandled exception: {e}")


if __name__ == "__main__":
    asyncio.run(main())
