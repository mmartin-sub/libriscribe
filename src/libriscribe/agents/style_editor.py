# src/libriscribe/agents/style_editor.py

import logging
from pathlib import Path

from libriscribe.agents.agent_base import Agent
from libriscribe.utils.openai_client import OpenAIClient
from libriscribe.utils.file_utils import read_markdown_file, write_markdown_file, read_json_file, extract_json_from_markdown
from libriscribe.project_data import ProjectData

logger = logging.getLogger(__name__)
class StyleEditorAgent(Agent):
    """Refines the writing style of a chapter."""

    def __init__(self):
        super().__init__("StyleEditorAgent")
        self.openai_client = OpenAIClient()
        self.project_data: Optional[ProjectData] = None
    def execute(self, chapter_path: str) -> None:
        """Refines style based on project settings."""
        chapter_content = read_markdown_file(chapter_path)
        if not chapter_content:
            print(f"ERROR: Chapter file is empty or not found: {chapter_path}")
            return
        # Get project data
        project_data_path = Path(chapter_path).parent / "project_data.json"
        if project_data_path.exists():
            data = read_json_file(str(project_data_path))
            self.project_data = ProjectData(**data)
        else:
            self.logger.error("Project Data was not loaded correctly")
            print("Error: Failed to load project data")
            return

        if not self.project_data:
            print("ERROR: project_data.json not found. Cannot determine style preferences.")
            return
        tone = self.project_data.get('tone', 'Neutral')
        target_audience = self.project_data.get('target_audience', 'General')

        prompt = f"""
        You are a style editor.  Refine the writing style of the following chapter excerpt...

        Target Tone: {tone}
        Target Audience: {target_audience}

        Make specific suggestions for changes, and then provide the REVISED text within a Markdown code block.

        ```markdown
        [The full revised chapter content]
        ```

        Chapter Excerpt:
        ---
        {chapter_content}
        ---
        """  # Added Markdown code block
        try:
            response = self.openai_client.generate_content(prompt, max_tokens=3000)
            revised_text = self.extract_revised_text(response)  # Use Markdown extraction
            if revised_text:
                write_markdown_file(chapter_path, revised_text)
                print(f"Style editing complete for {chapter_path}. Revised version saved.")
            else:
                print(f"ERROR: Could not extract revised text for {chapter_path}.")
                self.logger.error(f"Could not extract from StyleEditor response for {chapter_path}.")

        except Exception as e:
            self.logger.exception(f"Error during style editing for {chapter_path}: {e}")
            print(f"ERROR: Failed to edit style for chapter {chapter_path}. See log.")

    def extract_revised_text(self, response: str) -> str:
        """Extracts revised text (using Markdown extraction)."""
        return extract_json_from_markdown(response) or ""