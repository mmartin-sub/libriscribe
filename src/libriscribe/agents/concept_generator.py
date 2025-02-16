# src/libriscribe/agents/concept_generator.py
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.llm_client import LLMClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import extract_json_from_markdown, read_json_file, write_json_file
#MODIFIED
from libriscribe.knowledge_base import ProjectKnowledgeBase

logger = logging.getLogger(__name__)

class ConceptGeneratorAgent(Agent):
    """Generates book concepts."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("ConceptGeneratorAgent", llm_client)

    def execute(self, project_knowledge_base: ProjectKnowledgeBase, output_path: Optional[str] = None) -> None:
        """Generates a book concept using an iterative refinement process."""
        try:
            # --- Step 1: Initial Concept Generation ---
            initial_prompt = f"""Generate a detailed book concept for a {project_knowledge_base.genre} {project_knowledge_base.category}. Initial ideas: {project_knowledge_base.description}.
            Return a JSON object, and make sure it's inside a markdown codeblock. Include a 'title', a 'logline', and a 'description'(around 200-300 words):

            ```json
            {{
                "title": "My Book Title",
                "logline": "A one-sentence summary of my book.",
                "description": "A more detailed description of my book (200-300 words)."
            }}
            ```"""
            initial_concept_md = self.llm_client.generate_content_with_json_repair(initial_prompt)
            if not initial_concept_md:
                logger.error("Initial concept generation failed.")
                return None
            initial_concept_json = extract_json_from_markdown(initial_concept_md)
            if not initial_concept_json:
                logger.error("Initial concept parsing failed.")
                return None

            # --- Step 2: Critique the Concept ---
            critique_prompt = f"""You are a helpful AI assistant. Critique the following book concept:

            ```json
            {json.dumps(initial_concept_json)}
            ```

            Identify any weaknesses, areas for improvement, or potential issues. Be specific.
            """
            critique = self.llm_client.generate_content(critique_prompt)

            # --- Step 3: Refine the Concept ---
            refine_prompt = f"""Based on the following critique, refine the book concept.  Address the weaknesses identified and improve the concept overall.

            Original Concept:
            ```json
            {json.dumps(initial_concept_json)}
            ```

            Critique:
            {critique}

            Return the REFINED concept as a JSON object inside a Markdown code block, with the same structure as before:
             ```json
            {{
                "title": "My Book Title",
                "logline": "A one-sentence summary of my book.",
                "description": "A more detailed description of my book (200-300 words)."
            }}
            ```
            """
            refined_concept_md = self.llm_client.generate_content_with_json_repair(refine_prompt)
            if not refined_concept_md:
                logger.error("Refined concept generation failed.")
                return None
            refined_concept_json = extract_json_from_markdown(refined_concept_md)
            if not refined_concept_json:
                logger.error("Refined concept parsing failed")
                return None
            # --- Step 4: Update and Return ProjectData ---

            project_knowledge_base.title = refined_concept_json.get('title', 'Untitled')
            project_knowledge_base.logline = refined_concept_json.get('logline', 'No logline provided.')
            project_knowledge_base.description = refined_concept_json.get('description', 'No description provided.')
            logger.info(f"Concept generated (refined): Title: {project_knowledge_base.title}, Logline: {project_knowledge_base.logline}")


        except Exception as e:
            self.logger.exception(f"Error generating concept: {e}")
            print(f"ERROR: Failed to generate concept. See log for details.")
            return None