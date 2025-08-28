import sys
from pathlib import Path

from libriscribe2.settings import Settings
from libriscribe2.utils.llm_client import LLMClient

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_config.py <path_to_config_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    if not Path(config_file).is_file():
        print(f"Error: Config file not found at {config_file}")
        sys.exit(1)

    print(f"--- Loading settings from: {config_file} ---")
    settings = Settings(config_file=config_file)

    print("\n--- Settings Object ---")
    print(f"  default_llm: {settings.default_llm}")
    print(f"  mock: {settings.mock}")
    print(f"  openai_api_key: {settings.openai_api_key}")
    print(f"  openai_base_url: {settings.openai_base_url}")

    print("\n--- Initializing LLMClient ---")
    llm_client = LLMClient(provider=settings.default_llm, settings=settings)

    print("\n--- LLMClient Object ---")
    print(f"  Provider: {llm_client.provider}")
    # Note: The LLMClient currently gets the base_url from os.getenv,
    # so we'll check the environment variable directly to see if it was set.
    import os

    print(f"  OPENAI_BASE_URL from env: {os.getenv('OPENAI_BASE_URL')}")

    print("\n--- Debugging Complete ---")
