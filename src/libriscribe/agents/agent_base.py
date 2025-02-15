# src/libriscribe/agents/agent_base.py
# Abstract base class for agents
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.openai_client import OpenAIClient
from libriscribe.utils import prompts_context as prompts

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