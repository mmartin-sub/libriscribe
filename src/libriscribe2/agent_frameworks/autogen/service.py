"""
AutoGen Service

This module provides a service layer for managing AutoGen-based book creation workflows.
It orchestrates multi-agent interactions using AutoGen and provides structured integration
with the existing LibriScribe system.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

# AutoGen imports
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import ChatAgent, Team
from autogen_ext.models.openai import OpenAIChatCompletionClient

from ...settings import Settings
from ...utils.llm_client import LLMClient
from ..base import BaseFrameworkService
from .wrapper import AutoGenAgentWrapper

AUTOGEN_AVAILABLE = True

logger = logging.getLogger(__name__)

'''# Fallback classes for when AutoGen is not available
class AutoGenAgent:  # type: ignore
    """Dummy class for when AutoGen is not available."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        logger.warning("AutoGen not installed. Using dummy AutoGenAgent.")

class AssistantAgent(AutoGenAgent):  # type: ignore
    """Dummy class for when AutoGen is not available."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        logger.warning("AutoGen not installed. Using dummy AssistantAgent.")

class UserProxyAgent(AutoGenAgent):  # type: ignore
    """Dummy class for when AutoGen is not available."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        logger.warning("AutoGen not installed. Using dummy UserProxyAgent.")

    async def a_initiate_chat(self, *args: Any, **kwargs: Any) -> dict[str, str]:
        """Dummy method for when AutoGen is not available."""
        logger.warning("AutoGen not installed, cannot initiate chat.")
        return {"summary": "AutoGen not installed."}
'''


class AutoGenService(BaseFrameworkService):
    """
    Service for managing AutoGen-based book creation workflows.

    This service provides high-level orchestration of AutoGen multi-agent
    conversations for book creation tasks.
    """

    def __init__(self, settings: Settings, llm_client: LLMClient):
        super().__init__(settings, llm_client)
        self.wrapper = AutoGenAgentWrapper(settings, llm_client)
        self.logger = logging.getLogger(__name__)

        # Conversation tracking
        self.conversation_history: list[dict[str, Any]] = []
        self.performance_metrics: dict[str, Any] = {}

    async def create_book(self, project_knowledge_base: Any, **kwargs: Any) -> bool:
        """
        Create a book using AutoGen multi-agent team.

        Args:
            project_knowledge_base: The project knowledge base
            **kwargs: Additional arguments including max_conversation_turns, save_conversation

        Returns:
            True if successful, False otherwise
        """
        max_conversation_turns = kwargs.get("max_conversation_turns", 50)
        save_conversation = kwargs.get("save_conversation", True)

        try:
            self.logger.info("Starting AutoGen book creation workflow")

            # Create AutoGen agents from project knowledge base
            agents = self._create_autogen_agents_from_knowledge_base(project_knowledge_base)

            if not agents:
                self.logger.error("No agents available for AutoGen workflow")
                return False

            # Create workflow messages
            workflow_messages = self._create_book_workflow_messages(project_knowledge_base)

            # Execute the conversation
            success = await self._execute_autogen_conversation(
                agents, workflow_messages, max_conversation_turns, save_conversation
            )

            if success:
                self.logger.info("AutoGen book creation completed successfully")
            else:
                self.logger.error("AutoGen book creation failed")

            return success

        except Exception as e:
            self.logger.error(f"Error in AutoGen book creation: {e}")
            return False

    async def create_book_with_hybrid_approach(self, project_knowledge_base: Any) -> bool:
        """
        Create a book using a hybrid approach: AutoGen for coordination,
        LibriScribe agents for execution.

        Args:
            project_knowledge_base: The project knowledge base

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Starting hybrid AutoGen + LibriScribe workflow")

            # Use AutoGen for high-level coordination
            coordination_agents = self._create_coordination_agents()

            # Create coordination messages
            coordination_messages = self._create_coordination_messages(project_knowledge_base)

            # Execute coordination conversation
            coordination_result = await self._execute_coordination_conversation(
                coordination_agents, coordination_messages
            )

            if coordination_result:
                # Use LibriScribe agents for actual execution
                execution_success = await self._execute_with_libriscribe_agents(project_knowledge_base)
                return execution_success
            else:
                self.logger.error("Coordination phase failed")
                return False

        except Exception as e:
            self.logger.error(f"Error in hybrid workflow: {e}")
            return False

    def _create_autogen_agents_from_knowledge_base(self, project_knowledge_base: Any) -> list[ChatAgent | Team]:
        """Create AutoGen agents from project knowledge base."""

        agents: list[ChatAgent | Team] = []
        model_client = OpenAIChatCompletionClient(
            model=self.settings.openai_default_model_name,
            api_key=self.settings.openai_api_key,
            base_url=getattr(self.settings, "openai_base_url", self.settings.openai_base_url_default),
        )

        # Create specialized agents for book creation
        agent_configs = [
            {
                "name": "concept_generator",
                "type": "assistant",
                "system_message": "You are a creative concept generator. Generate innovative book ideas and concepts.",
            },
            {
                "name": "outline_creator",
                "type": "assistant",
                "system_message": "You are an outline creator. Create detailed book outlines and structure.",
            },
            {
                "name": "content_writer",
                "type": "assistant",
                "system_message": "You are a content writer. Write engaging book content and chapters.",
            },
            {
                "name": "editor",
                "type": "assistant",
                "system_message": "You are an editor. Review and improve book content for clarity and quality.",
            },
        ]

        for config in agent_configs:
            try:
                agent = AssistantAgent(
                    name=config["name"],
                    system_message=config["system_message"],
                    model_client=model_client,
                )
                agents.append(agent)
                self.logger.info(f"Created AutoGen agent: {config['name']}")
            except Exception as e:
                self.logger.error(f"Failed to create agent {config['name']}: {e}")

        return agents

    def _create_book_workflow_messages(self, project_knowledge_base: Any) -> list[str]:
        """Create workflow messages for book creation."""

        messages = [
            "Let's create a comprehensive book together. We'll work through concept generation, outline creation, content writing, and editing.",
            "First, let's generate a compelling book concept that will engage readers.",
            "Next, we'll create a detailed outline that structures the book effectively.",
            "Then, we'll write the actual content, chapter by chapter.",
            "Finally, we'll review and edit the content for quality and clarity.",
        ]

        return messages

    async def _execute_autogen_conversation(
        self, agents: list[ChatAgent | Team], messages: list[str], max_turns: int, save_conversation: bool
    ) -> bool:
        """Execute AutoGen conversation."""

        try:
            from autogen_agentchat.teams import RoundRobinGroupChat

            groupchat = RoundRobinGroupChat(participants=agents, max_turns=max_turns)

            # Start conversation with first message
            if messages:
                chat_result = await groupchat.run(task=messages[0])

                # Track conversation
                if chat_result:
                    self._track_conversation(chat_result)

                # Save conversation if requested
                if save_conversation and chat_result:
                    self._save_conversation_to_file(chat_result)

                return True
            else:
                self.logger.error("No messages to execute")
                return False

        except Exception as e:
            self.logger.error(f"Error executing AutoGen conversation: {e}")
            return False

    def _create_coordination_agents(self) -> list[ChatAgent | Team]:
        """Create agents for coordination phase."""

        agents: list[ChatAgent | Team] = []
        model_client = OpenAIChatCompletionClient(
            model=self.settings.openai_default_model_name,
            api_key=self.settings.openai_api_key,
            base_url=getattr(self.settings, "openai_base_url", self.settings.openai_base_url_default),
        )

        # Coordinator agent
        coordinator = AssistantAgent(
            name="coordinator",
            system_message="You are a project coordinator. You plan and coordinate book creation tasks.",
            model_client=model_client,
        )
        agents.append(coordinator)

        # Planner agent
        planner = AssistantAgent(
            name="planner",
            system_message="You are a project planner. You create detailed plans for book creation tasks.",
            model_client=model_client,
        )
        agents.append(planner)

        return agents

    def _create_coordination_messages(self, project_knowledge_base: Any) -> list[str]:
        """Create messages for coordination phase."""

        return [
            "Let's plan the book creation process step by step.",
            "We need to coordinate concept generation, outline creation, writing, and editing phases.",
            "Each phase should have clear deliverables and quality criteria.",
        ]

    async def _execute_coordination_conversation(self, agents: list[ChatAgent | Team], messages: list[str]) -> bool:
        """Execute coordination conversation."""

        try:
            from autogen_agentchat.teams import RoundRobinGroupChat

            groupchat = RoundRobinGroupChat(participants=agents, max_turns=10)

            if messages:
                await groupchat.run(task=messages[0])
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"Error in coordination conversation: {e}")
            return False

    async def _execute_with_libriscribe_agents(self, project_knowledge_base: Any) -> bool:
        """Execute book creation using LibriScribe agents."""

        # This would integrate with existing LibriScribe agents
        # For now, return True as placeholder
        self.logger.info("Executing with LibriScribe agents")
        return True

    def _track_conversation(self, chat_result: Any) -> None:
        """Track conversation for analytics."""

        self.conversation_history.append(
            {"timestamp": datetime.now().isoformat(), "result": str(chat_result), "success": True}
        )

    def _save_conversation_to_file(self, chat_result: Any) -> None:
        """Save conversation to file."""

        try:
            output_dir = Path("autogen_conversations")
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"conversation_{timestamp}.json"

            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "result": str(chat_result),
                "settings": {
                    "model": self.settings.openai_default_model_name,
                    "temperature": self.settings.default_temperature,
                },
            }

            with open(output_file, "w") as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Conversation saved to: {output_file}")

        except Exception as e:
            self.logger.error(f"Failed to save conversation: {e}")

    def get_conversation_analytics(self) -> dict[str, Any]:
        """Get analytics from conversation history."""

        if not self.conversation_history:
            return {"total_conversations": 0}

        return {
            "total_conversations": len(self.conversation_history),
            "successful_conversations": len([c for c in self.conversation_history if c.get("success", False)]),
            "latest_conversation": self.conversation_history[-1] if self.conversation_history else None,
            "conversation_timestamps": [c["timestamp"] for c in self.conversation_history],
        }

    def export_conversation_log(self, output_path: str) -> None:
        """Export conversation log to file."""
        try:
            import json

            with open(output_path, "w") as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Conversation log exported to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to export conversation log: {e}")

    def get_analytics(self) -> dict[str, Any]:
        """Get analytics from the framework."""
        return {
            "conversation_history": self.conversation_history,
            "performance_metrics": self.performance_metrics,
            "framework": "autogen",
            "available": AUTOGEN_AVAILABLE,
        }

    def export_logs(self, output_path: str) -> None:
        """Export framework logs."""
        self.export_conversation_log(output_path)


class AutoGenConfigurationManager:
    """
    Manager for AutoGen configuration and best practices.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_recommended_configuration(self, use_case: str) -> dict[str, Any]:
        """Get recommended configuration for a specific use case."""

        settings = Settings()
        configurations = {
            "book_creation": {
                "max_conversation_turns": 50,
                "temperature": settings.default_temperature,
                "timeout": 300,
                "agent_types": ["assistant", "user_proxy"],
                "recommended_models": ["gpt-4", "gpt-4-32k"],
            },
            "content_editing": {
                "max_conversation_turns": 30,
                "temperature": 0.5,
                "timeout": 180,
                "agent_types": ["assistant", "text_analyzer"],
                "recommended_models": ["gpt-4", "gpt-3.5-turbo"],
            },
            "concept_generation": {
                "max_conversation_turns": 20,
                "temperature": 0.9,
                "timeout": 120,
                "agent_types": ["assistant"],
                "recommended_models": ["gpt-4", "gpt-4-32k"],
            },
        }

        return configurations.get(use_case, configurations["book_creation"])

    def validate_configuration(self, config: dict[str, Any]) -> list[str]:
        """Validate configuration and return any issues."""

        issues = []

        required_keys = ["max_conversation_turns", "temperature", "timeout"]
        for key in required_keys:
            if key not in config:
                issues.append(f"Missing required configuration key: {key}")

        if "temperature" in config:
            temp = config["temperature"]
            if not (0 <= temp <= 1):
                issues.append(f"Temperature must be between 0 and 1, got: {temp}")

        if "timeout" in config:
            timeout = config["timeout"]
            if timeout <= 0:
                issues.append(f"Timeout must be positive, got: {timeout}")

        return issues
