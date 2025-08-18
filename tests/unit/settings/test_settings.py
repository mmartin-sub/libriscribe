"""
Unit tests for Settings class configuration loading.

This module tests the core functionality of the Settings class,
including configuration file loading and model configuration.
"""

import json
import tempfile
from pathlib import Path

from libriscribe2.settings import Settings


class TestSettings:
    """Test cases for Settings class."""

    def test_initialization_without_config_file(self):
        """Test Settings initialization without config file."""
        # Arrange & Act
        settings = Settings()

        # Assert
        assert settings.projects_dir == "projects"
        assert settings.default_llm == "openai"
        assert settings.llm_timeout == 300.0
        assert settings.environment == "production"
        assert settings.project_type == "novel"
        assert settings.auto_size is True
        assert settings.num_chapters == 15
        assert settings.scenes_per_chapter == "3-6"
        assert settings.mock is False

    def test_initialization_with_config_file(self):
        """Test Settings initialization with config file."""
        # Arrange
        config_data = {
            "openai_api_key": "test-key",
            "openai_base_url": "http://test.com",
            "openai_default_model": "test-model",
            "default_llm": "test-llm",
            "llm_timeout": 600,
            "projects_dir": "./test-projects",
            "models": {
                "default": "test-default-model",
                "concept": "test-concept-model",
                "outline": "test-outline-model",
                "character": "test-character-model",
                "chapter": "test-chapter-model",
                "formatting": "test-formatting-model",
                "worldbuilding": "test-worldbuilding-model",
                "scene_outline": "test-scene-outline-model",
                "editor": "test-editor-model",
                "research": "test-research-model",
                "scene": "test-scene-model",
                "keyword_generation": "test-keyword-model",
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            # Act
            settings = Settings(config_file=config_path)

            # Assert
            assert settings.openai_api_key == "test-key"
            assert settings.default_llm == "test-llm"
            assert settings.llm_timeout == 600.0
            assert settings.projects_dir == "./test-projects"
            assert hasattr(settings, "_config_file")
            assert settings._config_file == config_path

        finally:
            # Cleanup
            Path(config_path).unlink(missing_ok=True)

    def test_get_model_config_without_config_file(self):
        """Test get_model_config without config file."""
        # Arrange
        settings = Settings()

        # Act
        model_config = settings.get_model_config()

        # Assert
        assert "default" in model_config
        assert "concept" in model_config
        assert "outline" in model_config
        assert "character" in model_config
        assert "chapter" in model_config
        assert "formatting" in model_config
        assert "worldbuilding" in model_config
        assert "scene_outline" in model_config
        assert "editor" in model_config
        assert "research" in model_config
        assert "scene" in model_config
        assert "keyword_generation" in model_config

    def test_get_model_config_with_config_file(self):
        """Test get_model_config with config file."""
        # Arrange
        config_data = {
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
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            settings = Settings(config_file=config_path)

            # Act
            model_config = settings.get_model_config()

            # Assert
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

    def test_get_model_config_with_specific_file(self):
        """Test get_model_config with specific model config file."""
        # Arrange
        model_config_data = {
            "models": {
                "default": "specific-default-model",
                "concept": "specific-concept-model",
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(model_config_data, f)
            model_config_path = f.name

        try:
            settings = Settings()

            # Act
            model_config = settings.get_model_config(model_config_path)

            # Assert
            assert model_config["default"] == "specific-default-model"
            assert model_config["concept"] == "specific-concept-model"

        finally:
            # Cleanup
            Path(model_config_path).unlink(missing_ok=True)

    def test_get_model_config_with_invalid_file(self):
        """Test get_model_config with invalid config file."""
        # Arrange
        settings = Settings()

        # Act
        model_config = settings.get_model_config("nonexistent_file.json")

        # Assert
        assert model_config == {}

    def test_get_project_type_config(self):
        """Test get_project_type_config for different project types."""
        # Arrange
        settings = Settings()

        # Act & Assert for different project types
        novel_config = settings.get_project_type_config()
        assert novel_config["num_chapters"] == 12
        assert novel_config["scenes_per_chapter"] == "4-7"
        assert novel_config["book_length"] == "high"

        # Test with different project type
        settings.project_type = "short_story"
        short_story_config = settings.get_project_type_config()
        assert short_story_config["num_chapters"] == 1
        assert short_story_config["scenes_per_chapter"] == "2-4"
        assert short_story_config["book_length"] == "short"

    def test_get_effective_chapters(self):
        """Test get_effective_chapters method."""
        # Arrange
        settings = Settings()

        # Act & Assert with auto_size=True
        assert settings.get_effective_chapters() == 12  # novel default

        # Act & Assert with auto_size=False
        settings.auto_size = False
        settings.num_chapters = 5
        assert settings.get_effective_chapters() == 5

    def test_get_effective_scenes_per_chapter(self):
        """Test get_effective_scenes_per_chapter method."""
        # Arrange
        settings = Settings()

        # Act & Assert with auto_size=True
        assert settings.get_effective_scenes_per_chapter() == "4-7"  # novel default

        # Act & Assert with auto_size=False
        settings.auto_size = False
        settings.scenes_per_chapter = "5-8"
        assert settings.get_effective_scenes_per_chapter() == "5-8"

    def test_get_effective_book_length(self):
        """Test get_effective_book_length method."""
        # Arrange
        settings = Settings()

        # Act & Assert
        assert settings.get_effective_book_length() == "high"  # novel default

        # Test with different project type
        settings.project_type = "short_story"
        assert settings.get_effective_book_length() == "short"
