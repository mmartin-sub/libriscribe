# src/libriscribe2/services/book_creator.py
import asyncio
import hashlib
import logging
import re
import warnings
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

from libriscribe2.agents.project_manager import ProjectManagerAgent
from libriscribe2.knowledge_base import ProjectKnowledgeBase
from libriscribe2.settings import Settings
from libriscribe2.utils.content_exporters import export_characters_to_markdown, export_worldbuilding_to_markdown
from libriscribe2.utils.exceptions import LLMGenerationError
from ..utils.llm_client_protocol import LLMClientProtocol

# Configure warnings to be treated as errors
warnings.filterwarnings("error", category=RuntimeWarning)

logger = logging.getLogger(__name__)


class BookCreatorService:
    """Service for creating books via CLI without interactive prompts."""

    def __init__(
        self,
        config_file: str | None = None,
        mock: bool = False,
        log_file: str | None = None,
        log_level: str = "INFO",
        llm_client: LLMClientProtocol | None = None,
    ):
        """
        Initialize the BookCreatorService.

        Args:
            config_file: Path to configuration file (.env, .yaml, .yml, or .json)
            mock: Whether to use mock LLM provider
            log_file: Path to log file
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            llm_client: Optional pre-configured LLM client
        """
        self.settings = Settings(config_file=config_file)
        self.config: dict[str, Any] = {}  # Config is now handled by Settings
        self.model_config = self.settings.get_model_config()
        self.mock = mock
        self.project_manager: ProjectManagerAgent | None = None
        self.log_file = log_file
        self.llm_client = llm_client
        self.log_level = self._validate_log_level(log_level)
        self.console = Console()

    def _slugify(self, text: str) -> str:
        """Convert text to a URL-friendly slug."""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

    def _generate_unique_folder_name(self, title: str) -> str:
        """Generate a unique folder name based on title, date, and hash."""
        from ..utils.timestamp_utils import format_timestamp_for_folder_name

        timestamp = format_timestamp_for_folder_name()
        title_slug = self._slugify(title)
        # Use SHA-256 for better security, even though this is not a security-critical use case
        # The hash is only used for uniqueness, not for cryptographic purposes
        unique_hash = hashlib.sha256(f"{title}{timestamp}".encode()).hexdigest()[:8]
        return f"{title_slug}-{timestamp}-{unique_hash}"

    def _validate_log_level(self, log_level: str) -> int:
        """Validate and convert log level string to logging constant."""
        valid_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        log_level_upper = log_level.upper()
        if log_level_upper not in valid_levels:
            logger.warning(f"Invalid log level '{log_level}', using INFO instead")
            return logging.INFO

        return valid_levels[log_level_upper]

    def _is_valid_project_name(self, project_name: str) -> bool:
        """Validate project name format."""
        import re

        # Allow letters, numbers, hyphens, underscores, and spaces
        # Spaces are allowed but not recommended for better compatibility
        pattern = r"^[a-zA-Z0-9_\-\s]+$"
        return bool(re.match(pattern, project_name))

    def _create_project_directory_safely(self, project_dir: Path, project_name: str) -> Path:
        """
        Create project directory in a thread-safe manner.

        Args:
            project_dir: The desired project directory path
            project_name: The project name for logging

        Returns:
            The actual project directory path (may be modified if conflicts)

        Raises:
            ValueError: If custom project name is specified but directory exists and is not empty
        """
        import os
        import secrets
        import time

        # If this is a custom project name, check if it exists and is empty
        if project_name != self._generate_unique_folder_name("temp"):
            if project_dir.exists():
                if any(project_dir.iterdir()):
                    raise ValueError(f"Project directory '{project_name}' already exists and is not empty")
                else:
                    # Directory exists but is empty, safe to use
                    project_dir.mkdir(parents=True, exist_ok=True)
                    return project_dir
            else:
                # Directory doesn't exist, safe to create
                project_dir.mkdir(parents=True, exist_ok=True)
                return project_dir

        # For auto-generated names, handle potential conflicts
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                # Try to create the directory atomically
                project_dir.mkdir(parents=True, exist_ok=False)
                return project_dir
            except FileExistsError:
                if attempt == max_attempts - 1:
                    # Last attempt failed, generate a new name with additional randomness
                    from ..utils.timestamp_utils import format_timestamp_for_folder_name

                    timestamp = format_timestamp_for_folder_name()
                    process_id = os.getpid()
                    random_suffix = f"{timestamp}-{process_id}-{secrets.randbelow(9000) + 1000}"
                    new_project_name = f"{project_name}-{random_suffix}"
                    new_project_dir = project_dir.parent / new_project_name
                    new_project_dir.mkdir(parents=True, exist_ok=False)
                    logger.warning(f"Project name conflict resolved: using '{new_project_name}'")
                    return new_project_dir
                else:
                    # Add small delay and retry with slightly modified name
                    time.sleep(0.1)
                    timestamp = format_timestamp_for_folder_name()
                    project_name = f"{project_name}-{timestamp}"
                    project_dir = project_dir.parent / project_name

        # This should never be reached, but return the final project_dir for completeness
        return project_dir

    def setup_logging(self, project_dir: Path) -> None:
        """Set up logging for this book project."""
        if self.log_file:
            log_path = Path(self.log_file)
        else:
            # Ensure the project directory exists before creating the log file
            project_dir.mkdir(parents=True, exist_ok=True)
            log_path = project_dir / "book_creation.log"

        # Configure logging to write to the specified log file
        file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")

        # Normalize logger names by removing libriscribe2 prefix and using consistent format
        class NormalizedFormatter(logging.Formatter):
            def format(self, record):
                # Remove libriscribe2 prefix from logger names
                if record.name.startswith("libriscribe2."):
                    record.name = record.name[13:]  # Remove 'libriscribe2.'
                return super().format(record)

        file_handler.setFormatter(NormalizedFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        file_handler.setLevel(self.log_level)  # Use specified log level

        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)

        # Ensure root logger level allows all messages to pass through
        if root_logger.level > logging.DEBUG:
            root_logger.setLevel(logging.DEBUG)

        logger.info(f"Project logging configured at: {log_path}")
        logger.debug(f"Project directory: {project_dir}")
        logger.debug(f"Project log file: {log_path}")

        # Log links to other relevant log files
        logger.info("---")
        logger.info("Other log files:")
        for log_pattern in ["llm_output_*.log", "libriscribe_*.log"]:
            for log_file in project_dir.glob(log_pattern):
                logger.info(f"  - {log_file.name}")
        logger.info("---")

    def create_book(self, args: dict[str, Any]) -> bool:
        """
        Synchronous book creation. For async usage, prefer `await acreate_book(args)`.
        """

        return asyncio.run(self.acreate_book(args))

    async def create_book_from_cli(self, args: dict[str, Any]) -> bool:
        """
        Creates a book from the raw CLI arguments.
        """
        return await self.acreate_book(args)

    async def acreate_book(self, args: dict[str, Any]) -> bool:
        """
        Asynchronous book creation. This is the preferred method for async code.
        """
        try:
            # Handle auto-title generation
            title = args.get("title")

            # If no title provided, use temporary title for project creation
            if not title:
                title = "Untitled Book"
                args["title"] = title
                logger.info("No title provided, using temporary title for project creation")
            else:
                logger.info(f"Using provided title: {title}")

            # Determine project name
            if args.get("project_name"):
                project_name = args["project_name"]
                # Validate custom project name
                if not self._is_valid_project_name(project_name):
                    raise ValueError(
                        f"Invalid project name: {project_name}. Use only letters, numbers, hyphens, underscores, and spaces."
                    )
            else:
                project_name = self._generate_unique_folder_name(args["title"])

            # Use projects_dir from settings
            output_dir = Path(self.settings.projects_dir)
            project_dir = output_dir / project_name

            # Thread-safe project directory creation
            project_dir = self._create_project_directory_safely(project_dir, project_name)

            # Set up logging early to capture all messages
            self.setup_logging(project_dir)

            # Display project information early
            self.console.print(f"📁 [cyan]Project directory: {project_dir}[/cyan]")
            self.console.print(f"📚 [cyan]Creating book: {args['title']}[/cyan]")

            logger.info(f"Starting book creation: {args['title']}")
            logger.info(f"Project directory: {project_dir}")

            # Create project knowledge base
            kb = self._create_knowledge_base(args, project_name)

            # Initialize project manager with model configuration
            self.project_manager = ProjectManagerAgent(settings=self.settings, model_config=self.model_config, llm_client=self.llm_client)

            if not self.llm_client:
                # Initialize LLM client and agents
                # Use mock provider if mock flag is set, otherwise use specified LLM or default
                if self.mock:
                    llm_provider = "mock"
                else:
                    llm_provider = args.get("llm") or self.settings.default_llm
                # Get user from args if provided
                user = args.get("user")
                self.project_manager.initialize_llm_client(llm_provider, user)

            # Create the project
            if self.project_manager:
                self.project_manager.create_project_from_kb(kb, str(project_dir))
            else:
                logger.error("Failed to initialize project manager")
                return False

            # Execute requested generation steps
            try:
                success = await self._execute_generation_steps(args)
            except Exception:
                raise

            if success:
                # Display book statistics
                self._display_book_statistics()
                logger.info("Book creation completed successfully")
                self.console.print(f"\n✅ [green]Book created successfully in: {project_dir}[/green]")
            else:
                logger.error("Book creation failed")

            return success

        except Exception as e:
            # Log the full error for debugging to file only
            logger.exception("Error during book creation")

            # Check if mock mode is already being used
            is_mock_mode = args.get("mock", False)

            # Convert all exceptions to RuntimeError for consistent handling
            if not isinstance(e, RuntimeError):
                e = RuntimeError(str(e))

            # Provide helpful error messages for common issues
            if "API key not found" in str(e) or "missing_api_key" in str(e):
                if is_mock_mode:
                    error_msg = "❌ Configuration error. Check your config file and API keys."
                else:
                    error_msg = (
                        "❌ No API key found. To use real LLM providers:\n"
                        "  1. Provide a configuration file with your API keys, or\n"
                        "  2. Use --mock flag for testing without API keys\n\n"
                        "Example: create-book --title 'My Book' --all --mock"
                    )
                raise RuntimeError(error_msg) from e
            elif "not fully implemented" in str(e) or "not_implemented" in str(e):
                if is_mock_mode:
                    error_msg = "❌ LLM provider not fully implemented yet."
                else:
                    error_msg = (
                        "❌ LLM provider not fully implemented yet.\n"
                        "  Use --mock flag for testing: create-book --title 'My Book' --all --mock"
                    )
                raise RuntimeError(error_msg) from e
            elif "Timeout" in str(e) or "timeout" in str(e).lower():
                if is_mock_mode:
                    error_msg = "❌ Request timed out. Try again later."
                else:
                    error_msg = (
                        "❌ Request timed out. This could be due to:\n"
                        "  1. Network connectivity issues\n"
                        "  2. LLM service being slow or unavailable\n"
                        "  3. Request being too complex\n\n"
                        "💡 Try again or use --mock flag for testing"
                    )
                raise RuntimeError(error_msg) from e
            elif "408" in str(e):
                if is_mock_mode:
                    error_msg = "❌ Request timeout (408 error). Try again later."
                else:
                    error_msg = (
                        "❌ Request timeout (408 error). The LLM service is taking too long to respond.\n"
                        "💡 Try again later or use --mock flag for testing"
                    )
                raise RuntimeError(error_msg) from e
            else:
                # For other errors, provide a generic message without suggesting --mock
                error_msg = "❌ Book creation failed. Check the log file for detailed error information."
                raise RuntimeError(error_msg) from e

    async def generate_concept(self, project_name: str) -> None:
        """Generates a book concept."""
        if not self.project_manager:
            self.project_manager = ProjectManagerAgent(settings=self.settings, model_config=self.model_config)
        self.project_manager.load_project_data(project_name)
        await self.project_manager.generate_concept()

    async def generate_outline(self, project_name: str) -> None:
        """Generates a book outline."""
        if not self.project_manager:
            self.project_manager = ProjectManagerAgent(settings=self.settings, model_config=self.model_config)
        self.project_manager.load_project_data(project_name)
        await self.project_manager.generate_outline()

    async def generate_characters(self, project_name: str) -> None:
        """Generates character profiles."""
        if not self.project_manager:
            self.project_manager = ProjectManagerAgent(settings=self.settings, model_config=self.model_config)
        self.project_manager.load_project_data(project_name)
        await self.project_manager.generate_characters()

    async def generate_worldbuilding(self, project_name: str) -> None:
        """Generates worldbuilding details."""
        if not self.project_manager:
            self.project_manager = ProjectManagerAgent(settings=self.settings, model_config=self.model_config)
        self.project_manager.load_project_data(project_name)
        await self.project_manager.generate_worldbuilding()

    async def write_chapter(self, project_name: str, chapter_number: int) -> None:
        """Writes a specific chapter."""
        if not self.project_manager:
            self.project_manager = ProjectManagerAgent(settings=self.settings, model_config=self.model_config)
        self.project_manager.load_project_data(project_name)
        await self.project_manager.write_and_review_chapter(chapter_number)

    async def edit_chapter(self, project_name: str, chapter_number: int) -> None:
        """Edits a specific chapter."""
        if not self.project_manager:
            self.project_manager = ProjectManagerAgent(settings=self.settings, model_config=self.model_config)
        self.project_manager.load_project_data(project_name)
        await self.project_manager.edit_chapter(chapter_number)

    async def format_book(self, project_name: str) -> None:
        """Formats the book."""
        if not self.project_manager:
            self.project_manager = ProjectManagerAgent(settings=self.settings, model_config=self.model_config)
        self.project_manager.load_project_data(project_name)
        await self.project_manager.format_book()

    async def research_topic(self, query: str) -> None:
        """Performs web research on a given query."""
        if not self.project_manager:
            self.project_manager = ProjectManagerAgent(settings=self.settings, model_config=self.model_config)
        await self.project_manager.research_topic(query)

    async def resume_project(self, project_name: str) -> None:
        """Resumes a project from the last checkpoint."""
        if not self.project_manager:
            self.project_manager = ProjectManagerAgent(settings=self.settings, model_config=self.model_config)

        try:
            self.project_manager.load_project_data(project_name)
            logger.info(f"Project '{project_name}' resumed successfully.")
            self.console.print(f"✅ [green]Project '{project_name}' resumed.[/green]")
        except FileNotFoundError:
            logger.error(f"Project '{project_name}' not found.")
            self.console.print(f"❌ [red]Error: Project '{project_name}' not found.[/red]")
        except Exception:
            logger.exception(f"Failed to resume project '{project_name}'")
            self.console.print(
                f"❌ [red]Error: Failed to resume project '{project_name}'. Check logs for details.[/red]"
            )

    def _create_knowledge_base(self, args: dict[str, Any], project_name: str) -> ProjectKnowledgeBase:
        """Create a ProjectKnowledgeBase from CLI arguments."""
        kb = ProjectKnowledgeBase(project_name=project_name)

        # Set basic properties
        kb.project_name = project_name
        kb.title = args["title"]
        kb.category = args.get("category", "Fiction")
        kb.genre = args.get("genre", "")
        kb.description = args.get("description", "")
        kb.language = args.get("language") or self.settings.default_language
        from libriscribe2.utils.validation_mixin import ValidationMixin as VM

        kb.target_audience = VM.validate_target_audience(args.get("target_audience", "General"))
        kb.auto_title = args.get("auto_title", False)  # Save auto-title flag
        # Set number of characters - compute default based on book length if not specified
        specified_characters = args.get("characters")
        if specified_characters is not None:
            # Handle advanced character specification (e.g., "5", "3-7", "5+")
            if isinstance(specified_characters, str):
                # Store the original string for logging
                kb.num_characters_str = specified_characters
                # Generate random character count from range
                kb.num_characters = VM.generate_random_character_count(specified_characters)
                logger.info(
                    f"Using manual character override: {specified_characters} → selected {kb.num_characters} characters"
                )
            else:
                # Handle integer input (backward compatibility)
                kb.num_characters = specified_characters
                logger.info(f"Using manual character override: {kb.num_characters}")
        else:
            # Compute default based on book length
            if args.get("chapters"):
                num_chapters = args["chapters"]
            else:
                # Check for configuration override
                import os

                config_chapters = os.getenv("NUM_CHAPTERS")
                if config_chapters:
                    try:
                        num_chapters = int(config_chapters)
                    except ValueError:
                        # Fall back to category default
                        if args.get("category", "Fiction").lower() == "fiction":
                            num_chapters = 10
                        else:
                            num_chapters = 5
                else:
                    # Use default based on category
                    if args.get("category", "Fiction").lower() == "fiction":
                        num_chapters = 10
                    else:
                        num_chapters = 5

            # Compute reasonable character count based on chapters
            if num_chapters <= 5:
                kb.num_characters = 3  # Short story
            elif num_chapters <= 10:
                kb.num_characters = 5  # Novella
            elif num_chapters <= 15:
                kb.num_characters = 7  # Novel
            else:
                kb.num_characters = 10  # Epic novel
        kb.worldbuilding_needed = args.get("worldbuilding", False)

        # Set project type and determine chapters/scenes
        project_type = args.get("project_type", "novel")
        kb.project_type = project_type

        # Get effective chapters and scenes based on project type
        if args.get("chapters"):
            # Manual override - handle string ranges
            chapters_spec = args["chapters"]
            if isinstance(chapters_spec, str):
                # Store the original string for logging
                kb.chapters_str = chapters_spec
                # Generate random chapter count from range
                kb.num_chapters = VM.generate_random_chapter_count(chapters_spec)
                logger.info(f"Using manual chapter override: {chapters_spec} → selected {kb.num_chapters} chapters")
            else:
                # Handle integer input (backward compatibility)
                kb.num_chapters = chapters_spec
                logger.info(f"Using manual chapter override: {kb.num_chapters}")
            kb.auto_size = False
        else:
            # Use project type defaults
            kb.num_chapters = self.settings.get_effective_chapters()
            kb.auto_size = True
            logger.info(f"Using project type '{project_type}' default chapters: {kb.num_chapters}")

        # Set scenes per chapter
        if args.get("scenes_per_chapter"):
            # Manual override
            scenes_spec = args["scenes_per_chapter"]
            # Check if it's a comma-separated list of integers
            if isinstance(scenes_spec, str) and "," in scenes_spec:
                try:
                    kb.scenes_per_chapter_list = [int(s.strip()) for s in scenes_spec.split(",")]
                    logger.info(f"Using fixed scenes per chapter: {kb.scenes_per_chapter_list}")
                except ValueError:
                    logger.warning(
                        f"Invalid format for --scenes-per-chapter: '{scenes_spec}'. Expected a comma-separated list of numbers. Falling back to default."
                    )
                    kb.scenes_per_chapter = self.settings.get_effective_scenes_per_chapter()
            else:
                kb.scenes_per_chapter = scenes_spec
                logger.info(f"Using manual scenes override: {kb.scenes_per_chapter}")
        else:
            # Use project type defaults
            kb.scenes_per_chapter = self.settings.get_effective_scenes_per_chapter()
            logger.info(f"Using project type '{project_type}' default scenes: {kb.scenes_per_chapter}")

        # Set book length based on project type
        kb.book_length = self.settings.get_effective_book_length()
        logger.info(f"Project type '{project_type}' → Book length: {kb.book_length}")

        # Set review preference (non-interactive mode doesn't need review)
        kb.review_preference = "no"

        logger.info(f"Created knowledge base for: {kb.title}")
        logger.info(f"  Category: {kb.category}")
        logger.info(f"  Genre: {kb.genre}")
        logger.info(f"  Language: {kb.language}")
        logger.info(f"  Target Audience: {kb.target_audience}")
        logger.info(f"  Chapters: {kb.num_chapters}")
        logger.info(f"  Characters: {kb.num_characters}")
        logger.info(f"  Scenes per chapter: {kb.scenes_per_chapter}")
        logger.info(f"  Worldbuilding: {kb.worldbuilding_needed}")

        return kb

    def _display_book_statistics(self) -> None:
        """Display book statistics after successful creation."""
        if not self.project_manager or not self.project_manager.project_knowledge_base:
            return

        kb = self.project_manager.project_knowledge_base

        self.console.print(
            Panel(
                f"[bold blue]Statistics for '{kb.project_name}'[/bold blue]",
                expand=False,
            )
        )
        self.console.print(f"  [bold]Title:[/bold] {kb.title}")
        self.console.print(f"  [bold]Genre:[/bold] {kb.genre}")
        self.console.print(f"  [bold]Language:[/bold] {kb.language}")
        self.console.print(f"  [bold]Category:[/bold] {kb.category}")
        self.console.print(f"  [bold]Book Length:[/bold] {kb.book_length}")
        self.console.print(f"  [bold]Number of Characters:[/bold] {kb.num_characters}")
        self.console.print(f"  [bold]Number of Chapters:[/bold] {kb.num_chapters}")
        self.console.print(f"  [bold]Worldbuilding Needed:[/bold] {kb.worldbuilding_needed}")
        self.console.print(f"  [bold]Review Preference:[/bold] {kb.review_preference}")
        self.console.print(f"  [bold]Description:[/bold] {kb.description[:100]}...")  # Truncate for display

        # Calculate and display word and character count
        if self.project_manager.project_dir:
            manuscript_path = self.project_manager.project_dir / self.settings.manuscript_md_filename
            if manuscript_path.exists():
                content = manuscript_path.read_text(encoding="utf-8")
                word_count = len(content.split())
                char_count = len(content)
                self.console.print(f"  [bold]Word Count:[/bold] {word_count}")
                self.console.print(f"  [bold]Character Count:[/bold] {char_count}")

        # Display dynamic questions and answers
        if kb.dynamic_questions:
            self.console.print(Panel("[bold blue]Dynamic Questions & Answers[/bold blue]", expand=False))
            for q_id, answer in kb.dynamic_questions.items():
                self.console.print(f"  [bold]{q_id}:[/bold] {answer}")

        # Display chapter status
        if kb.chapters:
            self.console.print(Panel("[bold blue]Chapter Status[/bold blue]", expand=False))
            for chapter_number, chapter in kb.chapters.items():
                if self.project_manager.project_dir:
                    chapter_path = self.project_manager.project_dir / f"chapter_{chapter_number}.md"
                    status = "[green]Exists[/green]" if chapter_path.exists() else "[red]Missing[/red]"
                    self.console.print(f"  Chapter {chapter_number}: {chapter.title} - {status}")
                else:
                    self.console.print("[red]Error: Project directory not set[/red]")
                    return
        else:
            self.console.print("[yellow]No chapters recorded yet.[/yellow]")

    async def _execute_generation_steps(self, args: dict[str, Any]) -> bool:
        """Execute the requested book generation steps."""
        # If 'all' is specified, enable all steps
        if args.get("all", False):
            steps = {
                "generate_concept": True,
                "generate_outline": True,
                "generate_characters": True,
                "generate_worldbuilding": True,
                "write_chapters": True,
                "format_book": True,
            }
        else:
            steps = {
                "generate_concept": args.get("generate_concept", False),
                "generate_outline": args.get("generate_outline", False),
                "generate_characters": args.get("generate_characters", False),
                "generate_worldbuilding": args.get("generate_worldbuilding", False),
                "write_chapters": args.get("write_chapters", False),
                "format_book": args.get("format_book", False),
            }

        # Check if any generation steps are enabled
        any_steps_enabled = any(steps.values())
        if not any_steps_enabled:
            logger.warning(
                "No generation steps specified. Use --all or individual flags like --generate-concept, --generate-outline, etc."
            )
            logger.info("Available generation steps:")
            logger.info("  --generate-concept: Generate book concept")
            logger.info("  --generate-outline: Generate book outline")
            logger.info("  --generate-characters: Generate character profiles")
            logger.info("  --generate-worldbuilding: Generate worldbuilding details (requires --worldbuilding)")
            logger.info("  --write-chapters: Write all chapters")
            logger.info("  --format-book: Format the book into final output")
            logger.info("  --all: Perform all generation steps")
            return True

        # Execute steps in order
        if not self.project_manager:
            logger.error("Project manager not initialized")
            raise RuntimeError("Project manager not initialized")

        if steps["generate_concept"]:
            logger.info("Generating book concept...")
            try:
                await self.project_manager.generate_concept()
                logger.info("✅ Book concept generated successfully")
            except LLMGenerationError as e:
                logger.error(f"Concept generation failed: {e}")
                raise RuntimeError("Concept generation failed: LLM not reachable or API error.") from e
            except Exception as e:
                # Log detailed error to file only
                logger.exception("Failed to generate concept")
                raise RuntimeError(f"Concept generation failed: {e}") from e

        if steps["generate_outline"]:
            logger.info("Generating book outline...")
            try:
                await self.project_manager.generate_outline()
                logger.info("✅ Book outline generated successfully")
            except Exception as e:
                logger.error(f"Failed to generate outline: {e}")
                raise RuntimeError(f"Outline generation failed: {e}")

        if steps["generate_characters"] and self.project_manager.project_knowledge_base:
            num_characters = self.project_manager.project_knowledge_base.num_characters
            # Handle None case first
            if num_characters is None:
                num_characters = 0
            elif isinstance(num_characters, tuple):
                num_characters = num_characters[1] if len(num_characters) > 1 else num_characters[0]

            if num_characters > 0:
                logger.info("Generating character profiles...")
                try:
                    await self.project_manager.generate_characters()
                    logger.info("✅ Character profiles generated successfully")

                    # Export characters to markdown
                    if self.project_manager.project_dir:
                        characters_path = Path(self.project_manager.project_dir) / "characters.md"
                        export_characters_to_markdown(
                            self.project_manager.project_knowledge_base.characters, str(characters_path)
                        )
                        logger.info(f"✅ Characters exported to {characters_path}")
                except Exception as e:
                    logger.error(f"Failed to generate characters: {e}")
                    raise RuntimeError(f"Character generation failed: {e}")
            else:
                logger.info("Skipping character generation (no characters specified)")

        if (
            steps["generate_worldbuilding"]
            and self.project_manager.project_knowledge_base
            and self.project_manager.project_knowledge_base.worldbuilding_needed
        ):
            logger.info("Generating worldbuilding details...")
            try:
                await self.project_manager.generate_worldbuilding()
                logger.info("✅ Worldbuilding details generated successfully")

                # Export worldbuilding to markdown
                if self.project_manager.project_dir:
                    worldbuilding_path = Path(self.project_manager.project_dir) / "worldbuilding.md"
                    export_worldbuilding_to_markdown(
                        self.project_manager.project_knowledge_base.worldbuilding, str(worldbuilding_path)
                    )
                    logger.info(f"✅ Worldbuilding exported to {worldbuilding_path}")
            except Exception as e:
                logger.error(f"Failed to generate worldbuilding: {e}")
                raise RuntimeError(f"Worldbuilding generation failed: {e}")

        if steps["write_chapters"]:
            logger.info("Writing chapters...")
            if self.project_manager.project_knowledge_base:
                num_chapters = self.project_manager.project_knowledge_base.num_chapters
                # Handle None case first
                if num_chapters is None:
                    num_chapters = 1  # Default to 1 chapter
                # Handle tuple case
                elif isinstance(num_chapters, tuple):
                    num_chapters = num_chapters[1] if len(num_chapters) > 1 else num_chapters[0]

                logger.info(f"Chapter writing: num_chapters={num_chapters}, range=1 to {num_chapters}")
                for i in range(1, num_chapters + 1):
                    logger.info(f"Writing chapter {i}/{num_chapters}...")
                    try:
                        await self.project_manager.write_chapter(i)
                    except Exception as e:
                        logger.error(f"Failed to write chapter {i}: {e}")
                        raise RuntimeError(f"Chapter {i} writing failed: {e}")
                logger.info("✅ All chapters written successfully")

        if steps["format_book"]:
            logger.info("Formatting book...")
            try:
                await self.project_manager.format_book()
                logger.info("✅ Book formatted successfully")
            except Exception as e:
                logger.error(f"Failed to format book: {e}")
                raise RuntimeError(f"Book formatting failed: {e}")

        # Generate title if auto-title is enabled and we have content
        auto_title = args.get("auto_title", False)
        provided_title = args.get("title", "")

        if auto_title and self.project_manager.project_knowledge_base:
            # Check if we have a real title (not temporary)
            has_real_title = provided_title and provided_title.strip() and provided_title != "Untitled Book"

            if has_real_title:
                logger.info(
                    f"Auto-title enabled but title already provided: '{provided_title}' - skipping title generation"
                )
            else:
                # Only generate title if we have substantial content to base it on
                # Prefer full manuscript (chapters) over just concept/outline
                has_full_manuscript = steps["write_chapters"] and self.project_manager.project_knowledge_base.chapters
                has_substantial_content = has_full_manuscript or (
                    steps["generate_concept"] and steps["generate_outline"] and steps["generate_characters"]
                )

                if has_substantial_content:
                    logger.info("Generating title based on full manuscript content...")
                    try:
                        from libriscribe2.agents.title_generator import TitleGeneratorAgent

                        title_generator = TitleGeneratorAgent(self.project_manager.llm_client)
                        await title_generator.execute(self.project_manager.project_knowledge_base)
                        logger.info("✅ Title generated successfully")
                    except Exception as e:
                        logger.error(f"Failed to generate title: {e}")
                        # Don't fail the entire book creation for title generation errors
                        # but log it as an error for visibility
                elif has_full_manuscript:
                    logger.info("Generating title based on full manuscript...")
                    try:
                        from libriscribe2.agents.title_generator import TitleGeneratorAgent

                        title_generator = TitleGeneratorAgent(self.project_manager.llm_client)
                        await title_generator.execute(self.project_manager.project_knowledge_base)
                        logger.info("✅ Title generated successfully")
                    except Exception as e:
                        logger.error(f"Failed to generate title: {e}")
                        # Don't fail the entire book creation for title generation errors
                        # but log it as an error for visibility
                else:
                    logger.info("Skipping title generation (insufficient content available to base title on)")
                    logger.info("  Title generation works best with: --write-chapters or --all")
        elif auto_title:
            logger.info("Auto-title enabled but no project knowledge base available")
        else:
            if provided_title and provided_title != "Untitled Book":
                logger.info(f"Using provided title: '{provided_title}'")
            else:
                logger.info("No title provided - use --auto-title to generate a title based on content")

        return True
