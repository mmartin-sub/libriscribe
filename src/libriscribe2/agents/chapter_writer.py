# src/libriscribe2/agents/chapter_writer.py

import logging
import re
from pathlib import Path
from typing import Any

from rich.console import Console

from ..knowledge_base import Chapter, Scene
from ..utils import prompts_context as prompts
from ..utils.file_utils import (
    write_markdown_file,
)
from ..utils.llm_client import LLMClient
from ..utils.markdown_processor import format_chapter_filename, format_scene_filename
from .agent_base import Agent

console = Console()

logger = logging.getLogger(__name__)


class ChapterWriterAgent(Agent):
    """Writes chapters."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("ChapterWriterAgent", llm_client)

    def format_scene(self, scene_title: str, scene_content: str) -> str:
        """
        Formats a scene by removing any visible scene title.
        Scene titles are removed to create cleaner chapter content without level 3 headers.
        """
        # Remove any Markdown heading that starts with the scene title (robust to variants)
        content = scene_content.lstrip()
        # Regex: match headings like ### **Scene 1: ...**, ### Scene 1: ..., **Scene 1: ...**, Scene 1: ...
        pattern = re.compile(
            rf"^(#{{1,6}}\s*)?(\*\*)?{re.escape(scene_title)}.*?(\*\*)?\s*\n*-*\n*",
            re.IGNORECASE | re.DOTALL,
        )
        content, n = pattern.subn("", content, count=1)
        if n == 0:
            self.logger.debug(f"No scene title heading matched for removal in scene: '{scene_title}'")
        # Return clean content without commented headers
        return content

    async def execute(
        self,
        project_knowledge_base: Any,
        output_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Writes a chapter scene by scene."""
        try:
            # Extract chapter_number from kwargs
            chapter_number = kwargs.get("chapter_number")
            if chapter_number is None:
                console.print("[red]Error: chapter_number is required[/red]")
                return

            # Get chapter data
            chapter = project_knowledge_base.get_chapter(chapter_number)
            if not chapter:
                console.print(f"[red]ERROR: Chapter {chapter_number} not found in knowledge base.[/red]")
                # Create a default chapter if not found
                chapter = Chapter(
                    chapter_number=chapter_number,
                    title=f"Chapter {chapter_number}",
                    summary="A new chapter in the unfolding story.",
                )
                # Add a default scene
                default_scene = Scene(
                    scene_number=1,
                    summary="The story continues with new developments.",
                    characters=["Shade"],
                    setting="Neo-London",
                    goal="Advance the plot",
                    emotional_beat="Tension",
                )
                chapter.scenes.append(default_scene)
                project_knowledge_base.add_chapter(chapter)
                console.print(f"[yellow]Created default chapter {chapter_number} to proceed.[/yellow]")

            console.print(f"\n[cyan]📝 Writing Chapter {chapter_number}: {chapter.title}[/cyan]")

            # Make sure there's at least one scene
            if not chapter.scenes:
                console.print(
                    f"[yellow]No scenes found for Chapter {chapter_number}. Creating a default scene.[/yellow]"
                )
                default_scene = Scene(
                    scene_number=1,
                    summary="The story continues with new developments.",
                    characters=["Shade"],
                    setting="Neo-London",
                    goal="Advance the plot",
                    emotional_beat="Tension",
                )
                chapter.scenes.append(default_scene)

            # Make sure scenes are ordered by scene number
            ordered_scenes = sorted(chapter.scenes, key=lambda s: s.scene_number)
            # Process each scene individually
            scene_contents = []

            for scene in ordered_scenes:
                console.print(f"🎬 Creating Scene/Section {scene.scene_number} of {len(ordered_scenes)}...")

                # Use full summary for scene title
                scene_title = f"Scene {scene.scene_number}: {scene.summary}"

                self.logger.debug(f"Prompting LLM for scene {scene.scene_number} with title: {scene_title}")

                # Create a prompt for this specific scene
                scene_prompt = prompts.SCENE_PROMPT.format(
                    chapter_number=chapter_number,
                    chapter_title=chapter.title,
                    book_title=project_knowledge_base.title,
                    genre=project_knowledge_base.genre,
                    category=project_knowledge_base.category,
                    language=project_knowledge_base.language,
                    chapter_summary=chapter.summary,
                    scene_number=scene.scene_number,
                    scene_summary=scene.summary,
                    characters=", ".join(scene.characters) if scene.characters else "None specified",
                    setting=scene.setting if scene.setting else "None specified",
                    goal=scene.goal if scene.goal else "None specified",
                    emotional_beat=scene.emotional_beat if scene.emotional_beat else "None specified",
                    total_scenes=len(ordered_scenes),
                )

                # Add the new instruction from prompts.py
                scene_prompt += "\n\n" + prompts.SCENE_TITLE_INSTRUCTION.format(
                    scene_number=scene.scene_number, scene_summary=scene.summary
                )

                scene_content = await self.llm_client.generate_content(
                    scene_prompt, prompt_type="scene"
                )  # , max_tokens=2000
                self.logger.debug(
                    f"LLM output for scene {scene.scene_number} (first 100 chars): {scene_content[:100]!r}"
                )
                if not scene_content:
                    error_msg = f"Failed to generate content for Scene {scene.scene_number}."
                    console.print(f"[red]{error_msg}[/red]")
                    raise RuntimeError(error_msg)

                # Save individual scene file (preserves level 3 headers as source)
                if project_knowledge_base.project_dir is not None:
                    scene_filename = format_scene_filename(chapter_number, scene.scene_number)
                    scene_path = str(Path(project_knowledge_base.project_dir) / scene_filename)
                    write_markdown_file(scene_path, scene_content)

                scene_content = self.format_scene(scene_title, scene_content)
                scene_contents.append(scene_content)

            # Combine scenes into a complete chapter
            chapter_content = f"# Chapter {chapter_number}: {chapter.title}\n\n"
            chapter_content += "\n\n".join(scene_contents)

            # Save the chapter
            if output_path is None:
                if project_knowledge_base.project_dir is not None:
                    chapter_filename = format_chapter_filename(chapter_number)
                    output_path = str(Path(project_knowledge_base.project_dir) / chapter_filename)
                else:
                    # TODO: Handle None project_dir (mypy error [arg-type])
                    console.print("[red]Error: Project directory not set[/red]")
                    return
            write_markdown_file(output_path, chapter_content)

            console.print(f"[green]✅ Chapter {chapter_number} completed with {len(ordered_scenes)} scenes![/green]")

        except Exception:
            # Log the error once with full traceback for debugging
            self.logger.exception(f"Error writing chapter {chapter_number}")
            # Re-raise the original exception to preserve the error chain
            raise
