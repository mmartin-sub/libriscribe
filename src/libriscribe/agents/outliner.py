# src/libriscribe/agents/outliner.py

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.llm_client import LLMClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import read_markdown_file, write_markdown_file, extract_json_from_markdown  # Import
#MODIFIED
from libriscribe.knowledge_base import ProjectKnowledgeBase, Chapter, Scene


logger = logging.getLogger(__name__)


class OutlinerAgent(Agent):
    """Generates book outlines."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("OutlinerAgent", llm_client)

    def execute(self, project_knowledge_base: ProjectKnowledgeBase, output_path: Optional[str] = None) -> None:
        """Generates an outline using an iterative refinement process."""
        try:
            # --- Step 1: Initial Outline Generation ---
            # Use scene-level prompt
            initial_prompt = prompts.SCENE_OUTLINE_PROMPT.format(**project_knowledge_base.model_dump())  # Use model_dump
            initial_outline = self.llm_client.generate_content(initial_prompt, max_tokens=5000) #Increased tokens
            if not initial_outline:
                logger.error("Initial outline generation failed.")
                return

            # --- Step 2: Critique the Outline ---
            critique_prompt = f"""Critique the following book outline:

            {initial_outline}

            Identify any weaknesses, areas for improvement, potential plot holes, or inconsistencies. Be specific.
            """
            critique = self.llm_client.generate_content(critique_prompt, max_tokens=1000)

            # --- Step 3: Refine the Outline ---
            refine_prompt = f"""Based on the following critique, refine the book outline. Address the identified weaknesses and improve the outline overall.

            Original Outline:
            {initial_outline}

            Critique:
            {critique}

            Return the REFINED outline in Markdown format.
            """
            refined_outline = self.llm_client.generate_content(refine_prompt, max_tokens=5000) #Increased tokens
            if not refined_outline:
                logger.error("Refined outline generation failed.")
                return

            # --- Step 4: Process and Store in Knowledge Base ---
            self.process_outline(project_knowledge_base, refined_outline)


            # --- Step 5: Save and Return ---
            #Now we save the markdown to use it later
            if output_path is None:
                output_path = str(Path(project_knowledge_base.project_name).parent / "outline.md")
            write_markdown_file(output_path, refined_outline)  # Use write_markdown_file
            project_knowledge_base.outline = refined_outline # Save outline
            self.logger.info(f"Outline generated (refined) and saved to knowledge base and {output_path}")


        except Exception as e:
            self.logger.exception(f"Error generating outline: {e}")
            print(f"ERROR: Failed to generate outline. See log for details.")

    def process_outline(self, project_knowledge_base: ProjectKnowledgeBase, outline_markdown: str):
        """Parses the Markdown outline and populates the knowledge base."""
        lines = outline_markdown.split("\n")
        current_chapter = None

        for line in lines:
            line = line.strip()
            if line.startswith("# Chapter"):
                # Extract chapter number and title
                parts = line.split(":", 1)  # Split on first colon only
                if len(parts) != 2:
                    continue
                chapter_number_str = parts[0].replace("# Chapter", "").strip()
                chapter_title = parts[1].strip()

                try:
                    chapter_number = int(chapter_number_str)
                    current_chapter = Chapter(chapter_number=chapter_number, title=chapter_title)
                    project_knowledge_base.add_chapter(current_chapter)
                except ValueError:
                    logger.warning(f"Invalid chapter number: {chapter_number_str}")
                    current_chapter = None # Reset

            elif line.startswith("## Scene") and current_chapter:
                # Extract scene number
                scene_number_str = line.replace("## Scene", "").strip()
                try:
                    scene_number = int(scene_number_str)
                    scene = Scene(scene_number=scene_number)
                    project_knowledge_base.add_scene_to_chapter(current_chapter.chapter_number, scene)

                    # Look for scene details in subsequent lines (until next scene or chapter)
                    scene_details = {}
                    for detail_line in lines[lines.index(line) + 1:]:
                        detail_line = detail_line.strip()
                        if detail_line.startswith("## Scene") or detail_line.startswith("# Chapter"):
                            break  # End of scene details

                        if ":" in detail_line:
                            key, value = detail_line.split(":", 1)
                            scene_details[key.strip().lower()] = value.strip()
                    # Now populate the scene object
                    scene.summary = scene_details.get("summary", "")

                    if "characters" in scene_details:
                         scene.characters = [c.strip() for c in scene_details["characters"].split(",") if c.strip()]
                    scene.setting = scene_details.get("setting", "")
                    scene.goal = scene_details.get("goal", "")
                    scene.emotional_beat = scene_details.get("emotional beat", "")
                except ValueError:
                     logger.warning(f"Invalid Scene Number {scene_number_str}")
                     continue # Skip to next line

            elif current_chapter and line.startswith("Summary:") and not line.startswith("## Scene"):
                #Allow to save chapter summaries even if the scenes where not generated
                current_chapter.summary = line.replace("Summary:", "").strip()