# src/libriscribe2/utils/llm_client_protocol.py
"""
Protocol for LLM clients.
"""

from collections.abc import AsyncIterator
from typing import Any, Protocol


class LLMClientProtocol(Protocol):
    """
    Protocol for LLM clients, ensuring a consistent interface for real and mock implementations.
    """

    async def generate_content(
        self,
        prompt: str,
        prompt_type: str = "default",
        temperature: float | None = None,
        max_tokens: int | None = None,
        language: str | None = None,
        timeout: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate content from a prompt."""
        ...

    def generate_streaming_content(
        self,
        prompt: str,
        prompt_type: str = "default",
        temperature: float | None = None,
        max_tokens: int | None = None,
        language: str | None = None,
        timeout: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Generate streaming content from a prompt."""
        ...

    async def generate_content_with_content_filtering_fallback(
        self,
        primary_prompt: str,
        fallback_prompt: str | None = None,
        prompt_type: str = "general",
        temperature: float | None = None,
        max_retries: int = 2,
        **kwargs: Any,
    ) -> str | None:
        """Generate content with fallback for content filtering issues."""
        ...
