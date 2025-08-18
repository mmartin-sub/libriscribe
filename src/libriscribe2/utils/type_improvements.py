# src/libriscribe2/utils/type_improvements.py
"""
Python 3.12 type improvements for libriscribe2.

This module demonstrates the use of Python 3.12 features including:
- Type parameter syntax (PEP 695)
- Improved error messages
- Better typing support
- Performance improvements
"""

import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

# Python 3.12: Type parameter syntax (PEP 695)
# Before: TypeVar('T', bound=SomeClass)
# After: type T = TypeVar('T', bound=SomeClass)
# Using TypeAlias for mypy compatibility
from typing import Any, Protocol, TypeVar, cast

from ..settings import DEFAULT_TEMPERATURE, DEFAULT_TIMEOUT


# Define base classes for type bounds
class BaseAgent:
    """Base agent class for type bounds."""

    async def initialize_session(self) -> None:
        """Initialize agent session."""
        pass

    async def cleanup_session(self) -> None:
        """Cleanup agent session."""
        pass

    async def prepare(self) -> None:
        """Prepare agent for execution."""
        pass

    def is_available(self) -> bool:
        """Check if agent is available."""
        return True


class BaseConfig:
    """Base config class for type bounds."""

    pass


AgentType = TypeVar("AgentType", bound=BaseAgent)
ConfigType = TypeVar("ConfigType", bound=BaseConfig)
ResultType = TypeVar("ResultType")
T = TypeVar("T")


class AgentRegistry[T]:
    """Generic agent registry using Python 3.12 type parameter syntax."""

    def __init__(self) -> None:
        self._agents: dict[str, T] = {}

    def register(self, name: str, agent: T) -> None:
        """Register an agent with the given name."""
        self._agents[name] = agent

    def get(self, name: str) -> T | None:
        """Get an agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> list[str]:
        """List all registered agent names."""
        return list(self._agents.keys())


# Python 3.12: Improved Protocol syntax
class LLMClientProtocol(Protocol):
    """Protocol for LLM clients using Python 3.12 features."""

    async def generate_content(self, prompt: str, **kwargs: Any) -> str:
        """Generate content from a prompt."""
        ...

    async def generate_streaming_content(self, prompt: str, **kwargs: Any) -> Iterator[str]:
        """Generate streaming content from a prompt."""
        ...


# Python 3.12: Better dataclass support with slots
@dataclass(slots=True)
class AgentConfig:
    """Agent configuration using Python 3.12 dataclass improvements."""

    name: str
    model: str
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = 4000
    timeout: float = DEFAULT_TIMEOUT

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not (0 <= self.temperature <= 1):
            raise ValueError("Temperature must be between 0 and 1")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")


# Python 3.12: Improved async context managers
@asynccontextmanager
async def agent_session[T: BaseAgent](agent: T) -> AsyncIterator[T]:
    """Async context manager for agent sessions."""
    try:
        # Initialize agent session
        await agent.initialize_session()
        yield agent
    finally:
        # Cleanup agent session
        await agent.cleanup_session()


# Python 3.12: Better error messages and debugging
class AgentError(Exception):
    """Base exception for agent-related errors with improved error messages."""

    def __init__(self, message: str, agent_name: str, context: dict[str, Any] | None = None) -> None:
        self.agent_name = agent_name
        self.context = context or {}
        super().__init__(f"Agent '{agent_name}' error: {message}")


# Python 3.12: Improved type annotations with union syntax
# Type aliases for better type safety
type AgentResult = str | dict[str, Any] | None | Any
type AgentInput = str | dict[str, Any] | Path


# Python 3.12: Better generic function signatures
def process_agent_result(result: T, validator: Callable[[T], bool]) -> T:
    """Process agent result with validation."""
    if not validator(result):
        raise ValueError(f"Invalid result: {result}")
    return result


# Python 3.12: Improved async function signatures
async def execute_agent_with_timeout(
    agent: BaseAgent, input_data: AgentInput, timeout: float = DEFAULT_TIMEOUT
) -> AgentResult:
    """Execute agent with timeout using Python 3.12 features."""

    async def _execute() -> AgentResult:
        if hasattr(agent, "execute"):
            return await cast(Any, agent).execute(input_data)
        elif hasattr(agent, "process"):
            return await cast(Any, agent).process(input_data)
        else:
            raise AttributeError(f"Agent {type(agent).__name__} has no execute or process method")

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except TimeoutError:
        raise AgentError(f"Execution timed out after {timeout} seconds", getattr(agent, "name", "unknown"))


# Python 3.12: Better list comprehensions and generator expressions
def create_agent_pipeline(agents: list[BaseAgent]) -> Iterator[BaseAgent]:
    """Create an agent pipeline using Python 3.12 generator improvements."""
    for agent in agents:
        if not agent.is_available():
            continue
        yield agent


# Python 3.12: Improved string formatting and f-strings
def format_agent_message(agent_name: str, message: str, **kwargs: Any) -> str:
    """Format agent message using Python 3.12 string improvements."""
    # Python 3.12: Better f-string support
    base_message = f"Agent '{agent_name}': {message}"

    if kwargs:
        # Python 3.12: Improved string formatting
        details = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        return f"{base_message} ({details})"

    return base_message


# Python 3.12: Better exception handling
async def safe_agent_execution(
    agent: BaseAgent, input_data: AgentInput, fallback: Callable[[AgentInput], AgentResult] | None = None
) -> AgentResult:
    """Safely execute an agent with fallback support."""

    try:
        result = await execute_agent_with_timeout(agent, input_data)
        if isinstance(result, str | dict) or result is None:
            return result
        else:
            return str(result)
    except AgentError as e:
        # Python 3.12: Better exception chaining
        if fallback:
            try:
                fallback_result = fallback(input_data)
                if isinstance(fallback_result, str | dict) or fallback_result is None:
                    return fallback_result
                else:
                    return str(fallback_result)
            except Exception as fallback_error:
                raise AgentError(
                    f"Both primary execution and fallback failed: {e} -> {fallback_error}",
                    e.agent_name,
                    e.context,
                ) from e
        # Re-raise the original exception if no fallback
        raise e


# Python 3.12: Improved type checking utilities
def validate_agent_type[T](agent: T, expected_type: type) -> T:
    """Validate agent type using Python 3.12 features."""
    if not isinstance(agent, expected_type):
        raise TypeError(f"Expected {expected_type.__name__}, got {type(agent).__name__}")
    return agent


# Python 3.12: Better async iteration support
class AsyncAgentIterator[T: BaseAgent]:
    """Async iterator for agents using Python 3.12 features."""

    def __init__(self, agents: list[T]) -> None:
        self.agents = agents
        self.index = 0

    def __aiter__(self) -> "AsyncAgentIterator[T]":
        return self

    async def __anext__(self) -> T:
        if self.index >= len(self.agents):
            raise StopAsyncIteration

        agent = self.agents[self.index]
        self.index += 1

        # Python 3.12: Better async support
        await agent.prepare()

        return agent


# Python 3.12: Improved performance with better memory management
class AgentPool[T]:
    """Agent pool with improved memory management."""

    def __init__(self, max_size: int = 10) -> None:
        self.max_size = max_size
        self._agents: list[T] = []
        self._available: list[T] = []

    def add_agent(self, agent: T) -> None:
        """Add an agent to the pool."""
        if len(self._agents) < self.max_size:
            self._agents.append(agent)
            self._available.append(agent)

    async def get_agent(self) -> T:
        """Get an available agent from the pool."""
        if not self._available:
            raise RuntimeError("No available agents in pool")

        agent = self._available.pop()

        # Python 3.12: Better async context management
        async with agent_session(agent):  # type: ignore
            return agent

    def return_agent(self, agent: T) -> None:
        """Return an agent to the pool."""
        if agent in self._agents and agent not in self._available:
            self._available.append(agent)
