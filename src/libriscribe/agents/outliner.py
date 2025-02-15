# src/libriscribe/agents/outliner.py

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.openai_client import OpenAIClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent

logger = logging.getLogger(__name__)


class OutlinerAgent(Agent):
    """Generates book outlines."""

    def __init__(self):
        super().__init__("OutlinerAgent")

    def execute(self, project_data: Dict[str, Any], output_path: str) -> None:
        """Generates an outline and saves it to a file.

        Args:
            project_data:  A dictionary containing project information (title, genre, description, etc.).
            output_path: The path to the output file (e.g., "projects/my_book/outline.md").
        """
        try:
            prompt = prompts.OUTLINE_PROMPT.format(**project_data) # Use a prompt template
            outline_content = self.openai_client.generate_content(prompt, max_tokens=3000)

            # Ensure the output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(outline_content)

            self.logger.info(f"Outline generated and saved to {output_path}")

        except Exception as e:
            self.logger.exception(f"Error generating outline: {e}")
            #In a CLI environment, you might also want to print an error message to the console
            print(f"ERROR: Failed to generate outline. See log for details.")