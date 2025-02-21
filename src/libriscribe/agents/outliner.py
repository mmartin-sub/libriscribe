# Modified version of src/libriscribe/agents/outliner.py

import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.llm_client import LLMClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import read_markdown_file, write_markdown_file, extract_json_from_markdown
from libriscribe.knowledge_base import ProjectKnowledgeBase, Chapter, Scene
import typer
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


class OutlinerAgent(Agent):
    """Generates book outlines."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("OutlinerAgent", llm_client)

    def execute(self, project_knowledge_base: ProjectKnowledgeBase, output_path: Optional[str] = None) -> None:
        """Generates a chapter outline and then iterates to generate scene outlines."""
        try:
            # --- Step 1: Generate Chapter-Level Outline ---
            # Determine max chapters based on book length
            max_chapters = self._get_max_chapters(project_knowledge_base.book_length)
            
            # Enhance the prompt with explicit chapter count instruction
            if project_knowledge_base.book_length == "Short Story":
                initial_prompt = prompts.OUTLINE_PROMPT.format(**project_knowledge_base.model_dump())
                initial_prompt += f"\n\nIMPORTANT: This is a SHORT STORY. Generate EXACTLY {max_chapters} chapters. Do not exceed this limit."
            else:
                initial_prompt = prompts.OUTLINE_PROMPT.format(**project_knowledge_base.model_dump())

            console.print(f"{self.name} is: Generating Chapter Outline...")
            initial_outline = self.llm_client.generate_content(initial_prompt, max_tokens=3000, temperature=0.5)
            if not initial_outline:
                logger.error("Initial outline generation failed.")
                return

            # Process outline and limit chapters if needed
            self.process_outline(project_knowledge_base, initial_outline)
            self._enforce_chapter_limit(project_knowledge_base, max_chapters)

            # --- Step 2: Generate Scene Outlines for Each Chapter ---
            console.print(f"{self.name} is: Generating Scene Outlines...")
            for chapter_number, chapter in project_knowledge_base.chapters.items():
                self.generate_scene_outline(project_knowledge_base, chapter)

            # Save after both chapter and scene outlines are generated
            if output_path is None:
                output_path = str(project_knowledge_base.project_dir / "outline.md")
            
            # Update the outline if we trimmed chapters
            if project_knowledge_base.get("num_chapters", 0) <= max_chapters:
                project_knowledge_base.outline = self._update_outline_markdown(initial_outline, max_chapters)
            else:
                project_knowledge_base.outline = initial_outline
                
            write_markdown_file(output_path, project_knowledge_base.outline)  # Save overall outline

            self.logger.info(f"Outline generated and saved to knowledge base and {output_path}")

        except Exception as e:
            self.logger.exception(f"Error generating outline: {e}")
            print(f"ERROR: Failed to generate outline. See log for details.")

    def _get_max_chapters(self, book_length: str) -> int:
        """Determine the maximum number of chapters based on book length."""
        if book_length == "Short Story":
            return 2  # Short stories should have 1-2 chapters
        elif book_length == "Novella":
            return 8  # Novellas should have 5-8 chapters
        else:  # Novel or Full Book
            return 20  # Novels can have more chapters
    
    def _enforce_chapter_limit(self, project_knowledge_base: ProjectKnowledgeBase, max_chapters: int) -> None:
        """Limit the number of chapters in the knowledge base to max_chapters."""
        if project_knowledge_base.get("num_chapters", 0) > max_chapters:
            logger.info(f"Limiting chapters from {project_knowledge_base.num_chapters} to {max_chapters}")
            console.print(f"[yellow]Trimming outline to {max_chapters} chapters for {project_knowledge_base.book_length}[/yellow]")
            
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

    def generate_scene_outline(self, project_knowledge_base: ProjectKnowledgeBase, chapter: Chapter):
        """Generates the scene outline for a single chapter."""
        try:
            scene_prompt = prompts.SCENE_OUTLINE_PROMPT.format(
                genre=project_knowledge_base.genre,
                title=project_knowledge_base.title,
                category=project_knowledge_base.category,
                description=project_knowledge_base.description,
            )

            console.print(f"  Generating Scene Outline for Chapter {chapter.chapter_number}...")
            scene_outline_md = self.llm_client.generate_content(scene_prompt, max_tokens=2000, temperature=0.5)
            if not scene_outline_md:
                logger.error(f"Scene outline generation failed for Chapter {chapter.chapter_number}.")
                return

            # Process and store scene information
            self.process_scene_outline(chapter, scene_outline_md)

        except Exception as e:
            logger.exception(f"Error generating scene outline for chapter {chapter.chapter_number}: {e}")


    def process_scene_outline(self, chapter: Chapter, scene_outline_md: str):
        """Parses the Markdown scene outline and adds scenes to the chapter."""
        lines = scene_outline_md.split("\n")
        current_scene = None
        scene_number = 1  # Initialize scene number
        
        # Clear existing scenes to avoid duplication
        chapter.scenes = []
        
        # Variables to collect scene information
        current_summary = ""
        current_characters = []
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
                        emotional_beat=current_emotional_beat
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
                        current_summary = current_summary[:-2].strip()
                
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
            elif in_scene_section and not any(marker in line.lower() for marker in ["characters:", "setting:", "goal:", "emotional beat:", "emotion:", "scene"]):
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
                            emotional_beat=current_emotional_beat
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
                        current_summary = current_summary[:-2].strip()
        
        # Don't forget to add the last scene if there is one
        if current_summary:
            current_scene = Scene(
                scene_number=scene_number,
                summary=current_summary.strip(),
                characters=current_characters,
                setting=current_setting,
                goal=current_goal,
                emotional_beat=current_emotional_beat
            )
            chapter.scenes.append(current_scene)
        
        # Ensure they are ordered by scene number and do a final cleanup
        chapter.scenes.sort(key=lambda s: s.scene_number)

        # Remove any scenes with empty or placeholder summaries
        chapter.scenes = [
            s for s in chapter.scenes
            if s.summary.strip() and not s.summary.strip().startswith("Continue")
            and "..." not in s.summary and len(s.summary) > 5
        ]

        # Re-number scenes sequentially
        for i, scene in enumerate(chapter.scenes):
            scene.scene_number = i + 1
    def process_outline(self, project_knowledge_base: ProjectKnowledgeBase, outline_markdown: str):
        """Parses the Markdown outline and populates the knowledge base."""
        lines = outline_markdown.split("\n")
        current_chapter = None
        chapter_count = 0
        current_section = None  # Track what section we're in
        current_content = []   # Store content for current section

        logger.info("Processing outline...")

        for i, line in enumerate(lines):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Chapter header detection
            if "Chapter" in line and ("**Chapter" in line or "## Chapter" in line):
                # If we were processing a previous chapter, save its content
                if current_chapter and current_content:
                    if current_section == "summary":
                        current_chapter.summary = "\n".join(current_content).strip()
                    current_content = []

                try:
                    # Clean up the line
                    chapter_text = line.replace("**Chapter", "").replace("##", "").replace("Chapter", "").strip()
                    if ":" in chapter_text:
                        chapter_num_str, chapter_title = chapter_text.split(":", 1)
                    else:
                        # Try to extract number from start of text
                        import re
                        match = re.match(r'(\d+)\s*(.*)', chapter_text)
                        if match:
                            chapter_num_str, chapter_title = match.groups()
                        else:
                            continue

                    chapter_number = int(''.join(filter(str.isdigit, chapter_num_str)))
                    chapter_title = chapter_title.strip()

                    logger.info(f"Found Chapter {chapter_number}: {chapter_title}")

                    current_chapter = Chapter(
                        chapter_number=chapter_number,
                        title=chapter_title,
                        summary=""  # Initialize summary
                    )
                    project_knowledge_base.add_chapter(current_chapter)
                    chapter_count += 1
                    current_section = None
                    current_content = []

                except Exception as e:
                    logger.error(f"Error processing chapter line '{line}': {e}")
                    continue

            # Summary section detection
            elif "Summary" in line: # Removed ":"
                if current_chapter:
                    current_section = "summary"
                    current_content = []
                    continue

            # Key Plot Points detection
            elif "Key Plot Points:" in line or "**Key Plot Points:**" in line:
                if current_chapter and current_content:
                    current_chapter.summary = "\n".join(current_content).strip()
                current_section = "plot_points"
                current_content = []
                continue

            # Collect content for current section
            elif current_chapter and current_section:
                # Clean up bullet points and asterisks
                cleaned_line = line.replace("*", "").strip()
                if cleaned_line:
                    current_content.append(cleaned_line)
                    # For summary, update immediately
                    if current_section == "summary":
                        current_chapter.summary = "\n".join(current_content).strip()

        # Save any remaining content from the last chapter
        if current_chapter and current_content:
            if current_section == "summary":
                current_chapter.summary = "\n".join(current_content).strip()

        # Update the project knowledge base
        if chapter_count > 0:
            project_knowledge_base.num_chapters = chapter_count
            logger.info(f"Successfully processed {chapter_count} chapters")

            # Verify all chapters and print details
            for chapter_num in range(1, chapter_count + 1):
                chapter = project_knowledge_base.get_chapter(chapter_num)
                if chapter:
                    console.print(f"[green]Chapter {chapter_num} verified: {chapter.title}[/green]")
                    console.print(f"  - [cyan]Summary:[/cyan] {chapter.summary}")  # Print summary
                    for scene_num, scene in enumerate(chapter.scenes):
                        console.print(f"    - Scene {scene_num + 1}: {scene.summary}") #Print scene summary

                else:
                    logger.error(f"Chapter {chapter_num} missing after processing!")
        else:
            logger.warning("No chapters found in outline")
            # For short stories/novellas, ensure at least one chapter exists
            if project_knowledge_base.book_length in ["Short Story", "Novella"]:
                default_chapter = Chapter(
                    chapter_number=1,
                    title="The Story",
                    summary="Main story content"
                )
                # ADD THIS: Create a default scene
                default_scene = Scene(scene_number=1, summary="Main content of the story.")
                default_chapter.scenes.append(default_scene)

                project_knowledge_base.add_chapter(default_chapter)
                project_knowledge_base.num_chapters = 1
                logger.info("Created default chapter")