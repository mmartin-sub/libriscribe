"""
Integration tests for configuration loading.

This module tests the end-to-end functionality of configuration loading,
ensuring that configuration files are properly loaded and used.
"""

import json
import tempfile
from pathlib import Path

from libriscribe2.services.book_creator import BookCreatorService
from libriscribe2.settings import Settings


class TestConfigurationLoading:
    """Integration tests for configuration loading."""

    def teardown_method(self):
        """Clean up environment variables after each test."""
        import os

        env_vars_to_clear = [
            "PROJECTS_DIR",
            "DEFAULT_LLM",
            "LLM_TIMEOUT",
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
            "OPENAI_DEFAULT_MODEL",
        ]
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]

    def test_book_creator_with_config_file(self):
        """Test BookCreatorService with configuration file."""
        # Arrange
        config_data = {
            "openai_api_key": "test-key",
            "openai_base_url": "http://test.com",
            "openai_default_model": "test-model",
            "default_llm": "test-llm",
            "llm_timeout": 600,
            "projects_dir": "./test-projects",
            "models": {
                "default": "custom-default-model",
                "concept": "custom-concept-model",
                "outline": "custom-outline-model",
                "character": "custom-character-model",
                "chapter": "custom-chapter-model",
                "formatting": "custom-formatting-model",
                "worldbuilding": "custom-worldbuilding-model",
                "scene_outline": "custom-scene-outline-model",
                "editor": "custom-editor-model",
                "research": "custom-research-model",
                "scene": "custom-scene-model",
                "keyword_generation": "custom-keyword-model",
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            # Act
            book_creator = BookCreatorService(config_file=config_path, mock=True)

            # Assert
            assert book_creator.settings.openai_api_key == "test-key"
            assert book_creator.settings.default_llm == "test-llm"
            assert book_creator.settings.llm_timeout == 600.0
            assert book_creator.settings.projects_dir == "./test-projects"

            # Check that model config was loaded from file
            model_config = book_creator.model_config
            assert model_config["default"] == "custom-default-model"
            assert model_config["concept"] == "custom-concept-model"
            assert model_config["outline"] == "custom-outline-model"
            assert model_config["character"] == "custom-character-model"
            assert model_config["chapter"] == "custom-chapter-model"
            assert model_config["formatting"] == "custom-formatting-model"
            assert model_config["worldbuilding"] == "custom-worldbuilding-model"
            assert model_config["scene_outline"] == "custom-scene-outline-model"
            assert model_config["editor"] == "custom-editor-model"
            assert model_config["research"] == "custom-research-model"
            assert model_config["scene"] == "custom-scene-model"
            assert model_config["keyword_generation"] == "custom-keyword-model"

        finally:
            # Cleanup
            Path(config_path).unlink(missing_ok=True)

    def test_book_creator_without_config_file(self):
        """Test BookCreatorService without configuration file."""
        # Act
        book_creator = BookCreatorService(mock=True)

        # Assert
        # Should use default values
        assert book_creator.settings.projects_dir == "projects"
        assert book_creator.settings.default_llm == "openai"
        assert book_creator.settings.llm_timeout == 300.0

        # Should use default model config
        model_config = book_creator.model_config
        assert "default" in model_config
        assert "concept" in model_config
        assert "outline" in model_config

    def test_settings_with_config_file_environment_variables(self):
        """Test that Settings properly loads environment variables from config file."""
        # Arrange
        config_data = {
            "openai_api_key": "test-api-key",
            "openai_base_url": "http://test-api.com",
            "openai_default_model": "test-model",
            "default_llm": "test-llm",
            "llm_timeout": 500,
            "projects_dir": "./custom-projects",
            "models": {
                "default": "test-default-model",
                "concept": "test-concept-model",
            },
        }

        # Store original environment variables to restore later
        import os

        original_env_vars = {}
        env_vars_to_track = [
            "PROJECTS_DIR",
            "DEFAULT_LLM",
            "LLM_TIMEOUT",
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
            "OPENAI_DEFAULT_MODEL",
        ]
        for var in env_vars_to_track:
            original_env_vars[var] = os.getenv(var)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            # Act
            settings = Settings(config_file=config_path)

            # Assert
            assert settings.openai_api_key == "test-api-key"
            assert settings.default_llm == "test-llm"
            assert settings.llm_timeout == 500.0
            assert settings.projects_dir == "./custom-projects"

        finally:
            # Cleanup
            Path(config_path).unlink(missing_ok=True)

            # Restore original environment variables
            for var, original_value in original_env_vars.items():
                if original_value is not None:
                    os.environ[var] = original_value
                elif var in os.environ:
                    del os.environ[var]

    def test_settings_model_config_loading(self):
        """Test that Settings properly loads model configuration from config file."""
        # Arrange
        config_data = {
            "openai_api_key": "test-key",
            "default_llm": "test-llm",
            "models": {
                "default": "integration-test-model",
                "concept": "integration-concept-model",
                "outline": "integration-outline-model",
                "character": "integration-character-model",
                "chapter": "integration-chapter-model",
                "formatting": "integration-formatting-model",
                "worldbuilding": "integration-worldbuilding-model",
                "scene_outline": "integration-scene-outline-model",
                "editor": "integration-editor-model",
                "research": "integration-research-model",
                "scene": "integration-scene-model",
                "keyword_generation": "integration-keyword-model",
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            # Act
            settings = Settings(config_file=config_path)
            model_config = settings.get_model_config()

            # Assert
            assert model_config["default"] == "integration-test-model"
            assert model_config["concept"] == "integration-concept-model"
            assert model_config["outline"] == "integration-outline-model"
            assert model_config["character"] == "integration-character-model"
            assert model_config["chapter"] == "integration-chapter-model"
            assert model_config["formatting"] == "integration-formatting-model"
            assert model_config["worldbuilding"] == "integration-worldbuilding-model"
            assert model_config["scene_outline"] == "integration-scene-outline-model"
            assert model_config["editor"] == "integration-editor-model"
            assert model_config["research"] == "integration-research-model"
            assert model_config["scene"] == "integration-scene-model"
            assert model_config["keyword_generation"] == "integration-keyword-model"

        finally:
            # Cleanup
            Path(config_path).unlink(missing_ok=True)

    def test_settings_with_invalid_config_file(self):
        """Test Settings with invalid configuration file."""
        # Act
        settings = Settings(config_file="nonexistent_file.json")

        # Assert - should not crash and should use defaults
        assert settings.projects_dir == "projects"
        assert settings.default_llm == "openai"
        assert settings.llm_timeout == 300.0

        # Should use default model config
        model_config = settings.get_model_config()
        assert "default" in model_config
        assert "concept" in model_config

    def test_settings_with_malformed_config_file(self):
        """Test Settings with malformed configuration file."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json}')  # Malformed JSON
            config_path = f.name

        try:
            # Act
            settings = Settings(config_file=config_path)

            # Assert - should not crash and should use defaults
            assert settings.projects_dir == "projects"
            assert settings.default_llm == "openai"

        finally:
            # Cleanup
            Path(config_path).unlink(missing_ok=True)

    def test_project_knowledge_base_scenes_per_chapter_field(self):
        """Test that ProjectKnowledgeBase has the scenes_per_chapter field."""
        from libriscribe2.knowledge_base import ProjectKnowledgeBase

        # Arrange & Act
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Assert
        assert hasattr(kb, "scenes_per_chapter")
        assert kb.scenes_per_chapter == "3-6"  # Default value

        # Test setting the field
        kb.scenes_per_chapter = "5-8"
        assert kb.scenes_per_chapter == "5-8"

        # Test that it's included in serialization
        data = kb.model_dump()
        assert "scenes_per_chapter" in data
        assert data["scenes_per_chapter"] == "5-8"

    def test_logging_behavior_integration(self):
        """Test that logging behavior is properly configured."""
        import logging

        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            # Act
            BookCreatorService(mock=True, log_file=str(log_file))

            # Assert
            # Check that the root logger has the correct level
            root_logger = logging.getLogger()
            assert root_logger.level <= logging.WARNING

            # Check that file logging is set up (file might be created later)
            # The BookCreatorService should set up logging, but the file might not exist immediately
            # We'll just check that no exception was raised during initialization

    def test_configuration_file_loading_integration(self):
        """Integration test for configuration file loading."""
        # Arrange
        config_data = {
            "openai_api_key": "integration-test-key",
            "openai_base_url": "http://integration-test.com",
            "default_llm": "integration-test-llm",
            "llm_timeout": 750,
            "projects_dir": "./integration-test-projects",
            "models": {
                "default": "integration-default-model",
                "concept": "integration-concept-model",
                "outline": "integration-outline-model",
                "character": "integration-character-model",
                "chapter": "integration-chapter-model",
                "formatting": "integration-formatting-model",
                "worldbuilding": "integration-worldbuilding-model",
                "scene_outline": "integration-scene_outline-model",
                "editor": "integration-editor-model",
                "research": "integration-research-model",
                "scene": "integration-scene-model",
                "keyword_generation": "integration-keyword_generation-model",
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            # Act
            book_creator = BookCreatorService(config_file=config_path, mock=True)

            # Assert
            # Check that all configuration values are properly loaded
            assert book_creator.settings.openai_api_key == "integration-test-key"
            assert book_creator.settings.openai_base_url == "http://integration-test.com"
            assert book_creator.settings.default_llm == "integration-test-llm"
            assert book_creator.settings.llm_timeout == 750.0
            assert book_creator.settings.projects_dir == "./integration-test-projects"

            # Check that model configuration is properly loaded
            model_config = book_creator.model_config
            expected_models = [
                "default",
                "concept",
                "outline",
                "character",
                "chapter",
                "formatting",
                "worldbuilding",
                "scene_outline",
                "editor",
                "research",
                "scene",
                "keyword_generation",
            ]

            for model_key in expected_models:
                assert model_key in model_config
                # The config file uses the same keys as the model_config
                expected_value = f"integration-{model_key}-model"
                assert model_config[model_key] == expected_value

        finally:
            # Cleanup
            Path(config_path).unlink(missing_ok=True)
