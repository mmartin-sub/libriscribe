# src/libriscribe/config.py
import json
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """Handles loading environment variables and configuration from various sources."""
    
    def __init__(self, env_file: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize environment configuration.
        
        Args:
            env_file: Path to custom .env file
            config_file: Path to additional configuration file (JSON/YAML)
        """
        self.env_file = env_file
        self.config_file = config_file
        self.config_data: Dict[str, Any] = {}
        self.model_config: Dict[str, str] = {}
        
        # Load configurations
        self._load_env_file()
        self._load_config_file()
    
    def _load_env_file(self) -> None:
        """Load environment variables from .env file."""
        if self.env_file:
            if Path(self.env_file).exists():
                load_dotenv(self.env_file, override=True)
                logger.info(f"Loaded environment variables from: {self.env_file}")
            else:
                logger.warning(f"Environment file not found: {self.env_file}")
        else:
            # Load default .env file if it exists
            if Path(".env").exists():
                load_dotenv(".env")
                logger.info("Loaded default .env file")
    
    def _load_config_file(self) -> None:
        """Load additional configuration from JSON or YAML file."""
        if not self.config_file:
            return
            
        config_path = Path(self.config_file)
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {self.config_file}")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    self.config_data = yaml.safe_load(f) or {}
                elif config_path.suffix.lower() == '.json':
                    self.config_data = json.load(f)
                else:
                    logger.warning(f"Unsupported configuration file format: {config_path.suffix}")
                    return
            
            logger.info(f"Loaded configuration from: {self.config_file}")
            
            # Extract model configuration if present
            if 'models' in self.config_data:
                self.model_config = self.config_data['models']
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
            'openai_api_key': 'OPENAI_API_KEY',
            'openai_base_url': 'OPENAI_BASE_URL',
            'openai_default_model': 'OPENAI_DEFAULT_MODEL',
            'default_llm': 'DEFAULT_LLM',
            'llm_timeout': 'LLM_TIMEOUT',
            'projects_dir': 'PROJECTS_DIR'
        }
        
        for config_key, env_var in env_mapping.items():
            if config_key in self.config_data:
                # Only set if not already set in environment
                if not os.getenv(env_var):
                    os.environ[env_var] = str(self.config_data[config_key])
                    logger.debug(f"Set {env_var} from config file")
    
    def get_model_config(self) -> Dict[str, str]:
        """Get model configuration."""
        return self.model_config.copy()
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config_data.get(key, default)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration data."""
        return self.config_data.copy()


def load_model_config(model_config_file: Optional[str] = None) -> Dict[str, str]:
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
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                model_config = yaml.safe_load(f) or {}
            elif config_path.suffix.lower() == '.json':
                model_config = json.load(f)
            else:
                logger.warning(f"Unsupported model config file format: {config_path.suffix}")
                return {}
        
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
    example_json_config = {
        "openai_api_key": "your-openai-api-key-here",
        "openai_base_url": "https://api.openai.com/v1",
        "openai_default_model": "gpt-4o-mini",
        "default_llm": "openai",
        "llm_timeout": 360,
        "projects_dir": "./projects",
        "models": {
            "default": "gpt-4o-mini",
            "outline": "gpt-4o",
            "worldbuilding": "gpt-4o",
            "chapter": "gpt-4o-mini",
            "formatting": "gpt-4o",
            "concept": "gpt-4o-mini",
            "character": "gpt-4o"
        }
    }
    
    # Example YAML configuration
    example_yaml_config = """# LibriScribe Configuration File
# This file contains configuration settings for LibriScribe

# OpenAI Configuration
openai_api_key: "your-openai-api-key-here"
openai_base_url: "https://api.openai.com/v1"
openai_default_model: "gpt-4o-mini"

# General Settings
default_llm: "openai"
llm_timeout: 360
projects_dir: "./projects"

# Model Configuration
# Specify which model to use for different types of content generation
models:
  default: "gpt-4o-mini"      # Default model when none specified
  outline: "gpt-4o"          # For generating book outlines
  worldbuilding: "gpt-4o"    # For worldbuilding content
  chapter: "gpt-4o-mini"     # For writing chapters
  formatting: "gpt-4o"       # For formatting tasks
  concept: "gpt-4o-mini"     # For generating book concepts
  character: "gpt-4o"        # For character generation
"""
    
    # Example model-only configuration
    example_model_config = {
        "default": "gpt-4o-mini",
        "outline": "gpt-4o",
        "worldbuilding": "gpt-4o",
        "chapter": "gpt-4o-mini",
        "formatting": "gpt-4o",
        "concept": "gpt-4o-mini",
        "character": "gpt-4o"
    }
    
    # Write example files
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    # JSON config example
    with open(examples_dir / "config.json", 'w', encoding='utf-8') as f:
        json.dump(example_json_config, f, indent=2)
    
    # YAML config example
    with open(examples_dir / "config.yaml", 'w', encoding='utf-8') as f:
        f.write(example_yaml_config)
    
    # Model config example
    with open(examples_dir / "models.json", 'w', encoding='utf-8') as f:
        json.dump(example_model_config, f, indent=2)
    
    logger.info("Created example configuration files in examples/ directory")


if __name__ == "__main__":
    # Create example files when run directly
    create_example_config_files()