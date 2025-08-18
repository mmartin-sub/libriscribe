# src/libriscribe2/agents/outliner.py

import logging
from pathlib import Path
from typing import Any

from rich.console import Console

from ..knowledge_base import Chapter, ProjectKnowledgeBase, Scene
from ..settings import SCENES_JSON
from ..utils import prompts_context as prompts
from ..utils.file_utils import (
    write_json_file,
    write_markdown_file,
)
from ..utils.llm_client import LLMClient
from ..utils.markdown_processor import remove_h3_from_markdown
from .agent_base import Agent

console = Console()
logger = logging.getLogger(__name__)


class OutlinerAgent(Agent):
    """Generates book outlines."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("OutlinerAgent", llm_client)

    async def execute(
        self,
        project_knowledge_base: Any,
        output_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Generates a chapter outline and then iterates to generate scene outlines."""
        try:
            # --- Step 1: Determine chapters based on project type ---
            # Use the configured num_chapters from the knowledge base
            configured_chapters = project_knowledge_base.num_chapters
            if isinstance(configured_chapters, tuple) and len(configured_chapters) > 0:
                configured_chapters = configured_chapters[1] if len(configured_chapters) > 1 else configured_chapters[0]
            elif isinstance(configured_chapters, tuple):
                configured_chapters = 12  # Default if empty tuple

            # Use configured chapters (no arbitrary limits)
            max_chapters = configured_chapters if configured_chapters else 12  # Default to novel length

            logger.info(f"Outliner: configured_chapters={configured_chapters}, max_chapters={max_chapters}")
            console.print(
                f"[cyan]📝 Generating outline with {max_chapters} chapters for {project_knowledge_base.project_type} project[/cyan]"
            )

            # Enhance the prompt with explicit chapter count instruction based on project type
            project_type = project_knowledge_base.project_type
            initial_prompt = prompts.OUTLINE_PROMPT.format(**project_knowledge_base.model_dump())

            if project_type == "short_story":
                initial_prompt += f"\n\nIMPORTANT: This is a SHORT STORY. Generate EXACTLY {max_chapters} chapters. Do not exceed this limit."
            elif project_type == "novella":
                initial_prompt += f"\n\nIMPORTANT: This is a NOVELLA. Generate EXACTLY {max_chapters} chapters. Do not exceed this limit."
            elif project_type == "book":
                initial_prompt += f"\n\nIMPORTANT: This is a BOOK (80-150 pages). Generate EXACTLY {max_chapters} chapters. Do not exceed this limit."
            elif project_type == "novel":
                initial_prompt += f"\n\nIMPORTANT: This is a NOVEL. Generate EXACTLY {max_chapters} chapters. Do not exceed this limit."
            elif project_type == "epic":
                initial_prompt += f"\n\nIMPORTANT: This is an EPIC NOVEL. Generate EXACTLY {max_chapters} chapters. Do not exceed this limit."
            else:
                initial_prompt += f"\n\nIMPORTANT: Generate EXACTLY {max_chapters} chapters. Do not exceed this limit."

            console.print("📝 [cyan]Creating chapter outline...[/cyan]")
            initial_outline = await self.safe_generate_content(
                initial_prompt, prompt_type="outline", temperature=0.5
            )  # max_tokens=3000
            if not initial_outline:
                console.print("[red]Initial outline generation failed.[/red]")
                logger.error("Initial outline generation failed.")
                raise RuntimeError("Initial outline generation failed.")

            # Process outline with max_chapters limit already included in prompt
            self.process_outline(project_knowledge_base, initial_outline, max_chapters)

            # Validate that chapters were actually created
            if not project_knowledge_base.chapters or len(project_knowledge_base.chapters) == 0:
                console.print("[red]No chapters were created from outline. Aborting.[/red]")
                logger.error("No chapters were created from outline. Aborting.")
                raise RuntimeError("No chapters were created from outline. Aborting.")

            # Save the overall outline first
            if output_path is None:
                if project_knowledge_base.project_dir is None:
                    raise ValueError("Project directory is not set")
                output_path = str(project_knowledge_base.project_dir / "outline.md")

            project_knowledge_base.outline = initial_outline

            # Remove level 3 headers from the outline
            try:
                processed_outline = remove_h3_from_markdown(project_knowledge_base.outline, action="remove")
                self.log_debug("Removed level 3 headers from outline")
                write_markdown_file(output_path, processed_outline)
            except (ValueError, RuntimeError) as e:
                console.print(f"[yellow]⚠️ Warning: Could not process level 3 headers in outline: {e}[/yellow]")
                # Continue with original content if processing fails
                write_markdown_file(output_path, project_knowledge_base.outline)

            # --- Step 2: Generate scene outlines for each chapter ---
            console.print("🎬 [cyan]Creating scene/sections breakdowns for each chapter...[/cyan]")

            # Loop through all chapters and generate scenes for each
            for chapter_num, chapter in project_knowledge_base.chapters.items():
                if chapter_num <= max_chapters:  # Only process up to max_chapters
                    console.print(f"📋 Working on Chapter {chapter_num}: {chapter.title}")

                    await self.generate_scene_outline(project_knowledge_base, chapter)

                    # Log for verification
                    if chapter.scenes:
                        console.print(
                            f"  [green]✅ Created {len(chapter.scenes)} scenes for Chapter {chapter_num}[/green]"
                        )
                    else:
                        console.print(f"[red]No scenes were generated for Chapter {chapter_num}. Aborting.[/red]")
                        logger.error(f"No scenes were generated for Chapter {chapter_num}.")
                        raise RuntimeError(f"No scenes were generated for Chapter {chapter_num}.")

            # Save the updated project data with scenes
            if hasattr(project_knowledge_base, "project_dir") and project_knowledge_base.project_dir:
                scenes_path = str(Path(project_knowledge_base.project_dir) / SCENES_JSON)

                # Create a simplified structure to save scene data
                scenes_data = {}
                for chapter_num, chapter in project_knowledge_base.chapters.items():
                    scenes_data[str(chapter_num)] = [scene.model_dump() for scene in chapter.scenes]

                write_json_file(scenes_path, scenes_data)

            self.logger.info(f"Outline and scenes generated and saved to knowledge base and {output_path}")

        except Exception:
            # Log the error once with full traceback for debugging
            self.logger.exception("Error generating outline")
            # Re-raise the original exception to preserve the error chain
            raise

    def _get_project_type_chapters(self, project_type: str) -> int:
        """Get recommended chapter count based on project type."""
        type_chapters = {"short_story": 1, "novella": 5, "book": 8, "novel": 12, "epic": 20}
        return type_chapters.get(project_type, 12)  # Default to novel

    def _enforce_chapter_limit(self, project_knowledge_base: ProjectKnowledgeBase, max_chapters: int) -> None:
        """Limit the number of chapters in the knowledge base to max_chapters."""
        if len(project_knowledge_base.chapters) > max_chapters:
            logger.info(f"Limiting chapters from {len(project_knowledge_base.chapters)} to {max_chapters}")
            console.print(f"[yellow]Trimming outline to {max_chapters} chapters (automatic mode limit)[/yellow]")

            # Keep only the first max_chapters
            chapters_to_keep = {}
            for i in range(1, max_chapters + 1):
                if i in project_knowledge_base.chapters:
                    chapters_to_keep[i] = project_knowledge_base.chapters[i]

            project_knowledge_base.chapters = chapters_to_keep
            project_knowledge_base.num_chapters = max_chapters

    def _update_outline_markdown(self, original_outline: str, max_chapters: int) -> str:
        """Update the markdown outline to include only the specified number of chapters."""
        lines = original_outline.split("\n")
        updated_lines = []

        in_chapter_section = False
        current_chapter = 0

        for line in lines:
            # Look for chapter headers
            if "Chapter" in line and ("**Chapter" in line or "## Chapter" in line):
                in_chapter_section = True
                current_chapter += 1

                if current_chapter > max_chapters:
                    # Skip this chapter and all content until we find another chapter or end
                    continue

            # If we're not in a chapter we need to skip, add the line
            if not in_chapter_section or current_chapter <= max_chapters:
                updated_lines.append(line)

        return "\n".join(updated_lines)

    async def generate_scene_outline(self, project_knowledge_base: ProjectKnowledgeBase, chapter: Chapter) -> bool:
        """Generates the scene outline for a single chapter."""
        try:
            # Generate random scene count for this chapter
            from libriscribe2.utils.validation_mixin import ValidationMixin

            scene_range = getattr(project_knowledge_base, "scenes_per_chapter", "3-6")
            scene_count = ValidationMixin.generate_random_scene_count(scene_range)

            logger.info(f"Chapter {chapter.chapter_number}: Generating {scene_count} scenes (range: {scene_range})")

            # Create a more detailed scene prompt with chapter information
            scene_prompt = f"""
            Create a detailed outline for the scenes in Chapter {chapter.chapter_number}: {chapter.title}
            of a {project_knowledge_base.genre} book titled \"{project_knowledge_base.title}\"
            which is categorized as {project_knowledge_base.category}.
            The book should be written in {project_knowledge_base.language}.

            Book Description: {project_knowledge_base.description}

            Chapter Summary: {chapter.summary}

            The outline should include a breakdown of EXACTLY {scene_count} scenes for this chapter, with EACH scene having:
            * Scene Number: (e.g., Scene 1, Scene 2, etc.)
            * Summary: (A short description of what happens in the scene, 1-2 sentences)
            * Characters: (A list of the characters involved, separated by commas)
            * Setting: (Where the scene takes place)
            * Goal: (The purpose of the scene)
            * Emotional Beat: (The primary emotion conveyed in the scene)

            IMPORTANT: Format the scene outline using Markdown bullet points, as shown below:

            Scene 1:
                * Summary: [Scene summary here]
                * Characters: [Character 1, Character 2, ...]
                * Setting: [Scene setting]
                * Goal: [Scene goal]
                * Emotional Beat: [Scene emotional beat]

            Scene 2:
                * Summary: [Scene summary here]
                * Characters: [Character 1, Character 2, ...]
                * Setting: [Scene setting]
                * Goal: [Scene goal]
                * Emotional Beat: [Scene emotional beat]

            [Repeat for exactly {scene_count} scenes, maintaining the exact same bullet point format]

            Be sure to include all main characters relevant to this chapter and create a natural flow between scenes.
            """

            console.print(f"  Generating Scene Outline for Chapter {chapter.chapter_number}...")
            scene_outline_md = await self.safe_generate_content(
                scene_prompt, prompt_type="scene_outline", temperature=0.5
            )  # max_tokens=2000,
            if not scene_outline_md:
                console.print(f"[red]Scene outline generation failed for Chapter {chapter.chapter_number}.[/red]")
                logger.error(f"Scene outline generation failed for Chapter {chapter.chapter_number}.")
                raise RuntimeError(f"Scene outline generation failed for Chapter {chapter.chapter_number}.")

            # Clear existing scenes to avoid duplication
            chapter.scenes = []

            # Split the response by scene to better parse each scene section
            scene_sections = self._split_into_scene_sections(scene_outline_md)

            for scene_number, scene_section in enumerate(scene_sections, 1):
                # Parse the scene data
                scene_data = self._extract_scene_data(scene_section, scene_number)

                if scene_data:
                    # Create and add the scene
                    scene = Scene(**scene_data)
                    chapter.scenes.append(scene)
                    logger.debug(f"Added Scene {scene_number} to Chapter {chapter.chapter_number}")
                else:
                    console.print(
                        f"[red]Failed to extract data for Scene {scene_number} in Chapter {chapter.chapter_number}. Aborting.[/red]"
                    )
                    logger.error(f"Failed to extract data for Scene {scene_number} in Chapter {chapter.chapter_number}")
                    raise RuntimeError(
                        f"Failed to extract data for Scene {scene_number} in Chapter {chapter.chapter_number}"
                    )

            # Ensure they are ordered by scene number
            chapter.scenes.sort(key=lambda s: s.scene_number)

            # If no scenes were created, raise
            if not chapter.scenes:
                console.print(f"[red]No scenes parsed for Chapter {chapter.chapter_number}. Aborting.[/red]")
                logger.error(f"No scenes parsed for Chapter {chapter.chapter_number}.")
                raise RuntimeError(f"No scenes parsed for Chapter {chapter.chapter_number}.")

            return True

        except Exception:
            # Log the error once with full traceback for debugging
            logger.exception(f"Error generating scene outline for chapter {chapter.chapter_number}")
            # Re-raise the original exception to preserve the error chain
            raise

    def _split_into_scene_sections(self, scene_outline_md: str) -> list[str]:
        """Split the scene outline into sections for each scene."""
        # First, normalize line endings and clean up the text
        scene_outline_md = scene_outline_md.replace("\r\n", "\n").replace("\r", "\n")
        lines = scene_outline_md.split("\n")

        scene_sections = []
        current_section: list[str] = []
        is_in_scene = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect new scene headers
            if "Scene" in line and (":" in line or line.strip().startswith("Scene")):
                # If we were already in a scene, save it
                if is_in_scene and current_section:
                    scene_sections.append("\n".join(current_section))
                    current_section = []

                is_in_scene = True
                current_section.append(line)
            elif is_in_scene:
                current_section.append(line)

        # Don't forget to add the last scene
        if current_section:
            scene_sections.append("\n".join(current_section))

        return scene_sections

    def _extract_scene_data(self, scene_section: str, default_scene_number: int) -> dict[str, Any] | None:
        """Extract scene data from a scene section."""
        scene_data: dict[str, Any] = {
            "scene_number": default_scene_number,
            "summary": "",
            "characters": [],
            "setting": "",
            "goal": "",
            "emotional_beat": "",
        }

        lines = scene_section.split("\n")

        # Extract scene number if present in the header
        header_line = lines[0] if lines else ""
        if "Scene" in header_line and ":" in header_line:
            try:
                # Try to extract number from "Scene X:" format
                number_part = header_line.split("Scene", 1)[1].split(":", 1)[0].strip()
                if number_part.isdigit():
                    scene_data["scene_number"] = int(number_part)
            except (IndexError, ValueError):
                # If extraction fails, use the default
                pass

        # Process each line to extract scene components
        for line in lines:
            line = line.strip()

            # Skip empty lines and headers
            if not line or line.startswith("Scene"):
                continue

            # Extract data based on bullet points or similar markers
            for field, marker in [
                ("summary", "Summary:"),
                ("characters", "Characters:"),
                ("setting", "Setting:"),
                ("goal", "Goal:"),
                ("emotional_beat", "Emotional Beat:"),
            ]:
                if marker.lower() in line.lower():
                    # Get the content after the marker
                    content = (
                        line.split(marker, 1)[1].strip() if marker in line else line.split(marker.lower(), 1)[1].strip()
                    )

                    # Clean up the content (remove bullets, asterisks, brackets)
                    content = content.lstrip("*-[]").strip()

                    if field == "characters":
                        # Split by commas and clean each character name
                        characters = [name.strip() for name in content.split(",") if name.strip()]
                        scene_data["characters"] = characters
                    else:
                        scene_data[field] = content

        # Ensure we at least have a summary
        if not scene_data["summary"]:
            # If no summary found, try to use the whole section as a summary
            for line in lines:
                if line and not any(
                    marker in line.lower()
                    for marker in [
                        "scene",
                        "summary:",
                        "characters:",
                        "setting:",
                        "goal:",
                        "emotional beat:",
                    ]
                ):
                    if scene_data["summary"]:
                        scene_data["summary"] += " " + line.strip()
                    else:
                        scene_data["summary"] = line.strip()

        # Only return the data if we have at least a summary
        return scene_data if scene_data["summary"] else None

    def process_scene_outline(self, chapter: Chapter, scene_outline_md: str) -> None:
        """Parses the Markdown scene outline and adds scenes to the chapter."""
        lines = scene_outline_md.split("\n")
        current_scene = None
        scene_number = 1  # Initialize scene number

        # Clear existing scenes to avoid duplication
        chapter.scenes = []

        # Variables to collect scene information
        current_summary = ""
        current_characters: list[str] = []
        current_setting = ""
        current_goal = ""
        current_emotional_beat = ""
        in_scene_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Scene header detection (various formats)
            if ("scene" in line.lower() or "**scene" in line.lower()) and not in_scene_section:
                # If we were already collecting a scene, save it first
                if current_summary:
                    # Create new scene with collected information
                    current_scene = Scene(
                        scene_number=scene_number,
                        summary=current_summary.strip(),
                        characters=current_characters,
                        setting=current_setting,
                        goal=current_goal,
                        emotional_beat=current_emotional_beat,
                    )
                    chapter.scenes.append(current_scene)
                    scene_number += 1  # Increment scene number

                    # Reset collection variables
                    current_summary = ""
                    current_characters = []
                    current_setting = ""
                    current_goal = ""
                    current_emotional_beat = ""

                in_scene_section = True
                # Extract scene summary if it's on the same line
                if ":" in line:
                    parts = line.split(":", 1)
                    current_summary = parts[1].strip()
                    # Clean up any ** marks
                    if current_summary.startswith("**"):
                        current_summary = current_summary[2:].strip()
                    if current_summary.endswith("**"):
                        current_summary = current_summary[:-2:].strip()

            # Character detection
            elif "characters:" in line.lower() or "character:" in line.lower():
                in_scene_section = True
                if ":" in line:
                    chars_part = line.split(":", 1)[1].strip()
                    # Handle various character formats
                    if "[" in chars_part and "]" in chars_part:
                        # Characters in square brackets or list format
                        chars_part = chars_part.replace("[", "").replace("]", "")

                    chars = chars_part.split(",")
                    current_characters = [c.strip() for c in chars if c.strip()]

                    # Clean up any * or ** marks
                    current_characters = [c.replace("*", "").strip() for c in current_characters]

            # Setting detection
            elif "setting:" in line.lower():
                in_scene_section = True
                if ":" in line:
                    current_setting = line.split(":", 1)[1].strip()
                    # Clean up any * or ** marks
                    if current_setting.startswith("*"):
                        current_setting = current_setting[1:].strip()
                    if current_setting.endswith("*"):
                        current_setting = current_setting[:-1].strip()

            # Goal detection
            elif "goal:" in line.lower():
                in_scene_section = True
                if ":" in line:
                    current_goal = line.split(":", 1)[1].strip()
                    # Clean up any * or ** marks
                    if current_goal.startswith("*"):
                        current_goal = current_goal[1:].strip()
                    if current_goal.endswith("*"):
                        current_goal = current_goal[:-1].strip()

            # Emotional beat detection
            elif "emotional beat:" in line.lower() or "emotion:" in line.lower():
                in_scene_section = True
                if ":" in line:
                    current_emotional_beat = line.split(":", 1)[1].strip()
                    # Clean up any * or ** marks
                    if current_emotional_beat.startswith("*"):
                        current_emotional_beat = current_emotional_beat[1:].strip()
                    if current_emotional_beat.endswith("*"):
                        current_emotional_beat = current_emotional_beat[:-1].strip()

            # If we're in a scene section but none of the above, it might be part of the summary
            elif in_scene_section and not any(
                marker in line.lower()
                for marker in [
                    "characters:",
                    "setting:",
                    "goal:",
                    "emotional beat:",
                    "emotion:",
                    "scene",
                ]
            ):
                # Check if this looks like a new chapter marker
                if "chapter" in line.lower() and (":" in line or "**" in line):
                    # This is likely a new chapter marker, end current scene collection
                    in_scene_section = False
                    if current_summary:
                        # Save the current scene before moving to a new section
                        current_scene = Scene(
                            scene_number=scene_number,
                            summary=current_summary.strip(),
                            characters=current_characters,
                            setting=current_setting,
                            goal=current_goal,
                            emotional_beat=current_emotional_beat,
                        )
                        chapter.scenes.append(current_scene)
                        scene_number += 1

                        # Reset collection variables
                        current_summary = ""
                        current_characters = []
                        current_setting = ""
                        current_goal = ""
                        current_emotional_beat = ""
                else:
                    # This is additional summary content
                    if current_summary:
                        current_summary += " " + line
                    else:
                        current_summary = line

                    # Clean up any ** marks in the summary
                    if current_summary.startswith("**"):
                        current_summary = current_summary[2:].strip()
                    if current_summary.endswith("**"):
                        current_summary = current_summary[:-2:].strip()

        # Don't forget to add the last scene if there is one
        if current_summary:
            current_scene = Scene(
                scene_number=scene_number,
                summary=current_summary.strip(),
                characters=current_characters,
                setting=current_setting,
                goal=current_goal,
                emotional_beat=current_emotional_beat,
            )
            chapter.scenes.append(current_scene)

        # Ensure they are ordered by scene number and do a final cleanup
        chapter.scenes.sort(key=lambda s: s.scene_number)

        # Remove any scenes with empty or placeholder summaries
        chapter.scenes = [
            s
            for s in chapter.scenes
            if s.summary.strip()
            and not s.summary.strip().startswith("Continue")
            and "..." not in s.summary
            and len(s.summary) > 5
        ]

        # Re-number scenes sequentially
        for i, scene in enumerate(chapter.scenes):
            scene.scene_number = i + 1

    def process_outline(
        self,
        project_knowledge_base: ProjectKnowledgeBase,
        outline_markdown: str,
        max_chapters: int,
    ) -> None:
        """Parses the Markdown outline and populates the knowledge base."""
        lines = outline_markdown.split("\n")
        current_chapter = None
        chapter_count = 0
        current_section = None  # Track what section we're in
        current_content: list[str] = []  # Store content for current section

        logger.info("Processing outline...")

        for i, line in enumerate(lines):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Chapter header detection (more robust pattern matching)
            if "Chapter" in line and (line.startswith("Chapter") or "##" in line or "**" in line):
                # If we've reached the maximum number of chapters, stop processing
                if chapter_count >= max_chapters:
                    break

                # If we were processing a previous chapter, save its content
                if current_content:
                    if current_chapter and current_section == "summary":
                        current_chapter.summary = "\n".join(current_content).strip()
                    current_content = []

                try:
                    # Extract chapter number and title
                    chapter_parts = line.replace("##", "").replace("**", "").replace("Chapter", "").strip()

                    # Handle different formats: "1: Title", "1 - Title", or just "1"
                    if ":" in chapter_parts:
                        chapter_num_str, chapter_title = chapter_parts.split(":", 1)
                    elif "-" in chapter_parts:
                        chapter_num_str, chapter_title = chapter_parts.split("-", 1)
                    else:
                        # Try to extract just the number
                        import re

                        match = re.match(r"(\d+)\s*(.*)", chapter_parts)
                        if match:
                            chapter_num_str, chapter_title = match.groups()
                        else:
                            # Fallback: create sequential chapter
                            chapter_num_str = str(chapter_count + 1)
                            chapter_title = f"Chapter {chapter_num_str}"

                    chapter_number = int("".join(filter(str.isdigit, chapter_num_str)))
                    chapter_title = chapter_title.strip()

                    logger.info(f"Found Chapter {chapter_number}: {chapter_title}")

                    current_chapter = Chapter(
                        chapter_number=chapter_number,
                        title=chapter_title,
                        summary="",  # Initialize summary
                    )
                    project_knowledge_base.add_chapter(current_chapter)
                    chapter_count += 1
                    current_section = None
                    current_content = []

                except Exception as e:
                    logger.error(f"Error processing chapter line '{line}': {e}")
                    continue

            # If no chapters found yet, check if this is a book summary section
            elif "Book Summary" in line and chapter_count == 0:
                # Next lines will be the book summary
                book_summary_lines = []
                j = i + 1
                while j < len(lines):
                    current_line = lines[j].strip()
                    if current_line.startswith("Chapter") or "Chapter List" in current_line:
                        break
                    if current_line:
                        book_summary_lines.append(current_line)
                    j += 1

                # Set the book description from the summary if there is one
                if book_summary_lines:
                    project_knowledge_base.description = "\n".join(book_summary_lines)

            # Summary section detection
            elif current_chapter and ("Summary" in line or line.startswith("Summary")):
                current_section = "summary"
                current_content = []
                continue

            # Key Events/Plot Points detection
            elif current_chapter and ("Key Events" in line or "Plot Points" in line):
                if current_content:
                    current_chapter.summary = "\n".join(current_content).strip()
                current_section = "plot_points"
                current_content = []
                continue

            # Collect content for current section
            elif current_chapter and current_section:
                # Clean up bullet points and asterisks
                cleaned_line = line.replace("*", "").replace("[", "").replace("]", "").strip()
                if cleaned_line:
                    current_content.append(cleaned_line)
                    # For summary, update immediately
                    if current_section == "summary":
                        current_chapter.summary = "\n".join(current_content).strip()

            # Look for number of chapters information
            elif "Chapter List" in line or "chapters" in line.lower():
                try:
                    # Try to extract chapter count information
                    next_line = lines[i + 1] if i + 1 < len(lines) else ""
                    if next_line:
                        # Look for digits in the line after "Chapter List"
                        import re

                        digits = re.findall(r"\d+", next_line)
                        if digits:
                            total_chapters = int(digits[0])
                            logger.info(f"Found total chapters: {total_chapters}")
                            if total_chapters > 0 and total_chapters <= max_chapters:
                                # Set the number of chapters
                                project_knowledge_base.num_chapters = total_chapters
                except Exception as e:
                    logger.error(f"Error extracting chapter count: {e}")

        # Save any remaining content from the last chapter
        if current_chapter and current_content:
            if current_section == "summary":
                current_chapter.summary = "\n".join(current_content).strip()

        # If no chapters found, create a default chapter 1 for the story
        if chapter_count == 0:
            logger.warning("No chapters found in outline")
            default_chapter = Chapter(
                chapter_number=1,
                title="Shadow's Discovery",
                summary="Shade, a daemon eking out a meager existence in the polluted shadows of Neo-London, stumbles upon a pulsating dragon egg during a scavenging run. He grapples with whether to protect it or preserve his anonymity.",
            )
            # Add a default scene
            default_scene = Scene(
                scene_number=1,
                summary="Shade discovers the dragon egg in an abandoned research facility.",
                characters=["Shade"],
                setting="Abandoned research facility in Neo-London",
                goal="Introduce the protagonist and the discovery that changes everything",
                emotional_beat="Wonder mixed with apprehension",
            )
            default_chapter.scenes.append(default_scene)

            project_knowledge_base.add_chapter(default_chapter)
            project_knowledge_base.num_chapters = 1
            logger.info("Created default chapter with scene")
        else:
            # Set the number of chapters that were actually found
            project_knowledge_base.num_chapters = chapter_count
            logger.info(f"Successfully processed {chapter_count} chapters")

        # Determine if we need to extract the estimated number of chapters from the text
        if isinstance(project_knowledge_base.num_chapters, int) and project_knowledge_base.num_chapters <= 1:
            # Try to detect the number of chapters from the outline
            try:
                full_text = outline_markdown.lower()
                if "chapter list" in full_text:
                    # Look for text like "10 chapters" or "Total chapters: 8"
                    import re

                    chapter_count_patterns = [
                        r"(\d+)\s+chapters",
                        r"total\s+chapters:\s*(\d+)",
                        r"chapter\s+list\s*[\(:]?\s*(\d+)",
                    ]

                    for pattern in chapter_count_patterns:
                        matches = re.search(pattern, full_text)
                        if matches:
                            estimated_chapters = int(matches.group(1))
                            if 1 <= estimated_chapters <= max_chapters:
                                project_knowledge_base.num_chapters = estimated_chapters
                                logger.info(f"Extracted estimated chapter count: {estimated_chapters}")
                                break
            except Exception as e:
                logger.error(f"Error extracting chapter count from text: {e}")
