# src/libriscribe/agents/worldbuilding.py

import json
import logging
from typing import Any, Optional
from pathlib import Path

from libriscribe.utils.llm_client import LLMClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import write_json_file, extract_json_from_markdown

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
            aspects = prompts.WORLDBUILDING_ASPECTS.get(project_knowledge_base.category.lower(), "")
            console.print(f"{self.name} is: Generating Worldbuilding...")
            prompt = prompts.WORLDBUILDING_PROMPT.format(
                worldbuilding_aspects=aspects,
                title=project_knowledge_base.title,
                genre=project_knowledge_base.genre,
                category=project_knowledge_base.category,
                description=project_knowledge_base.description
            )

            worldbuilding_json_str = self.llm_client.generate_content_with_json_repair(prompt, max_tokens=4000, temperature=0.7)
            if not worldbuilding_json_str:
                print("ERROR: Worldbuilding generation failed.")
                return

            try:
                worldbuilding_data = extract_json_from_markdown(worldbuilding_json_str)
                if worldbuilding_data is None:
                    print("ERROR: Invalid worldbuilding data received (could not extract JSON).")
                    return

                if not isinstance(worldbuilding_data, dict):
                    self.logger.warning("Worldbuilding data is not a dictionary.")
                    worldbuilding_data = {}


                # --- KEY FIX: Flatten Nested JSON and Normalize Keys ---
                flattened_data = {}
                for key, value in worldbuilding_data.items():
                    if isinstance(value, dict):
                        # Flatten the nested dictionary into a single string
                        flattened_value = ""
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, str):
                                flattened_value += f"{sub_value} "  # Only include the value
                            else:
                                flattened_value += f"{json.dumps(sub_value)} "
                        flattened_data[key] = flattened_value.strip()

                    elif isinstance(value, str):
                        flattened_data[key] = value
                    else:
                        flattened_data[key] = json.dumps(value)  # Handle other types

                 # Get the list of expected fields based on category.
                if project_knowledge_base.category.lower() == "fiction":
                    expected_fields = [
                        "geography", "culture_and_society", "history", "rules_and_laws",
                        "technology_level", "magic_system", "key_locations",
                        "important_organizations", "flora_and_fauna", "languages",
                        "religions_and_beliefs", "economy", "conflicts"
                    ]
                elif project_knowledge_base.category.lower() == "non-fiction":
                    expected_fields = [
                      "setting_context","key_figures","major_events","underlying_causes",
                      "consequences", "relevant_data", "different_perspectives",
                      "key_concepts"
                    ]
                elif project_knowledge_base.category.lower() == "business":
                    expected_fields = [
                        "industry_overview", "target_audience", "market_analysis",
                        "business_model", "marketing_and_sales_strategy", "operations",
                        "financial_projections", "management_team",
                        "legal_and_regulatory_environment", "risks_and_challenges",
                        "opportunities_for_growth"
                    ]

                elif project_knowledge_base.category.lower() == "research paper":
                    expected_fields = [
                        "introduction", "literature_review", "methodology", "results",
                        "discussion", "conclusion", "references", "appendices"
                    ]
                else:
                    expected_fields = []


                for key, value in flattened_data.items():
                    normalized_key = key.lower().replace(" ", "_")
                    if normalized_key in expected_fields:  # Check against expected
                        if hasattr(project_knowledge_base.worldbuilding, normalized_key) and isinstance(value, str) and value.strip():
                            setattr(project_knowledge_base.worldbuilding, normalized_key, value)
                        else:
                            logger.warning(f"Skipping invalid worldbuilding field: {key} (value: {value})")
                    else:
                        logger.debug(f"Ignoring unexpected field: {key}")  # Log unexpected

            except json.JSONDecodeError:
                print("ERROR: Invalid JSON data received from LLM after repair attempts.")
                return
            except Exception as e:
                print("Error:", e)
                return

            # Log all fields
            console.print("[green]Generated worldbuilding elements:[/green]")
            for key, value in project_knowledge_base.worldbuilding.model_dump().items():
                console.print(f"- [cyan]{key.replace('_', ' ').title()}:[/cyan] {value}")

            if output_path is None:
                output_path = str(Path(project_knowledge_base.project_dir) / "world.json")
            write_json_file(output_path, project_knowledge_base.worldbuilding.model_dump())  # Save as JSON
            console.print(f"Worldbuilding details saved to: {output_path}")

        except Exception as e:
            self.logger.exception(f"Error generating worldbuilding details: {e}")
            print(f"ERROR: Failed to generate worldbuilding details. See log.")