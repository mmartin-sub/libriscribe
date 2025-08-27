# src/libriscribe2/agents/editor.py

import logging
import re
from pathlib import Path
from typing import Any

# Add this import
from rich.console import Console

from ..settings import Settings
from ..utils import prompts_context as prompts
from ..utils.file_utils import (
    read_markdown_file,
    write_markdown_file,
)
from ..utils.llm_client_protocol import LLMClientProtocol
from ..utils.markdown_processor import format_revised_chapter_filename, remove_h3_from_markdown
from .agent_base import Agent
from .content_reviewer import ContentReviewerAgent

console = Console()


logger = logging.getLogger(__name__)


class EditorAgent(Agent):
    """Edits and refines chapters."""

    def __init__(self, llm_client: LLMClientProtocol, settings: Settings):
        super().__init__("EditorAgent", llm_client, settings)

    async def execute(
        self,
        project_knowledge_base: Any,
        output_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Edits a chapter and saves the revised version."""
        try:
            # Extract chapter_number from kwargs
            chapter_number = kwargs.get("chapter_number")
            if chapter_number is None:
                console.print("[red]Error: chapter_number is required[/red]")
                return

            # --- FIX: Construct the path correctly using project_dir ---
            if project_knowledge_base.project_dir is None:
                console.print("[red]Error: Project directory not set[/red]")
                return
            chapter_path = str(Path(project_knowledge_base.project_dir) / f"chapter_{chapter_number}.md")
            chapter_content = read_markdown_file(chapter_path)
            if not chapter_content:
                print(f"ERROR: Chapter file is empty: {chapter_path}")
                return
            chapter_title = self.extract_chapter_title(chapter_content)

            # Get the review results first
            reviewer_agent = ContentReviewerAgent(self.llm_client, self.settings)
            await reviewer_agent.execute(project_knowledge_base, chapter_path=chapter_path)

            scene_titles = self.extract_scene_titles(chapter_content)
            scene_titles_instruction = ""
            if scene_titles:
                scene_titles_str = "\n".join(f"- {title}" for title in scene_titles)
                scene_titles_instruction = f"""
                    IMPORTANT: This chapter contains scene titles that must be preserved in your edit.
                    Make sure each scene begins with its title in bold format (using **Scene X: Title**).
                    Here are the scene titles to preserve:

                    {scene_titles_str}

                    If any scene is missing a title in the format "**Scene X: Title**", please add an appropriate title.
                    """
            prompt_data = {
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "book_title": project_knowledge_base.title,
                "genre": project_knowledge_base.genre,
                "language": project_knowledge_base.language,
                "chapter_content": chapter_content,
                "review_feedback": getattr(reviewer_agent, "last_review_results", {}).get("review", ""),
            }

            console.print(f"✏️ [cyan]Editing Chapter {chapter_number} based on feedback...[/cyan]")
            prompt = prompts.EDITOR_PROMPT.format(**prompt_data) + scene_titles_instruction
            edited_response = await self.llm_client.generate_content(prompt, prompt_type="editor")  # , max_tokens=8000
            # --- KEY FIX: Use extract_json_from_markdown and check for None ---
            if "```" in edited_response:
                start = edited_response.find("```") + 3
                end = edited_response.rfind("```")

                # Skip the language identifier if present (e.g., ```markdown)
                next_newline = edited_response.find("\n", start)
                if next_newline < end and next_newline != -1:
                    start = next_newline + 1

                revised_chapter = edited_response[start:end].strip()
            else:
                # If no code blocks, try to extract the content after a leading explanation
                lines = edited_response.split("\n")
                content_start = 0
                for i, line in enumerate(lines):
                    if line.startswith("#") or line.startswith("Chapter"):
                        content_start = i
                        break

                if content_start > 0:
                    revised_chapter = "\n".join(lines[content_start:])
                else:
                    revised_chapter = edited_response

            if revised_chapter:
                # Use centralized mistletoe-based processing to remove level 3 headers
                try:
                    revised_chapter = remove_h3_from_markdown(revised_chapter, action="remove")
                    self.log_debug("Removed level 3 headers from revised chapter")
                except (ValueError, RuntimeError) as e:
                    console.print(f"[yellow]⚠️ Warning: Could not process level 3 headers: {e}[/yellow]")
                    # Continue with original content if processing fails
                    pass

                # Ensure first non-empty line is a single '#'
                lines = revised_chapter.splitlines()
                for i, line in enumerate(lines):
                    if line.strip().startswith("#"):
                        lines[i] = "# " + line.lstrip("#").strip()
                        break

                revised_chapter = "\n".join(lines)

                # Save as chapter_XX_revised.md with proper formatting
                revised_chapter_filename = format_revised_chapter_filename(chapter_number)
                revised_chapter_path = str(Path(project_knowledge_base.project_dir) / revised_chapter_filename)
                write_markdown_file(revised_chapter_path, revised_chapter)
                console.print(f"[green]✅ Edited chapter saved as {revised_chapter_filename}![/green]")
            else:
                print("ERROR: Could not extract revised chapter from editor output.")
                self.logger.error("Could not extract revised chapter content.")
                # --- ADD THIS: Log the raw response for debugging ---
                self.logger.error(f"Raw editor response: {edited_response}")

        except Exception as e:
            self.logger.exception(f"Error editing chapter {chapter_path}: {e}")
            print("ERROR: Failed to edit chapter. See log.")

    def extract_chapter_number(self, chapter_path: str) -> int:
        """Extracts chapter number."""
        try:
            return int(chapter_path.split("_")[1].split(".")[0])
        except Exception:
            return -1

    def extract_chapter_title(self, chapter_content: str) -> str:
        """Extracts chapter title."""
        lines = chapter_content.split("\n")
        for line in lines:
            if line.startswith("#"):
                return line.replace("#", "").strip()
        return "Untitled Chapter"

    def extract_scene_titles(self, chapter_content: str) -> list[str]:
        """
        Extracts scene titles from chapter content.
        Handles:
        - Lines starting with '##' and containing a colon.
        - Lines with '**...**' containing a colon.
        - Scene titles inside HTML comments.
        """
        scene_titles = []
        # Regex for scene titles in various formats
        scene_title_patterns = [
            r"^\s*##\s*(.+?:.+)$",  # Markdown heading
            r"^\s*\*\*(.+?:.+)\*\*\s*$",  # Bolded
            r"<!--\s*\*\*(.+?:.+)\*\*\s*-->",  # Bolded inside HTML comment
            r"<!--\s*##\s*(.+?:.+)\s*-->",  # Heading inside HTML comment
        ]
        lines = chapter_content.splitlines()
        for line in lines:
            for pattern in scene_title_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    title = match.group(1).strip()
                    scene_titles.append(title)
                    break  # Only match one pattern per line
        return scene_titles
