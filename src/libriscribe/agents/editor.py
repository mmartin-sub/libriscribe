# src/libriscribe/agents/editor.py

import logging
from pathlib import Path

from libriscribe.agents.agent_base import Agent
from libriscribe.utils import prompts_context as prompts
from libriscribe.utils.file_utils import read_markdown_file, write_markdown_file, read_json_file, extract_json_from_markdown
from libriscribe.project_data import ProjectData
from libriscribe.utils.llm_client import LLMClient


logger = logging.getLogger(__name__)

class EditorAgent(Agent):
    """Edits and refines chapters."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("EditorAgent", llm_client)
        self.project_data: Optional[ProjectData] = None

    def execute(self, chapter_path: str) -> None:
        """Edits a chapter and saves the revised version."""
        try:
            chapter_content = read_markdown_file(chapter_path)
            if not chapter_content:
                print(f"ERROR: Chapter file is empty: {chapter_path}")
                return
            chapter_number = self.extract_chapter_number(chapter_path)
            chapter_title = self.extract_chapter_title(chapter_content)

            #Get Project Data
            project_file = Path(chapter_path).parent / "project_data.json"
            if project_file.exists():
                data = read_json_file(str(project_file), ProjectData)
                if data:
                    self.project_data = data
                else:
                    self.logger.error("Project Data was not loaded correctly")
                    print("ERROR: Failed to load project data")
                    return
            else:
                self.logger.error("Project Data was not loaded correctly")
                print("ERROR: Failed to load project data")
                return
            prompt_data = {
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "book_title": self.project_data.get("title", "Untitled"),
                "genre": self.project_data.get("genre", "Unknown Genre"),
                "chapter_content": chapter_content,
            }
            prompt = prompts.EDITOR_PROMPT.format(**prompt_data)
            edited_response = self.llm_client.generate_content(prompt, max_tokens=4000)
            revised_chapter = self.extract_revised_chapter(edited_response)  # Using Markdown extraction
            if revised_chapter:
                write_markdown_file(chapter_path, revised_chapter)
            else:
                print("ERROR: Could not extract revised chapter from editor output.")
                self.logger.error("Could not extract revised chapter content.")

        except Exception as e:
            self.logger.exception(f"Error editing chapter {chapter_path}: {e}")
            print(f"ERROR: Failed to edit chapter. See log.")

    def extract_chapter_number(self, chapter_path: str) -> int:
        """Extracts chapter number."""
        try:
            return int(chapter_path.split("_")[1].split(".")[0])
        except:
            return -1

    def extract_chapter_title(self, chapter_content: str) -> str:
        """Extracts chapter title."""
        lines = chapter_content.split("\n")
        for line in lines:
            if line.startswith("#"):
                return line.replace("#", "").strip()
        return "Untitled Chapter"
    def extract_revised_chapter(self, edited_response: str) -> str:
        """Extracts the revised chapter content from the editor's output (using Markdown extraction)."""
        return extract_json_from_markdown(edited_response) or ""