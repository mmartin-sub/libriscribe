#!/usr/bin/env python3

import asyncio
import json
import os

import aiohttp
import pytest
from aiohttp import ClientResponse, ClientSession, ClientTimeout


@pytest.mark.skipif(
    not os.path.exists(os.path.join("tests", ".config-test.json")),
    reason="No test config found, skipping live LLM API test.",
)
@pytest.mark.asyncio
async def test_api():
    """Test the API endpoint directly"""

    # Prefer test config if present
    config_path = os.path.join("tests", ".config-test.json")

    with open(config_path) as f:
        config = json.load(f)

    api_key = config["openai_api_key"]
    base_url = config["openai_base_url"]
    model = config["openai_default_model"]

    print(f"Testing API: {base_url}")
    print(f"Model: {model}")
    print(f"API Key: {api_key[:5]}...")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello, this is a test."}],
        "temperature": 0.7,
        "timeout": 30,
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions", json=payload, headers=headers, timeout=ClientTimeout(total=30)
            ) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("Full API Response:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    if "choices" in data and data["choices"] and len(data["choices"]) > 0:
                        if "message" in data["choices"][0] and "content" in data["choices"][0]["message"]:
                            print(f"Response: {data['choices'][0]['message']['content'][:100]}...")
                            assert data["choices"][0]["message"]["content"]  # Assert we got a response
                        else:
                            pytest.fail("API response does not contain the expected message structure")
                    else:
                        pytest.fail("API response does not contain any choices")
                else:
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    pytest.fail(f"API request failed with status {response.status}: {error_text}")
    except Exception as e:
        print(f"Exception: {e}")
        pytest.fail(f"API test failed with exception: {e}")


if __name__ == "__main__":
    asyncio.run(test_api())
