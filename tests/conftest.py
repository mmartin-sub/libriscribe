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


def pytest_addoption(parser):
    """Add a command-line option to specify the test config file."""
    parser.addoption(
        "--test-config-file",
        action="store",
        default="tests/.config-test.json",
        help="Path to the test configuration file.",
    )


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


@pytest.fixture(scope="function")
def test_config(pytestconfig) -> dict:
    """
    Loads the test configuration from the file specified by --test-config-file,
    if it exists, otherwise returns a default mock configuration.
    """
    config_path = Path(pytestconfig.getoption("--test-config-file"))
    if config_path.is_file():
        with open(config_path) as f:
            import json

            try:
                return json.load(f)
            except json.JSONDecodeError:
                pytest.fail(f"Failed to decode {config_path}. Please ensure it is a valid JSON file.")
    else:
        # Return a default mock configuration if the file doesn't exist
        return {"default_llm": "mock", "mock": True}


@pytest.fixture(scope="function")
def integration_settings(pytestconfig) -> Generator[Settings, None, None]:
    """
    Creates a Settings instance for integration tests.
    If the config file specified by --test-config-file exists, it's used.
    Otherwise, mock settings are created.

    This fixture also handles cleaning up environment variables to ensure
    test isolation.
    """
    import os

    config_path = Path(pytestconfig.getoption("--test-config-file"))

    env_mapping = {
        "openai_api_key": "OPENAI_API_KEY",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "google_api_key": "GOOGLE_API_KEY",
        "openai_base_url": "OPENAI_BASE_URL",
        "openai_default_model": "OPENAI_DEFAULT_MODEL",
        "default_llm": "DEFAULT_LLM",
        "llm_timeout": "LLM_TIMEOUT",
    }

    original_env = {key: os.environ.get(key) for key in env_mapping.values()}

    try:
        if config_path.is_file():
            settings = Settings(config_file=str(config_path))
        else:
            settings = Settings(mock=True)

        yield settings

    finally:
        # Restore original environment
        for key, value in original_env.items():
            if value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = value


@pytest.fixture
def _handle_llm_client_error():
    """
    A fixture that wraps test execution in a try-except block to catch
    LLMClientError and provide more informative messages.
    """
    from libriscribe2.utils.llm_client import LLMClientError

    try:
        yield
    except LLMClientError as e:
        if "invalid_api_key" in str(e) or "401" in str(e):
            pytest.skip("Skipping test due to an invalid API key. Please check the key in your .config-test.json.")
        elif "rate_limit" in str(e):
            pytest.skip("Skipping test due to rate limiting. Check your API plan or try again later.")
        else:
            pytest.fail(f"LLMClientError occurred during test execution: {e}")
