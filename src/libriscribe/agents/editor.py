# libriscribe/src/agents/editor.py
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.openai_client import OpenAIClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import read_markdown_file, write_markdown_file, read_json_file

logger = logging.getLogger(__name__)

class EditorAgent(Agent):
    """Edits and refines chapters."""

    def __init__(self):
        super().__init__("EditorAgent")

    def execute(self, chapter_path: str) -> None:
        """Edits a chapter and saves the revised version."""
        try:
            chapter_content = read_markdown_file(chapter_path)
            if not chapter_content:
                print(f"ERROR: Chapter file is empty: {chapter_path}")
                return

            # Extract chapter number and title (best effort)
            chapter_number = self.extract_chapter_number(chapter_path)
            chapter_title = self.extract_chapter_title(chapter_content)

            # --- Get project data
            project_data = {} # Initialize
            project_file = Path(chapter_path).parent / "project_data.json" # Same dir as chapter
            if project_file.exists():
                project_data = read_json_file(str(project_file))

            prompt_data = {
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "book_title": project_data.get("title", "Untitled"),
                "genre": project_data.get("genre", "Unknown Genre"),
                "chapter_content": chapter_content
            }
            prompt = prompts.EDITOR_PROMPT.format(**prompt_data)
            edited_response = self.openai_client.generate_content(prompt, max_tokens=4000) # Increased tokens

            # Extract revised chapter (very important to parse correctly)
            revised_chapter = self.extract_revised_chapter(edited_response)
            if revised_chapter:
                write_markdown_file(chapter_path, revised_chapter)  # Overwrite
            else:
                print("ERROR: Could not extract revised chapter from editor output.")
                self.logger.error("Could not extract revised chapter content.")

        except Exception as e:
            self.logger.exception(f"Error editing chapter {chapter_path}: {e}")
            print(f"ERROR: Failed to edit chapter. See log.")

    def extract_chapter_number(self, chapter_path: str) -> int:
        """Extracts the chapter number from the file path."""
        try:
            return int(chapter_path.split("_")[1].split(".")[0])
        except:
            return -1 # Indicate error

    def extract_chapter_title(self, chapter_content:str) -> str:
        """Extract chapter title, handles if there's no title"""
        lines = chapter_content.split("\n")
        for line in lines:
            if line.startswith("#"):
                return line.replace("#", "").strip()
        return "Untitled Chapter" # Default

    def extract_revised_chapter(self, edited_response: str) -> str:
        """Extracts the revised chapter content from the editor's output."""
        try:
            start_marker = "**Revised Chapter:**"
            start_index = edited_response.find(start_marker)
            if start_index == -1:
                return ""  # Marker not found

            start_index += len(start_marker)  # Move past the marker
            revised_content = edited_response[start_index:].strip()
            return revised_content
        except Exception as e:
            self.logger.exception(f"Error extracting revised chapter: {e}")
            return ""