# libriscribe/src/settings.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    openai_api_key: str
    projects_dir: str = str(Path(__file__).parent.parent.parent / "projects")

    class Config:
        env_file = ".env"