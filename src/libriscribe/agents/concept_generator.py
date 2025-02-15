# libriscribe/src/agents/concept_generator.py
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.openai_client import OpenAIClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import extract_json_from_markdown

logger = logging.getLogger(__name__)

class ConceptGeneratorAgent(Agent):
    """Generates book concepts."""

    def __init__(self):
        super().__init__("ConceptGeneratorAgent")

    def execute(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a book concept and returns it as a dictionary."""

        try:
            prompt = f"""Generate a detailed book concept for a {project_data['genre']} {project_data['category']}. Initial ideas: {project_data.get('description', 'None')}.
            Return a JSON object. Include a 'title', a 'logline', and a 'description'(around 200-300 words):

            Example:
            {{
                "title": "My Book Title",
                "logline": "A one-sentence summary of my book.",
                "description": "A more detailed description of my book (200-300 words)."
            }}
            """
            concept_details = self.openai_client.generate_content(prompt)

            # Use the helper function to extract JSON
            concept_json = extract_json_from_markdown(concept_details)
            if concept_json:
                project_data['title'] = concept_json.get('title', 'Untitled')
                project_data['logline'] = concept_json.get('logline', 'No logline provided.')
                project_data['description'] = concept_json.get('description', 'No description provided.')
            else:
                # Keep original project_data if parsing fails
                self.logger.error(f"Concept generator returned invalid JSON: {concept_details}")
                print("ERROR: Invalid concept data received.")


            self.logger.info(f"Concept generated: Title: {project_data.get('title')}, Logline: {project_data.get('logline')}")
            return project_data

        except Exception as e:
            self.logger.exception(f"Error generating concept: {e}")
            print(f"ERROR: Failed to generate concept. See log for details.")
            return project_data