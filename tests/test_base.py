# tests/test_base.py
"""Base test class with common test utilities and fixtures."""

import logging
import os
import tempfile
from typing import Any
from unittest.mock import MagicMock

import pytest

from libriscribe2.knowledge_base import ProjectKnowledgeBase
from libriscribe2.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)


class BaseTestCase:
    """Base class for all test cases with common utilities."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def sample_knowledge_base(self) -> ProjectKnowledgeBase:
        """Create a sample knowledge base for testing."""
        return ProjectKnowledgeBase(
            project_name="test_project",
            title="Test Book",
            genre="Fantasy",
            description="A test book for unit testing",
            category="Fiction",
            language="English",
            num_characters=3,
            num_chapters=3,  # Reduced for testing
            worldbuilding_needed=True,
            book_length="Novel",
            scenes_per_chapter="2-4",  # Test-specific scene range
        )

    @pytest.fixture
    def mock_llm_client(self) -> MagicMock:
        """Create a mock LLM client for testing."""
        mock_client = MagicMock(spec=LLMClient)
        mock_client.generate_content.return_value = "Mock response"
        mock_client.generate_content_with_json_repair.return_value = '{"test": "data"}'
        return mock_client

    def create_temp_file(self, content: str, suffix: str = ".txt") -> str:
        """Create a temporary file with given content."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    def cleanup_temp_file(self, file_path: str) -> None:
        """Clean up a temporary file."""
        try:
            os.unlink(file_path)
        except OSError as e:
            logger.warning(f"Failed to clean up temporary file {file_path}: {e}")

    def assert_valid_json(self, data: Any) -> None:
        """Assert that data is valid JSON structure."""
        assert data is not None
        assert isinstance(data, dict | list)

    def assert_knowledge_base_valid(self, kb: ProjectKnowledgeBase) -> None:
        """Assert that a knowledge base has valid required fields."""
        assert kb.project_name
        assert kb.title
        assert kb.genre
        assert kb.description
        assert kb.category
        assert kb.language

    def create_test_project_structure(self, temp_dir: str) -> dict[str, str | dict[str, str]]:
        """Create a test project directory structure."""
        project_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(project_dir, exist_ok=True)

        # Create subdirectories
        chapters_dir = os.path.join(project_dir, "chapters")
        os.makedirs(chapters_dir, exist_ok=True)

        # Create sample files
        files = {
            "project_data.json": '{"project_name": "test", "title": "Test Book"}',
            "chapters/chapter_1.md": "# Chapter 1\n\nTest content.",
            "chapters/chapter_2.md": "# Chapter 2\n\nMore test content.",
        }

        for file_path, content in files.items():
            full_path = os.path.join(project_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        return {
            "project_dir": project_dir,
            "chapters_dir": chapters_dir,
            "files": files,
        }

    def assert_file_exists(self, file_path: str) -> None:
        """Assert that a file exists."""
        assert os.path.exists(file_path), f"File does not exist: {file_path}"

    def assert_file_content(self, file_path: str, expected_content: str) -> None:
        """Assert that a file contains expected content."""
        self.assert_file_exists(file_path)
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        assert content == expected_content, f"File content mismatch in {file_path}"

    def assert_directory_exists(self, dir_path: str) -> None:
        """Assert that a directory exists."""
        assert os.path.exists(dir_path), f"Directory does not exist: {dir_path}"
        assert os.path.isdir(dir_path), f"Path is not a directory: {dir_path}"


class ValidationTestCase(BaseTestCase):
    """Base class for validation-related tests."""

    def test_validate_title_valid(self):
        """Test valid title validation."""
        from libriscribe2.utils.validation_mixin import ValidationMixin

        valid_titles = ["Test Book", "  My Title  ", "A Very Long Title"]
        for title in valid_titles:
            result = ValidationMixin.validate_title(title)
            assert result == title.strip()

    def test_validate_title_invalid(self):
        """Test invalid title validation."""
        from libriscribe2.utils.validation_mixin import ValidationMixin

        invalid_titles = ["", "   ", None]
        for title in invalid_titles:
            with pytest.raises(ValueError):
                ValidationMixin.validate_title(title)

    def test_validate_language_valid(self):
        """Test valid language validation."""
        from libriscribe2.utils.validation_mixin import ValidationMixin

        valid_languages = ["English", "Spanish", "  French  "]
        for language in valid_languages:
            result = ValidationMixin.validate_language(language)
            assert result == language.strip()

    def test_validate_language_invalid(self):
        """Test invalid language validation."""
        from libriscribe2.utils.validation_mixin import ValidationMixin

        invalid_languages = ["", "   ", None]
        for language in invalid_languages:
            with pytest.raises(ValueError):
                ValidationMixin.validate_language(language)
