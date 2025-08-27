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
from libriscribe2.settings import Settings
from libriscribe2.utils.mock_llm_client import MockLLMClient


from typing import AsyncGenerator


class FailingMockLLMClient(MockLLMClient):
    """Mock LLM client that fails after a specified number of calls."""

    def __init__(self, fail_after_calls: int, settings: Settings):
        super().__init__(
            llm_provider="mock",
            settings=settings,
            model_config={"default": "mock-model"},
            project_name="test-project",
            user="test-user",
        )
        self.fail_after_calls = fail_after_calls
        self.call_count = 0
        self.actual_call_count_for_failure = 0

    async def generate_content(
        self,
        primary_prompt: str,
        prompt_type: str = "default",
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        # The counting and failure logic is handled by generate_streaming_content,
        # which is called by super().generate_content()
        return await super().generate_content(primary_prompt, prompt_type, temperature, **kwargs)

    async def generate_streaming_content(
        self,
        primary_prompt: str,
        prompt_type: str = "default",
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        self.call_count += 1
        if self.call_count >= self.fail_after_calls:
            if self.actual_call_count_for_failure == 0:
                self.actual_call_count_for_failure = self.call_count
            raise RuntimeError(f"Mock LLM client failed after {self.fail_after_calls} calls")
        async for chunk in super().generate_streaming_content(
            primary_prompt, prompt_type, temperature, **kwargs
        ):
            yield chunk


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
    @patch("libriscribe2.settings.Settings")
    @pytest.mark.asyncio
    async def test_mock_fails_at_specific_call(self, mock_settings_class, fail_after_calls):
        """Test that CLI fails properly when mock LLM fails at specific call position."""
        mock_settings_class.return_value = self._create_mock_settings()
        failing_client = FailingMockLLMClient(fail_after_calls=fail_after_calls, settings=mock_settings_class.return_value)
        book_creator = BookCreatorService(mock=True, llm_client=failing_client)

        # A successful run has 8 calls.
        # If we configure failure after 8 calls, it should still succeed.
        # Failure at call 9 or later should also result in success.
        SHOULD_FAIL_THRESHOLD = 8

        if fail_after_calls <= SHOULD_FAIL_THRESHOLD:
            with pytest.raises(RuntimeError):
                await book_creator.acreate_book(self._create_book_args(f"-{fail_after_calls}"))
            # Check that the first failure happened at the expected call count
            assert failing_client.actual_call_count_for_failure == fail_after_calls
        else:
            # If we expect failure after the process is complete, it should succeed
            await book_creator.acreate_book(self._create_book_args(f"-{fail_after_calls}"))
            assert failing_client.call_count == SHOULD_FAIL_THRESHOLD

    @patch("libriscribe2.settings.Settings")
    @pytest.mark.asyncio
    async def test_mock_succeeds_with_no_failure(self, mock_settings_class):
        """Test that book creation succeeds when no failure is programmed."""
        mock_settings_class.return_value = self._create_mock_settings()
        normal_client = FailingMockLLMClient(fail_after_calls=100, settings=mock_settings_class.return_value)
        book_creator = BookCreatorService(mock=True, llm_client=normal_client)

        # Test that book creation succeeds
        await book_creator.acreate_book(self._create_book_args("-success"))
        assert normal_client.call_count == 8

    @pytest.mark.asyncio
    async def test_failing_mock_client_call_counting(self):
        """Test that the FailingMockLLMClient correctly counts calls."""
        mock_settings = self._create_mock_settings()
        client = FailingMockLLMClient(fail_after_calls=2, settings=mock_settings)

        # First call should succeed
        result1 = await client.generate_content("test prompt 1")
        assert "Mock response" in result1
        assert client.call_count == 1

        # Second call should fail
        with pytest.raises(RuntimeError, match="Mock LLM client failed after 2 calls"):
            await client.generate_content("test prompt 2")
        assert client.call_count == 2

    @pytest.mark.asyncio
    async def test_failing_mock_client_different_prompt_types(self):
        """Test that the FailingMockLLMClient fails regardless of prompt type."""
        mock_settings = self._create_mock_settings()
        client = FailingMockLLMClient(fail_after_calls=1, settings=mock_settings)

        # First call with concept prompt should fail
        with pytest.raises(RuntimeError, match="Mock LLM client failed after 1 calls"):
            await client.generate_content("test", prompt_type="concept")
        assert client.call_count == 1
