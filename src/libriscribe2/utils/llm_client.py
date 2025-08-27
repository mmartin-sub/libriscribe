# src/libriscribe2/utils/llm_client.py
"""
LLM Client

This module provides a client for interacting with Large Language Models.
"""

import asyncio
import json
import logging
import os
import re
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, TypeVar

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from ..settings import Settings
from .llm_client_protocol import LLMClientProtocol
from .mock_llm_client import MockLLMClient

T = TypeVar("T")

# Python 3.12: Type parameter syntax (using compatible syntax for mypy)
# type ModelType = str
# type PromptType = str
# type ResponseType = str | dict[str, Any]


# Use traditional type aliases for better mypy compatibility
ModelType = str
PromptType = str
ResponseType = str | dict[str, Any]


# Python 3.12: Better error messages and debugging
class LLMClientError(Exception):
    """Exception for LLM client errors with improved error messages."""

    def __init__(self, message: str, provider: str, context: dict[str, Any] | None = None) -> None:
        self.provider = provider
        self.context = context or {}
        # Python 3.12: Better error message formatting
        super().__init__(f"LLM Client ({provider}) error: {message}")


class LLMClient(LLMClientProtocol):
    """LLM Client using Python 3.12 features."""

    def __init__(
        self,
        provider: str,
        settings: Settings,
        model_config: dict[str, str] | None = None,
        timeout: float | None = None,
        environment: str | None = None,
        project_name: str = "",
        user: str | None = None,
    ):
        self.provider = provider
        self.settings = settings
        self.model_config = model_config or self.settings.default_model_config
        self.timeout = timeout if timeout is not None else self.settings.default_timeout
        self.environment = environment or self.settings.default_environment
        self.project_name = project_name
        self.user = user
        self.logger = logging.getLogger(f"LLMClient({provider})")
        self._logged_url: str | None = None  # Track logged URL to avoid repetition
        self._logged_headers_info: bool = False  # Track if headers were logged at INFO level

        # Python 3.12: Better configuration validation
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        """Validate client configuration using Python 3.12 features."""
        if not self.provider:
            raise ValueError("Provider cannot be empty")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

        # Model configuration validation is handled by the provider-specific implementations
        # The model_config contains model names for different prompt types, not API keys

    def get_model_for_prompt_type(self, prompt_type: str) -> str:
        """Gets the specific model for a given prompt type, falling back to default."""
        return self.model_config.get(prompt_type, self.model_config.get("default", self.settings.fallback_model))

    # Python 3.12: Improved async method signatures
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
        """Generate content with improved error handling and timeout."""
        try:
            self.logger.debug(f"Starting content generation with timeout: {self.timeout} seconds")

            async def _consume_stream() -> str:
                chunks = [
                    chunk
                    async for chunk in self.generate_streaming_content(
                        prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        prompt_type=prompt_type,
                        language=language,
                        **kwargs,
                    )
                ]
                return "".join(chunks)

            return await asyncio.wait_for(_consume_stream(), timeout=self.timeout)
        except TimeoutError:
            self.logger.error(f"Content generation timed out after {self.timeout} seconds")
            raise LLMClientError(f"Generation timed out after {self.timeout} seconds", self.provider)
        except Exception as e:
            # Don't log here - let the calling code handle logging
            raise LLMClientError(f"Content generation failed: {e}", self.provider)

    # Python 3.12: Better async iteration support
    async def generate_streaming_content(
        self,
        prompt: str,
        prompt_type: str = "default",
        temperature: float | None = None,
        max_tokens: int | None = None,
        language: str | None = None,
        timeout: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Generate streaming content with improved async iteration."""
        try:
            model_to_use = self.get_model_for_prompt_type(prompt_type)
            self.logger.debug(f"Using model '{model_to_use}' for prompt_type '{prompt_type}'")

            if self.provider == "openai":
                async for chunk in self._generate_openai_streaming(
                    prompt,
                    temperature or self.settings.default_temperature,
                    max_tokens,
                    model=model_to_use,
                    **kwargs,
                ):
                    yield chunk
            elif self.provider == "mock":
                async for chunk in self._generate_mock_streaming(
                    prompt,
                    temperature or self.settings.default_temperature,
                    prompt_type=prompt_type,
                    language=language,
                    **kwargs,
                ):
                    yield chunk
            else:
                raise LLMClientError(f"Unsupported provider for streaming: {self.provider}", self.provider)
        except Exception as e:
            self.logger.error(f"Streaming content generation failed: {e}")
            raise LLMClientError(f"Streaming generation failed: {e}", self.provider)

    # Python 3.12: Improved async context manager
    @asynccontextmanager
    async def client_session(self) -> AsyncIterator["LLMClient"]:
        """Async context manager for LLM client sessions."""
        try:
            self.logger.info("Starting LLM client session")
            yield self
        except Exception as e:
            self.logger.error(f"LLM client session failed: {e}")
            raise
        finally:
            self.logger.info("LLM client session completed")

    # Python 3.12: Better performance monitoring
    async def generate_content_with_timing(self, prompt: str, **kwargs: Any) -> tuple[str, float]:
        """Generate content with timing information."""

        start_time = time.time()
        try:
            result = await self.generate_content(prompt, **kwargs)
            duration = time.time() - start_time
            self.logger.info(f"Content generation completed in {duration:.2f} seconds")
            return result, duration
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Content generation failed after {duration:.2f} seconds: {e}")
            raise

    # Python 3.12: Improved error handling with fallback
    async def generate_content_with_fallback(
        self, primary_prompt: str, fallback_prompt: str | None = None, **kwargs: Any
    ) -> str:
        """Generate content with fallback support."""

        try:
            return await self.generate_content(primary_prompt, **kwargs)
        except Exception as e:
            self.logger.warning(f"Primary generation failed: {e}")

            if fallback_prompt:
                try:
                    self.logger.info("Attempting fallback generation")
                    return await self.generate_content(fallback_prompt, **kwargs)
                except Exception as fallback_error:
                    # Python 3.12: Better exception chaining
                    raise LLMClientError(
                        f"Both primary and fallback generation failed: {e} -> {fallback_error}",
                        self.provider,
                        {"primary_error": str(e), "fallback_error": str(fallback_error)},
                    ) from e

            # Re-raise the original exception if no fallback
            raise

    # Python 3.12: Better configuration management
    def get_client_config(self) -> dict[str, Any]:
        """Get client configuration using Python 3.12 features."""
        return {
            "provider": self.provider,
            "timeout": self.timeout,
            "environment": self.environment,
            "project_name": self.project_name,
            "user": self.user,
            "model_config": self.model_config,
            "capabilities": ["content_generation", "streaming_generation"],
            "version": self.settings.client_version,
        }

    # Python 3.12: Improved validation methods
    def validate_prompt(self, prompt: Any) -> bool:
        """Validate prompt using Python 3.12 features."""

        if not isinstance(prompt, str):
            return False

        if not prompt.strip():
            return False

        # Python 3.12: Better string handling
        if len(prompt) > self.settings.default_max_tokens:  # Reasonable limit
            return False

        return True

    # Python 3.12: Better async resource management
    async def __aenter__(self) -> "LLMClient":
        """Async context manager entry."""
        await self.initialize_session()
        return self

    async def __aexit__(self, exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.cleanup_session()

    async def initialize_session(self) -> None:
        """Initialize client session."""
        self.logger.info("Initializing LLM client session")

    async def cleanup_session(self) -> None:
        """Cleanup client session."""
        self.logger.info("Cleaning up LLM client session")

    def _analyze_content_filtering_triggers(self, prompt: Any) -> list[str]:
        """Analyze prompt for potential content filtering triggers."""
        if not isinstance(prompt, str):
            return []

        triggers = []

        # Check for potentially sensitive content patterns
        sensitive_patterns = [
            (r"\\u[0-9a-fA-F]{4}", "Unicode escape sequences"),
            (r"[<>]", "HTML-like tags"),
            (r"javascript:", "JavaScript injection"),
            (r"data:", "Data URI injection"),
            (r"http[s]?://", "URLs"),
            (r"@\w+", "Email-like patterns"),
            (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "IP addresses"),
            (r"\b\d{4}-\d{2}-\d{2}\b", "Date patterns"),
            (r"\b\d{10,}\b", "Long numeric sequences"),
            (r"[^\x00-\x7F]", "Non-ASCII characters"),
        ]

        for pattern, description in sensitive_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                triggers.append(description)

        # Check for very long prompts
        if len(prompt) > 4000:
            triggers.append("Very long prompt")

        # Check for repeated patterns
        if prompt.count("\\") > 10:
            triggers.append("Many escape sequences")

        # Check for suspicious language combinations
        if "\\u00e9" in prompt or "\\u00e8" in prompt or "\\u0153" in prompt:
            triggers.append("French Unicode characters")

        return triggers

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

        temp = temperature or self.settings.default_temperature

        for attempt in range(max_retries + 1):
            try:
                if attempt == 0:
                    # Try with primary prompt
                    result = await self.generate_content(primary_prompt, prompt_type, temp, **kwargs)
                else:
                    # Try with fallback prompt
                    if fallback_prompt:
                        self.logger.info(f"Retry {attempt}: Using fallback prompt for {prompt_type}")
                        result = await self.generate_content(fallback_prompt, prompt_type, temp, **kwargs)
                    else:
                        # Generate a simplified fallback prompt
                        simplified_prompt = self._create_simplified_prompt(primary_prompt, prompt_type)
                        self.logger.info(f"Retry {attempt}: Using auto-generated simplified prompt for {prompt_type}")
                        result = await self.generate_content(simplified_prompt, prompt_type, temp, **kwargs)

                if result:
                    return result

            except Exception as e:
                if "content filtering" in str(e).lower() or "null content" in str(e).lower():
                    self.logger.warning(f"Content filtering detected on attempt {attempt + 1}: {e}")
                    if attempt < max_retries:
                        continue
                    else:
                        self.logger.error(f"All attempts failed due to content filtering for {prompt_type}")
                        return None
                else:
                    # Re-raise non-content-filtering errors
                    raise

        return None

    def _create_simplified_prompt(self, original_prompt: str, prompt_type: str) -> str:
        """Create a simplified version of the prompt to avoid content filtering."""
        if prompt_type == "critique":
            # Extract just the essential information for critique
            if "```json" in original_prompt:
                # Try to extract just the title and logline
                json_start = original_prompt.find("```json") + 7
                json_end = original_prompt.find("```", json_start)
                if json_start != -1 and json_end != -1:
                    json_content = original_prompt[json_start:json_end].strip()
                    try:
                        import json

                        data = json.loads(json_content)
                        title = data.get("title", "Unknown Title")
                        logline = data.get("logline", "Unknown Summary")
                        return f"""Review this book concept:

Title: {title}
Summary: {logline}

Provide a brief evaluation focusing on:
- Main strengths
- Areas for improvement
- Overall potential

Write directly without introductions."""
                    except (json.JSONDecodeError, KeyError, TypeError):
                        pass

            # Fallback to very simple prompt
            return "Review this book concept and provide brief feedback on strengths and areas for improvement."

        elif prompt_type == "concept":
            # Simplify concept generation
            return "Create a simple book concept with title, logline, and brief description."

        elif prompt_type == "refine":
            # Simplify refinement
            return "Improve this book concept based on the feedback provided."

        else:
            # Generic simplification
            return original_prompt[:500] + "..." if len(original_prompt) > 500 else original_prompt

    async def _generate_openai_streaming(
        self, prompt: str, temperature: float, max_tokens: int | None, model: str | None = None, **kwargs: Any
    ) -> AsyncIterator[str]:
        """Generate streaming content using OpenAI."""
        model = model or self.settings.openai_default_model_name
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMClientError("OpenAI API key not found.", "openai", {"missing_api_key": True})

        base_url = os.getenv("OPENAI_BASE_URL", self.settings.openai_base_url_default)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        try:
            async with ClientSession() as session:
                async with session.post(
                    f"{base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise LLMClientError(
                            f"OpenAI API request failed with status {response.status}: {error_text}",
                            "openai",
                            {"status_code": response.status, "error": error_text},
                        )

                    async for line in response.content:
                        line = line.strip()
                        if not line:
                            continue

                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data:"):
                            data_str = decoded_line[len("data: ") :].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if data.get("choices"):
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                self.logger.warning(f"Failed to decode JSON stream data: {data_str}")
                                continue
        except aiohttp.ClientError as e:
            raise LLMClientError(f"Network error connecting to OpenAI API: {e}", "openai", {"network_error": str(e)})

    async def _generate_mock_streaming(self, prompt: str, temperature: float, **kwargs: Any) -> AsyncIterator[str]:
        """Generate mock streaming content for testing."""
        mock_client = MockLLMClient(
            model_config=self.model_config,
            project_name=self.project_name,
            user=self.user,
            settings=self.settings,
        )
        async for chunk in mock_client.generate_streaming_content(prompt, temperature=temperature, **kwargs):
            yield chunk
