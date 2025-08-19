# src/libriscribe2/utils/llm_client.py
"""
LLM Client

This module provides a client for interacting with Large Language Models.
"""

import asyncio
import logging
import os
import re
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Protocol, TypeVar

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from ..settings import Settings

T = TypeVar("T")

# Python 3.12: Type parameter syntax (using compatible syntax for mypy)
# type ModelType = str
# type PromptType = str
# type ResponseType = str | dict[str, Any]

# Use traditional type aliases for better mypy compatibility
ModelType = str
PromptType = str
ResponseType = str | dict[str, Any]


# Python 3.12: Improved Protocol syntax
class LLMProviderProtocol(Protocol):
    """Protocol for LLM providers using Python 3.12 features."""

    async def generate_content(self, prompt: str, **kwargs: Any) -> str:
        """Generate content from a prompt."""
        ...

    async def generate_streaming_content(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Generate streaming content from a prompt."""
        ...


# Python 3.12: Better error messages and debugging
class LLMClientError(Exception):
    """Exception for LLM client errors with improved error messages."""

    def __init__(self, message: str, provider: str, context: dict[str, Any] | None = None) -> None:
        self.provider = provider
        self.context = context or {}
        # Python 3.12: Better error message formatting
        super().__init__(f"LLM Client ({provider}) error: {message}")


class LLMClient:
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
        prompt_type: str = "general",
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate content with improved error handling and timeout."""

        async def _generate() -> str:
            try:
                # Get the appropriate model for this prompt type
                model_to_use = self.model_config.get(
                    prompt_type, self.model_config.get("default", self.settings.fallback_model)
                )
                self.logger.debug(f"Using model '{model_to_use}' for prompt_type '{prompt_type}'")

                # Python 3.12: Better async support
                if self.provider == "openai":
                    return await self._generate_openai_content(
                        prompt,
                        temperature or self.settings.default_temperature,
                        max_tokens,
                        model=model_to_use,
                        **kwargs,
                    )

                elif self.provider == "mock":
                    return await self._generate_mock_content(
                        prompt, temperature or self.settings.default_temperature, prompt_type=prompt_type, **kwargs
                    )
                else:
                    raise LLMClientError(f"Unsupported provider: {self.provider}", self.provider)

            except Exception as e:
                # Don't log here - let the calling code handle logging
                raise LLMClientError(f"Content generation failed: {e}", self.provider) from e

        try:
            self.logger.debug(f"Starting content generation with timeout: {self.timeout} seconds")
            return await asyncio.wait_for(_generate(), timeout=self.timeout)
        except TimeoutError:
            self.logger.error(f"Content generation timed out after {self.timeout} seconds")
            raise LLMClientError(f"Generation timed out after {self.timeout} seconds", self.provider)

    # Python 3.12: Better async iteration support
    async def generate_streaming_content(
        self, prompt: str, temperature: float | None = None, max_tokens: int | None = None, **kwargs: Any
    ) -> AsyncIterator[str]:
        """Generate streaming content with improved async iteration."""

        try:
            if self.provider == "openai":
                async for chunk in self._generate_openai_streaming(
                    prompt, temperature or self.settings.default_temperature, max_tokens, **kwargs
                ):
                    yield chunk
            elif self.provider == "mock":
                async for chunk in self._generate_mock_streaming(
                    prompt, temperature or self.settings.default_temperature, **kwargs
                ):
                    yield chunk
            else:
                raise LLMClientError(f"Unsupported provider for streaming: {self.provider}", self.provider)

        except Exception as e:
            self.logger.error(f"Streaming content generation failed: {e}")
            raise LLMClientError(f"Streaming generation failed: {e}", self.provider) from e

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

    async def _generate_openai_content(
        self, prompt: str, temperature: float, max_tokens: int | None, model: str | None = None, **kwargs: Any
    ) -> str:
        """Generate content using OpenAI."""
        model = model or self.settings.openai_default_model_name
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMClientError(
                "OpenAI API key not found. Please provide a configuration file with your API keys or use --mock for testing.",
                "openai",
                {"missing_api_key": True},
            )

        # Validate API key format
        if not api_key.startswith("sk-"):
            self.logger.warning(f"API key format may be invalid: {api_key[:10]}...")

        # Get base URL from environment (defaults to OpenAI's official API)
        base_url = os.getenv("OPENAI_BASE_URL", self.settings.openai_base_url_default)

        # Prepare the request payload
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "timeout": self.timeout,  # Pass timeout to LiteLLM server
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        # Prepare LiteLLM headers (use only x-litellm-tags)
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        # Build x-litellm-tags: sanitized user + date (YYYY-MM-DD)
        from . import project_state
        from .timestamp_utils import get_utc_date_str

        # Prefer global project initial date if set, else today's UTC date
        initial_date = None
        try:
            initial_date = project_state.get_initial_date()
        except Exception:
            initial_date = None
        date_tag = initial_date if isinstance(initial_date, str) and initial_date else get_utc_date_str()

        user_tag = ""
        if isinstance(self.user, str) and self.user.strip():
            # sanitize: trim and remove commas to avoid breaking tag list
            user_tag = self.user.strip().replace(",", " ")

        tag_items: list[str] = []
        if user_tag:
            tag_items.append(user_tag)
        if date_tag:
            tag_items.append(date_tag)

        if self.settings.send_litellm_tags and tag_items:
            headers["x-litellm-tags"] = ",".join(tag_items)

        # Log LiteLLM metadata and timeout (with API key truncated)
        safe_headers = headers.copy()
        if "Authorization" in safe_headers:
            auth_value = safe_headers["Authorization"]
            if auth_value.startswith("Bearer "):
                api_key = auth_value[7:]  # Remove "Bearer " prefix
                truncated_key = api_key[:5] + "..." if len(api_key) > 5 else api_key
                safe_headers["Authorization"] = f"Bearer {truncated_key}"

        # Log headers at INFO level only once, then use DEBUG level
        if not self._logged_headers_info:
            self.logger.info(f"OpenAI headers: {safe_headers}")
            self._logged_headers_info = True
        else:
            self.logger.debug(f"OpenAI headers: {safe_headers}")

        self.logger.debug(f"Request timeout: {self.timeout} seconds")
        self.logger.debug(f"Request payload: {payload}")

        # Log URL only once or when it changes
        current_url = f"{base_url}/chat/completions"
        if self._logged_url != current_url:
            self.logger.info(f"Request URL: {current_url}")
            self._logged_url = current_url

        try:
            async with ClientSession() as session:
                async with session.post(
                    f"{base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status == 200:
                        data: dict[str, Any] = await response.json()
                        if "choices" not in data or not data["choices"]:
                            raise LLMClientError(
                                f"Invalid response format: no choices in response. Response: {data}",
                                "openai",
                                {"invalid_response": "no_choices", "response_data": str(data)[:500]},
                            )
                        choices = data["choices"]
                        if not isinstance(choices, list) or len(choices) == 0:
                            raise LLMClientError(
                                f"Invalid response format: choices is not a valid list. Response: {data}",
                                "openai",
                                {"invalid_response": "invalid_choices", "response_data": str(data)[:500]},
                            )
                        first_choice = choices[0]
                        if not isinstance(first_choice, dict) or "message" not in first_choice:
                            raise LLMClientError(
                                f"Invalid response format: first choice missing message. Response: {data}",
                                "openai",
                                {"invalid_response": "missing_message", "response_data": str(data)[:500]},
                            )
                        message = first_choice["message"]
                        if not isinstance(message, dict) or "content" not in message:
                            raise LLMClientError(
                                f"Invalid response format: message missing content. Response: {data}",
                                "openai",
                                {"invalid_response": "missing_content", "response_data": str(data)[:500]},
                            )
                        content = message["content"]
                        if content is None:
                            # Log the request prompt for debugging
                            messages = payload.get("messages", [])
                            request_prompt = ""
                            if messages and isinstance(messages, list) and len(messages) > 0:
                                first_message = messages[0]
                                if isinstance(first_message, dict):
                                    request_prompt = first_message.get("content", "")
                            from ..settings import Settings

                            settings = Settings()
                            prompt_preview = (
                                request_prompt[: settings.content_dump_threshold]
                                if isinstance(request_prompt, str)
                                else ""
                            )

                            # Enhanced error logging for content filtering issues
                            self.logger.error(f"API returned null content. Request prompt: {prompt_preview}")

                            # Check for potential content filtering triggers
                            content_filtering_indicators = self._analyze_content_filtering_triggers(request_prompt)
                            if content_filtering_indicators:
                                self.logger.warning(
                                    f"Potential content filtering triggers detected: {content_filtering_indicators}"
                                )

                            # Provide more specific error message
                            error_context = {
                                "invalid_response": "content_is_null",
                                "full_response": str(data)[:1000],
                                "content_filtering_indicators": content_filtering_indicators,
                                "prompt_length": len(request_prompt) if isinstance(request_prompt, str) else 0,
                            }

                            raise LLMClientError(
                                f"API returned null content. This may be due to content filtering or model issues. "
                                f"Response: {str(data)[:500]}",
                                "openai",
                                error_context,
                            )
                        if not isinstance(content, str):
                            raise LLMClientError(
                                f"Invalid response format: content is not a string. Content type: {type(content)}, Response: {str(data)[:500]}",
                                "openai",
                                {"invalid_response": "content_not_string", "content_type": str(type(content))},
                            )
                        return str(content)
                    else:
                        error_text = await response.text()
                        self.logger.error(f"API request failed with status {response.status}: {error_text[:200]}...")
                        # Check if it's a timeout error
                        if response.status == 408 or "timeout" in error_text.lower():
                            self.logger.error(f"Request timed out after {self.timeout} seconds")
                            raise LLMClientError(
                                f"Request timed out after {self.timeout} seconds. Server response: {error_text}",
                                "openai",
                                {"status_code": response.status, "error": error_text, "timeout": self.timeout},
                            )
                        else:
                            raise LLMClientError(
                                f"OpenAI API request failed with status {response.status}: {error_text}",
                                "openai",
                                {"status_code": response.status, "error": error_text},
                            )
        except aiohttp.ClientError as e:  # pyright: ignore[reportGeneralTypeIssues]
            raise LLMClientError(f"Network error connecting to OpenAI API: {e}", "openai", {"network_error": str(e)})
        except Exception as e:
            raise LLMClientError(f"Unexpected error in OpenAI API call: {e}", "openai", {"unexpected_error": str(e)})

    async def _generate_mock_content(self, prompt: str, temperature: float, **kwargs: Any) -> str:
        """Generate mock content for testing."""
        from .mock_llm_client import MockLLMClient

        # Create a mock client instance with LiteLLM metadata
        mock_client = MockLLMClient(
            model_config=self.model_config,
            project_name=self.project_name,
            user=self.user,
            settings=self.settings,
        )

        # Extract prompt_type from kwargs or use default
        prompt_type = kwargs.get("prompt_type", "general")

        # Extract language from prompt if available
        language = self.settings.default_language
        if "language" in prompt:
            # Try to extract language from prompt format like "language=French" or "The book is written in French"
            import re

            language_match = re.search(r"language[=:]\s*([A-Za-z]+)", prompt)
            if language_match:
                language = language_match.group(1)
            else:
                # Look for "written in {language}" pattern
                written_in_match = re.search(r"written in ([A-Za-z]+)", prompt)
                if written_in_match:
                    language = written_in_match.group(1)

        # Generate mock content using the MockLLMClient
        return mock_client.generate_content(prompt, prompt_type, temperature, language)

    async def _generate_openai_streaming(
        self, prompt: str, temperature: float, max_tokens: int | None, **kwargs: Any
    ) -> AsyncIterator[str]:
        """Generate streaming content using OpenAI."""
        # Implementation would go here
        words = f"OpenAI streaming response to: {prompt[:50]}...".split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.1)

    async def _generate_mock_streaming(self, prompt: str, temperature: float, **kwargs: Any) -> AsyncIterator[str]:
        """Generate mock streaming content for testing."""
        words = f"Mock streaming response to: {prompt[:50]}...".split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.1)
