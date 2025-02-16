# src/libriscribe/agents/worldbuilding.py
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.llm_client import LLMClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import write_json_file, read_json_file, extract_json_from_markdown
#MODIFIED
from libriscribe.knowledge_base import ProjectKnowledgeBase, Worldbuilding


logger = logging.getLogger(__name__)

class WorldbuildingAgent(Agent):
    """Generates worldbuilding details."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("WorldbuildingAgent", llm_client)

    def execute(self, project_knowledge_base: ProjectKnowledgeBase, output_path: Optional[str] = None) -> None: # Use project data
        """Generates worldbuilding details and saves them to a JSON file."""
        try:
            # Select the appropriate aspects based on category
            aspects = prompts.WORLDBUILDING_ASPECTS.get(project_knowledge_base.category, "")
            prompt = prompts.WORLDBUILDING_PROMPT.format(worldbuilding_aspects=aspects, **project_knowledge_base.model_dump())

            worldbuilding_json_str = self.llm_client.generate_content_with_json_repair(prompt, max_tokens=4000) #Use json repair
            if not worldbuilding_json_str:
                print("ERROR: Worldbuilding generation failed. See Log")
                return


            # Attempt to parse the JSON, and handle potential errors gracefully
            worldbuilding_data = extract_json_from_markdown(worldbuilding_json_str)
            if worldbuilding_data is None:
                print("ERROR: Invalid worldbuilding data received. Cannot save.")
                return
            if not isinstance(worldbuilding_data, dict):
                    self.logger.warning("Returned worldbuilding data is not a dictionary.")
                    worldbuilding_data = {} # Use an empty dict
            else:
                #Update knowledge Base
                project_knowledge_base.worldbuilding = Worldbuilding(**worldbuilding_data)

            if output_path is None:
                output_path = str(Path(project_knowledge_base.project_name).parent / "world.json")
            write_json_file(output_path, worldbuilding_data) # Save data

        except Exception as e:
            self.logger.exception(f"Error generating worldbuilding details: {e}")
            print(f"ERROR: Failed to generate worldbuilding details. See log.")