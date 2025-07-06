# src/libriscribe/utils/llm_client.py
import openai
from openai import OpenAI  # For OpenAI
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential
from libriscribe.settings import Settings

import anthropic  # For Claude
import google.generativeai as genai  # For Google AI Studio
import requests  # For DeepSeek and Mistral

# ADDED THIS: Import the function
from libriscribe.utils.file_utils import extract_json_from_markdown

logger = logging.getLogger(__name__)

# Configure httpx logger to be less verbose
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)  # Or ERROR, to suppress even warnings

llm_logger = logging.getLogger("libriscribe.llm")
llm_log_handler = logging.FileHandler("libriscribe_llm.log", mode="a", encoding="utf-8")
llm_log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
llm_logger.addHandler(llm_log_handler)
llm_logger.setLevel(logging.INFO)


class LLMClient:
    """Unified LLM client for multiple providers."""

    def __init__(self, llm_provider: str):
        self.settings = Settings()
        # Use default_llm from settings if llm_provider is None or empty
        self.llm_provider = llm_provider or getattr(self.settings, "default_llm", None)
        if not self.llm_provider:
            raise ValueError("No LLM provider specified and no default_llm set in settings.")
        self.client = self._get_client()  # Initialize the correct client
        self.model = self._get_default_model()

    def _get_client(self):
        """Initializes the appropriate client based on the provider."""
        if self.llm_provider == "openai":
            if not self.settings.openai_api_key:
                raise ValueError("OpenAI API key is not set.")
            return OpenAI(
                api_key=self.settings.openai_api_key,
                base_url=getattr(self.settings, "openai_base_url", "https://api.openai.com/v1")
            )
        elif self.llm_provider == "claude":
            if not self.settings.claude_api_key:
                raise ValueError("Claude API key is not set.")
            return anthropic.Anthropic(api_key=self.settings.claude_api_key)
        elif self.llm_provider == "google_ai_studio":
            if not self.settings.google_ai_studio_api_key:
                raise ValueError("Google AI Studio API key is not set.")
            genai.configure(api_key=self.settings.google_ai_studio_api_key)
            return genai  # We don't instantiate a client, we use the module directly
        elif self.llm_provider == "deepseek":
             if not self.settings.deepseek_api_key:
                raise ValueError("DeepSeek API key is not set.")
             return None  # No client object, we'll use requests directly
        elif self.llm_provider == "mistral":
             if not self.settings.mistral_api_key:
                raise ValueError("Mistral API key is not set")
             return None
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def _get_default_model(self):
        """Gets the default model name for the selected provider."""
        if self.llm_provider == "openai":
            return getattr(self.settings, "openai_default_model", "gpt-4o-mini")
        elif self.llm_provider == "claude":
            return getattr(self.settings, "claude_default_model", "claude-3-opus-20240229")
        elif self.llm_provider == "google_ai_studio":
            return getattr(self.settings, "google_ai_studio_default_model", "gemini-2.5-flash-lite-preview-06-17")
        elif self.llm_provider == "deepseek":
            return getattr(self.settings, "deepseek_default_model", "deepseek-coder-6.7b-instruct")
        elif self.llm_provider == "mistral":
            return getattr(self.settings, "mistral_default_model", "mistral-medium-latest")
        else:
            return "unknown"  # Should not happen, but good for safety
    def set_model(self, model_name: str):
      self.model = model_name

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate_content(
        self,
        prompt: str,
        max_tokens: int = 2000, # Deprecated
        temperature: float = 0.7,
        language: str = "English",
        timeout: int = None,  # <-- Add timeout parameter
    ) -> str:
        """
        Generates text using the selected LLM provider.
        Now supports specifying the output language explicitly.
        """
        try:
            # Use timeout from settings if not provided
            if timeout is None:
                timeout = getattr(self.settings, "llm_timeout", 60)

            # Append language instruction to prompt if not already included
            if "IMPORTANT: The content should be written entirely in" not in prompt and language != "English":
                prompt += f"\n\nIMPORTANT: Generate the response in {language}."

            llm_logger.debug(f"PROMPT (provider={self.llm_provider}, model={self.model}):\n{prompt}")

            if self.llm_provider == "openai":
                logger.debug(f"OpenAI base_url: {getattr(self.client, 'base_url', 'unknown')}")
                logger.debug(f"OpenAI timeout: {timeout}")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                #    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=timeout,
                )
                result = response.choices[0].message.content.strip()
                logger.debug(f"LLMClient response (OpenAI):\n{result}")
                llm_logger.debug(f"RESPONSE (provider={self.llm_provider}, model={self.model}):\n{result}")
                return result

            else:
                logger.error(f"Unknown LLM provider: {self.llm_provider}")
                return ""

        except openai.APITimeoutError:
            logger.error(
                f"OpenAI API timed out.\n"
                f"Base URL: {getattr(self.client, 'base_url', 'unknown')}\n"
                f"Model: {self.model}\n"
                f"Prompt: {prompt[:500]}{'...' if len(prompt) > 500 else ''}"
            )
            print(
                f"ERROR: OpenAI API timed out.\n"
                f"Base URL: {getattr(self.client, 'base_url', 'unknown')}\n"
                f"Model: {self.model}\n"
                f"Prompt: {prompt[:500]}{'...' if len(prompt) > 500 else ''}"
            )
            raise
        except Exception as e:
            logger.exception(f"Error during {self.llm_provider} API call: {e}")
            print(
                f"ERROR: {self.llm_provider} API error: {e}\n"
                f"Base URL: {getattr(self.client, 'base_url', 'unknown')}\n"
                f"Model: {self.model}\n"
                f"Prompt: {prompt[:500]}{'...' if len(prompt) > 500 else ''}"
            )
            raise
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    def generate_content_with_json_repair(self, original_prompt: str, temperature:float=0.7) -> str: # max_tokens:int = 2000,
        """Generates content and attempts to repair JSON errors."""
        response_text = self.generate_content(prompt=original_prompt, temperature=temperature) # max_tokens,
        if response_text:
            json_data = extract_json_from_markdown(response_text)
            if json_data is not None:
                return response_text # Return the original markdown
            else:

                # If JSON extraction failed, attempt to repair the JSON
                repair_prompt = f"You are a helpful AI that only returns valid JSON. Fix the following broken JSON:\n\n```json\n{response_text}\n```"
                repaired_response = self.generate_content(prompt=repair_prompt,  temperature=0.2) # Low temp for corrections, max_tokens=max_tokens,
                if repaired_response:
                    repaired_json = extract_json_from_markdown(repaired_response)
                    if repaired_json is not None:
                        # CRITICAL CHANGE:  Return the JSON *string*, not wrapped in Markdown.
                        return repaired_response
        logger.error("JSON repair failed.")
        return "" # Return empty