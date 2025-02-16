# src/libriscribe/agents/outliner.py

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.llm_client import LLMClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import read_markdown_file, write_markdown_file, extract_json_from_markdown  # Import
from libriscribe.project_data import ProjectData


logger = logging.getLogger(__name__)


class OutlinerAgent(Agent):
    """Generates book outlines."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("OutlinerAgent", llm_client)

    def execute(self, project_data: ProjectData, output_path: str) -> None:
        """Generates an outline using an iterative refinement process."""
        try:
            # --- Step 1: Initial Outline Generation ---
            initial_prompt = prompts.OUTLINE_PROMPT.format(**project_data.model_dump())  # Use model_dump
            initial_outline = self.llm_client.generate_content(initial_prompt, max_tokens=3000)
            if not initial_outline:
                logger.error("Initial outline generation failed.")
                return

            # --- Step 2: Critique the Outline ---
            critique_prompt = f"""Critique the following book outline:

            {initial_outline}

            Identify any weaknesses, areas for improvement, potential plot holes, or inconsistencies. Be specific.
            """
            critique = self.llm_client.generate_content(critique_prompt, max_tokens=1000)

            # --- Step 3: Refine the Outline ---
            refine_prompt = f"""Based on the following critique, refine the book outline. Address the identified weaknesses and improve the outline overall.

            Original Outline:
            {initial_outline}

            Critique:
            {critique}

            Return the REFINED outline in Markdown format.
            """
            refined_outline = self.llm_client.generate_content(refine_prompt, max_tokens=3000)
            if not refined_outline:
                logger.error("Refined outline generation failed.")
                return


            # Ensure the output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # --- Step 4: Save and Return ---
            write_markdown_file(output_path, refined_outline)  # Use write_markdown_file
            self.logger.info(f"Outline generated (refined) and saved to {output_path}")

        except Exception as e:
            self.logger.exception(f"Error generating outline: {e}")
            print(f"ERROR: Failed to generate outline. See log for details.")