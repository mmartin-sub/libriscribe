"""
AutoGen Agent Wrapper

This module provides a wrapper to make LibriScribe agents compatible with AutoGen.
It allows existing LibriScribe agents to participate in AutoGen multi-agent conversations.
"""

import importlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from ...agents.agent_base import Agent as LibriScribeAgent
from ...settings import Settings
from ...utils.llm_client import LLMClient
from ..base import BaseFrameworkWrapper, FrameworkAgent

# We avoid direct imports from autogen_agentchat to prevent mypy attr-defined errors
# when type stubs are missing or incomplete. During type checking, we declare
# minimal Protocols. At runtime, we import dynamically via importlib and fetch
# symbols with getattr, falling back to None when unavailable.

# Typing-only Protocols
if TYPE_CHECKING:

    class ConversableAgentT(Protocol):
        name: str

        async def a_generate_reply(self, _sender: Any | None, messages: list[Any]) -> Any: ...

    class AssistantAgentT(ConversableAgentT, Protocol): ...

    class UserProxyAgentT(ConversableAgentT, Protocol):
        async def a_initiate_chat(self, _other: "ConversableAgentT", message: str, max_turns: int = ...) -> Any: ...

    class TextAnalyzerAgentT(ConversableAgentT, Protocol): ...
else:
    ConversableAgentT = Any
    AssistantAgentT = Any
    UserProxyAgentT = Any
    TextAnalyzerAgentT = Any

# Runtime dynamic import
AssistantAgent: Any = None
ConversableAgent: Any = None
UserProxyAgent: Any = None
TextAnalyzerAgent: Any = None
try:
    autogen_agentchat = importlib.import_module("autogen_agentchat")
    contrib_mod = importlib.import_module("autogen_agentchat.contrib.text_analyzer_agent")
    AssistantAgent = getattr(autogen_agentchat, "AssistantAgent", None)
    ConversableAgent = getattr(autogen_agentchat, "ConversableAgent", None)
    UserProxyAgent = getattr(autogen_agentchat, "UserProxyAgent", None)
    TextAnalyzerAgent = getattr(contrib_mod, "TextAnalyzerAgent", None)
    AUTOGEN_AVAILABLE = all([AssistantAgent, ConversableAgent, UserProxyAgent, TextAnalyzerAgent])
except Exception:
    AUTOGEN_AVAILABLE = False

logger = logging.getLogger(__name__)


class AutoGenAgentAdapter:
    """Adapter to make AutoGen agents compatible with FrameworkAgent protocol."""

    def __init__(self, autogen_agent: "ConversableAgentT"):
        self.autogen_agent = autogen_agent
        self.name = autogen_agent.name

    async def execute(self, input_data: Any, **kwargs: Any) -> Any:
        """Execute the agent with input data."""
        # This would need to be implemented based on AutoGen's API
        return await self.autogen_agent.a_generate_reply(_sender=None, messages=[input_data])

    def get_config(self) -> dict[str, Any]:
        """Get agent configuration."""
        return {"name": self.name, "type": type(self.autogen_agent).__name__, "framework": "autogen"}


class AutoGenAgentWrapper(BaseFrameworkWrapper):
    """
    Wrapper to convert LibriScribe agents to AutoGen agents.

    This class provides a bridge between LibriScribe's custom agent architecture
    and AutoGen's multi-agent conversation framework.
    """

    def __init__(self, settings: Settings, llm_client: LLMClient):
        super().__init__(settings, llm_client)
        self.logger = logging.getLogger(__name__)

    def create_agent(
        self, libriscribe_agent: LibriScribeAgent, agent_type: str = "assistant", **kwargs: Any
    ) -> FrameworkAgent:
        """
        Create an AutoGen agent from a LibriScribe agent.

        Args:
            libriscribe_agent: The LibriScribe agent to wrap
            agent_type: Type of AutoGen agent to create ("assistant", "user_proxy", "text_analyzer")
            **kwargs: Additional arguments for the AutoGen agent

        Returns:
            AutoGen agent adapter instance
        """
        system_message = self._get_agent_system_message(libriscribe_agent)
        llm_config = self._get_llm_config()

        if agent_type == "assistant" and AssistantAgent is not None:
            autogen_agent = AssistantAgent(
                name=libriscribe_agent.name,
                system_message=system_message,
                llm_config=llm_config,
                **kwargs,
            )
        elif agent_type == "user_proxy" and UserProxyAgent is not None:
            autogen_agent = UserProxyAgent(
                name=libriscribe_agent.name,
                system_message=system_message,
                llm_config=llm_config,
                **kwargs,
            )
        elif agent_type == "text_analyzer" and TextAnalyzerAgent is not None:
            autogen_agent = TextAnalyzerAgent(
                name=libriscribe_agent.name,
                system_message=system_message,
                llm_config=llm_config,
                **kwargs,
            )
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        return AutoGenAgentAdapter(autogen_agent)

    def _get_agent_system_message(self, agent: LibriScribeAgent) -> str:
        """Get the system message for an agent based on its type."""

        base_message = f"You are {agent.name}, a specialized AI agent for book creation."

        # Add role-specific instructions
        if "concept" in agent.name.lower():
            return f"{base_message} You specialize in generating creative book concepts and ideas."
        elif "outline" in agent.name.lower():
            return f"{base_message} You specialize in creating detailed book outlines and structure."
        elif "writer" in agent.name.lower():
            return f"{base_message} You specialize in writing engaging book content and chapters."
        elif "editor" in agent.name.lower():
            return f"{base_message} You specialize in editing and improving book content."
        elif "reviewer" in agent.name.lower():
            return f"{base_message} You specialize in reviewing and providing feedback on book content."
        else:
            return f"{base_message} You are a general-purpose book creation assistant."

    def _get_llm_config(self) -> dict[str, Any]:
        """Get LLM configuration for AutoGen agents."""

        return {
            "config_list": [
                {
                    "model": self.settings.openai_default_model_name,
                    "api_key": self.settings.openai_api_key,
                    "base_url": getattr(self.settings, "openai_base_url", self.settings.openai_base_url_default),
                }
            ],
            "temperature": self.settings.default_temperature,
            "timeout": self.settings.default_timeout,
        }

    def setup_book_creation_team(self, agents: dict[str, LibriScribeAgent]) -> list[FrameworkAgent]:
        """
        Set up a team of AutoGen agents for book creation.

        Args:
            agents: Dictionary of LibriScribe agents to convert

        Returns:
            List of framework agents ready for conversation
        """
        autogen_agents = []

        for name, agent in agents.items():
            try:
                autogen_agent = self.create_agent(agent)
                autogen_agents.append(autogen_agent)
                self.logger.info(f"Created AutoGen agent: {name}")
            except Exception as e:
                self.logger.error(f"Failed to create AutoGen agent for {name}: {e}")

        return autogen_agents

    def create_service(self):
        """Create an AutoGen service."""
        from .service import AutoGenService

        return AutoGenService(self.settings, self.llm_client)

    def is_available(self) -> bool:
        """Check if AutoGen is available."""
        return AUTOGEN_AVAILABLE

    def get_framework_info(self) -> dict[str, Any]:
        """Get information about the AutoGen framework."""
        return {
            "name": "AutoGen",
            "version": "0.2.0+",
            "description": "Microsoft's multi-agent conversation framework",
            "available": AUTOGEN_AVAILABLE,
            "capabilities": [
                "multi-agent conversations",
                "agent coordination",
                "conversation management",
            ],
            "website": "https://github.com/microsoft/autogen",
        }

    async def create_book_with_autogen(
        self, agents: list["ConversableAgentT"], book_concept: str, output_path: Path | None = None
    ) -> bool:
        """
        Create a book using AutoGen multi-agent conversation.

        Args:
            agents: List of AutoGen agents
            book_concept: The book concept to work on
            output_path: Optional path to save the conversation

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a user proxy agent to initiate the conversation
            if UserProxyAgent is None:
                raise RuntimeError("AutoGen is not available")
            user_proxy = UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=10,
                llm_config=self._get_llm_config(),
            )

            # Start the conversation
            chat_result = await user_proxy.a_initiate_chat(
                agents[0],  # Start with the first agent
                message=f"Let's create a book about: {book_concept}",
                max_turns=50,
            )

            # Save conversation if output path is provided
            if output_path:
                self._save_conversation(chat_result, output_path)

            return True

        except Exception as e:
            self.logger.error(f"Failed to create book with AutoGen: {e}")
            return False

    def _save_conversation(self, chat_result: Any, output_path: Path) -> None:
        """Save the conversation to a file."""
        try:
            with open(output_path, "w") as f:
                f.write(str(chat_result))
            self.logger.info(f"Conversation saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save conversation: {e}")


class AutoGenBestPractices:
    """
    Best practices and guidelines for using AutoGen with libriscribe2.
    """

    @staticmethod
    def get_security_guidelines() -> list[str]:
        """Get security guidelines for AutoGen usage."""
        return [
            "Never expose API keys in code or logs",
            "Use environment variables for sensitive configuration",
            "Validate all inputs before processing",
            "Implement rate limiting to prevent abuse",
            "Monitor API usage and costs",
            "Use secure communication channels",
            "Regularly audit agent permissions and capabilities",
        ]

    @staticmethod
    def get_performance_guidelines() -> list[str]:
        """Get performance guidelines for AutoGen usage."""
        return [
            "Use async/await for I/O operations",
            "Implement proper timeout handling",
            "Cache responses when appropriate",
            "Monitor memory usage during conversations",
            "Use streaming for long responses",
            "Implement retry logic for failed requests",
            "Optimize prompt length and complexity",
        ]

    @staticmethod
    def get_agent_configuration_guidelines() -> list[str]:
        """Get guidelines for agent configuration."""
        return [
            "Define clear system messages for each agent",
            "Set appropriate temperature values for creativity vs consistency",
            "Use role-based agent types (assistant, user_proxy, etc.)",
            "Implement proper error handling in agent responses",
            "Monitor conversation flow and agent interactions",
            "Use structured prompts for better results",
            "Implement conversation history management",
        ]

    @staticmethod
    def get_integration_guidelines() -> list[str]:
        """Get guidelines for integrating AutoGen with libriscribe2."""
        return [
            "Maintain compatibility with existing LibriScribe agents",
            "Use wrapper pattern for framework abstraction",
            "Implement proper error handling and fallbacks",
            "Monitor performance and resource usage",
            "Provide clear documentation for AutoGen features",
            "Test thoroughly before production deployment",
            "Plan for framework migration and updates",
        ]
