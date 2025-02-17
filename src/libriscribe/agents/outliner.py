# src/libriscribe/agents/outliner.py

import asyncio
import json
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
        """Generates an outline, optimized for speed and short story handling."""
        try:
            # --- Initial Outline Generation (Simplified) ---
            if project_knowledge_base.book_length == "Short Story":
                # VERY concise prompt for short stories
                initial_prompt = """
                Create a brief outline for a {genre} short story titled "{title}" (category: {category}).

                Description: {description}

                Focus on a single, central conflict. The outline should likely have only ONE chapter, or at most 2-3 very short chapters.  Provide:

                * A brief summary of the entire short story.
                * A chapter breakdown (if multiple chapters), with:
                    * Chapter Title
                    * Short Summary

                Return the outline in Markdown format.
                """.format(**project_knowledge_base.model_dump())
            else:
                # Simplified chapter-level prompt for longer works
                initial_prompt = """
                Create a chapter-level outline for a {genre} book titled "{title}" (category: {category}).

                Description: {description}

                Include:
                * A brief summary of the entire book.
                * A breakdown of chapters, with each chapter having:
                    * A title.
                    * A short summary of the events in the chapter.
                    * Key plot points.

                Return the outline in Markdown format.
                """.format(**project_knowledge_base.model_dump())

            console.print(f"{self.name} is: Generating Outline... (approx. 30-60 seconds)")  # Indicate stage
            initial_outline = self.llm_client.generate_content(initial_prompt, max_tokens=3000, temperature=0.5) # Reduced max_tokens and temperature
            if not initial_outline:
                logger.error("Initial outline generation failed.")
                return

            # --- Process and Store in Knowledge Base ---
            self.process_outline(project_knowledge_base, initial_outline)

            # --- Save and Return ---
            if output_path is None:
                output_path = str(project_knowledge_base.project_dir / "outline.md")
            write_markdown_file(output_path, initial_outline)
            project_knowledge_base.outline = initial_outline
            self.logger.info(f"Outline generated and saved to knowledge base and {output_path}")

        except Exception as e:
            self.logger.exception(f"Error generating outline: {e}")
            print(f"ERROR: Failed to generate outline. See log for details.")

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
                        summary=""
                    )
                    project_knowledge_base.add_chapter(current_chapter)
                    chapter_count += 1
                    current_section = None
                    current_content = []
                    
                except Exception as e:
                    logger.error(f"Error processing chapter line '{line}': {e}")
                    continue
            
            # Summary section detection
            elif "Summary:" in line or "**Summary:**" in line:
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
            
            # Verify all chapters
            for chapter_num in range(1, chapter_count + 1):
                chapter = project_knowledge_base.get_chapter(chapter_num)
                if chapter:
                    logger.info(f"Chapter {chapter_num} verified: {chapter.title}")
                    logger.info(f"Summary length: {len(chapter.summary) if chapter.summary else 0} chars")
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
                project_knowledge_base.add_chapter(default_chapter)
                project_knowledge_base.num_chapters = 1
                logger.info("Created default chapter")