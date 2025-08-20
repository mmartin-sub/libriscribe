# src/libriscribe2/agents/agent_base.py
"""
Agent Base Module

This module provides the base classes and interfaces for all LibriScribe agents.
It defines the common structure and behavior that all agents should implement.
"""

import logging
import re
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Protocol, TypeVar

import pyjson5 as json

from ..settings import Settings
from ..utils.llm_client import LLMClient
from ..utils.timestamp_utils import get_iso8601_utc_timestamp

T = TypeVar("T")

# Python 3.12: Type parameter syntax (using compatible syntax for mypy)
# type AgentResult = str | dict[str, Any] | None
# type AgentInput = str | dict[str, Any] | Path

# Use traditional type aliases for better mypy compatibility
AgentResult = str | dict[str, Any] | None
AgentInput = str | dict[str, Any] | Path | None


# Python 3.12: Improved Protocol syntax
class AgentProtocol(Protocol):
    """Protocol for agents using Python 3.12 features."""

    name: str

    async def execute(self, input_data: AgentInput, **kwargs: Any) -> AgentResult:
        """Execute the agent with input data."""
        ...

    def log_info(self, message: str) -> None:
        """Log info message."""
        ...

    def log_error(self, message: str) -> None:
        """Log error message."""
        ...


# Python 3.12: Better error messages and debugging
class AgentExecutionError(Exception):
    """Exception for agent execution errors with improved error messages."""

    def __init__(self, message: str, agent_name: str, context: dict[str, Any] | None = None) -> None:
        self.agent_name = agent_name
        self.context = context or {}
        # Python 3.12: Better error message formatting
        super().__init__(f"Agent '{agent_name}' execution error: {message}")


class Agent(ABC):
    """Base agent class using Python 3.12 features."""

    def __init__(self, name: str, llm_client: LLMClient, settings: Settings | None = None):
        self.name = name
        self.llm_client = llm_client
        self.settings = settings or Settings()
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    async def execute(self, project_knowledge_base: Any, output_path: str | None = None, **kwargs: Any) -> None:
        """Execute the agent's main functionality."""
        pass

    def log_info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(f"[{self.name}] {message}")

    def log_debug(self, message: str) -> None:
        """Log a debug message (only to file, not console)."""
        self.logger.debug(f"[{self.name}] {message}")

    def log_success(self, message: str) -> None:
        """Log a success message."""
        self.logger.info(f"[{self.name}] ✅ {message}")

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(f"[{self.name}] ⚠️ {message}")

    def _dump_raw_response(self, content: str, output_path: str | None, content_type: str) -> None:
        """Dump raw response content to a JSON file for debugging."""
        try:
            if not output_path:
                return

            # Create the output directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create the debug file path
            debug_file = output_dir / f"{content_type}.json"

            # Prepare the debug data
            debug_data = {
                "content_type": content_type,
                "agent_name": self.name,
                "timestamp": get_iso8601_utc_timestamp(),
                "content_length": len(content),
                "content_preview": content[:500] + "..." if len(content) > 500 else content,
            }
            if content_type not in ["concept", "concept_revised"]:
                debug_data["raw_content"] = content

            # Write the debug file
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(debug_data, indent=2, ensure_ascii=False))

            self.log_debug(f"Raw {content_type} response dumped to: {debug_file}")

        except Exception as e:
            self.log_warning(f"Failed to dump raw response: {e}")

    # Python 3.12: Improved async context manager
    @asynccontextmanager
    async def agent_context(self) -> AsyncIterator["Agent"]:
        """Async context manager for agent operations."""
        try:
            yield self
        except Exception as e:
            self.log_error(f"Error in agent context: {e}")
            raise

    async def safe_generate_content(
        self,
        prompt: str,
        prompt_type: str = "general",
        temperature: float | None = None,
        timeout: float | None = None,
    ) -> str | None:
        """Safely generate content with error handling."""
        try:
            settings = Settings()
            temp = temperature or settings.default_temperature

            async def _generate() -> str | None:
                return await self.llm_client.generate_content(prompt, prompt_type=prompt_type, temperature=temp)

            return await self.execute_with_fallback(_generate)
        except Exception as e:
            # Log detailed error to file only (DEBUG level)
            self.log_debug(f"Content generation failed: {e}")
            # Don't log ERROR level here since the calling code will handle it
            return None

    def safe_extract_json(
        self, content: str, content_type: str, output_path: str | None = None
    ) -> dict[str, Any] | None:
        """Safely extract JSON from content with error handling."""
        try:
            # Try to find JSON in the content
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without markdown formatting
                json_match = re.search(r"(\{.*\})", content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    self.log_debug(f"Could not find JSON in {content_type}")  # Log to file only
                    return None

            result = json.loads(json_str)
            if isinstance(result, dict):
                return dict[str, Any](result)
            else:
                self.log_debug(f"Expected dict from {content_type}, got {type(result)}")  # Log to file only
                return None
        except ValueError as e:
            self.log_error(f"Failed to parse {content_type} data - JSON decode error: {e}")
            if output_path:
                issue_path = Path(output_path).parent / f"{content_type}.json.issue"
                with open(issue_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.log_error(f"Problematic JSON content saved to: {issue_path.as_uri()}")
            return None
        except Exception as e:
            self.log_debug(f"Error extracting JSON from {content_type}: {e}")  # Log to file only
            return None

    def safe_extract_json_list(
        self, content: str, content_type: str, output_path: str | None = None
    ) -> list[Any] | None:
        """Safely extract JSON list from content with error handling."""
        try:
            # Try to find JSON array in the content
            json_match = re.search(r"```json\s*(\[.*?\])\s*```", content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON array without markdown formatting
                json_match = re.search(r"(\[.*\])", content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON object that might be wrapped in an array
                    json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
                    if json_match:
                        # Single object, wrap it in an array
                        json_str = f"[{json_match.group(1)}]"
                    else:
                        # Try to find single object without markdown
                        json_match = re.search(r"(\{.*\})", content, re.DOTALL)
                        if json_match:
                            # Single object, wrap it in an array
                            json_str = f"[{json_match.group(1)}]"
                        else:
                            self.log_debug(f"Could not find JSON array or object in {content_type}")  # Log to file only
                            return None

            result = json.loads(json_str)
            if isinstance(result, list):
                return list[Any](result)
            else:
                self.log_debug(f"Expected list from {content_type}, got {type(result)}")  # Log to file only
                return None
        except ValueError as e:
            self.log_error(f"Failed to parse {content_type} data - JSON decode error: {e}")
            if output_path:
                issue_path = Path(output_path).parent / f"{content_type}.json.issue"
                with open(issue_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.log_error(f"Problematic JSON content saved to: {issue_path.as_uri()}")
            return None
        except Exception as e:
            self.log_debug(f"Error extracting JSON list from {content_type}: {e}")  # Log to file only
            return None

    async def execute_with_fallback(
        self,
        primary_method: Callable[[], Awaitable[T]],
        fallback_method: Callable[[], Awaitable[T]] | None = None,
        error_context: str = "execution",
    ) -> T | None:
        """Execute with fallback method if primary fails."""
        try:
            return await primary_method()
        except Exception as e:
            if fallback_method:
                try:
                    return await fallback_method()
                except Exception as fallback_error:
                    error_msg = f"Both primary and fallback {error_context} failed: {e} -> {fallback_error}"
                    self.log_debug(error_msg)  # Log detailed error to file only
                    raise e
            else:
                raise e

    # Python 3.12: Improved validation methods
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate input data using Python 3.12 features."""

        if isinstance(input_data, str):
            return bool(input_data.strip())
        elif isinstance(input_data, dict):
            return bool(input_data)
        elif isinstance(input_data, Path):
            return input_data.exists()
        elif input_data is None:
            return False

        # For any other type, return True as a fallback
        return True

    # Python 3.12: Better async iteration support
    async def process_streaming_content(self, prompt: str, chunk_handler: Callable[[str], None] | None = None) -> str:
        """Process streaming content with chunk handling."""

        full_content = ""

        try:
            async for chunk in self.llm_client.generate_streaming_content(prompt):
                full_content += chunk
                if chunk_handler:
                    chunk_handler(chunk)

            return full_content

        except Exception as e:
            self.log_error(f"Streaming content generation failed: {e}")
            return full_content

    # Python 3.12: Improved performance monitoring
    async def execute_with_timing(
        self, method: Callable[[], Awaitable[T]], operation_name: str = "operation"
    ) -> tuple[T, float]:
        """Execute method with timing information."""

        start_time = time.perf_counter()
        try:
            result = await method()
            duration = time.perf_counter() - start_time
            self.log_info(f"{operation_name} completed in {duration:.2f} seconds")
            return result, duration
        except Exception as e:
            duration = time.perf_counter() - start_time
            self.log_error(f"{operation_name} failed after {duration:.2f} seconds: {e}")
            raise

    # Python 3.12: Better configuration management
    def get_agent_config(self) -> dict[str, Any]:
        """Get agent configuration using Python 3.12 features."""
        return {
            "name": self.name,
            "class": self.__class__.__name__,
            "llm_client": type(self.llm_client).__name__,
            "capabilities": getattr(self, "capabilities", []),
            "version": getattr(self, "version", self.settings.client_version),
        }

    # Python 3.12: Improved string formatting
    def format_status_message(self, status: str, details: dict[str, Any] | None = None) -> str:
        """Format status message using Python 3.12 string improvements."""
        base_message = f"Agent '{self.name}': {status}"

        if details:
            # Python 3.12: Better f-string support
            detail_str = ", ".join(f"{k}={v!r}" for k, v in details.items())
            return f"{base_message} ({detail_str})"

        return base_message

    # Python 3.12: Better async resource management
    async def __aenter__(self) -> "Agent":
        """Async context manager entry."""
        await self.initialize_session()
        return self

    async def __aexit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.cleanup_session()

    async def initialize_session(self) -> None:
        """Initialize agent session."""
        self.log_info("Initializing agent session")

    async def cleanup_session(self) -> None:
        """Cleanup agent session."""
        self.log_info("Cleaning up agent session")
