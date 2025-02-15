# src/libriscribe/agents/chapter_writer.py
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.openai_client import OpenAIClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import read_markdown_file, read_json_file, write_markdown_file

logger = logging.getLogger(__name__)

class ChapterWriterAgent(Agent):
    """Writes chapters."""

    def __init__(self):
        super().__init__("ChapterWriterAgent")

    def execute(self, outline_path: str, character_path: str, world_path: str, chapter_number: int, output_path: str) -> None:
        """Writes a chapter and saves it to a file."""
        try:
            # Load data
            outline = read_markdown_file(outline_path)
            characters = read_json_file(character_path)
            worldbuilding = read_json_file(world_path)
            project_data = {} # Initialize to prevent error if file not found
            project_file = Path(outline_path).parent / "project_data.json"
            if project_file.exists():
              project_data = read_json_file(str(project_file))


            # Extract chapter-specific outline (basic string search)
            chapter_outline = self.extract_chapter_outline(outline, chapter_number)
            chapter_title = self.extract_chapter_title(outline, chapter_number)


            # Prepare prompt
            prompt_data = {
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "book_title": project_data.get("title", "Untitled"),
                "genre": project_data.get("genre", "Unknown Genre"),
                "category": project_data.get("category", "Unknown Category"),
                "chapter_outline": chapter_outline,
                "book_outline": outline,
                "characters": json.dumps(characters, indent=2),
                "worldbuilding": json.dumps(worldbuilding, indent=2),
            }
            prompt = prompts.CHAPTER_PROMPT.format(**prompt_data)

            # Generate content
            chapter_content = self.openai_client.generate_content(prompt, max_tokens=3000)

            write_markdown_file(output_path, chapter_content)


        except Exception as e:
            self.logger.exception(f"Error writing chapter {chapter_number}: {e}")
            print(f"ERROR: Failed to write chapter {chapter_number}. See log.")


    def extract_chapter_outline(self, outline: str, chapter_number: int) -> str:
        """Extracts the outline for a specific chapter."""
        try:
            # Convert chapter_number to string for easier manipulation
            chapter_number_str = str(chapter_number)

            # Find the start and end of the chapter section
            start = outline.find(f"# Chapter {chapter_number_str}:")
            if start == -1:
                # Try finding with chapter name alone, in case numbering is off.
                start = outline.find(f"# Chapter {chapter_number_str} ")
                if start == -1:
                  return "Chapter outline not found." # Not found

            # Find the next chapter heading or the end of the string
            next_chapter_num = str(chapter_number + 1)
            end = outline.find(f"# Chapter {next_chapter_num}:", start)
            if end == -1:
                end = len(outline)  # End of the document

            return outline[start:end].strip()
        except Exception as e:
            self.logger.exception(f"Error while extracting outline for chapter {chapter_number}:{e}")
            return ""

    def extract_chapter_title(self, outline:str, chapter_number:int) -> str:
      """Extracts chapter title"""
      try:
        chapter_number_str = str(chapter_number)

        start = outline.find(f"# Chapter {chapter_number_str}:")
        if start == -1:
            return f"Chapter {chapter_number}" # Default title

        # Find the end of the title (next newline)
        end_of_title = outline.find("\n", start)
        title_line = outline[start:end_of_title].strip()

        # Extract title from the line.
        title = title_line.replace(f"# Chapter {chapter_number_str}:", "").strip()
        return title
      except Exception as e:
          self.logger.exception(f"Error while extracting title for chapter{chapter_number}: {e}")
          return ""