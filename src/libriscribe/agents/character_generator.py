# src/libriscribe/agents/character_generator.py
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.openai_client import OpenAIClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import write_json_file
from libriscribe.utils.file_utils import extract_json_from_markdown

logger = logging.getLogger(__name__)

class CharacterGeneratorAgent(Agent):
    """Generates character profiles."""

    def __init__(self):
        super().__init__("CharacterGeneratorAgent")

    def execute(self, project_data: Dict[str, Any], output_path: str) -> None:
        """Generates character profiles, handling Markdown-wrapped JSON."""
        try:
            prompt = prompts.CHARACTER_PROMPT.format(**project_data)
            character_json_str = self.openai_client.generate_content(prompt, max_tokens=4000)

            characters = extract_json_from_markdown(character_json_str)
            if characters is None:  # Parsing failed
                print("ERROR: Invalid character data received. Cannot save.")
                return

            if not isinstance(characters, list):
                self.logger.warning("Character data is not a list.")
                characters = []

            write_json_file(output_path, characters)

        except Exception as e:
            self.logger.exception(f"Error generating character profiles: {e}")
            print(f"ERROR: Failed to generate character profiles. See log.")