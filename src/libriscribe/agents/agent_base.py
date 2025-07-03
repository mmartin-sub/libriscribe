# src/libriscribe/agents/agent_base.py
import logging
from typing import Any

from libriscribe.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

class Agent:
    """Base class for all agents."""

    def __init__(self, name: str, llm_client: LLMClient):  # Receive LLMClient
        self.name = name
        self.llm_client = llm_client  # Use the passed LLMClient
        self.logger = logging.getLogger(self.name)

    def execute(self, *args, **kwargs) -> Any:
        """Executes the agent's main task. Must be implemented by subclasses."""
        raise NotImplementedError

    def log_start(self, chapter_number=None, chapter_path=None, extra_info=None):
        msg = f"{self.__class__.__name__}: Working"
        if chapter_number is not None:
            msg += f" on chapter {chapter_number}"
        if chapter_path is not None:
            msg += f" ({chapter_path})"
        if extra_info:
            msg += f" | {extra_info}"
        self.logger.info(msg)