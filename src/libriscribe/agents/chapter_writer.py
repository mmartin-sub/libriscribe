# src/libriscribe/agents/chapter_writer.py

import logging
from pathlib import Path

from libriscribe.agents.agent_base import Agent
from libriscribe.utils import prompts_context as prompts
from libriscribe.utils.file_utils import read_markdown_file, read_json_file, write_markdown_file
from libriscribe.project_data import ProjectData
from libriscribe.utils.llm_client import LLMClient


logger = logging.getLogger(__name__)

class ChapterWriterAgent(Agent):
    """Writes chapters."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("ChapterWriterAgent", llm_client)
        self.project_data: Optional[ProjectData] = None

    def execute(self, outline_path: str, character_path: str, world_path: str, chapter_number: int, output_path: str, project_data: Optional[ProjectData] = None) -> None:
        """Writes a chapter and saves it to a file."""

        self.project_data = project_data
        try:
            # Load data
            outline = read_markdown_file(outline_path)
            if self.project_data is None: #Added check for loading project_data
                project_file = Path(outline_path).parent / "project_data.json"
                if project_file.exists():
                    data = read_json_file(str(project_file))
                    self.project_data = ProjectData(**data)
                else:
                    self.logger.error("Project Data was not loaded correctly")
                    print("ERROR: Failed to load project data")
                    return
            # Conditionally load characters and worldbuilding
            characters = []
            if self.project_data.get("num_characters", 0) > 0:
                if Path(character_path).exists():
                    characters = read_json_file(character_path)
                else:
                    self.logger.warning(f"Characters file expected but not found: {character_path}")

            worldbuilding = {}
            if self.project_data.get("worldbuilding_needed", False):
                if Path(world_path).exists():
                    worldbuilding = read_json_file(world_path)
                else:
                    self.logger.warning(f"Worldbuilding file expected but not found: {world_path}")

            chapter_outline = self.extract_chapter_outline(outline, chapter_number)
            chapter_title = self.extract_chapter_title(outline, chapter_number)

            # Check if extraction was successful
            if chapter_outline == "Chapter outline not found.":
                self.logger.error(f"Could not extract outline for chapter {chapter_number}.")
                print(f"ERROR: Could not find outline for chapter {chapter_number}.")
                return

            if not chapter_title:
                self.logger.error(f"Could not extract title for chapter {chapter_number}.")
                print(f"ERROR: Could not find title for chapter {chapter_number}")
                return


            prompt_data = {
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "book_title": self.project_data.get("title", "Untitled"),
                "genre": self.project_data.get("genre", "Unknown Genre"),
                "category": self.project_data.get("category", "Unknown Category"),
                "chapter_outline": chapter_outline,
                "book_outline": outline,
                "characters": json.dumps(characters, indent=2),
                "worldbuilding": json.dumps(worldbuilding, indent=2),
            }
            prompt = prompts.CHAPTER_PROMPT.format(**prompt_data)
            chapter_content = self.llm_client.generate_content(prompt, max_tokens=3000)
            write_markdown_file(output_path, chapter_content)

        except Exception as e:
            self.logger.exception(f"Error writing chapter {chapter_number}: {e}")
            print(f"ERROR: Failed to write chapter {chapter_number}. See log.")

    def extract_chapter_outline(self, outline: str, chapter_number: int) -> str:
        """Extracts chapter outline (same as before, but with error handling)."""
        try:
            chapter_number_str = str(chapter_number)
            start = outline.find(f"# Chapter {chapter_number_str}:")
            if start == -1:
                start = outline.find(f"# Chapter {chapter_number_str} ")
                if start == -1:
                    return "Chapter outline not found."
            next_chapter_num = str(chapter_number + 1)
            end = outline.find(f"# Chapter {next_chapter_num}:", start)
            if end == -1:
                end = len(outline)
            return outline[start:end].strip()
        except Exception as e:
            self.logger.exception(f"Error extracting outline for chapter {chapter_number}: {e}")
            return ""

    def extract_chapter_title(self, outline: str, chapter_number: int) -> str:
        """Extracts chapter title (same as before, but with error handling)."""
        try:
            chapter_number_str = str(chapter_number)
            start = outline.find(f"# Chapter {chapter_number_str}:")
            if start == -1:
                return f"Chapter {chapter_number}"
            end_of_title = outline.find("\n", start)
            title_line = outline[start:end_of_title].strip()
            title = title_line.replace(f"# Chapter {chapter_number_str}:", "").strip()
            return title
        except Exception as e:
            self.logger.exception(f"Error extracting title for chapter {chapter_number}: {e}")
            return ""