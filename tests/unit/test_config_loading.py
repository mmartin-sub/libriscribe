import json
import tempfile
from pathlib import Path

import pytest

from libriscribe2.config import load_model_config
from libriscribe2.settings import Settings


def test_load_model_config_valid():
    """Test `load_model_config` with a valid models.json file."""
    # Arrange
    model_config_data = {
        "default": "gpt-4o-mini",
        "outline": "gpt-4o",
        "worldbuilding": "claude-3-opus",
        "chapter": "gpt-4o-mini",
        "formatting": "gpt-4o",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(model_config_data, f)
        temp_model_config_file = f.name

    try:
        # Act
        model_config = load_model_config(temp_model_config_file)

        # Assert
        assert model_config == model_config_data

    finally:
        # Clean up
        Path(temp_model_config_file).unlink()


def test_missing_config_falls_back_to_mock(integration_settings):
    """
    Test that the integration_settings fixture falls back to mock mode
    when the config file is missing.
    """
    assert integration_settings.mock is True


def test_custom_config_loading(tmp_path, pytestconfig):
    """
    Test that the integration_settings fixture correctly loads a custom config file.
    """
    custom_config_content = {
        "default_llm": "anthropic",
        "anthropic_api_key": "dummy-anthropic-key",
        "models": {"default": "claude-3-opus-20240229"},
    }
    custom_config_path = tmp_path / "custom_config.json"
    with open(custom_config_path, "w") as f:
        json.dump(custom_config_content, f)

    # Use a new Settings object to avoid caching
    settings = Settings(config_file=str(custom_config_path))

    assert settings.default_llm == "anthropic"
    assert settings.anthropic_api_key == "dummy-anthropic-key"
    assert settings.get_model_config()["default"] == "claude-3-opus-20240229"


def test_mock_mode_from_config(tmp_path):
    """
    Test that the Settings class correctly enables mock mode when
    default_llm is "mock" in the config file.
    """
    mock_config_content = {
        "default_llm": "mock",
        "openai_api_key": "dummy-key",
        "models": {"default": "mock-model"},
    }
    mock_config_path = tmp_path / "mock_config.json"
    with open(mock_config_path, "w") as f:
        json.dump(mock_config_content, f)

    settings = Settings(config_file=str(mock_config_path))
    assert settings.mock is True
    assert settings.default_llm == "mock"


def test_api_key_loading(tmp_path):
    """
    Test that the Settings class correctly loads API keys from the config file.
    """
    api_key_config_content = {
        "default_llm": "openai",
        "openai_api_key": "dummy-openai-key",
        "anthropic_api_key": "dummy-anthropic-key",
        "google_api_key": "dummy-google-key",
        "models": {"default": "gpt-4o-mini"},
    }
    api_key_config_path = tmp_path / "api_key_config.json"
    with open(api_key_config_path, "w") as f:
        json.dump(api_key_config_content, f)

    settings = Settings(config_file=str(api_key_config_path))

    assert settings.openai_api_key == "dummy-openai-key"
    assert settings.anthropic_api_key == "dummy-anthropic-key"
    assert settings.google_api_key == "dummy-google-key"
