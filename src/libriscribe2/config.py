# src/libriscribe2/config.py
import json
import logging
import os
from pathlib import Path
from typing import Any

import pyjson5 as json5
import yaml
from dotenv import load_dotenv

from .settings import Settings

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """Handles loading environment variables and configuration from various sources."""

    def __init__(self, config_file: str | None = None):
        """
        Initialize environment configuration.

        Args:
            config_file: Path to configuration file (.env, .yaml, .yml, or .json)
        """
        self.config_file = config_file
        self.config_data: dict[str, Any] = {}
        self.model_config: dict[str, str] = {}

        # Load configurations based on file type
        self._load_config_file()

    def _load_config_file(self) -> None:
        """Load configuration from .env, YAML, or JSON file."""
        if not self.config_file:
            # Load default .env file if it exists
            if Path(".env").exists():
                load_dotenv(".env")
                logger.info("Loaded default .env file")
            return

        config_path = Path(self.config_file)
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {self.config_file}")
            return

        try:
            # Handle .env files
            if config_path.suffix.lower() == ".env":
                load_dotenv(self.config_file, override=True)
                logger.info(f"Loaded environment variables from: {self.config_file}")
                return

            # Handle YAML and JSON files
            if config_path.suffix.lower() in [".json", ".json5"]:
                from .schemas.config_schema import CONFIG_SCHEMA
                from .utils.json_utils import load_json_with_schema

                config_data = load_json_with_schema(str(config_path), CONFIG_SCHEMA)
                if not config_data:
                    logger.error(f"Configuration file {self.config_file} is invalid.")
                    return
            elif config_path.suffix.lower() in [".yaml", ".yml"]:
                with open(config_path, encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}
            else:
                logger.warning(f"Unsupported configuration file format: {config_path.suffix}")
                return

            logger.info(f"Loaded configuration from: {self.config_file}")

            # Store the full configuration data
            self.config_data = config_data
            logger.info(f"Loaded configuration with {len(self.config_data)} entries")

            # Extract model configuration if present
            if "models" in config_data:
                self.model_config = config_data["models"]
                logger.info(f"Loaded model configuration with {len(self.model_config)} entries")

            # Apply configuration to environment variables
            self._apply_config_to_env()

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            logger.error(f"Error parsing configuration file {self.config_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading configuration file {self.config_file}: {e}")

    def _apply_config_to_env(self) -> None:
        """Apply configuration values to environment variables."""
        # Map configuration keys to environment variable names
        env_mapping = {
            "openai_api_key": "OPENAI_API_KEY",
            "openai_base_url": "OPENAI_BASE_URL",
            "default_llm": "DEFAULT_LLM",
            "llm_timeout": "LLM_TIMEOUT",
            "projects_dir": "PROJECTS_DIR",
            "num_chapters": "NUM_CHAPTERS",
            "hide_generated_by": "HIDE_GENERATED_BY",
            "log_llm_output": "LOG_LLM_OUTPUT",
        }

        for config_key, env_var in env_mapping.items():
            if config_key in self.config_data:
                # Always set from config file, overriding environment if present
                config_value = str(self.config_data[config_key])
                os.environ[env_var] = config_value
                # Show full value for short strings, truncated for long ones
                # Special handling for API keys - only show first 5 chars
                if isinstance(self.config_data[config_key], str):
                    if "api_key" in config_key.lower():
                        logger.debug(f"Set {env_var} from config file: {config_value[:5]}...")
                    elif len(config_value) > 40:
                        logger.info(f"Set {env_var} from config file: {config_value[:40]}...")
                    else:
                        logger.info(f"Set {env_var} from config file: {config_value}")
                else:
                    logger.info(f"Set {env_var} from config file: {config_value}")
            else:
                # Log the default value being used from settings
                settings = Settings()
                default_value = getattr(settings, config_key, "N/A")
                logger.debug(f"Config key '{config_key}' not found, using default value: {default_value}")

    def get_model_config(self) -> dict[str, str]:
        """Get model configuration."""
        return self.model_config.copy()

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config_data.get(key, default)

    def get_all_config(self) -> dict[str, Any]:
        """Get all configuration data."""
        return self.config_data.copy()


def load_model_config(model_config_file: str | None = None) -> dict[str, str]:
    """
    Load model configuration from a dedicated model config file.

    Args:
        model_config_file: Path to model configuration file

    Returns:
        Dictionary mapping prompt types to model names

    Example model config file (JSON):
    {
        "default": "gpt-4o-mini",
        "outline": "gpt-4o",
        "worldbuilding": "gpt-4o",
        "chapter": "gpt-4o-mini",
        "formatting": "gpt-4o",
        "concept": "gpt-4o-mini",
        "character": "gpt-4o"
    }
    """
    if not model_config_file:
        return {}

    config_path = Path(model_config_file)
    if not config_path.exists():
        logger.warning(f"Model configuration file not found: {model_config_file}")
        return {}

    try:
        if config_path.suffix.lower() in [".json", ".json5"]:
            with open(config_path, encoding="utf-8") as f:
                content = f.read()
            config_data = json5.loads(content)
        elif config_path.suffix.lower() in [".yaml", ".yml"]:
            with open(config_path, encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
        else:
            logger.warning(f"Unsupported model config file format: {config_path.suffix}")
            return {}

        # Extract only the models section
        model_config = config_data

        # Validate that all values are strings
        validated_config = {}
        for key, value in model_config.items():
            if isinstance(value, str):
                validated_config[key] = value
            else:
                logger.warning(f"Invalid model config value for '{key}': {value} (must be string)")

        logger.info(f"Loaded model configuration from: {model_config_file}")
        return validated_config

    except (json.JSONDecodeError, yaml.YAMLError) as e:
        logger.error(f"Error parsing model configuration file {model_config_file}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading model configuration file {model_config_file}: {e}")
        return {}


def create_example_config_files() -> None:
    """Create example configuration files for reference."""

    # Example JSON configuration
    settings = Settings()
    example_json_config = {
        "openai_api_key": "your-openai-api-key-here",
        "openai_base_url": settings.openai_base_url_default,
        "openai_default_model": settings.openai_default_model_name,
        "default_llm": "openai",
        "llm_timeout": 360,
        "projects_dir": "./projects",
        "hide_generated_by": False,
        "models": {
            "default": settings.openai_default_model_name,
            "outline": "gpt-4o",
            "worldbuilding": "gpt-4o",
            "chapter": settings.openai_default_model_name,
            "formatting": "gpt-4o",
            "concept": settings.openai_default_model_name,
            "character": "gpt-4o",
            "scene_outline": settings.openai_default_model_name,
            "editor": "gpt-4o",
            "research": settings.openai_default_model_name,
            "scene": settings.openai_default_model_name,
            "keyword_generation": settings.openai_default_model_name,
        },
    }

    # Example YAML configuration
    example_yaml_config = f"""# LibriScribe Configuration File
# This file contains configuration settings for LibriScribe

# OpenAI Configuration
openai_api_key: "your-openai-api-key-here"
openai_base_url: "{settings.openai_base_url_default}"
openai_default_model: "{settings.openai_default_model_name}"

# General Settings
default_llm: "openai"
llm_timeout: 360
projects_dir: "./projects"
hide_generated_by: false

# Model Configuration
# Specify which model to use for different types of content generation
models:
  default: "{settings.openai_default_model_name}"      # Default model when none specified
  outline: "gpt-4o"          # For generating book outlines
  worldbuilding: "gpt-4o"    # For worldbuilding content
  chapter: "{settings.openai_default_model_name}"     # For writing chapters
  formatting: "gpt-4o"       # For formatting tasks
  concept: "{settings.openai_default_model_name}"     # For generating book concepts
  character: "gpt-4o"        # For character generation
  scene_outline: "{settings.openai_default_model_name}"  # For generating scene outlines
  editor: "gpt-4o"           # For editing and revision
  research: "{settings.openai_default_model_name}"    # For research tasks
  scene: "{settings.openai_default_model_name}"       # For writing individual scenes
  keyword_generation: "{settings.openai_default_model_name}"  # For generating keywords
"""

    # Example model-only configuration
    example_model_config = {
        "default": settings.openai_default_model_name,
        "outline": "gpt-4o",
        "worldbuilding": "gpt-4o",
        "chapter": settings.openai_default_model_name,
        "formatting": "gpt-4o",
        "concept": settings.openai_default_model_name,
        "character": "gpt-4o",
        "scene_outline": settings.openai_default_model_name,
        "editor": "gpt-4o",
        "research": settings.openai_default_model_name,
        "scene": settings.openai_default_model_name,
        "keyword_generation": settings.openai_default_model_name,
    }

    # Write example files
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)

    # JSON config example
    with open(examples_dir / "config-example.json", "w", encoding="utf-8") as f:
        json.dump(example_json_config, f, indent=2, ensure_ascii=False)

    # YAML config example
    with open(examples_dir / "config.yaml", "w", encoding="utf-8") as f:
        f.write(example_yaml_config)

    # Model config example
    with open(examples_dir / "models.json", "w", encoding="utf-8") as f:
        json.dump(example_model_config, f, indent=2, ensure_ascii=False)

    logger.info("Created example configuration files in examples/ directory")


if __name__ == "__main__":
    # Create example files when run directly
    create_example_config_files()
