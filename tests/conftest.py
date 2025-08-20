"""
Pytest configuration for LibriScribe2 tests.

This file sets up test-specific configurations and fixtures.
"""

import logging
import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from libriscribe2.settings import Settings

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def test_projects_dir() -> Path:
    """Create and return the test projects directory."""
    test_dir = Path("tests/output")
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


@pytest.fixture(scope="session")
def test_settings(test_projects_dir: Path) -> Generator[Settings, None, None]:
    """Create test-specific settings."""
    # Create a temporary config file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        test_config = {
            "projects_dir": str(test_projects_dir),
            "num_chapters": 3,
            "scenes_per_chapter": "2-4",
            "environment": "testing",
            "llm_timeout": 30,
            "mock": True,
            "models": {
                "default": "mock-model",
                "character": "mock-model",
                "outline": "mock-model",
                "chapter": "mock-model",
                "formatting": "mock-model",
                "concept": "mock-model",
                "title_generation": "mock-model",
            },
        }
        import json

        json.dump(test_config, f)
        config_path = f.name

    try:
        # Create settings with test config
        settings = Settings(config_file=config_path)
        yield settings
    finally:
        # Clean up temporary config file
        try:
            os.unlink(config_path)
        except OSError as e:
            logger.warning(f"Failed to clean up temporary config file {config_path}: {e}")


@pytest.fixture(autouse=True)
def cleanup_test_projects(test_projects_dir: Path) -> Generator[None, None, None]:
    """Clean up test projects after each test."""
    yield

    # Clean up test projects after each test
    if test_projects_dir.exists():
        for project_dir in test_projects_dir.iterdir():
            if project_dir.is_dir():
                try:
                    import shutil

                    shutil.rmtree(project_dir)
                except OSError as e:
                    logger.warning(f"Failed to clean up test project directory {project_dir}: {e}")


@pytest.fixture
def mock_llm_response() -> str:
    """Provide a mock LLM response for testing."""
    return """```json
[
    {
        "name": "Test Character",
        "age": "25",
        "physical_description": "Tall and athletic",
        "personality_traits": "Brave, loyal, curious",
        "background": "Test background",
        "motivations": "Test motivations",
        "relationships": {"Other": "Friend"},
        "role": "Protagonist",
        "internal_conflicts": "Test conflicts",
        "external_conflicts": "Test external conflicts",
        "character_arc": "Test character arc"
    }
]
```"""


@pytest.fixture
def mock_outline_response() -> str:
    """Provide a mock outline response for testing."""
    return """# Chapter Outline

## Chapter 1: The Beginning
- Scene 1: Introduction
- Scene 2: Conflict setup

## Chapter 2: The Middle
- Scene 1: Rising action
- Scene 2: Climax

## Chapter 3: The End
- Scene 1: Resolution
- Scene 2: Conclusion"""
