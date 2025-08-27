# src/libriscribe2/agents/style_editor.py

import logging
from pathlib import Path
from typing import Any

from rich.console import Console

from ..settings import Settings
from ..utils.file_utils import (
    read_markdown_file,
    write_markdown_file,
)
from ..utils.llm_client_protocol import LLMClientProtocol
from ..utils.markdown_processor import remove_h3_from_markdown
from .agent_base import Agent

console = Console()
logger = logging.getLogger(__name__)


class StyleEditorAgent(Agent):
    """Refines the writing style of a chapter."""

    def __init__(self, llm_client: LLMClientProtocol, settings: Settings):
        super().__init__("StyleEditorAgent", llm_client, settings)

    async def execute(self, project_knowledge_base: Any, output_path: str | None = None, **kwargs: Any) -> None:
        """Refines style based on project settings."""
        # Extract chapter_number from kwargs
        chapter_number = kwargs.get("chapter_number")
        if chapter_number is None:
            console.print("[red]Error: chapter_number is required[/red]")
            return

        if project_knowledge_base.project_dir is not None:
            chapter_path = str(Path(project_knowledge_base.project_dir) / f"chapter_{chapter_number}.md")
        else:
            # TODO: Handle None project_dir (mypy error [arg-type])
            console.print("[red]Error: Project directory not set[/red]")
            return
        chapter_content = read_markdown_file(chapter_path)
        if not chapter_content:
            print(f"ERROR: Chapter file is empty or not found: {chapter_path}")
            return

        # Get tone and target_audience with default values if not present
        tone = getattr(project_knowledge_base, "tone", "Informative")
        target_audience = getattr(project_knowledge_base, "target_audience", "General")

        console.print(f"🎨 [cyan]Polishing writing style for Chapter {chapter_number}...[/cyan]")
        prompt = f"""
        You are a style editor. Refine the writing style of the following chapter excerpt...

        Target Tone: {tone}
        Target Audience: {target_audience}
        Language: {project_knowledge_base.language}

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
            response = await self.llm_client.generate_content(prompt, prompt_type="style_editing")

            # Extract the revised content from the response
            if "```" in response:
                start = response.find("```") + 3
                end = response.rfind("```")

                # Skip the language identifier if present (e.g., ```markdown)
                next_newline = response.find("\n", start)
                if next_newline < end and next_newline != -1:
                    start = next_newline + 1

                revised_text = response[start:end].strip()
            else:
                # If no code blocks, try to extract the content after a leading explanation
                lines = response.split("\n")
                content_start = 0
                for i, line in enumerate(lines):
                    if line.startswith("#") or line.startswith("Chapter"):
                        content_start = i
                        break

                if content_start > 0:
                    revised_text = "\n".join(lines[content_start:])
                else:
                    revised_text = response

            if revised_text:
                revised_text = revised_text.strip()
                # Remove level 3 headers from the style-edited chapter
                try:
                    revised_text = remove_h3_from_markdown(revised_text, action="remove")
                    self.log_debug("Removed level 3 headers from style-edited chapter")
                except (ValueError, RuntimeError) as e:
                    console.print(f"[yellow]⚠️ Warning: Could not process level 3 headers in style edit: {e}[/yellow]")
                    # Continue with original content if processing fails
                    pass

                write_markdown_file(chapter_path, revised_text)
                console.print(f"[green]✅ Style improvements applied to Chapter {chapter_number}![/green]")
            else:
                print(f"ERROR: Could not extract revised text for {chapter_path}.")
                self.logger.error(f"Could not extract from StyleEditor response for {chapter_path}.")
                raise ValueError(f"Could not extract revised text for {chapter_path}.")

        except Exception as e:
            self.logger.exception(f"Error during style editing for {chapter_path}: {e}")
            print(f"ERROR: Failed to edit style for chapter {chapter_path}. See log.")
