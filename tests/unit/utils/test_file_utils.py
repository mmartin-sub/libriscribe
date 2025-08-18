"""
Unit tests for file_utils module.
"""

from unittest.mock import mock_open, patch

import pytest

from libriscribe2.utils.file_utils import (
    extract_json_from_markdown,
    get_chapter_files,
    read_json_file,
    read_markdown_file,
    write_json_file,
    write_markdown_file,
)
from libriscribe2.utils.markdown_validator import MarkdownValidationError


class TestFileUtils:
    """Test cases for file_utils module."""

    def test_read_markdown_file_success(self):
        """Test successful markdown file reading."""
        # Arrange
        mock_content = "# Test Markdown\n\nThis is test content."
        mock_file = mock_open(read_data=mock_content)

        # Act & Assert
        with patch("builtins.open", mock_file):
            content = read_markdown_file("test.md")
            assert content == mock_content

    def test_read_markdown_file_not_found(self):
        """Test reading markdown file that doesn't exist."""
        # Arrange & Act & Assert
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                read_markdown_file("nonexistent.md")

    def test_write_markdown_file_success(self):
        """Test successful markdown file writing."""
        # Arrange
        content = "# Test Markdown\n\nThis is test content."
        mock_file = mock_open()

        # Act & Assert
        with patch("builtins.open", mock_file):
            write_markdown_file("test.md", content)
            mock_file.assert_called_once_with("test.md", "w", encoding="utf-8")

    def test_write_markdown_file_with_validation_disabled(self):
        """Test markdown file writing with validation disabled."""
        # Arrange
        content = "# Test Markdown\n\nThis is test content."
        mock_file = mock_open()

        # Act & Assert
        with patch("builtins.open", mock_file):
            write_markdown_file("test.md", content, validate=False)
            mock_file.assert_called_once_with("test.md", "w", encoding="utf-8")

    def test_write_markdown_file_validation_error_in_tests(self):
        """Test markdown file writing with validation error in test mode."""
        # Arrange
        content = "# Test Markdown\n\nThis is test content."
        mock_file = mock_open()

        # Mock validate_markdown to raise an exception (simulating invalid markdown)
        with patch("libriscribe2.utils.file_utils.validate_markdown") as mock_validate:
            mock_validate.side_effect = MarkdownValidationError("Invalid markdown")

            with patch("builtins.open", mock_file):
                # The function should handle the validation error gracefully
                # and not write the file, but not re-raise the exception
                write_markdown_file("test.md", content)
                # File should not be written if validation fails
                mock_file.assert_not_called()

    def test_extract_json_from_markdown_success(self):
        """Test successful JSON extraction from markdown."""
        # Arrange
        markdown_content = """
        # Test Document

        Some text here.

        ```json
        {
            "title": "Test Book",
            "author": "Test Author"
        }
        ```

        More text here.
        """

        # Act
        result = extract_json_from_markdown(markdown_content)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result.get("title") == "Test Book"
        assert result.get("author") == "Test Author"

    def test_extract_json_from_markdown_no_json(self):
        """Test JSON extraction when no JSON is present."""
        # Arrange
        markdown_content = "# Test Document\n\nNo JSON here."

        # Act
        result = extract_json_from_markdown(markdown_content)

        # Assert
        assert result is None

    def test_extract_json_from_markdown_invalid_json(self):
        """Test JSON extraction with invalid JSON."""
        # Arrange
        markdown_content = """
        # Test Document

        ```json
        {
            "title": "Test Book",
            "author": "Test Author",
        ```
        """

        # Act
        result = extract_json_from_markdown(markdown_content)

        # Assert
        assert result is None

    def test_write_json_file_success(self):
        """Test successful JSON file writing."""
        # Arrange
        data = {"title": "Test Book", "author": "Test Author"}
        mock_file = mock_open()

        # Act & Assert
        with patch("builtins.open", mock_file):
            write_json_file("test.json", data)
            mock_file.assert_called_once_with("test.json", "w", encoding="utf-8")

    def test_read_json_file_success(self):
        """Test successful JSON file reading."""
        # Arrange
        mock_content = '{"title": "Test Book", "author": "Test Author"}'
        mock_file = mock_open(read_data=mock_content)

        # Act & Assert
        with patch("builtins.open", mock_file):
            data = read_json_file("test.json")
            assert data is not None
            assert isinstance(data, dict)
            assert data.get("title") == "Test Book"
            assert data.get("author") == "Test Author"

    def test_read_json_file_not_found(self):
        """Test reading JSON file that doesn't exist."""
        # Arrange & Act & Assert
        with patch("builtins.open", side_effect=FileNotFoundError):
            data = read_json_file("nonexistent.json")
            assert data is None

    def test_get_chapter_files_success(self):
        """Test getting chapter files from project directory."""
        # Arrange
        test_files = ["chapter_1.md", "chapter_2.md", "chapter_3.md", "other.txt"]

        # Act & Assert
        with patch("os.listdir", return_value=test_files):
            result = get_chapter_files("test_project")
            assert len(result) == 3
            assert "test_project/chapter_1.md" in result[0]
            assert "test_project/chapter_2.md" in result[1]
            assert "test_project/chapter_3.md" in result[2]

    def test_get_chapter_files_empty(self):
        """Test getting chapter files from empty directory."""
        # Arrange & Act & Assert
        with patch("os.listdir", return_value=[]):
            result = get_chapter_files("test_project")
            assert result == []

    def test_get_chapter_files_no_chapters(self):
        """Test getting chapter files when no chapter files exist."""
        # Arrange
        test_files = ["other.txt", "config.json", "readme.md"]

        # Act & Assert
        with patch("os.listdir", return_value=test_files):
            result = get_chapter_files("test_project")
            assert result == []
