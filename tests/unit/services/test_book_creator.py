"""
Unit tests for BookCreatorService.

This module tests the core functionality of the BookCreatorService class,
including book creation workflows, error handling, and service interactions.
"""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from libriscribe2.services.book_creator import BookCreatorService


class TestBookCreatorService:
    """Test cases for BookCreatorService."""

    def test_initialization_with_mock(self):
        """Test BookCreatorService initialization with mock enabled."""
        # Arrange & Act
        service = BookCreatorService(mock=True)

        # Assert
        assert service.settings is not None
        assert service.model_config is not None
        assert service.mock is True

    def test_slugify(self):
        """Test slugify method."""
        # Arrange
        service = BookCreatorService()

        # Act & Assert
        assert service._slugify("Test Book Title") == "test-book-title"
        assert service._slugify("Special Characters!@#") == "special-characters"
        assert service._slugify("Multiple   Spaces") == "multiple-spaces"

    def test_generate_unique_folder_name(self):
        """Test generate_unique_folder_name method."""
        # Arrange
        service = BookCreatorService()

        # Act
        result = service._generate_unique_folder_name("Test Book")

        # Assert
        assert "test-book" in result
        assert len(result) > 10  # Should have timestamp and hash

    def test_is_valid_project_name(self):
        """Test is_valid_project_name method."""
        # Arrange
        service = BookCreatorService()

        # Act & Assert
        assert service._is_valid_project_name("valid-project") is True
        assert service._is_valid_project_name("valid_project") is True
        assert service._is_valid_project_name("valid project") is True
        assert service._is_valid_project_name("invalid@project") is False
        assert service._is_valid_project_name("invalid#project") is False

    def test_create_project_directory_safely(self, tmp_path):
        """Test that _create_project_directory_safely creates a directory."""
        service = BookCreatorService()
        project_dir = tmp_path / "test-project"
        result_dir = service._create_project_directory_safely(project_dir, "test-project")
        assert result_dir.exists()

    def test_create_project_directory_safely_with_existing_dir(self, tmp_path):
        """Test that _create_project_directory_safely raises an error for existing, non-empty dir."""
        service = BookCreatorService()
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        (project_dir / "file.txt").touch()
        with pytest.raises(ValueError):
            service._create_project_directory_safely(project_dir, "test-project")

    def test_setup_logging(self, tmp_path):
        """Test that setup_logging sets up logging."""
        service = BookCreatorService()
        project_dir = tmp_path / "test-project"
        service.setup_logging(project_dir)
        assert (project_dir / "book_creation.log").exists()

    def test_create_knowledge_base(self):
        """Test that _create_knowledge_base creates a knowledge base."""
        service = BookCreatorService()
        args = {"title": "Test Title"}
        kb = service._create_knowledge_base(args, "test-project")
        assert kb.title == "Test Title"
        assert kb.project_name == "test-project"

    @pytest.mark.asyncio
    @patch("libriscribe2.services.book_creator.ProjectManagerAgent")
    async def test_acreate_book(self, mock_pm_agent, tmp_path):
        """Test that acreate_book creates a book."""
        service = BookCreatorService()
        mock_pm_agent.return_value.acreate_book = AsyncMock(return_value=True)
        args = {"title": "Test Title", "all": True}
        with patch.object(service, "_execute_generation_steps", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = True
            result = await service.acreate_book(args)
            assert result is True
            mock_execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_display_book_statistics_with_counts(self, tmp_path):
        """Test that _display_book_statistics includes word and character counts."""
        from libriscribe2.knowledge_base import ProjectKnowledgeBase

        service = BookCreatorService()

        # Setup a mock project manager and knowledge base
        pm = MagicMock()
        pm.project_dir = tmp_path
        kb = ProjectKnowledgeBase(project_name="test_stats", title="Stats Book")
        pm.project_knowledge_base = kb
        service.project_manager = pm

        # Create a dummy manuscript file
        manuscript_content = "Hello world, this is a test."
        (tmp_path / "manuscript.md").write_text(manuscript_content)

        with patch.object(service.console, "print") as mock_print:
            # Act
            service._display_book_statistics()

            # Assert
            output = ""
            for call in mock_print.call_args_list:
                arg = call.args[0]
                if hasattr(arg, "renderable"):
                    output += str(arg.renderable)
                else:
                    output += str(arg)

            assert "Word Count:" in output
            assert "Character Count:" in output
            # 6 words, 29 characters
            assert "6" in output
            assert "28" in output
