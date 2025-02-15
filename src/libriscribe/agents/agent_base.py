# src/libriscribe/agents/agent_base.py

import logging
from typing import Any

from libriscribe.utils.openai_client import OpenAIClient

logger = logging.getLogger(__name__)

class Agent:
    """Base class for all agents."""

    def __init__(self, name: str):
        self.name = name
        self.openai_client = OpenAIClient()
        self.logger = logging.getLogger(self.name)

    def execute(self, *args, **kwargs) -> Any:
        """Executes the agent's main task. Must be implemented by subclasses."""
        raise NotImplementedError