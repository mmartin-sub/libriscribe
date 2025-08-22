"""
Unit tests for Agent base class logging behavior.

This module tests the core functionality of the Agent base class,
including logging behavior and error handling.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from libriscribe2.agents.agent_base import Agent
from libriscribe2.knowledge_base import ProjectKnowledgeBase
from libriscribe2.utils.exceptions import LLMGenerationError
from libriscribe2.utils.llm_client import LLMClient


class MockAgent(Agent):
    """Test implementation of Agent for testing."""

    async def execute(self, project_knowledge_base: ProjectKnowledgeBase, output_path: str | None = None, **kwargs):
        """Test implementation of execute method."""
        self.log_info("Test execution started")
        self.log_debug("Debug message for file only")
        self.log_error("Error message for console")
        self.log_success("Success message")
        self.log_warning("Warning message")


class TestAgentBase:
    """Test cases for Agent base class."""

    def setup_method(self):
        """Set up test method."""
        # Create a mock LLM client
        self.mock_llm_client = MagicMock(spec=LLMClient)
        self.mock_llm_client.provider = "mock"

        # Create test agent
        self.agent = MockAgent("TestAgent", self.mock_llm_client)

    def test_agent_initialization(self):
        """Test Agent initialization."""
        # Arrange & Act
        agent = MockAgent("TestAgent", self.mock_llm_client)

        # Assert
        assert agent.name == "TestAgent"
        assert agent.llm_client == self.mock_llm_client
        assert agent.logger is not None

    def test_log_info(self):
        """Test log_info method."""
        # Arrange
        with patch.object(self.agent.logger, "info") as mock_info:
            # Act
            self.agent.log_info("Test info message")

            # Assert
            mock_info.assert_called_once_with("[TestAgent] Test info message")

    def test_log_error(self):
        """Test log_error method."""
        # Arrange
        with patch.object(self.agent.logger, "error") as mock_error:
            # Act
            self.agent.log_error("Test error message")

            # Assert
            mock_error.assert_called_once_with("[TestAgent] Test error message")

    def test_log_debug(self):
        """Test log_debug method."""
        # Arrange
        with patch.object(self.agent.logger, "debug") as mock_debug:
            # Act
            self.agent.log_debug("Test debug message")

            # Assert
            mock_debug.assert_called_once_with("[TestAgent] Test debug message")

    def test_log_success(self):
        """Test log_success method."""
        # Arrange
        with patch.object(self.agent.logger, "info") as mock_info:
            # Act
            self.agent.log_success("Test success message")

            # Assert
            mock_info.assert_called_once_with("[TestAgent] ✅ Test success message")

    def test_log_warning(self):
        """Test log_warning method."""
        # Arrange
        with patch.object(self.agent.logger, "warning") as mock_warning:
            # Act
            self.agent.log_warning("Test warning message")

            # Assert
            mock_warning.assert_called_once_with("[TestAgent] ⚠️ Test warning message")

    @pytest.mark.asyncio
    async def test_safe_generate_content_success(self):
        """Test safe_generate_content with successful generation."""
        # Arrange
        expected_content = "Generated content"
        self.mock_llm_client.generate_content.return_value = expected_content

        # Act
        result = await self.agent.safe_generate_content("Test prompt", "concept")

        # Assert
        assert result == expected_content
        self.mock_llm_client.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_safe_generate_content_failure(self):
        """Test safe_generate_content with generation failure."""
        # Arrange
        self.mock_llm_client.generate_content.side_effect = Exception("LLM error")

        # Act & Assert
        with pytest.raises(LLMGenerationError):
            await self.agent.safe_generate_content("Test prompt", "concept")

    def test_safe_extract_json_success(self):
        """Test safe_extract_json with valid JSON."""
        # Arrange
        content = '```json\n{"key": "value"}\n```'

        # Act
        result = self.agent.safe_extract_json(content, "test content")

        # Assert
        assert result == {"key": "value"}

    def test_safe_extract_json_no_markdown(self):
        """Test safe_extract_json with JSON without markdown."""
        # Arrange
        content = '{"key": "value"}'

        # Act
        result = self.agent.safe_extract_json(content, "test content")

        # Assert
        assert result == {"key": "value"}

    def test_safe_extract_json_failure(self):
        """Test safe_extract_json with invalid JSON."""
        # Arrange
        content = "Invalid JSON content"

        # Act
        result = self.agent.safe_extract_json(content, "test content")

        # Assert
        assert result is None

    def test_safe_extract_json_list_success(self):
        """Test safe_extract_json_list with valid JSON array."""
        # Arrange
        content = '```json\n[{"item": "value"}]\n```'

        # Act
        result = self.agent.safe_extract_json_list(content, "test content")

        # Assert
        assert result == [{"item": "value"}]

    def test_safe_extract_json_list_single_object(self):
        """Test safe_extract_json_list with single object (should be wrapped in array)."""
        # Arrange
        content = '```json\n{"item": "value"}\n```'

        # Act
        result = self.agent.safe_extract_json_list(content, "test content")

        # Assert
        assert result == [{"item": "value"}]

    def test_safe_extract_json_list_failure(self):
        """Test safe_extract_json_list with invalid JSON."""
        # Arrange
        content = "Invalid JSON content"

        # Act
        result = self.agent.safe_extract_json_list(content, "test content")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_with_fallback_success(self):
        """Test execute_with_fallback with successful primary method."""

        # Arrange
        async def primary_method():
            return "success"

        # Act
        result = await self.agent.execute_with_fallback(primary_method)

        # Assert
        assert result == "success"

    @pytest.mark.asyncio
    async def test_execute_with_fallback_with_fallback_success(self):
        """Test execute_with_fallback with fallback method."""

        # Arrange
        async def primary_method():
            raise Exception("Primary failed")

        async def fallback_method():
            return "fallback success"

        # Act
        result = await self.agent.execute_with_fallback(primary_method, fallback_method)

        # Assert
        assert result == "fallback success"

    @pytest.mark.asyncio
    async def test_execute_with_fallback_both_fail(self):
        """Test execute_with_fallback with both methods failing."""

        # Arrange
        async def primary_method():
            raise Exception("Primary failed")

        async def fallback_method():
            raise Exception("Fallback failed")

        # Act & Assert
        with pytest.raises(Exception, match="Primary failed"):
            await self.agent.execute_with_fallback(primary_method, fallback_method)

    def test_dump_raw_response(self):
        """Test _dump_raw_response method."""
        # Arrange
        content = "Test content"
        output_path = tempfile.mkdtemp()
        content_type = "test_type"

        try:
            # Act
            self.agent._dump_raw_response(content, output_path, content_type)

            # Assert
            # The method creates the file in the parent directory of output_path
            expected_file = Path(output_path).parent / f"{content_type}.json"
            assert expected_file.exists()
            # The content is stored as JSON, so we need to check the JSON structure
            import json

            with open(expected_file) as f:
                content = f.read()
                assert content
                data = json.loads(content)
            assert data["raw_content"] == "Test content"
            assert data["content_type"] == content_type

        finally:
            # Cleanup
            import shutil

            shutil.rmtree(output_path)

    def test_dump_raw_response_no_output_path(self):
        """Test _dump_raw_response with no output path."""
        # Arrange
        content = "Test content"
        content_type = "test_type"

        # Act - should not raise exception
        self.agent._dump_raw_response(content, None, content_type)

        # Assert - no file should be created
        # (This test just ensures no exception is raised)

    def test_validate_input_string(self):
        """Test validate_input with string input."""
        # Arrange & Act & Assert
        assert self.agent.validate_input("valid string") is True
        assert self.agent.validate_input("") is False
        assert self.agent.validate_input("   ") is False

    def test_validate_input_dict(self):
        """Test validate_input with dict input."""
        # Arrange & Act & Assert
        assert self.agent.validate_input({"key": "value"}) is True
        assert self.agent.validate_input({}) is False

    def test_validate_input_path(self):
        """Test validate_input with Path input."""
        # Arrange
        with tempfile.NamedTemporaryFile() as f:
            # Act & Assert
            assert self.agent.validate_input(Path(f.name)) is True
            assert self.agent.validate_input(Path("nonexistent")) is False

    def test_validate_input_none(self):
        """Test validate_input with None input."""
        # Arrange & Act & Assert
        assert self.agent.validate_input(None) is False

    def test_get_agent_config(self):
        """Test get_agent_config method."""
        # Act
        config = self.agent.get_agent_config()

        # Assert
        assert isinstance(config, dict)
        assert "name" in config
        assert config["name"] == "TestAgent"

    def test_format_status_message(self):
        """Test format_status_message method."""
        # Arrange
        status = "running"
        details = {"progress": "50%"}

        # Act
        message = self.agent.format_status_message(status, details)

        # Assert
        assert "TestAgent" in message
        assert "running" in message
        assert "50%" in message

    def test_format_status_message_no_details(self):
        """Test format_status_message method without details."""
        # Arrange
        status = "completed"

        # Act
        message = self.agent.format_status_message(status)

        # Assert
        assert "TestAgent" in message
        assert "completed" in message
