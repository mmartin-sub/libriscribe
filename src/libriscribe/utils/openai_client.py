# src/libriscribe/utils/openai_client.py (Corrected)

import openai
from openai import OpenAI
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential
from libriscribe.settings import Settings

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        settings = Settings()
        self.client = OpenAI(api_key=settings.openai_api_key)  # Initialize new client
        self.model = "gpt-4o-mini"

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate_content(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """Generates text using the OpenAI API (Synchronous)."""
        try:
            response = self.client.chat.completions.create(  # No 'await' here
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.exception(f"Error during OpenAI API call: {e}")
            print(f"ERROR: OpenAI API error: {e}")
            return ""