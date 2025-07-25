# src/libriscribe/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from .config import EnvironmentConfig, load_model_config

# Manuscript file constants
MANUSCRIPT_FILENAME: str = "manuscript"
MANUSCRIPT_MD_FILENAME: str = MANUSCRIPT_FILENAME + ".md"
MANUSCRIPT_PDF_FILENAME: str = MANUSCRIPT_FILENAME + ".pdf"

REVISED_SUFFIX: str = "revised"  # <--- Add this line
SCENES_JSON: str = "scenes.json"


class Settings(BaseSettings):
    openai_api_key: str = ""  # Optional, can be empty
    projects_dir: str = str(Path(__file__).parent.parent.parent / "projects")
    default_llm: str = "openai"  # Set a default

    openai_base_url: str = "https://api.openai.com/v1"
    openai_default_model: str = "gpt-4o-mini"

    llm_timeout: int = 360  # Default timeout in seconds, important for self hosted

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')  # type: ignore
    
    def __init__(self, env_file: Optional[str] = None, config_file: Optional[str] = None, **kwargs):
        """
        Initialize settings with support for custom environment and configuration files.
        
        Args:
            env_file: Path to custom .env file
            config_file: Path to additional configuration file (JSON/YAML)
            **kwargs: Additional keyword arguments
        """
        # Load environment configuration BEFORE parent initialization
        if env_file or config_file:
            env_config = EnvironmentConfig(env_file=env_file, config_file=config_file)
        else:
            # Load default .env if it exists
            load_dotenv()
            env_config = None
        
        # Initialize the parent class after environment is loaded
        super().__init__(**kwargs)
        
        # Store the environment config for later use
        object.__setattr__(self, '_env_config', env_config)
    
    def get_model_config(self, model_config_file: Optional[str] = None) -> Dict[str, str]:
        """
        Get model configuration from various sources.
        
        Args:
            model_config_file: Path to dedicated model configuration file
            
        Returns:
            Dictionary mapping prompt types to model names
        """
        model_config = {}
        
        # First, try to get from environment config
        if self._env_config:
            model_config.update(self._env_config.get_model_config())
        
        # Then, try to load from dedicated model config file
        if model_config_file:
            dedicated_config = load_model_config(model_config_file)
            model_config.update(dedicated_config)
        
        return model_config
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value from the loaded config.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if self._env_config:
            return self._env_config.get_config_value(key, default)
        return default