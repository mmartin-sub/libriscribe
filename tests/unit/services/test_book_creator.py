"""
Unit tests for BookCreatorService.

This module tests the core functionality of the BookCreatorService class,
including book creation workflows, error handling, and service interactions.
"""

from libriscribe2.services.book_creator import BookCreatorService


class TestBookCreatorService:
    """Test cases for BookCreatorService."""

    def test_initialization(self):
        """Test BookCreatorService initialization."""
        # Arrange & Act
        service = BookCreatorService()

        # Assert
        assert service.settings is not None
        assert service.model_config is not None
        assert service.project_manager is None
        assert service.mock is False

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

    def test_display_book_statistics_no_project_manager(self):
        """Test display_book_statistics when project_manager is None."""
        # Arrange
        service = BookCreatorService()
        service.project_manager = None

        # Act & Assert - should not raise exception
        service._display_book_statistics()

    def test_display_book_statistics_no_knowledge_base(self):
        """Test display_book_statistics when project_knowledge_base is None."""
        from unittest.mock import MagicMock

        # Arrange
        service = BookCreatorService()
        service.project_manager = MagicMock()
        service.project_manager.project_knowledge_base = None

        # Act & Assert - should not raise exception
        service._display_book_statistics()

    def test_display_book_statistics_success(self):
        """Test display_book_statistics with valid data."""
        from pathlib import Path
        from unittest.mock import MagicMock, patch

        from libriscribe2.knowledge_base import ProjectKnowledgeBase

        # Arrange
        service = BookCreatorService()
        service.project_manager = MagicMock()

        # Create a mock knowledge base with test data
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
        kb.dynamic_questions = {"q1": "answer1"}
        kb.chapters = {1: MagicMock(title="Chapter 1")}

        service.project_manager.project_knowledge_base = kb
        service.project_manager.project_dir = Path("/test/path")

        # Mock console to capture output
        with patch.object(service.console, "print") as mock_print:
            with patch.object(Path, "exists", return_value=True):
                # Act
                service._display_book_statistics()

                # Assert
                assert mock_print.call_count > 0
                # Check that key information is displayed
                call_args_list = [str(call) for call in mock_print.call_args_list]
                output_text = " ".join(call_args_list)
                assert "Test Book" in output_text
                assert "Fantasy" in output_text
                assert "Fiction" in output_text
