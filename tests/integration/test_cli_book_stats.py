"""
Integration tests for CLI book-stats command.

This module tests the book-stats command functionality including
project loading and statistics display.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from libriscribe2.cli import app
from libriscribe2.knowledge_base import ProjectKnowledgeBase


class TestCLIBookStats:
    """Test cases for CLI book-stats command."""

    def setup_method(self):
        """Set up test method."""
        self.runner = CliRunner()

    def test_book_stats_success(self):
        """Test book-stats command with valid project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test project
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir(parents=True, exist_ok=True)

            # Create project knowledge base and save it
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

            from libriscribe2.settings import Settings

            settings = Settings()
            project_data_file = project_dir / settings.project_data_filename
            kb.save_to_file(str(project_data_file))

            # Mock settings to use temp directory
            with patch("libriscribe2.cli.Settings") as mock_settings:
                # Configure the mock to return the temporary directory and the correct filename
                mock_settings.return_value.projects_dir = temp_dir
                mock_settings.return_value.project_data_filename = settings.project_data_filename

                # Act
                result = self.runner.invoke(app, ["book-stats", "--project-name", "test_project"])

                # Assert
                assert result.exit_code == 0
                assert "Test Book" in result.stdout
                assert "Fantasy" in result.stdout
                assert "Fiction" in result.stdout

    def test_book_stats_project_not_found(self):
        """Test book-stats command with non-existent project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock settings to use temp directory
            with patch("libriscribe2.cli.Settings") as mock_settings:
                mock_settings.return_value.projects_dir = temp_dir

                # Act
                result = self.runner.invoke(app, ["book-stats", "--project-name", "nonexistent_project"])

                # Assert
                assert result.exit_code == 0  # Command doesn't exit with error code
                assert "not found" in result.stdout

    def test_book_stats_corrupted_project_data(self):
        """Test book-stats command with corrupted project data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test project with corrupted data
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir(parents=True, exist_ok=True)

            # Create corrupted project data file
            from libriscribe2.settings import Settings

            settings = Settings()
            project_data_file = project_dir / settings.project_data_filename
            project_data_file.write_text("invalid json")

            # Mock settings to use temp directory
            with patch("libriscribe2.cli.Settings") as mock_settings:
                mock_settings.return_value.projects_dir = temp_dir

                # Act
                result = self.runner.invoke(app, ["book-stats", "--project-name", "test_project"])

                # Assert
                assert result.exit_code == 0  # Command doesn't exit with error code
                assert "Error:" in result.stdout
