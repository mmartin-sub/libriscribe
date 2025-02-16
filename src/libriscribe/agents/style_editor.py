# src/libriscribe/agents/style_editor.py

import logging
from pathlib import Path

from libriscribe.agents.agent_base import Agent
from libriscribe.utils.llm_client import LLMClient
from libriscribe.utils.file_utils import read_markdown_file, write_markdown_file, read_json_file, extract_json_from_markdown
#MODIFIED
from libriscribe.knowledge_base import ProjectKnowledgeBase

logger = logging.getLogger(__name__)
class StyleEditorAgent(Agent):
    """Refines the writing style of a chapter."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("StyleEditorAgent", llm_client)
        self.llm_client = llm_client

    def execute(self, project_knowledge_base: ProjectKnowledgeBase, chapter_number: int) -> None:
        """Refines style based on project settings."""
        chapter_path = str(Path(project_knowledge_base.project_name).parent / f"chapter_{chapter_number}.md")
        chapter_content = read_markdown_file(chapter_path)
        if not chapter_content:
            print(f"ERROR: Chapter file is empty or not found: {chapter_path}")
            return

        tone = project_knowledge_base.tone
        target_audience = project_knowledge_base.target_audience

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
            response = self.llm_client.generate_content(prompt, max_tokens=3000)
            revised_text = extract_json_from_markdown(response)  # Use Markdown extraction
            if revised_text:
                write_markdown_file(chapter_path, revised_text)
                print(f"Style editing complete for {chapter_path}. Revised version saved.")
            else:
                print(f"ERROR: Could not extract revised text for {chapter_path}.")
                self.logger.error(f"Could not extract from StyleEditor response for {chapter_path}.")

        except Exception as e:
            self.logger.exception(f"Error during style editing for {chapter_path}: {e}")
            print(f"ERROR: Failed to edit style for chapter {chapter_path}. See log.")