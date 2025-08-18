"""
Base Framework Abstraction

This module provides a base abstraction layer for different agent frameworks.
It allows LibriScribe to work with multiple agent frameworks while maintaining
a consistent interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol


class FrameworkAgent(Protocol):
    """Protocol for framework-specific agents."""

    name: str

    async def execute(self, input_data: Any, **kwargs: Any) -> Any:
        """Execute the agent with input data."""
        ...

    def get_config(self) -> dict[str, Any]:
        """Get agent configuration."""
        ...


class FrameworkService(Protocol):
    """Protocol for framework-specific services."""

    async def create_book(self, project_knowledge_base: Any, **kwargs: Any) -> bool:
        """Create a book using the framework."""
        ...

    def get_analytics(self) -> dict[str, Any]:
        """Get analytics from the framework."""
        ...


class BaseFrameworkWrapper(ABC):
    """
    Base class for framework wrappers.

    This provides a common interface for different agent frameworks
    while allowing framework-specific implementations.
    """

    def __init__(self, settings: Any, llm_client: Any):
        self.settings = settings
        self.llm_client = llm_client

    @abstractmethod
    def create_agent(self, libriscribe_agent: Any, **kwargs: Any) -> FrameworkAgent:
        """Create a framework agent from a LibriScribe agent."""
        pass

    @abstractmethod
    def create_service(self) -> FrameworkService:
        """Create a framework service."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the framework is available."""
        pass

    @abstractmethod
    def get_framework_info(self) -> dict[str, Any]:
        """Get information about the framework."""
        pass


class BaseFrameworkService(ABC):
    """
    Base class for framework services.

    This provides a common interface for different framework services
    while allowing framework-specific implementations.
    """

    def __init__(self, settings: Any, llm_client: Any):
        self.settings = settings
        self.llm_client = llm_client

    @abstractmethod
    async def create_book(self, project_knowledge_base: Any, **kwargs: Any) -> bool:
        """Create a book using the framework."""
        pass

    @abstractmethod
    def get_analytics(self) -> dict[str, Any]:
        """Get analytics from the framework."""
        pass

    @abstractmethod
    def export_logs(self, output_path: str) -> None:
        """Export framework logs."""
        pass


class FrameworkRegistry:
    """
    Registry for managing different agent frameworks.

    This allows LibriScribe to work with multiple frameworks
    and switch between them as needed.
    """

    def __init__(self) -> None:
        self._frameworks: dict[str, BaseFrameworkWrapper] = {}
        self._active_framework: str | None = None

    def register_framework(self, name: str, framework: BaseFrameworkWrapper) -> None:
        """Register a framework."""
        self._frameworks[name] = framework

    def get_framework(self, name: str) -> BaseFrameworkWrapper | None:
        """Get a framework by name."""
        return self._frameworks.get(name)

    def list_frameworks(self) -> list[str]:
        """List all registered frameworks."""
        return list(self._frameworks.keys())

    def get_available_frameworks(self) -> list[str]:
        """Get list of available frameworks."""
        return [name for name, framework in self._frameworks.items() if framework.is_available()]

    def set_active_framework(self, name: str) -> bool:
        """Set the active framework."""
        if name in self._frameworks and self._frameworks[name].is_available():
            self._active_framework = name
            return True
        return False

    def get_active_framework(self) -> BaseFrameworkWrapper | None:
        """Get the active framework."""
        if self._active_framework:
            return self._frameworks.get(self._active_framework)
        return None

    def get_framework_info(self, name: str) -> dict[str, Any]:
        """Get information about a framework."""
        framework = self._frameworks.get(name)
        if framework:
            return framework.get_framework_info()
        return {}

    def get_all_framework_info(self) -> dict[str, dict[str, Any]]:
        """Get information about all frameworks."""
        return {name: framework.get_framework_info() for name, framework in self._frameworks.items()}
