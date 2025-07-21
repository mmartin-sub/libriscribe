# src/libriscribe/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Manuscript file constants
MANUSCRIPT_FILENAME: str = "manuscript"
MANUSCRIPT_MD_FILENAME: str = MANUSCRIPT_FILENAME + ".md"
MANUSCRIPT_PDF_FILENAME: str = MANUSCRIPT_FILENAME + ".pdf"

REVISED_SUFFIX: str = "revised"  # <--- Add this line
SCENES_JSON:str = "scenes.json"
class Settings(BaseSettings):
    openai_api_key: str = ""  # Optional, can be empty
    projects_dir: str = str(Path(__file__).parent.parent.parent / "projects")
    default_llm: str = "openai" # Set a default

    openai_base_url: str = "https://api.openai.com/v1"
    openai_default_model: str = "gpt-4o-mini"

    llm_timeout: int = 360  # Default timeout in seconds, important for self hosted

    model_config = SettingsConfigDict(env_file=".env", extra='ignore') # type: ignore