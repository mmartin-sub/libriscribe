import json
import os
from pathlib import Path

import pytest

from libriscribe2.settings import Settings
from libriscribe2.utils.llm_client import LLMClient

# Define the path to the config file
CONFIG_PATH = Path(__file__).parent / "config.json"

# Load the config file to check for real API keys
try:
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    OPENAI_API_KEY = config.get("openai_api_key")
except (FileNotFoundError, json.JSONDecodeError):
    OPENAI_API_key = None

# A guard to check if the API key is a real key or a placeholder
IS_REAL_KEY = OPENAI_API_KEY and "dummy-key" not in OPENAI_API_KEY


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not IS_REAL_KEY, reason="Integration tests require a real OpenAI API key in tests/config.json")
async def test_openai_integration():
    """
    This is an integration test that calls the real OpenAI API.
    It will be skipped if a real API key is not provided in tests/config.json.
    """
    # Set the API key in the environment for the LLMClient
    if OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    settings = Settings()
    llm_client = LLMClient(llm_provider="openai", settings=settings, model_config={"default": "gpt-4o-mini"})

    prompt = "This is a test prompt. Say 'Hello, World!'."
    response = await llm_client.generate_content(prompt)

    assert "Hello, World!" in response
