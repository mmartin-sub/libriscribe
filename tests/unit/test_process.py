from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import typer

from libriscribe2.process import (
    generate_questions_with_llm,
    select_from_list,
    select_llm,
)


class TestSelectLlm:
    """Test cases for the select_llm function."""

    @patch("libriscribe2.process.Settings")
    def test_select_llm_with_mock_mode(self, mock_settings):
        """Test that select_llm returns 'mock' in mock_mode."""
        result = select_llm(MagicMock(), mock_mode=True)
        assert result == "mock"

    @patch("libriscribe2.process.Settings")
    @patch("typer.prompt", return_value="1")
    def test_select_llm_with_openai_key(self, mock_prompt, mock_settings):
        """Test that select_llm returns 'openai' when an API key is present."""
        mock_settings.return_value.openai_api_key = "test_key"  # pragma: allowlist secret
        result = select_llm(MagicMock())
        assert result == "openai"

    @patch("libriscribe2.process.Settings")
    def test_select_llm_with_no_keys(self, mock_settings):
        """Test that select_llm raises an exception when no API keys are present."""
        mock_settings.return_value.openai_api_key = None
        with pytest.raises(typer.Exit):
            select_llm(MagicMock())


class TestSelectFromList:
    """Test cases for the select_from_list function."""

    @patch("typer.prompt", return_value="1")
    def test_select_from_list_with_valid_choice(self, mock_prompt):
        """Test that select_from_list returns the correct choice."""
        result = select_from_list("Select an option:", ["a", "b", "c"])
        assert result == "a"

    @patch("typer.prompt", side_effect=["2", "custom_value"])
    def test_select_from_list_with_custom_value(self, mock_prompt):
        """Test that select_from_list returns a custom value."""
        result = select_from_list("Select an option:", ["a"], allow_custom=True)
        assert result == "custom_value"


@pytest.mark.asyncio
class TestGenerateQuestionsWithLlm:
    """Test cases for the generate_questions_with_llm function."""

    async def test_generate_questions_with_valid_response(self):
        """Test that generate_questions_with_llm returns a dictionary of questions."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate_content = AsyncMock(return_value='{"q1": "What is the central conflict?"}')
        result = await generate_questions_with_llm("Fantasy", "Epic", mock_llm_client)
        assert result == {"q1": "What is the central conflict?"}

    async def test_generate_questions_with_invalid_response(self):
        """Test that generate_questions_with_llm returns default questions."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate_content = AsyncMock(return_value="not a valid json")
        result = await generate_questions_with_llm("Fantasy", "Epic", mock_llm_client)
        assert "q1" in result
        assert "q2" in result
        assert "q3" in result

    async def test_generate_questions_with_no_llm_client(self):
        """Test that generate_questions_with_llm returns an empty dictionary."""
        result = await generate_questions_with_llm("Fantasy", "Epic", None)
        assert result == {}
