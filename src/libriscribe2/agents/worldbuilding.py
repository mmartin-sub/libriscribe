# src/libriscribe2/agents/worldbuilding.py

import logging
from typing import Any

from ..knowledge_base import ProjectKnowledgeBase, Worldbuilding
from ..settings import Settings
from ..utils import prompts_context as prompts
from ..utils.file_utils import write_json_file
from ..utils.json_utils import JSONProcessor
from ..utils.llm_client import LLMClient
from ..utils.prompts_context import get_worldbuilding_aspects
from .agent_base import Agent

logger = logging.getLogger(__name__)


class WorldbuildingAgent(Agent):
    """Generates worldbuilding details."""

    def __init__(self, llm_client: LLMClient, settings: Settings):
        super().__init__("WorldbuildingAgent", llm_client)
        self.settings = settings

    async def execute(
        self,
        project_knowledge_base: ProjectKnowledgeBase,
        output_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        try:
            # Check if worldbuilding is needed
            if not project_knowledge_base.worldbuilding_needed:
                self.log_warning("Worldbuilding not needed for this project. Skipping.")
                return

            # If worldbuilding is needed but the worldbuilding object doesn't exist, create it
            if project_knowledge_base.worldbuilding is None:
                project_knowledge_base.worldbuilding = Worldbuilding()

            aspects = get_worldbuilding_aspects(project_knowledge_base.category)
            self.log_info("Creating world details...")

            prompt = prompts.WORLDBUILDING_PROMPT.format(
                worldbuilding_aspects=aspects,
                title=project_knowledge_base.title,
                genre=project_knowledge_base.genre,
                category=project_knowledge_base.category,
                language=project_knowledge_base.language,
                description=project_knowledge_base.description,
            )

            worldbuilding_response = await self.safe_generate_content(
                prompt, prompt_type="worldbuilding", temperature=self.settings.default_temperature
            )

            if not worldbuilding_response:
                self.log_error("Worldbuilding generation failed.")
                return

            # Dump raw response for debugging
            self._dump_raw_response(worldbuilding_response, output_path, "worldbuilding")

            worldbuilding_data = self.safe_extract_json(worldbuilding_response, "worldbuilding response")
            if not worldbuilding_data:
                self.log_error("Invalid worldbuilding data received (could not extract JSON).")
                return

            # Process and flatten the worldbuilding data
            processed_data = self._process_worldbuilding_data(worldbuilding_data, project_knowledge_base.category)

            # Update the worldbuilding object
            self._update_worldbuilding(project_knowledge_base.worldbuilding, processed_data)

            # Save to file if output path provided
            if output_path:
                try:
                    write_json_file(output_path, processed_data)
                    self.log_success("Worldbuilding data saved!")
                except Exception as e:
                    self.log_error(f"Failed to save worldbuilding data: {e}")

            self.log_success("Worldbuilding details generated successfully!")

        except Exception:
            # Log the error once with full traceback for debugging
            logger.exception("Error during worldbuilding generation")
            # Re-raise the original exception to preserve the error chain
            raise

    def _process_worldbuilding_data(self, worldbuilding_data: dict[str, Any], category: str) -> dict[str, Any]:
        """Process and flatten worldbuilding data."""
        # Use JSONProcessor for consistent data handling
        flattened_data = JSONProcessor.flatten_nested_dict(worldbuilding_data)

        # Normalize keys to lowercase
        normalized_data = JSONProcessor.normalize_dict_keys(flattened_data)

        # Clean the data
        cleaned_data = JSONProcessor.clean_json_data(normalized_data)

        return cleaned_data

    def _update_worldbuilding(self, worldbuilding: Worldbuilding, data: dict[str, Any]) -> None:
        """Update the worldbuilding object with processed data."""
        # Map common worldbuilding fields
        field_mapping = {
            "geography": "geography",
            "climate": "climate",
            "culture": "culture",
            "history": "history",
            "politics": "politics",
            "economy": "economy",
            "technology": "technology",
            "magic_system": "magic_system",
            "religion": "religion",
            "social_structure": "social_structure",
            "conflicts": "conflicts",
            "traditions": "traditions",
            "languages": "languages",
            "architecture": "architecture",
            "transportation": "transportation",
            "food": "food",
            "clothing": "clothing",
            "art": "art",
            "music": "music",
            "education": "education",
            "government": "government",
            "military": "military",
            "trade": "trade",
            "resources": "resources",
            "environment": "environment",
            "wildlife": "wildlife",
            "settlements": "settlements",
            "landmarks": "landmarks",
            "legends": "legends",
            "customs": "customs",
        }

        # Update worldbuilding object with available data
        for data_key, worldbuilding_field in field_mapping.items():
            value = JSONProcessor.extract_string_from_json(data, data_key, "")
            if value and hasattr(worldbuilding, worldbuilding_field):
                setattr(worldbuilding, worldbuilding_field, value)
