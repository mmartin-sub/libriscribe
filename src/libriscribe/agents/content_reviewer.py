# src/libriscribe/agents/content_reviewer.py
import asyncio
import logging
from typing import Any, Dict

from libriscribe.agents.agent_base import Agent
from libriscribe.utils.openai_client import OpenAIClient
from libriscribe.utils.file_utils import read_markdown_file

logger = logging.getLogger(__name__)

class ContentReviewerAgent(Agent):
    """Reviews chapter content for consistency and clarity."""

    def __init__(self):
        super().__init__("ContentReviewerAgent")
        self.openai_client = OpenAIClient() # Explicitly create an instance

    def execute(self, chapter_path: str) -> Dict[str, Any]:
        """Reviews a chapter for consistency, clarity, and plot holes.

        Args:
            chapter_path: Path to the chapter file.

        Returns:
            A dictionary containing review findings (e.g., inconsistencies, suggestions).
            Returns an empty dictionary if the file doesn't exist or is empty.
        """
        chapter_content = read_markdown_file(chapter_path)
        if not chapter_content:
            print(f"ERROR: Chapter file is empty or not found: {chapter_path}")
            return {}

        prompt = f"""
        You are a meticulous content reviewer. Review the following chapter for:

        1.  **Internal Consistency:** Are character actions, dialogue, and motivations consistent with their established personalities and the overall plot?
        2.  **Clarity:** Are there any confusing passages, ambiguous descriptions, or unclear plot points?
        3.  **Plot Holes:** Are there any logical inconsistencies or unresolved questions within the chapter's narrative?
        4. **Redundancy**: Are there any sentences that repeat too much, or don't contribute to the overall?
        5. **Flow and Transitions:** Does the chapter flow smoothly from one scene or idea to the next? Are transitions between scenes clear?
        6. **Engagement:** Does the chapter maintain reader interest? Are there any sections that drag or feel slow?

        Provide specific examples of any issues found, referencing line numbers or sections where possible.  Output your review in Markdown format,
        with clear headings for each section (Consistency, Clarity, Plot Holes, etc.).  If no issues are found in a category,
        state "No issues found."

        Chapter Content:
        ---
        {chapter_content}
        ---
        """
        try:
            review_results = self.openai_client.generate_content(prompt, max_tokens=1500)
            return {"review": review_results}
        except Exception as e:
            self.logger.exception(f"Error reviewing chapter {chapter_path}: {e}")
            print(f"ERROR: Failed to review chapter {chapter_path}. See log for details.")
            return {}