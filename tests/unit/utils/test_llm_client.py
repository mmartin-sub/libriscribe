"""
Unit tests for LLMClient.

This module tests the core functionality of the LLMClient class,
including initialization, configuration validation, content generation, and error handling.
"""

import pytest

from libriscribe2.utils.llm_client import LLMClient, LLMClientError


class TestLLMClient:
    """Test cases for LLMClient."""

    def test_initialization(self, integration_settings):
        """Test LLMClient initialization."""
        # Arrange & Act
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Assert
        assert client.provider == integration_settings.default_llm
        assert "general" in client.model_config
        assert client.timeout > 0
        assert client.environment is not None
        assert client.project_name == ""
        assert client.user is None

    def test_initialization_with_custom_config(self, integration_settings):
        """Test LLMClient initialization with custom configuration."""
        # Arrange
        model_config = {"default": "gpt-4o", "outline": "gpt-4o-mini"}

        # Act
        client = LLMClient(
            "anthropic",
            integration_settings,
            model_config=model_config,
            timeout=120.0,
            environment="production",
            project_name="test_project",
            user="test_user",
        )

        # Assert
        assert client.provider == "anthropic"
        assert client.model_config == model_config
        assert client.timeout == 120.0
        assert client.environment == "production"
        assert client.project_name == "test_project"
        assert client.user == "test_user"

    def test_initialization_invalid_provider(self, integration_settings):
        """Test LLMClient initialization with invalid provider."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Provider cannot be empty"):
            LLMClient("", integration_settings)

    def test_initialization_invalid_timeout(self, integration_settings):
        """Test LLMClient initialization with invalid timeout."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Timeout must be positive"):
            LLMClient(integration_settings.default_llm, integration_settings, timeout=0)

    def test_initialization_negative_timeout(self, integration_settings):
        """Test LLMClient initialization with negative timeout."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Timeout must be positive"):
            LLMClient(integration_settings.default_llm, integration_settings, timeout=-1)

    def test_get_model_for_prompt_type(self, integration_settings):
        """Test getting model for specific prompt type."""
        # Arrange
        model_config = {"default": "gpt-4o-mini", "outline": "gpt-4o", "concept": "gpt-4o-mini"}
        client = LLMClient(integration_settings.default_llm, integration_settings, model_config=model_config)

        # Act & Assert
        assert client.get_model_for_prompt_type("outline") == "gpt-4o"
        assert client.get_model_for_prompt_type("concept") == "gpt-4o-mini"
        assert client.get_model_for_prompt_type("nonexistent") == "gpt-4o-mini"

    def test_get_model_for_prompt_type_fallback(self, integration_settings):
        """Test getting model with fallback to default."""
        # Arrange
        model_config = {"outline": "gpt-4o"}
        client = LLMClient(integration_settings.default_llm, integration_settings, model_config=model_config)

        # Act & Assert
        assert client.get_model_for_prompt_type("outline") == "gpt-4o"
        assert client.get_model_for_prompt_type("concept") == "gpt-4o-mini"

    def test_validate_prompt_valid(self, integration_settings):
        """Test prompt validation with valid prompt."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Act & Assert
        assert client.validate_prompt("This is a valid prompt") is True
        assert client.validate_prompt("Another valid prompt") is True

    def test_validate_prompt_empty(self, integration_settings):
        """Test prompt validation with empty prompt."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Act & Assert
        assert client.validate_prompt("") is False
        assert client.validate_prompt("   ") is False

    def test_validate_prompt_none(self, integration_settings):
        """Test prompt validation with None prompt."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Act & Assert
        assert client.validate_prompt(None) is False

    def test_validate_prompt_invalid_type(self, integration_settings):
        """Test prompt validation with invalid type."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Act & Assert
        assert client.validate_prompt(123) is False
        assert client.validate_prompt([]) is False
        assert client.validate_prompt({}) is False

    def test_validate_prompt_too_long(self, integration_settings):
        """Test prompt validation with too long prompt."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)
        long_prompt = "x" * 100000  # Very long prompt

        # Act & Assert
        assert client.validate_prompt(long_prompt) is True  # No length limit in current implementation

    def test_get_client_config(self, integration_settings):
        """Test getting client configuration."""
        # Arrange
        client = LLMClient(
            integration_settings.default_llm,
            integration_settings,
            model_config={"default": "gpt-4o-mini"},
            timeout=60.0,
            environment="development",
            project_name="test_project",
            user="test_user",
        )

        # Act
        config = client.get_client_config()

        # Assert
        assert config["provider"] == integration_settings.default_llm
        assert config["timeout"] == 60.0
        assert config["environment"] == "development"
        assert config["project_name"] == "test_project"
        assert config["user"] == "test_user"
        assert config["model_config"] == {"default": "gpt-4o-mini"}
        assert "capabilities" in config
        assert "version" in config

    @pytest.mark.asyncio
    async def test_context_manager(self, integration_settings):
        """Test LLMClient as async context manager."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Act & Assert
        async with client as ctx_client:
            assert ctx_client == client

    @pytest.mark.asyncio
    async def test_initialize_session(self, integration_settings):
        """Test session initialization."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Act
        await client.initialize_session()

        # Assert - should not raise exception

    @pytest.mark.asyncio
    async def test_cleanup_session(self, integration_settings):
        """Test session cleanup."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Act
        await client.cleanup_session()

        # Assert - should not raise exception

    @pytest.mark.asyncio
    async def test_generate_content_basic(self, integration_settings, handle_llm_client_error):
        """Test basic content generation."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Act & Assert
        await client.generate_content("Test prompt")


    @pytest.mark.asyncio
    async def test_generate_content_with_fallback_basic(self, integration_settings, handle_llm_client_error):
        """Test basic content generation with fallback."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Act & Assert
        await client.generate_content_with_fallback("Primary prompt", "Fallback prompt")


    def test_llm_client_error(self):
        """Test LLMClientError exception."""
        # Arrange & Act
        error = LLMClientError("Test error", "openai", {"context": "test"})

        # Assert
        assert "Test error" in str(error)
        assert error.provider == "openai"
        assert error.context == {"context": "test"}

    def test_llm_client_error_without_context(self):
        """Test LLMClientError exception without context."""
        # Arrange & Act
        error = LLMClientError("Test error", "openai")

        # Assert
        assert "Test error" in str(error)
        assert error.provider == "openai"
        assert error.context == {}  # LLMClientError sets context to {} when None is passed

    def test_validate_configuration(self, integration_settings):
        """Test configuration validation."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)

        # Act & Assert - should not raise exception
        client._validate_configuration()

    def test_validate_configuration_empty_provider(self, integration_settings):
        """Test configuration validation with empty provider."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)
        client.provider = ""

        # Act & Assert
        with pytest.raises(ValueError, match="Provider cannot be empty"):
            client._validate_configuration()

    def test_validate_configuration_invalid_timeout(self, integration_settings):
        """Test configuration validation with invalid timeout."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)
        client.timeout = 0

        # Act & Assert
        with pytest.raises(ValueError, match="Timeout must be positive"):
            client._validate_configuration()

    def test_validate_configuration_negative_timeout(self, integration_settings):
        """Test configuration validation with negative timeout."""
        # Arrange
        client = LLMClient(integration_settings.default_llm, integration_settings)
        client.timeout = -1

        # Act & Assert
        with pytest.raises(ValueError, match="Timeout must be positive"):
            client._validate_configuration()
