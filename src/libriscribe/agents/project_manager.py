# src/libriscribe/agents/project_manager.py

import logging
from typing import Any, Dict, Optional
from pathlib import Path

from libriscribe.agents.concept_generator import ConceptGeneratorAgent
from libriscribe.agents.outliner import OutlinerAgent
from libriscribe.agents.character_generator import CharacterGeneratorAgent
from libriscribe.agents.worldbuilding import WorldbuildingAgent
from libriscribe.agents.chapter_writer import ChapterWriterAgent
from libriscribe.agents.editor import EditorAgent
from libriscribe.agents.researcher import ResearcherAgent
from libriscribe.agents.formatting import FormattingAgent
from libriscribe.agents.content_reviewer import ContentReviewerAgent
from libriscribe.agents.style_editor import StyleEditorAgent
from libriscribe.agents.plagiarism_checker import PlagiarismCheckerAgent
from libriscribe.agents.fact_checker import FactCheckerAgent

from libriscribe.settings import Settings
from libriscribe.utils.file_utils import write_json_file, read_json_file
from libriscribe.project_data import ProjectData  # Import ProjectData
from libriscribe.utils.llm_client import LLMClient


logger = logging.getLogger(__name__)

class ProjectManagerAgent:
    """Manages the book creation process."""

    def __init__(self, llm_client: LLMClient):
        self.settings = Settings()
        self.project_data: Optional[ProjectData] = None  # Use ProjectData type
        self.project_dir: Optional[Path] = None
        self.llm_client: Optional[LLMClient] = None  # Add LLMClient instance
        self.agents = {} # Will be initialized after llm

    def initialize_llm_client(self, llm_provider: str):
        """Initializes the LLMClient and agents."""
        self.llm_client = LLMClient(llm_provider)
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
    def initialize_project_with_data(self, project_data: ProjectData):
        """Initializes a project using the ProjectData object."""
        self.project_dir = Path(self.settings.projects_dir) / project_data.project_name
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.project_data = project_data
        self.save_project_data(str(self.project_dir / "project_data.json"))
        logger.info(f"🚀 Initialized project: {project_data.project_name}")
        print(f"Project '{project_data.project_name}' initialized in {self.project_dir}")

    def save_project_data(self, file_path: str):
        """Saves project data using the ProjectData object."""
        if self.project_data:
            write_json_file(file_path, self.project_data.model_dump())
        else:
            logger.warning("Attempted to save project data before initialization.")


    def load_project_data(self, project_name: str):
        """Loads project data."""
        self.project_dir = Path(self.settings.projects_dir) / project_name
        project_data_path = self.project_dir / "project_data.json"
        if project_data_path.exists():
            data = read_json_file(str(project_data_path))
            self.project_data = ProjectData(**data)
        else:
            raise FileNotFoundError(f"Project data not found for project: {project_name}")

    def run_agent(self, agent_name: str, *args, **kwargs):
        """Runs a specific agent, passing project_data."""
        if agent_name not in self.agents:
            print(f"ERROR: Agent '{agent_name}' not found.")
            return

        agent = self.agents[agent_name]
        # Pass project_data to agents that need it
        if agent_name in ["concept_generator", "outliner", "character_generator", "worldbuilding"]:
            if self.project_data:
                try:
                    agent.execute(self.project_data, *args, **kwargs)  # Pass project_data
                except Exception as e:
                    logger.exception(f"Error running agent {agent_name}: {e}")
                    print(f"ERROR: Agent {agent_name} failed. See log for details.")
            else:
                print(f"ERROR: Project data not initialized before running {agent_name}.")
        else:  # Other agents
            try:
                agent.execute(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Error running agent {agent_name}: {e}")
                print(f"ERROR: Agent {agent_name} failed. See log for details.")


    # --- Command Handlers (using ProjectData) ---

    def generate_concept(self):
        """Generates a detailed book concept."""
        if self.project_data is None:
            print("ERROR: No project initialized.")
            return
        self.agents["concept_generator"].execute(self.project_data) # type: ignore
        self.save_project_data(str(self.project_dir / "project_data.json")) # type: ignore


    def generate_outline(self):
        """Generates a book outline."""
        self.run_agent("outliner", str(self.project_dir / "outline.md")) # type: ignore


    def generate_characters(self):
        """Generates character profiles."""
        self.run_agent("character_generator", str(self.project_dir / "characters.json")) # type: ignore

    def generate_worldbuilding(self):
        """Generates worldbuilding details."""
        self.run_agent("worldbuilding", str(self.project_dir / "world.json")) # type: ignore

    def write_chapter(self, chapter_number: int):
        """Writes a specific chapter."""
        outline_path = str(self.project_dir / "outline.md") # type: ignore
        character_path = str(self.project_dir / "characters.json")# type: ignore
        world_path = str(self.project_dir / "world.json")# type: ignore
        output_path = str(self.project_dir / f"chapter_{chapter_number}.md")# type: ignore
        self.run_agent("chapter_writer", outline_path, character_path, world_path, chapter_number, output_path)

    def write_and_review_chapter(self, chapter_number: int):
        """Writes, reviews, and potentially edits a chapter (centralized review logic)."""
        self.write_chapter(chapter_number)  # Write the chapter
        self.review_content(chapter_number)  # Review for content issues

        if self.project_data and self.project_data.review_preference == "AI":
            self.edit_chapter(chapter_number)  # AI editing
            self.edit_style(chapter_number)  # AI style editing
        elif self.project_data and self.project_data.review_preference == "Human":
            chapter_path = str(self.project_dir / f"chapter_{chapter_number}.md") # type: ignore
            print(f"\nChapter {chapter_number} written to: {chapter_path}")
            if typer.confirm("Do you want to review and edit this chapter now?"):
                typer.edit(filename=chapter_path)
                print("\nChanges saved.")
            # Even for human review, we might want style editing
            if typer.confirm("Do you want AI to refine the writing style?"):
                 self.edit_style(chapter_number)


    def edit_chapter(self, chapter_number: int):
        """Refines an existing chapter (Editor Agent)."""
        chapter_path = str(self.project_dir / f"chapter_{chapter_number}.md") # type: ignore
        self.run_agent("editor", chapter_path)

    def format_book(self, output_path: str):
        """Formats the entire book."""
        self.run_agent("formatting", str(self.project_dir), output_path) # type: ignore

    def research(self, query: str):
        """Performs web research."""
        self.run_agent("researcher", query, str(self.project_dir / "research_results.md"))# type: ignore

    def edit_style(self, chapter_number: int):
        """Refines writing style."""
        chapter_path = str(self.project_dir / f"chapter_{chapter_number}.md")# type: ignore
        self.run_agent("style_editor", chapter_path)

    def check_plagiarism(self, chapter_number: int):
        """Checks for plagiarism."""
        chapter_path = str(self.project_dir / f"chapter_{chapter_number}.md")# type: ignore
        results = self.agents["plagiarism_checker"].execute(chapter_path)  # type: ignore
        print(f"Plagiarism check results for chapter {chapter_number}: {results}")

    def check_facts(self, chapter_number: int):
        """Checks factual claims."""
        chapter_path = str(self.project_dir / f"chapter_{chapter_number}.md")# type: ignore
        results = self.agents["fact_checker"].execute(chapter_path)  # type: ignore
        print(f"Fact-check results for chapter {chapter_number}: {results}")

    def review_content(self, chapter_number: int):
        """Reviews chapter content."""
        chapter_path = str(self.project_dir / f"chapter_{chapter_number}.md")# type: ignore
        results = self.agents["content_reviewer"].execute(chapter_path) # type: ignore
        print(f"Content review results for chapter {chapter_number}:\n{results.get('review', 'No review available.')}")

    def does_chapter_exist(self, chapter_number: int) -> bool:
        """Checks if a chapter file exists."""
        chapter_path = self.project_dir / f"chapter_{chapter_number}.md" # type: ignore
        return chapter_path.exists()