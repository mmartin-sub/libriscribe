# src/libriscribe2/agents/character_generator.py

import logging
from typing import Any

from ..knowledge_base import Character, ProjectKnowledgeBase
from ..settings import Settings
from ..utils import prompts_context as prompts
from ..utils.file_utils import write_json_file
from ..utils.json_utils import JSONProcessor
from ..utils.llm_client import LLMClient
from .agent_base import Agent

logger = logging.getLogger(__name__)


class CharacterGeneratorAgent(Agent):
    """Generates character profiles."""

    def __init__(self, llm_client: LLMClient, settings: Settings):
        super().__init__("CharacterGeneratorAgent", llm_client)
        self.settings = settings

    async def execute(
        self,
        project_knowledge_base: ProjectKnowledgeBase,
        output_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        try:
            self.log_info("Creating character profiles...")

            prompt = prompts.CHARACTER_PROMPT.format(
                title=project_knowledge_base.title,
                genre=project_knowledge_base.genre,
                category=project_knowledge_base.category,
                language=project_knowledge_base.language,
                description=project_knowledge_base.description,
                num_characters=project_knowledge_base.num_characters,
            )

            # Use the safe method from base class
            character_response = await self.safe_generate_content(
                prompt, prompt_type="character", temperature=self.settings.default_temperature
            )

            if not character_response:
                self.log_error("Character generation failed")
                return

            # Always dump the raw response to a file for debugging
            self._dump_raw_response(character_response, output_path, "character")

            # Use the safe JSON extraction from base class
            characters_data = self.safe_extract_json_list(character_response, "character response")
            if not characters_data:
                error_msg = "Failed to parse character data - JSON decode error"
                self.log_error(error_msg)
                # Log the raw response for debugging
                self.log_debug(f"Raw character response: {character_response[:500]}...")
                # Don't raise exception, just return gracefully
                return

            # Process and store characters in knowledge base
            processed_characters = []
            for char_data in characters_data:
                try:
                    # Use JSONProcessor for consistent data handling
                    normalized_data = JSONProcessor.normalize_dict_keys(char_data)

                    # Handle relationships with JSONProcessor
                    relationships_raw = JSONProcessor.extract_string_from_json(normalized_data, "relationships", "")

                    # Convert relationships to proper format
                    relationships = {}
                    if relationships_raw:
                        relationships = {"general": relationships_raw}

                    # Create character with cleaned data
                    character = Character(
                        name=JSONProcessor.extract_string_from_json(normalized_data, "name", "Unknown"),
                        age=JSONProcessor.extract_string_from_json(normalized_data, "age", ""),
                        physical_description=JSONProcessor.extract_string_from_json(
                            normalized_data, "physical_description", ""
                        ),
                        personality_traits=JSONProcessor.extract_string_from_json(
                            normalized_data, "personality_traits", ""
                        ),
                        background=JSONProcessor.extract_string_from_json(normalized_data, "background", ""),
                        motivations=JSONProcessor.extract_string_from_json(normalized_data, "motivations", ""),
                        relationships=relationships,
                        role=JSONProcessor.extract_string_from_json(normalized_data, "role", ""),
                        internal_conflicts=JSONProcessor.extract_string_from_json(
                            normalized_data, "internal_conflicts", ""
                        ),
                        external_conflicts=JSONProcessor.extract_string_from_json(
                            normalized_data, "external_conflicts", ""
                        ),
                        character_arc=JSONProcessor.extract_string_from_json(normalized_data, "character_arc", ""),
                    )

                    project_knowledge_base.add_character(character)
                    processed_characters.append(character)

                except Exception as e:
                    self.log_warning(f"Error processing character data: {e}")
                    continue

            if processed_characters:
                self.log_success(f"Created {len(processed_characters)} character profiles")

                # Save to file if output path provided
                if output_path:
                    try:
                        characters_dict = {char.name: char.model_dump() for char in processed_characters}
                        write_json_file(output_path, characters_dict)
                        self.log_success("Character profiles saved!")
                    except Exception as e:
                        self.log_error(f"Failed to save character profiles: {e}")
            else:
                error_msg = "No characters were successfully processed - all character data was invalid"
                self.log_error(error_msg)
                # Don't raise exception, just return gracefully
                return

        except Exception:
            # Log the error once with full traceback for debugging
            logger.exception("Error during character generation")
            # Re-raise the original exception to preserve the error chain
            raise
