import pytest

from libriscribe2.utils.llm_client import LLMClient
from libriscribe2.utils.mock_llm_client import MockLLMClient


def is_real_api_key(settings):
    """
    Checks if the provided API key is a real key or a placeholder.
    A key is considered a placeholder if it's missing or contains 'dummy-key'.
    """
    api_key = settings.openai_api_key
    return api_key and "dummy-key" not in api_key


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openai_integration(integration_settings, handle_llm_client_error):
    """
    This is an integration test that calls the real OpenAI API or a mock client.
    - If `default_llm` is "mock" in `.config-test.json` or if the file is missing,
      it runs in mock mode.
    - Otherwise, it attempts to run as a real integration test.
    """
    if integration_settings.mock:
        # Run in mock mode
        llm_client = MockLLMClient(settings=integration_settings)
        prompt = "This is a test prompt for the mock client."
        response = await llm_client.generate_content(prompt)
        assert "Mock response for prompt type:" in response

    else:
        # Run as a real integration test
        if not is_real_api_key(integration_settings):
            pytest.skip(
                "Skipping integration test: No valid API key found in .config-test.json. "
                "Please provide a real key to run this test."
            )

        llm_client = LLMClient(
            provider=integration_settings.default_llm,
            settings=integration_settings,
            model_config=integration_settings.get_model_config(),
        )

        prompt = "This is a test prompt. Say 'Hello, World!'."

        response = await llm_client.generate_content(prompt)

        assert "Hello, World!" in response
