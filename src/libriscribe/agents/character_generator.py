# src/libriscribe/agents/character_generator.py
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.llm_client import LLMClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import write_json_file, read_json_file, extract_json_from_markdown # Modified import

from libriscribe.knowledge_base import ProjectKnowledgeBase, Character
from rich.console import Console
console = Console()

logger = logging.getLogger(__name__)

class CharacterGeneratorAgent(Agent):
    """Generates character profiles."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("CharacterGeneratorAgent", llm_client)

    def execute(self, project_knowledge_base: ProjectKnowledgeBase, output_path: Optional[str] = None) -> None:
        try:
            console.print(f"{self.name} is: Generating characters and their personalities...")
            prompt = prompts.CHARACTER_PROMPT.format(**project_knowledge_base.model_dump())
            character_json_str = self.llm_client.generate_content_with_json_repair(prompt, max_tokens=4000)

            if not character_json_str:
                print("ERROR: Character generation failed. See Log")
                return

            characters = extract_json_from_markdown(character_json_str)
            if characters is None:
                print("ERROR: Invalid character data received.")
                return

            if not isinstance(characters, list):
                self.logger.warning("Character data is not a list.")
                characters = []
            else:
                # Process and store characters in knowledge base
                processed_characters = []  # List to store processed characters
                for char_data in characters:
                    try:
                        # Convert keys to lowercase
                        char_data = {k.lower(): v for k, v in char_data.items()}
                         # Ensure 'age' is a string
                        char_data['age'] = str(char_data.get('age', ''))
                        character = Character(**char_data)
                        project_knowledge_base.add_character(character)
                        processed_characters.append(character.model_dump()) #Append to processed_characters
                        # Only log the character name and role
                        console.print(f"Generated character: {character.name} ({character.role})")
                    except Exception as e:
                        logger.warning(f"Skipping a character: {str(e)}")
                        continue

            if output_path is None:
                output_path = str(Path(project_knowledge_base.project_dir) / "characters.json")  # Corrected path
            write_json_file(output_path, processed_characters)  # Save processed characters
            console.print(f"Character profiles saved to: {output_path}")

        except Exception as e:
            self.logger.exception(f"Error generating character profiles: {e}")
            print(f"ERROR: Failed to generate character profiles. See log.")