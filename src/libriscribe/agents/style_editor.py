# libriscribe/src/agents/style_editor.py
import asyncio
import logging
from typing import Any, Dict, List

from libriscribe.agents.agent_base import Agent
from libriscribe.utils.openai_client import OpenAIClient
from libriscribe.utils.file_utils import read_markdown_file, write_markdown_file, read_json_file
from pathlib import Path

logger = logging.getLogger(__name__)
class StyleEditorAgent(Agent):
    """Refines the writing style of a chapter."""

    def __init__(self):
        super().__init__("StyleEditorAgent")
        self.openai_client = OpenAIClient()

    def execute(self, chapter_path: str) -> None:
        """Refines the writing style of a chapter based on project settings.
          Args:
            chapter_path: The path to the chapter file.
        """

        chapter_content = read_markdown_file(chapter_path)
        if not chapter_content:
            print(f"ERROR: Chapter file is empty or not found: {chapter_path}")
            return

        # --- Get project data
        project_data_path = Path(chapter_path).parent / "project_data.json"
        project_data = read_json_file(str(project_data_path))
        if not project_data:
            print("ERROR: project_data.json not found. Cannot determine style preferences.")
            return

        # Get style preferences from project data
        tone = project_data.get('tone', 'Neutral')  # Default to Neutral
        target_audience = project_data.get('target_audience', 'General')

        prompt = f"""
        You are a style editor.  Refine the writing style of the following chapter excerpt to match
        the specified tone and target audience. Focus on improving clarity, word choice, sentence structure,
        and overall readability.

        Target Tone: {tone}
        Target Audience: {target_audience}

        Make specific suggestions for changes, and then provide the REVISED text. Output in the following format:

        ```
        Suggestions:
        1.  [Original sentence/phrase] -> [Revised sentence/phrase]: [Reason for change]
        2.  ...

        Revised Text:
        [The full revised chapter content]
        ```

        Chapter Excerpt:
        ---
        {chapter_content}
        ---
        """
        try:
            response = self.openai_client.generate_content(prompt, max_tokens=3000)  # Allow for longer responses

            # --- Extract Revised Text ---
            revised_text = self.extract_revised_text(response)
            if revised_text:
                write_markdown_file(chapter_path, revised_text)  # Overwrite with revised version
                print(f"Style editing complete for {chapter_path}.  Revised version saved.")
            else:
                print(f"ERROR:  Could not extract revised text for {chapter_path}.")
                self.logger.error(f"Could not extract revised text from StyleEditor response for {chapter_path}.")

        except Exception as e:
            self.logger.exception(f"Error during style editing for {chapter_path}: {e}")
            print(f"ERROR: Failed to edit style for chapter {chapter_path}. See log.")

    def extract_revised_text(self, response:str) -> str:
        """Extract the revised text portion from the LLM's response."""
        try:
            start_marker = "Revised Text:"
            start_index = response.find(start_marker)
            if start_index == -1:
                return "" # Marker not found

            start_index += len(start_marker) # Move past marker
            revised_content = response[start_index:].strip()
            return revised_content

        except Exception as e:
            self.logger.exception(f"Error extracting revised text from style editor: {e}")
            return""