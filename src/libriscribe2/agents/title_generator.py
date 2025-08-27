"""
Title Generator Agent

This module provides an agent for generating book titles based on content.
"""

import logging
from typing import Any

from libriscribe2.agents.agent_base import Agent
from libriscribe2.knowledge_base import ProjectKnowledgeBase
from libriscribe2.settings import Settings
from libriscribe2.utils.json_utils import JSONProcessor
from libriscribe2.utils.llm_client_protocol import LLMClientProtocol

logger = logging.getLogger(__name__)


class TitleGeneratorAgent(Agent):
    """Generates book titles based on content and metadata."""

    def __init__(self, llm_client: LLMClientProtocol, settings: Settings | None = None):
        super().__init__("TitleGeneratorAgent", llm_client, settings)

    async def execute(
        self,
        project_knowledge_base: ProjectKnowledgeBase,
        output_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Generate a title based on book content and metadata."""
        try:
            # Build the title generation prompt
            prompt = self._build_title_prompt(project_knowledge_base)

            # Generate title using LLM with proper prompt_type
            response = await self.llm_client.generate_content(
                prompt, prompt_type="title_generation", temperature=self.settings.default_temperature
            )

            # Extract title from response
            title_json = JSONProcessor.extract_json_from_response(response)
            if title_json and isinstance(title_json, dict):
                new_title = JSONProcessor.extract_string_from_json(title_json, "title", "")
                if new_title and new_title.strip():
                    # Update the knowledge base with the new title
                    project_knowledge_base.title = new_title.strip()
                    logger.info(f"Generated title: {new_title}")

                    # Save updated knowledge base
                    if project_knowledge_base.project_dir:
                        project_knowledge_base.save_to_file(
                            str(project_knowledge_base.project_dir / "knowledge_base.json")
                        )
                else:
                    logger.warning("Failed to extract valid title from response")
            else:
                logger.warning("Failed to parse title generation response")

        except Exception as e:
            logger.error(f"Error generating title: {e}")
            raise

    def _build_title_prompt(self, project_kb: ProjectKnowledgeBase) -> str:
        """Build the title generation prompt based on available content."""
        prompt_parts = []

        # Add basic metadata
        prompt_parts.append("Generate a compelling book title based on the following information:")
        prompt_parts.append(f"Genre: {project_kb.genre}")
        prompt_parts.append(f"Category: {project_kb.category}")
        prompt_parts.append(f"Language: {project_kb.language}")

        # Add description if available
        if project_kb.description and project_kb.description.strip():
            prompt_parts.append(f"Description: {project_kb.description}")

        # Add logline if available
        if project_kb.logline and project_kb.logline.strip():
            prompt_parts.append(f"Logline: {project_kb.logline}")

        # Add character information if available
        if project_kb.characters:
            character_names = list(project_kb.characters.keys())
            if character_names:
                prompt_parts.append(f"Main Characters: {', '.join(character_names[:3])}")

        # Add worldbuilding information if available
        if project_kb.worldbuilding:
            worldbuilding_summary = []
            if project_kb.worldbuilding.geography:
                worldbuilding_summary.append("geography")
            if project_kb.worldbuilding.culture_and_society:
                worldbuilding_summary.append("culture")
            if project_kb.worldbuilding.magic_system:
                worldbuilding_summary.append("magic")
            if worldbuilding_summary:
                prompt_parts.append(f"Worldbuilding Elements: {', '.join(worldbuilding_summary)}")

        # Add chapter information if available - analyze full manuscript
        if project_kb.chapters:
            chapter_summaries = []
            chapter_contents = []

            # Get all chapters sorted by number
            sorted_chapters = sorted(project_kb.chapters.keys())

            # Add summaries for first 3 chapters
            for chapter_num in sorted_chapters[:3]:
                chapter = project_kb.chapters[chapter_num]
                if chapter.summary:
                    chapter_summaries.append(f"Chapter {chapter_num}: {chapter.summary}")

            # Add content from all chapters for full manuscript analysis
            for chapter_num in sorted_chapters:
                chapter = project_kb.chapters[chapter_num]
                if chapter.title:
                    chapter_contents.append(f"Chapter {chapter_num} Title: {chapter.title}")
                if chapter.summary:
                    chapter_contents.append(f"Chapter {chapter_num} Summary: {chapter.summary}")

                # Add scene information if available
                if chapter.scenes:
                    scene_summaries = []
                    for scene in chapter.scenes[:3]:  # First 3 scenes per chapter
                        if scene.summary:
                            scene_summaries.append(f"Scene {scene.scene_number}: {scene.summary}")
                    if scene_summaries:
                        chapter_contents.append(f"Chapter {chapter_num} Scenes: {'; '.join(scene_summaries)}")

            if chapter_summaries:
                prompt_parts.append("Chapter Summaries:")
                prompt_parts.extend(chapter_summaries)

            if chapter_contents:
                prompt_parts.append("Full Manuscript Analysis:")
                prompt_parts.extend(chapter_contents)

        # Add keywords if available
        if project_kb.keywords:
            prompt_parts.append(f"Keywords: {', '.join(project_kb.keywords[:10])}")

        # Add instructions
        prompt_parts.append("""
        Requirements for the title:
        1. Be compelling and memorable
        2. Reflect the genre and tone of the book
        3. Be appropriate for the target audience
        4. Be between 1-8 words
        5. Avoid clichés unless they serve the story well
        6. Consider the full manuscript content, not just initial concepts

        Return a JSON object with:
        ```json
        {
            "title": "The generated title",
            "subtitle": "Optional subtitle (if appropriate)",
            "reasoning": "Brief explanation of why this title works"
        }
        ```
        """)

        return "\n".join(prompt_parts)

    def generate_title_from_content(self, content: str, metadata: dict[str, Any]) -> str:
        """Generate a title from raw content and metadata."""
        # This would need to be called with an LLM client
        # For now, return a placeholder
        return "Generated Title"
