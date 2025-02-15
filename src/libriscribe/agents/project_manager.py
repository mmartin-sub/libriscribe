# src/libriscribe/agents/project_manager.py

import asyncio
import logging
import typer
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
from libriscribe.settings import Settings
from libriscribe.utils.file_utils import write_json_file


logger = logging.getLogger(__name__)

class ProjectManagerAgent:
    """Manages the book creation process via the CLI."""

    def __init__(self):
        self.settings = Settings()  # Load settings from a config file
        self.agents = {
            "concept_generator": ConceptGeneratorAgent(),
            "outliner": OutlinerAgent(),
            "character_generator": CharacterGeneratorAgent(),
            "worldbuilding": WorldbuildingAgent(),
            "chapter_writer": ChapterWriterAgent(),
            "editor": EditorAgent(),
            "researcher": ResearcherAgent(),
            "formatting": FormattingAgent(),
        }
        self.project_data: Dict[str, Any] = {}
        self.project_dir: Optional[Path] = None

    def initialize_project(self, project_name: str, title: str, genre: str, description: str, category: str, num_characters: int, worldbuilding_needed:bool):
        """Initializes a new project."""
        self.project_dir = Path(self.settings.projects_dir) / project_name
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.project_data = {
            "project_name": project_name,
            "title": title,
            "genre": genre,
            "description": description,
            "category": category,
            "num_characters": num_characters,
            "worldbuilding_needed" : worldbuilding_needed
        }

        # Save project data to a JSON file
        project_data_path = self.project_dir / "project_data.json"
        write_json_file(str(project_data_path), self.project_data)


        logger.info(f"🚀 Initialized project: {project_name}")
        print(f"Project '{project_name}' initialized in {self.project_dir}")

    def run_agent(self, agent_name: str, *args, **kwargs):
        """Runs a specific agent."""
        if agent_name not in self.agents:
            print(f"ERROR: Agent '{agent_name}' not found.")
            return

        agent = self.agents[agent_name]
        try:
            agent.execute(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error running agent {agent_name}: {e}")
            print(f"ERROR: Agent {agent_name} failed. See log for details.")

    # --- CLI Command Handlers ---

    def create_project(self, project_name: str, title: str, genre: str, description: str, category: str, num_characters: int, worldbuilding_needed: bool):
        """Creates a new project."""
        self.initialize_project(project_name, title, genre, description, category, num_characters, worldbuilding_needed)


    def generate_concept(self):
        """Generates a detailed book concept."""
        if not self.project_data:
            print("ERROR: No project initialized.  Use 'create' command first.")
            return
        self.project_data = self.agents["concept_generator"].execute(self.project_data)  # type: ignore
        # Update the project_data.json file.
        project_data_path = self.project_dir / "project_data.json" # type: ignore
        write_json_file(str(project_data_path), self.project_data)


    def generate_outline(self):
        """Generates a book outline."""
        if not self.project_data:
            print("ERROR: No project initialized.  Use 'create' command first.")
            return
        logger.info(f"🗺️ Agent {self.agents['outliner'].name} generating outline...")# type: ignore
        self.run_agent("outliner", self.project_data, str(self.project_dir / "outline.md"))
        logger.info(f"🗺️ Outline completed.")


    def generate_characters(self):
       """Generates character profiles"""
       if not self.project_data:
            print("ERROR: No project initialized. Use 'create' command first.")
            return
       logger.info(f"🧑‍🤝‍🧑 Agent {self.agents['character_generator'].name} generating characters...")# type: ignore
       self.run_agent("character_generator", self.project_data, str(self.project_dir /"characters.json"))
       logger.info(f"🧑‍🤝‍🧑 Character generation completed.")

    def generate_worldbuilding(self):
        """Generates worldbuilding details."""
        if not self.project_data:
            print("ERROR: No project initialized. Use 'create' command first.")
            return
        logger.info(f"🌍 Agent {self.agents['worldbuilding'].name} generating worldbuilding...")# type: ignore
        self.run_agent("worldbuilding", self.project_data, str(self.project_dir / "world.json"))
        logger.info(f"🌍 Worldbuilding completed.")

    def write_chapter(self, chapter_number: int):
        """Writes a specific chapter."""
        if not self.project_data:
            print("ERROR: No project initialized.  Use 'create' command first.")
            return

        outline_path = str(self.project_dir / "outline.md")
        character_path = str(self.project_dir / "characters.json")
        world_path = str(self.project_dir / "world.json")
        output_path = str(self.project_dir / f"chapter_{chapter_number}.md")
        self.run_agent("chapter_writer", outline_path, character_path, world_path, chapter_number, output_path)

    def edit_chapter(self, chapter_number:int):
      """Refines an existing chapter via the Editor Agent."""
      if not self.project_data:
          print("ERROR: No project initialized.  Use 'create' command first.")
          return

      chapter_path = str(self.project_dir / f"chapter_{chapter_number}.md")
      self.run_agent("editor", chapter_path)

    def format_book(self):
        """Formats the entire book into a single Markdown or PDF file."""
        if not self.project_data:
            print("ERROR: No project initialized. Use 'create' command first.")
            return
        output_path = typer.prompt("Enter output file path (e.g., manuscript.md or manuscript.pdf)", type=str)
        self.run_agent("formatting", str(self.project_dir), output_path)

    def research(self, query:str):
      """Perform web research on a query using the research agent."""
      if not self.project_data:
          print("ERROR: No project initialized. Use 'create' command first.")
          return
      logger.info(f"🔍 Agent {self.agents['researcher'].name} researching: '{query}'...")# type: ignore
      self.run_agent("researcher", query, str(self.project_dir/"research_results.md"))
      logger.info(f"🔍 Research on '{query}' completed.")