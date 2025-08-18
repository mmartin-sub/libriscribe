"""
Test mock LLM client failure scenarios to ensure CLI fails properly.

This test module systematically tests failures at each call position from 1 to 19
to verify that the CLI handles failures correctly at any point in the book creation process.
Based on analysis, a typical book creation makes 18 LLM calls:
- Calls 1-4: Concept generation (concept, critique, refine, keywords)
- Call 5: Outline generation
- Calls 6-8: Scene outlines for 3 chapters
- Call 9: Character generation
- Calls 10-18: Scene writing (3 scenes × 3 chapters = 9 scenes)
"""

import asyncio
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from libriscribe2.services.book_creator import BookCreatorService
from libriscribe2.utils.mock_llm_client import MockLLMClient


class FailingMockLLMClient(MockLLMClient):
    """Mock LLM client that fails after a specified number of calls."""

    def __init__(self, fail_after_calls: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_after_calls = fail_after_calls
        self.call_count = 0

    def generate_content(
        self,
        prompt: str,
        prompt_type: str = "default",
        temperature: float = 0.7,
        language: str = "English",
        timeout: int | None = None,
    ) -> str:
        """Generate content but fail after specified number of calls."""
        self.call_count += 1

        if self.call_count > self.fail_after_calls:
            raise RuntimeError(f"Mock LLM client failed after {self.fail_after_calls} calls")

        # Return normal mock content for successful calls
        return super().generate_content(
            prompt=prompt, prompt_type=prompt_type, temperature=temperature, language=language, timeout=timeout
        )


class TestMockFailureScenarios:
    """Test scenarios where mock LLM client fails after N calls."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.projects_dir = self.temp_dir / "projects"
        self.projects_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Clean up test environment."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def _create_mock_settings(self):
        """Create mock settings instance."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.projects_dir = str(self.temp_dir / "projects")
        mock_settings_instance.get_model_config.return_value = {"default": "gpt-4o-mini"}
        mock_settings_instance.default_llm = "mock"
        mock_settings_instance.llm_timeout = 300.0
        mock_settings_instance.environment = "test"
        return mock_settings_instance

    def _create_book_args(self, unique_suffix=""):
        """Create standard book creation arguments."""
        return {
            "title": f"Test Book{unique_suffix}",
            "category": "Fiction",
            "genre": "Fantasy",
            "generate_concept": True,
            "generate_outline": True,
            "generate_characters": True,
            "write_chapters": True,
            "characters": 2,
            "chapters": 3,
            "all": False,
        }

    @pytest.mark.parametrize("fail_after_calls", range(1, 20))  # Test failures from call 1 to 19
    @patch("libriscribe2.utils.llm_client.LLMClient._generate_mock_content")
    @patch("libriscribe2.settings.Settings")
    @pytest.mark.asyncio
    async def test_mock_fails_at_specific_call(self, mock_settings_class, mock_generate_content, fail_after_calls):
        """Test that CLI fails properly when mock LLM fails at specific call position."""
        mock_settings_class.return_value = self._create_mock_settings()

        # Create failing mock client
        failing_client = FailingMockLLMClient(fail_after_calls=fail_after_calls)

        # Mock the generate_mock_content to use our failing client
        async def mock_generate_side_effect(prompt, temperature, **kwargs):
            prompt_type = kwargs.get("prompt_type", "general")
            language = "English"
            return failing_client.generate_content(prompt, prompt_type, temperature, language)

        mock_generate_content.side_effect = mock_generate_side_effect

        # Create book creator service
        book_creator = BookCreatorService(mock=True)

        # Test that book creation fails at the expected call
        if fail_after_calls < 18:
            with pytest.raises(RuntimeError, match="Book creation failed"):
                await book_creator.acreate_book(self._create_book_args(f"-{fail_after_calls}"))
            assert failing_client.call_count >= fail_after_calls
        else:
            await book_creator.acreate_book(self._create_book_args(f"-{fail_after_calls}"))

    @patch("libriscribe2.utils.llm_client.LLMClient._generate_mock_content")
    @patch("libriscribe2.settings.Settings")
    @pytest.mark.asyncio
    async def test_mock_succeeds_with_no_failure(self, mock_settings_class, mock_generate_content):
        """Test that book creation succeeds when no failure is programmed."""
        mock_settings_class.return_value = self._create_mock_settings()

        # Create mock client that never fails
        normal_client = FailingMockLLMClient(fail_after_calls=100)

        # Mock the generate_mock_content to use our normal client
        async def mock_generate_side_effect(prompt, temperature, **kwargs):
            prompt_type = kwargs.get("prompt_type", "general")
            language = "English"
            return normal_client.generate_content(prompt, prompt_type, temperature, language)

        mock_generate_content.side_effect = mock_generate_side_effect

        # Create book creator service
        book_creator = BookCreatorService(mock=True)

        # Test that book creation succeeds
        await book_creator.acreate_book(self._create_book_args("-success"))
        assert normal_client.call_count >= 18

    def test_failing_mock_client_call_counting(self):
        """Test that the FailingMockLLMClient correctly counts calls."""
        client = FailingMockLLMClient(fail_after_calls=2)

        # First call should succeed
        result1 = client.generate_content("test prompt 1")
        assert "Mock response" in result1
        assert client.call_count == 1

        # Second call should succeed
        result2 = client.generate_content("test prompt 2")
        assert "Mock response" in result2
        assert client.call_count == 2

        # Third call should fail
        with pytest.raises(RuntimeError, match="Mock LLM client failed after 2 calls"):
            client.generate_content("test prompt 3")
        assert client.call_count == 3

    def test_failing_mock_client_different_prompt_types(self):
        """Test that the FailingMockLLMClient fails regardless of prompt type."""
        client = FailingMockLLMClient(fail_after_calls=1)

        # First call with concept prompt should succeed
        result = client.generate_content("test", prompt_type="concept")
        assert "Mock Concept Title" in result
        assert client.call_count == 1

        # Second call with different prompt type should fail
        with pytest.raises(RuntimeError, match="Mock LLM client failed after 1 calls"):
            client.generate_content("test", prompt_type="outline")
        assert client.call_count == 2
