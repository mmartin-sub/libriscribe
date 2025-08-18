# src/libriscribe2/agents/project_manager.py

import logging
from pathlib import Path
from typing import Any

from rich.console import Console

# AutoGen integration
from ..agent_frameworks.autogen import AutoGenConfigurationManager, AutoGenService
from ..knowledge_base import ProjectKnowledgeBase
from ..settings import Settings
from ..utils.llm_client import LLMClient
from .chapter_writer import ChapterWriterAgent
from .character_generator import CharacterGeneratorAgent
from .concept_generator import ConceptGeneratorAgent
from .content_reviewer import ContentReviewerAgent
from .editor import EditorAgent
from .fact_checker import FactCheckerAgent
from .formatting import FormattingAgent
from .outliner import OutlinerAgent
from .plagiarism_checker import PlagiarismCheckerAgent
from .researcher import ResearcherAgent
from .style_editor import StyleEditorAgent
from .worldbuilding import WorldbuildingAgent

console = Console()

logger = logging.getLogger(__name__)


class ProjectManagerAgent:
    """Manages the book creation process."""

    def __init__(
        self,
        settings: Settings,
        llm_client: LLMClient | None = None,
        model_config: dict[str, str] | None = None,
        use_autogen: bool = False,
    ):
        self.settings = settings
        self.model_config = model_config or {}
        self.project_knowledge_base: ProjectKnowledgeBase | None = None  # Use ProjectKnowledgeBase
        self.project_dir: Path | None = None
        self.llm_client: LLMClient | None = llm_client  # Add LLMClient instance
        self.agents: dict[str, Any] = {}  # Will be initialized after llm
        self.logger = logging.getLogger(__name__)

        # AutoGen integration
        self.use_autogen = use_autogen
        self.autogen_service: AutoGenService | None = None
        self.autogen_config_manager = AutoGenConfigurationManager()

    def initialize_llm_client(self, llm_provider: str, user: str | None = None) -> None:
        """Initializes the LLMClient and agents."""
        # Merge model config from constructor with settings
        combined_model_config = self.settings.get_model_config()
        combined_model_config.update(self.model_config)

        # Get project name from knowledge base if available
        project_name = ""
        if hasattr(self, "project_knowledge_base") and self.project_knowledge_base:
            project_name = self.project_knowledge_base.project_name

        # Use the timeout from settings to ensure all LLM calls respect the configured timeout
        self.llm_client = LLMClient(
            llm_provider,
            model_config=combined_model_config,
            timeout=float(self.settings.llm_timeout),
            environment=self.settings.environment,
            project_name=project_name,
            user=user,
        )

        # Initialize traditional agents
        self.agents = {
            "content_reviewer": ContentReviewerAgent(self.llm_client),  # Pass client
            "concept_generator": ConceptGeneratorAgent(self.llm_client),
            "outliner": OutlinerAgent(self.llm_client),
            "character_generator": CharacterGeneratorAgent(self.llm_client),
            "worldbuilding": WorldbuildingAgent(self.llm_client),
            "chapter_writer": ChapterWriterAgent(self.llm_client),
            "editor": EditorAgent(self.llm_client),
            "researcher": ResearcherAgent(self.llm_client),
            "formatting": FormattingAgent(self.llm_client),
            "style_editor": StyleEditorAgent(self.llm_client),
            "plagiarism_checker": PlagiarismCheckerAgent(self.llm_client),
            "fact_checker": FactCheckerAgent(self.llm_client),
        }

        # Initialize AutoGen service if enabled
        if self.use_autogen:
            self.autogen_service = AutoGenService(self.settings, self.llm_client)
            logger.info("AutoGen service initialized")

    def initialize_project_with_data(self, project_data: ProjectKnowledgeBase):
        """Initializes a project using the ProjectKnowledgeBase object."""
        self.project_dir = Path(self.settings.projects_dir) / project_data.project_name
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.project_knowledge_base = project_data
        self.save_project_data()

    def create_project_from_kb(self, project_kb: ProjectKnowledgeBase, output_path: str = ""):
        """Creates a project from a ProjectKnowledgeBase object."""
        if output_path:
            self.project_dir = Path(output_path)
        else:
            self.project_dir = Path(self.settings.projects_dir) / project_kb.project_name

        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.project_knowledge_base = project_kb

        # Set the project_dir in the knowledge base so agents can access it
        self.project_knowledge_base.project_dir = self.project_dir

        self.save_project_data()

    def save_project_data(self):
        """Saves the project data to a JSON file."""
        if self.project_knowledge_base and self.project_dir:
            project_data_path = self.project_dir / "project_data.json"
            self.project_knowledge_base.save_to_file(str(project_data_path))

    def load_project_data(self, project_name: str) -> None:
        """Load project data from file system."""
        # Construct project directory path using settings.projects_dir
        project_dir = Path(self.settings.projects_dir) / project_name

        # Check if project directory exists
        if not project_dir.exists():
            raise FileNotFoundError(f"Project directory '{project_name}' not found in {self.settings.projects_dir}")

        # Check if project_data.json exists
        project_data_path = project_dir / "project_data.json"
        if not project_data_path.exists():
            raise FileNotFoundError(f"Project data file not found at {project_data_path}")

        try:
            # Load ProjectKnowledgeBase from file
            kb = ProjectKnowledgeBase.load_from_file(str(project_data_path))
            if not kb:
                raise ValueError(f"Failed to load project data from {project_data_path}")

            # Set properties
            self.project_knowledge_base = kb
            self.project_dir = project_dir

            # Set the project_dir in the knowledge base so agents can access it
            self.project_knowledge_base.project_dir = self.project_dir

            logger.info(f"Successfully loaded project '{project_name}' from {project_dir}")

        except Exception as e:
            if isinstance(e, FileNotFoundError | ValueError):
                raise
            else:
                raise ValueError(f"Corrupted project data in {project_data_path}: {e}") from e

    async def run_agent(self, agent_name: str, **kwargs) -> None:
        """Runs a specific agent."""
        if agent_name not in self.agents:
            error_msg = f"Agent {agent_name} not found"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        agent = self.agents[agent_name]
        try:
            if self.project_knowledge_base:
                await agent.execute(self.project_knowledge_base, **kwargs)
                self.save_project_data()
            else:
                error_msg = "Project knowledge base not initialized"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        except Exception as e:
            # Log the detailed error to file only
            self.logger.exception(f"Error running agent {agent_name}")
            # Re-raise without additional console output
            raise e

    async def run_autogen_workflow(self) -> bool:
        """Run the complete book creation workflow using AutoGen."""
        if not self.autogen_service or not self.project_knowledge_base:
            logger.error("AutoGen service or project knowledge base not initialized")
            return False

        try:
            logger.info("Starting AutoGen-based book creation workflow")

            # Use AutoGen for coordinated book creation
            success = await self.autogen_service.create_book(self.project_knowledge_base)

            if success:
                self.save_project_data()
                logger.info("AutoGen workflow completed successfully")
            else:
                logger.error("AutoGen workflow failed")

            return success

        except Exception as e:
            logger.error(f"Error in AutoGen workflow: {e}")
            return False

    async def run_hybrid_workflow(self) -> bool:
        """Run a hybrid workflow using AutoGen for coordination and LibriScribe agents for execution."""
        if not self.autogen_service or not self.project_knowledge_base:
            logger.error("AutoGen service or project knowledge base not initialized")
            return False

        try:
            logger.info("Starting hybrid AutoGen + LibriScribe workflow")

            # Use hybrid approach
            success = await self.autogen_service.create_book(self.project_knowledge_base)

            if success:
                self.save_project_data()
                logger.info("Hybrid workflow completed successfully")
            else:
                logger.error("Hybrid workflow failed")

            return success

        except Exception as e:
            logger.error(f"Error in hybrid workflow: {e}")
            return False

    async def generate_concept(self):
        """Generates a book concept."""
        if self.project_dir is None:
            logger.error("Project directory not initialized")
            return

        concept_output_path = str(self.project_dir / "concept.json")

        if self.use_autogen and self.autogen_service:
            # Use AutoGen for concept generation
            logger.info("Using AutoGen for concept generation")
            # This would be implemented as an async method
            # For now, fall back to traditional agent
            await self.run_agent("concept_generator", output_path=concept_output_path)
        else:
            await self.run_agent("concept_generator", output_path=concept_output_path)

    async def generate_outline(self):
        """Generates a book outline."""
        if self.use_autogen and self.autogen_service:
            logger.info("Using AutoGen for outline generation")
            await self.run_agent("outliner")
        else:
            await self.run_agent("outliner")

    async def generate_characters(self):
        """Generates character profiles."""
        if self.use_autogen and self.autogen_service:
            logger.info("Using AutoGen for character generation")
            await self.run_agent("character_generator")
        else:
            await self.run_agent("character_generator")

    async def generate_worldbuilding(self):
        """Generates worldbuilding details."""
        if self.use_autogen and self.autogen_service:
            logger.info("Using AutoGen for worldbuilding")
            await self.run_agent("worldbuilding")
        else:
            await self.run_agent("worldbuilding")

    async def write_chapter(self, chapter_number: int):
        """Writes a specific chapter."""
        if self.project_dir is None:
            print("ERROR: Project directory not initialized.")
            return
        await self.run_agent(
            "chapter_writer",
            chapter_number=chapter_number,
            output_path=str(self.project_dir / f"chapter_{chapter_number}.md"),
        )
        self.save_project_data()

    async def write_and_review_chapter(self, chapter_number: int):
        """Writes, reviews, and potentially edits a chapter (centralized review logic)."""
        await self.write_chapter(chapter_number)  # Write the chapter
        await self.review_content(chapter_number)  # Review for content issues

        # Auto-edit is not currently implemented in ProjectKnowledgeBase
        # This feature can be added later if needed
        # if (
        #     self.project_knowledge_base
        #     and hasattr(self.project_knowledge_base, "auto_edit")
        #     and self.project_knowledge_base.auto_edit
        # ):
        #     await self.edit_chapter(chapter_number)  # Auto-edit if enabled

    async def review_content(self, chapter_number: int):
        """Reviews content for quality and consistency."""
        if self.project_dir is None:
            print("ERROR: Project directory not initialized.")
            return
        await self.run_agent(
            "content_reviewer",
            chapter_number=chapter_number,
            output_path=str(self.project_dir / f"review_chapter_{chapter_number}.md"),
        )

    async def edit_chapter(self, chapter_number: int):
        """Edits a chapter for quality and style."""
        if self.project_dir is None:
            print("ERROR: Project directory not initialized.")
            return
        await self.run_agent(
            "editor",
            chapter_number=chapter_number,
            output_path=str(self.project_dir / f"edited_chapter_{chapter_number}.md"),
        )

    async def check_plagiarism(self, chapter_number: int):
        """Checks a chapter for plagiarism."""
        if self.project_dir is None:
            print("ERROR: Project directory not initialized.")
            return
        await self.run_agent(
            "plagiarism_checker",
            chapter_number=chapter_number,
            output_path=str(self.project_dir / f"plagiarism_check_chapter_{chapter_number}.md"),
        )

    async def fact_check(self, chapter_number: int):
        """Fact-checks a chapter."""
        if self.project_dir is None:
            print("ERROR: Project directory not initialized.")
            return
        await self.run_agent(
            "fact_checker",
            chapter_number=chapter_number,
            output_path=str(self.project_dir / f"fact_check_chapter_{chapter_number}.md"),
        )

    async def research_topic(self, topic: str):
        """Researches a specific topic."""
        if self.project_dir is None:
            print("ERROR: Project directory not initialized.")
            return
        await self.run_agent(
            "researcher",
            topic=topic,
            output_path=str(self.project_dir / f"research_{topic.replace(' ', '_')}.md"),
        )

    async def format_book(self):
        """Formats the book for publication."""
        if self.project_dir is None:
            print("ERROR: Project directory not initialized.")
            return
        await self.run_agent("formatting", output_path=str(self.project_dir / "formatted_book.md"))

    def get_autogen_analytics(self) -> dict[str, Any]:
        """Get analytics from AutoGen service if available."""
        if self.autogen_service:
            return self.autogen_service.get_conversation_analytics()
        return {}

    def export_autogen_logs(self, output_path: str) -> None:
        """Export AutoGen conversation logs."""
        if self.autogen_service:
            self.autogen_service.export_conversation_log(output_path)

    def get_autogen_configuration(self, use_case: str) -> dict[str, Any]:
        """Get recommended AutoGen configuration for a specific use case."""
        return self.autogen_config_manager.get_recommended_configuration(use_case)

    def validate_autogen_configuration(self, config: dict[str, Any]) -> list[str]:
        """Validate AutoGen configuration and return any issues."""
        return self.autogen_config_manager.validate_configuration(config)

    def checkpoint(self) -> None:
        """Save the current state of the project."""
        if self.project_knowledge_base and self.project_dir:
            self.save_project_data()
            logger.info("Project checkpoint saved")

    def needs_title_generation(self) -> bool:
        """Check if title generation is needed for this project."""
        if not self.project_knowledge_base:
            return False

        kb = self.project_knowledge_base
        return bool(
            kb.auto_title
            and (kb.title == "Untitled" or kb.title == "Untitled Book")
            and (kb.chapters or kb.characters or kb.outline)
        )

    async def generate_project_title(self) -> bool:
        """Generate a title for the project if auto-title is enabled."""
        if not self.needs_title_generation():
            return False

        if self.project_knowledge_base is None:
            logger.error("Project knowledge base not initialized")
            return False

        try:
            from libriscribe2.agents.title_generator import TitleGeneratorAgent

            title_generator: TitleGeneratorAgent = TitleGeneratorAgent(self.llm_client)
            await title_generator.execute(self.project_knowledge_base)
            self.save_project_data()
            return True
        except Exception:
            logger.exception("Error generating title")
            return False
