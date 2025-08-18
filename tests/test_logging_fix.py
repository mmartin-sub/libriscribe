#!/usr/bin/env python3
"""Test script to verify the logging fix works correctly."""

import shutil
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from libriscribe2.utils.file_utils import dump_content_for_logging


def test_short_content_returned_directly():
    """Test that short content is returned directly."""
    short_content = "This is short content"
    result = dump_content_for_logging(short_content)
    assert result == short_content, "Short content should be returned directly"


def test_long_content_saved_to_logs_directory():
    """Test that long content without project_dir goes to logs directory."""
    long_content = "x" * 500  # Content longer than threshold
    result = dump_content_for_logging(long_content, process_name="test")

    # Check that result is a file path in logs directory
    assert result.startswith("logs/"), f"Expected logs/ path, got: {result}"
    assert Path(result).exists(), f"Log file should exist: {result}"


def test_long_content_saved_to_project_directory():
    """Test that long content with project_dir goes to project directory."""
    project_dir = "test_project"
    Path(project_dir).mkdir(exist_ok=True)

    try:
        long_content = "x" * 500  # Content longer than threshold
        result = dump_content_for_logging(long_content, project_dir=project_dir, process_name="test_project")

        # Check that result is a file path in project directory
        assert result.startswith(project_dir), f"Expected {project_dir}/ path, got: {result}"
        assert Path(result).exists(), f"Log file should exist: {result}"
    finally:
        # Cleanup
        shutil.rmtree(project_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__])
