"""
Integration tests for automatic statistics display in book creation.

This module tests that statistics are automatically displayed after
successful book creation.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from libriscribe2.services.book_creator import BookCreatorService


class TestBookCreationStatistics:
    """Test cases for automatic statistics display in book creation."""

    @patch("libriscribe2.services.book_creator.ProjectManagerAgent")
    @pytest.mark.asyncio
    async def test_create_book_displays_statistics_on_success(self, mock_project_manager_class):
        """Test that statistics are displayed when book creation succeeds."""
        # Arrange
        # Create mock project manager instance
        mock_project_manager = MagicMock()
        mock_project_manager_class.return_value = mock_project_manager

        # Create mock knowledge base with test data
        from libriscribe2.knowledge_base import ProjectKnowledgeBase

        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.genre = "Fantasy"
        kb.language = "English"
        kb.category = "Fiction"
        kb.book_length = "Novel"
        kb.num_characters = 5
        kb.num_chapters = 10
        kb.worldbuilding_needed = True
        kb.review_preference = "yes"
        kb.description = "A test book description"

        mock_project_manager.project_knowledge_base = kb
        mock_project_manager.project_dir = Path("/test/path")

        # Create service
        service = BookCreatorService(mock=True)

        # Mock console to capture output
        with patch.object(service.console, "print") as mock_print:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Act
                args = {
                    "title": "Test Book",
                    "project_name": None,
                    "auto_title": False,
                    "category": "Fiction",
                    "project_type": "novel",
                    "genre": "Fantasy",
                    "description": "A test book",
                    "language": "English",
                    "chapters": None,
                    "characters": None,
                    "target_audience": "General",
                    "worldbuilding": False,
                    "generate_concept": False,
                    "generate_outline": False,
                    "generate_characters": False,
                    "generate_worldbuilding": False,
                    "write_chapters": False,
                    "format_book": False,
                    "scenes_per_chapter": None,
                    "user": None,
                    "all": True,
                }
                # Patch _execute_generation_steps to return True
                with patch.object(service, "_execute_generation_steps", return_value=True):
                    result = await service.acreate_book(args)
                # Assert
                assert result is True
                # Check that statistics were displayed
                assert mock_print.call_count > 0
                call_args_list = [str(call) for call in mock_print.call_args_list]
                output_text = " ".join(call_args_list)
                assert "Statistics for" in output_text or "Test Book" in output_text

    @patch("libriscribe2.services.book_creator.ProjectManagerAgent")
    @pytest.mark.asyncio
    async def test_create_book_no_statistics_on_failure(self, mock_project_manager_class):
        """Test that statistics are not displayed when book creation fails."""
        # Arrange
        # Create service
        service = BookCreatorService(mock=True)
        # Patch _execute_generation_steps to raise Exception
        with patch.object(service, "_execute_generation_steps", side_effect=Exception("Creation failed")):
            # Mock console to capture output
            with patch.object(service.console, "print") as mock_print:
                with tempfile.TemporaryDirectory() as temp_dir:
                    args = {
                        "title": "Test Book",
                        "project_name": None,
                        "auto_title": False,
                        "category": "Fiction",
                        "project_type": "novel",
                        "genre": "Fantasy",
                        "description": "A test book",
                        "language": "English",
                        "chapters": None,
                        "characters": None,
                        "target_audience": "General",
                        "worldbuilding": False,
                        "generate_concept": False,
                        "generate_outline": False,
                        "generate_characters": False,
                        "generate_worldbuilding": False,
                        "write_chapters": False,
                        "format_book": False,
                        "scenes_per_chapter": None,
                        "user": None,
                        "all": True,
                    }
                    with pytest.raises(RuntimeError):
                        await service.acreate_book(args)
                    # Check that statistics were not displayed
                    call_args_list = [str(call) for call in mock_print.call_args_list]
                    output_text = " ".join(call_args_list)
                    assert "Statistics for" not in output_text
