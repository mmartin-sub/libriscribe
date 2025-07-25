import typer
import re
import os
import sys
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console

from libriscribe.agents.project_manager import ProjectManagerAgent
from libriscribe.knowledge_base import ProjectKnowledgeBase, Chapter
from libriscribe.settings import Settings, MANUSCRIPT_MD_FILENAME

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
project_manager = ProjectManagerAgent(llm_client=None)

def validate_title(title: str) -> str:
    """Validate the book title."""
    if not title or len(title.strip()) == 0:
        raise ValueError("Book title cannot be empty")
    return title.strip()

def validate_output_dir(output_dir: Optional[str]) -> Optional[str]:
    """Validate the output directory if provided."""
    if output_dir:
        path = Path(output_dir)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")
            except Exception as e:
                raise ValueError(f"Could not create output directory: {e}")
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

def validate_genre(genre: Optional[str]) -> str:
    """Validate the book genre."""
    if genre is None:
        return "General"
    return genre.strip()

def validate_language(language: str) -> str:
    """Validate the book language."""
    if not language or len(language.strip()) == 0:
        raise ValueError("Book language cannot be empty")
    return language.strip()

def validate_description(description: Optional[str]) -> Optional[str]:
    """Validate the book description."""
    if description is not None and len(description.strip()) == 0:
        raise ValueError("Book description cannot be empty if provided")
    return description

def validate_chapters(chapters: Optional[int]) -> Optional[int]:
    """Validate the number of chapters."""
    if chapters is not None and chapters <= 0:
        raise ValueError("Number of chapters must be greater than 0")
    return chapters

def validate_characters(characters: Optional[int]) -> Optional[int]:
    """Validate the number of characters."""
    if characters is not None and characters < 0:
        raise ValueError("Number of characters cannot be negative")
    return characters

def validate_env_file(env_file: Optional[str]) -> Optional[str]:
    """Validate the environment file if provided."""
    if env_file and not Path(env_file).exists():
        raise ValueError(f"Environment file not found: {env_file}")
    return env_file

def validate_model_config(model_config: Optional[str]) -> Optional[str]:
    """Validate the model configuration file if provided."""
    if model_config and not Path(model_config).exists():
        raise ValueError(f"Model configuration file not found: {model_config}")
    return model_config

def validate_default_model(default_model: Optional[str]) -> Optional[str]:
    """Validate the default model if provided."""
    if default_model is not None and len(default_model.strip()) == 0:
        raise ValueError("Default model cannot be empty if provided")
    return default_model

def validate_config_file(config_file: Optional[str]) -> Optional[str]:
    """Validate the configuration file if provided."""
    if config_file and not Path(config_file).exists():
        raise ValueError(f"Configuration file not found: {config_file}")
    return config_file

def validate_log_file_path(log_file: Optional[str]) -> Optional[str]:
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
            raise ValueError(f"Invalid log file path: {e}")
    return log_file

def validate_llm_provider(llm: Optional[str]) -> Optional[str]:
    """Validate the LLM provider if provided."""
    if llm is not None:
        if len(llm.strip()) == 0:
            raise ValueError("LLM provider cannot be empty if provided")
        # List of supported providers could be expanded in the future
        supported_providers = ["openai", "anthropic", "google", "mistral", "ollama"]
        if llm.lower() not in supported_providers:
            logger.warning(f"Non-standard LLM provider specified: {llm}")
    return llm

def validate_generation_flags(all_flag: bool, **flags) -> Dict[str, bool]:
    """Validate generation flags."""
    # If all flag is set, override all other flags
    if all_flag:
        return {
            "generate_concept": True,
            "generate_outline": True,
            "generate_characters": True,
            "generate_worldbuilding": True,
            "write_chapters": True,
            "format_book": True
        }
    
    # Otherwise use provided flags
    result = {
        "generate_concept": flags.get("generate_concept", False),
        "generate_outline": flags.get("generate_outline", False),
        "generate_characters": flags.get("generate_characters", False),
        "generate_worldbuilding": flags.get("generate_worldbuilding", False),
        "write_chapters": flags.get("write_chapters", False),
        "format_book": flags.get("format_book", False)
    }
    
    # Check if at least one generation flag is set
    if not any(result.values()):
        logger.warning("No generation flags set. Book will be created but no content will be generated.")
    
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
            raise ValueError("Book title is required")
    
    # Check for optional parameters with prompts
    if updated_params.get("generate_characters", False) and updated_params.get("characters") is None:
        try:
            updated_params["characters"] = int(typer.prompt("Number of characters", default="3"))
        except (ValueError, typer.Abort):
            updated_params["characters"] = 3
            logger.warning("Invalid input for number of characters. Using default: 3")
    
    if updated_params.get("write_chapters", False) and updated_params.get("chapters") is None:
        try:
            updated_params["chapters"] = int(typer.prompt("Number of chapters", default="5"))
        except (ValueError, typer.Abort):
            updated_params["chapters"] = 5
            logger.warning("Invalid input for number of chapters. Using default: 5")
    
    return updated_params

def generate_unique_folder_name(title: str) -> str:
    """Generate a unique folder name based on title, date, and hash."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    title_slug = re.sub(r'[^\w\s-]', '', title.lower())
    title_slug = re.sub(r'[-\s]+', '-', title_slug).strip('-')
    unique_hash = hashlib.md5(f"{title}{timestamp}".encode()).hexdigest()[:8]
    return f"{title_slug}-{timestamp}-{unique_hash}"

@app.command()
def create_book(
    title: str = typer.Option(None, "--title", "-t", help="Book title"),
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
    format_book_flag: bool = typer.Option(False, "--format-book", help="Format the book"),
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
            "all": all
        }
        
        try:
            params = check_required_parameters(params)
        except ValueError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return EXIT_INVALID_ARGS
        
        # Update local variables from params
        title = params["title"]
        output_dir = params["output_dir"]
        category = params["category"]
        genre = params["genre"]
        description = params["description"]
        language = params["language"]
        chapters = params["chapters"]
        characters = params["characters"]
        worldbuilding = params["worldbuilding"]
        llm = params["llm"]
        model_config = params["model_config"]
        default_model = params["default_model"]
        env_file = params["env_file"]
        config_file = params["config_file"]
        log_file = params["log_file"]
        mock = params["mock"]
        generate_concept = params["generate_concept"]
        generate_outline = params["generate_outline"]
        generate_characters = params["generate_characters"]
        generate_worldbuilding = params["generate_worldbuilding"]
        write_chapters = params["write_chapters"]
        format_book_flag = params["format_book_flag"]
        all = params["all"]
        # Validate all parameters
        try:
            title = validate_title(title)
            output_dir = validate_output_dir(output_dir)
            category = validate_category(category)
            genre = validate_genre(genre)
            description = validate_description(description)
            language = validate_language(language)
            chapters = validate_chapters(chapters)
            characters = validate_characters(characters)
            env_file = validate_env_file(env_file)
            model_config = validate_model_config(model_config)
            config_file = validate_config_file(config_file)
            log_file = validate_log_file_path(log_file)
            llm = validate_llm_provider(llm)
            default_model = validate_default_model(default_model)
            
            # Validate generation flags
            generation_flags = validate_generation_flags(
                all,
                generate_concept=generate_concept,
                generate_outline=generate_outline,
                generate_characters=generate_characters,
                generate_worldbuilding=generate_worldbuilding,
                write_chapters=write_chapters,
                format_book=format_book_flag
            )
        except ValueError as e:
            console.print(f"[red]Error in command arguments: {str(e)}[/red]")
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
            console.print(f"[red]Error loading environment configuration: {str(e)}[/red]")
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
        if chapters is not None:
            project_knowledge_base.set("num_chapters", chapters)
        if characters is not None:
            project_knowledge_base.set("num_characters", characters)
        project_knowledge_base.set("worldbuilding_needed", worldbuilding)
        project_knowledge_base.set("review_preference", "AI")  # Always use AI review in non-interactive mode
        
        # Set LLM provider
        llm_provider = llm or settings.default_llm
        project_knowledge_base.set("llm_provider", llm_provider)
        
        # Initialize LLM client
        try:
            if mock:
                # TODO: Implement mock LLM client initialization
                console.print("[yellow]Using mock LLM provider[/yellow]")
                # This will be implemented in task 5.2
            else:
                project_manager.initialize_llm_client(llm_provider)
        except Exception as e:
            console.print(f"[red]Error initializing LLM client: {str(e)}[/red]")
            return EXIT_LLM_INIT_ERROR
        
        # Initialize project
        try:
            project_manager.initialize_project_with_data(project_knowledge_base, custom_dir=output_dir)
        except Exception as e:
            console.print(f"[red]Error initializing project: {str(e)}[/red]")
            return EXIT_FILE_SYSTEM_ERROR
        
        console.print(f"\n[green]✅ Project '{project_name}' created successfully![/green]")
        
        # Execute the requested steps
        try:
            if generation_flags["generate_concept"]:
                console.print("\n[cyan]✨ Generating book concept...[/cyan]")
                try:
                    project_manager.generate_concept()
                    project_manager.checkpoint()
                    console.print(f"[green]✅ Concept generated![/green]")
                except ConnectionError as e:
                    console.print(f"[red]Network error while generating concept: {str(e)}[/red]")
                    logger.exception("Network error during concept generation")
                    return EXIT_NETWORK_ERROR
                
            if generation_flags["generate_outline"]:
                console.print("\n[cyan]📝 Generating book outline...[/cyan]")
                try:
                    project_manager.generate_outline()
                    project_manager.checkpoint()
                    console.print(f"[green]✅ Outline generated![/green]")
                except ConnectionError as e:
                    console.print(f"[red]Network error while generating outline: {str(e)}[/red]")
                    logger.exception("Network error during outline generation")
                    return EXIT_NETWORK_ERROR
                
            if generation_flags["generate_characters"]:
                if project_knowledge_base.get("num_characters", 0) > 0:
                    console.print("\n[cyan]👥 Generating character profiles...[/cyan]")
                    try:
                        project_manager.generate_characters()
                        project_manager.checkpoint()
                        console.print(f"[green]✅ Character profiles generated![/green]")
                    except ConnectionError as e:
                        console.print(f"[red]Network error while generating characters: {str(e)}[/red]")
                        logger.exception("Network error during character generation")
                        return EXIT_NETWORK_ERROR
                else:
                    console.print("[yellow]⚠️ Skipping character generation (num_characters is 0 or not set)[/yellow]")
                
            if generation_flags["generate_worldbuilding"]:
                if project_knowledge_base.get("worldbuilding_needed", False):
                    console.print("\n[cyan]🏔️ Creating worldbuilding details...[/cyan]")
                    try:
                        project_manager.generate_worldbuilding()
                        project_manager.checkpoint()
                        console.print(f"[green]✅ Worldbuilding details generated![/green]")
                    except ConnectionError as e:
                        console.print(f"[red]Network error while generating worldbuilding: {str(e)}[/red]")
                        logger.exception("Network error during worldbuilding generation")
                        return EXIT_NETWORK_ERROR
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
                        console.print(f"[yellow]WARNING: Chapter {i} not found in outline. Creating basic structure...[/yellow]")
                        chapter = Chapter(
                            chapter_number=i,
                            title=f"Chapter {i}",
                            summary="To be written"
                        )
                        project_knowledge_base.add_chapter(chapter)
                    
                    console.print(f"[cyan]Writing Chapter {i}: {chapter.title}[/cyan]")
                    
                    try:
                        project_manager.write_and_review_chapter(i)
                        project_manager.checkpoint()
                        console.print(f"[green]✅ Chapter {i} completed successfully[/green]")
                    except ConnectionError as e:
                        console.print(f"[red]Network error writing chapter {i}: {str(e)}[/red]")
                        logger.exception(f"Network error writing chapter {i}")
                        return EXIT_NETWORK_ERROR
                    except Exception as e:
                        console.print(f"[red]ERROR writing chapter {i}: {str(e)}[/red]")
                        logger.exception(f"Error writing chapter {i}")
                
                console.print("[green]✅ All chapters written![/green]")
                
            if generation_flags["format_book"]:
                console.print("\n[cyan]📘 Formatting book...[/cyan]")
                output_format = "md"  # Default to markdown in non-interactive mode
                output_path = str(project_manager.project_dir / MANUSCRIPT_MD_FILENAME)
                try:
                    project_manager.format_book(output_path)
                    console.print(f"[green]✅ Book formatted and saved to: {output_path}[/green]")
                except ConnectionError as e:
                    console.print(f"[red]Network error while formatting book: {str(e)}[/red]")
                    logger.exception("Network error during book formatting")
                    return EXIT_NETWORK_ERROR
        except ConnectionError as e:
            console.print(f"[red]Network error during book creation: {str(e)}[/red]")
            logger.exception("Network error in book creation process")
            return EXIT_NETWORK_ERROR
        except Exception as e:
            console.print(f"[red]ERROR during book creation: {str(e)}[/red]")
            logger.exception("Error in book creation process")
            return EXIT_BOOK_CREATION_ERROR
        
        console.print("\n[green]🎉 Book creation process complete![/green]")
        console.print(f"[cyan]Project directory: {project_manager.project_dir}[/cyan]")
        return EXIT_SUCCESS
        
    except Exception as e:
        console.print(f"[red]ERROR: {str(e)}[/red]")
        logger.exception("Error in create_book command")
        return EXIT_GENERAL_ERROR

if __name__ == "__main__":
    app()