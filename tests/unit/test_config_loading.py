import json
import tempfile
from pathlib import Path

from libriscribe2.config import load_model_config


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
