# src/libriscribe/agents/chapter_writer.py

import logging
from pathlib import Path

from libriscribe.agents.agent_base import Agent
from libriscribe.utils import prompts_context as prompts
from libriscribe.utils.file_utils import read_markdown_file, read_json_file, write_markdown_file
from libriscribe.project_data import ProjectData
from libriscribe.utils.llm_client import LLMClient
import json


logger = logging.getLogger(__name__)

class ChapterWriterAgent(Agent):
    """Writes chapters."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("ChapterWriterAgent", llm_client)
        self.project_data: Optional[ProjectData] = None

    def execute(self, outline_path: str, character_path: str, world_path: str, chapter_number: int, output_path: str, project_data: Optional[ProjectData] = None) -> None:
        """Writes a chapter using an iterative refinement process (summary, critique, full chapter)."""

        self.project_data = project_data
        try:
            # Load data (same as before, but with ProjectData handling)
            outline = read_markdown_file(outline_path)
            if self.project_data is None:
                project_file = Path(outline_path).parent / "project_data.json"
                if project_file.exists():
                    data = read_json_file(str(project_file), ProjectData)
                    if data:
                        self.project_data = data
                    else:
                        self.logger.error("Failed to load or validate project data")
                        print("ERROR: Failed to load project data")
                        return
                else:
                    self.logger.error("Project Data was not loaded correctly")
                    print("ERROR: Failed to load project data")
                    return

            characters = []
            if self.project_data.get("num_characters", 0) > 0:
                if Path(character_path).exists():
                    characters = read_json_file(character_path)  # No model needed, it's a list
                else:
                    self.logger.warning(f"Characters file expected but not found: {character_path}")

            worldbuilding = {}
            if self.project_data.get("worldbuilding_needed", False):
                if Path(world_path).exists():
                    worldbuilding = read_json_file(world_path) # No model, it's a dict
                else:
                    self.logger.warning(f"Worldbuilding file expected but not found: {world_path}")

            chapter_outline = self.extract_chapter_outline(outline, chapter_number)
            chapter_title = self.extract_chapter_title(outline, chapter_number)
            if chapter_outline == "Chapter outline not found.":
                self.logger.error(f"Could not extract outline for chapter {chapter_number}.")
                return
            if not chapter_title:
                self.logger.error(f"Could not extract title for chapter {chapter_number}.")
                return

            # --- Step 1: Generate Chapter Summary ---
            summary_prompt_data = {
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "book_title": self.project_data.title,
                "genre": self.project_data.genre,
                "chapter_outline": chapter_outline,
            }
            summary_prompt = f"""Write a concise summary (around 200-300 words) for chapter {chapter_number} of a {summary_prompt_data['genre']} book titled "{summary_prompt_data['book_title']}".

            Chapter Title: {chapter_title}

            Outline for this chapter:
            {chapter_outline}
            """

            chapter_summary = self.llm_client.generate_content(summary_prompt, max_tokens=500)
            if not chapter_summary:
                self.logger.error(f"Failed to generate summary for chapter {chapter_number}.")
                return

            # --- Step 2: Critique Chapter Summary ---
            critique_prompt = f"""Critique the following chapter summary:

            {chapter_summary}

            Identify any weaknesses, areas for improvement, or potential plot holes. Be specific.
            """
            critique = self.llm_client.generate_content(critique_prompt, max_tokens=500)

            # --- Step 3: Generate Full Chapter ---

            prompt_data = {
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "book_title": self.project_data.title,
                "genre": self.project_data.genre,
                "category": self.project_data.category,
                "chapter_outline": chapter_outline,
                "book_outline": outline,
                "characters": json.dumps(characters, indent=2),
                "worldbuilding": json.dumps(worldbuilding, indent=2),
                "chapter_summary": chapter_summary,  # Include the summary
                "critique": critique,  # Include the critique
            }

            full_chapter_prompt = prompts.CHAPTER_PROMPT.format(**prompt_data) + f"""
            \n\nBased on the chapter summary and the critique, write the full chapter. Address any weaknesses identified in the critique.
            \n\nChapter Summary:\n{chapter_summary}\n\nCritique:\n{critique}"""


            chapter_content = self.llm_client.generate_content(full_chapter_prompt, max_tokens=3000)
            if not chapter_content:
                 self.logger.error(f"Failed to generate chapter {chapter_number}.")
                 return

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