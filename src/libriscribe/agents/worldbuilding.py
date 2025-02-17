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

from libriscribe.knowledge_base import ProjectKnowledgeBase, Worldbuilding
from rich.console import Console
console = Console()

logger = logging.getLogger(__name__)

class WorldbuildingAgent(Agent):
    """Generates worldbuilding details."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("WorldbuildingAgent", llm_client)

    def execute(self, project_knowledge_base: ProjectKnowledgeBase, output_path: Optional[str] = None) -> None:
        try:
            aspects = prompts.WORLDBUILDING_ASPECTS.get(project_knowledge_base.category, "")
            console.print(f"{self.name} is: Generating Worldbuilding...")
            prompt = prompts.WORLDBUILDING_PROMPT.format(worldbuilding_aspects=aspects, **project_knowledge_base.model_dump())

            worldbuilding_json_str = self.llm_client.generate_content_with_json_repair(prompt, max_tokens=4000)
            if not worldbuilding_json_str:
                print("ERROR: Worldbuilding generation failed.")
                return

            worldbuilding_data = extract_json_from_markdown(worldbuilding_json_str)
            if worldbuilding_data is None:
                print("ERROR: Invalid worldbuilding data received.")
                return

            if not isinstance(worldbuilding_data, dict):
                self.logger.warning("Worldbuilding data is not a dictionary.")
                worldbuilding_data = {}
           # Ensure that all Worldbuilding fields are strings
            for key, value in worldbuilding_data.items():
                if not isinstance(value, str):
                    worldbuilding_data[key] = json.dumps(value)  # Convert to string

            # Update knowledge base and log only key aspects
            project_knowledge_base.worldbuilding = Worldbuilding(**worldbuilding_data)
            # Log only the main sections that were generated
            console.print("Generated worldbuilding elements:")
            for key in worldbuilding_data.keys():
                if worldbuilding_data[key]:  # Only show non-empty sections
                    console.print(f"- {key.replace('_', ' ').title()}")

            if output_path is None:
                output_path = str(Path(project_knowledge_base.project_name).parent / "world.json")  # Corrected path
            write_json_file(output_path, worldbuilding_data)
            console.print(f"Worldbuilding details saved to: {output_path}")

        except Exception as e:
            self.logger.exception(f"Error generating worldbuilding details: {e}")
            print(f"ERROR: Failed to generate worldbuilding details. See log.")