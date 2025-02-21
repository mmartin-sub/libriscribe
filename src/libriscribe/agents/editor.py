# src/libriscribe/agents/editor.py

import logging
from pathlib import Path

from libriscribe.agents.agent_base import Agent
from libriscribe.utils import prompts_context as prompts
from libriscribe.utils.file_utils import read_markdown_file, write_markdown_file, read_json_file, extract_json_from_markdown
from libriscribe.knowledge_base import ProjectKnowledgeBase
from libriscribe.utils.llm_client import LLMClient
# Add this import
from rich.console import Console
console = Console()


logger = logging.getLogger(__name__)

class EditorAgent(Agent):
    """Edits and refines chapters."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("EditorAgent", llm_client)

    def execute(self, project_knowledge_base: ProjectKnowledgeBase, chapter_number: int) -> None:
        """Edits a chapter and saves the revised version."""
        try:
            chapter_path = str(Path(project_knowledge_base.project_dir) / f"chapter_{chapter_number}.md")
            chapter_content = read_markdown_file(chapter_path)
            if not chapter_content:
                print(f"ERROR: Chapter file is empty: {chapter_path}")
                return
            chapter_title = self.extract_chapter_title(chapter_content)

            # Get the review results first
            reviewer_agent = ContentReviewerAgent(self.llm_client)
            review_results = reviewer_agent.execute(chapter_path)
            
            prompt_data = {
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "book_title": project_knowledge_base.title,
                "genre": project_knowledge_base.genre,
                "chapter_content": chapter_content,
                "review_feedback": review_results.get("review", "")
            }
            
            console.print(f"{self.name} is: Editing Chapter {chapter_number} based on reviewer feedback...")
            prompt = prompts.EDITOR_PROMPT.format(**prompt_data)
            edited_response = self.llm_client.generate_content(prompt, max_tokens=8000)
            # --- KEY FIX: Use extract_json_from_markdown and check for None ---
            revised_chapter = extract_json_from_markdown(edited_response)  # Using Markdown extraction
            if revised_chapter:
                write_markdown_file(chapter_path, revised_chapter)
            else:
                print("ERROR: Could not extract revised chapter from editor output.")
                self.logger.error("Could not extract revised chapter content.")
                # --- ADD THIS: Log the raw response for debugging ---
                self.logger.error(f"Raw editor response: {edited_response}")


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