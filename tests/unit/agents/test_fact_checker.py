from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from libriscribe2.agents.fact_checker import FactCheckerAgent


@pytest.fixture
def mock_llm_client():
    """Fixture for a mock LLM client."""
    client = MagicMock()
    client.generate_content = AsyncMock()
    return client


class TestFactCheckerAgent:
    """Test cases for the FactCheckerAgent."""

    @pytest.mark.asyncio
    async def test_check_claim_with_valid_response(self, mock_llm_client):
        """Test that check_claim returns a dictionary with the correct keys."""
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm_client.generate_content.return_value = (
            '```json\n{"result": "True", "explanation": "It is true.", "sources": ["http://example.com"]}\n```'
        )
        agent = FactCheckerAgent(mock_llm_client, settings)
        result = await agent.check_claim("The sky is blue.")
        assert result["result"] == "True"
        assert result["explanation"] == "It is true."
        assert result["sources"] == ["http://example.com"]
        assert result["claim"] == "The sky is blue."

    @pytest.mark.asyncio
    async def test_check_claim_with_invalid_response(self, mock_llm_client):
        """Test that check_claim returns an error dictionary."""
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm_client.generate_content.return_value = "not a valid json"
        agent = FactCheckerAgent(mock_llm_client, settings)
        result = await agent.check_claim("The sky is blue.")
        assert result["result"] == "Error"
        assert result["explanation"] == "Failed to parse LLM Response"

    @pytest.mark.asyncio
    @patch("libriscribe2.agents.fact_checker.read_markdown_file", return_value="This is a test chapter.")
    @patch("libriscribe2.utils.file_utils.write_json_file")
    async def test_execute_with_valid_chapter(self, mock_write_json, mock_read_markdown, mock_llm_client, tmp_path):
        """Test the execute method with a valid chapter."""
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm_client.generate_content.side_effect = [
            '```json\n["claim 1", "claim 2"]\n```',
            '```json\n{"result": "True", "explanation": "It is true.", "sources": []}\n```',
            '```json\n{"result": "False", "explanation": "It is false.", "sources": []}\n```',
        ]
        agent = FactCheckerAgent(mock_llm_client, settings)
        output_path = str(tmp_path / "fact_check.json")
        await agent.execute(None, output_path=output_path, chapter_path="test_chapter.md")

        assert mock_llm_client.generate_content.call_count == 3
        mock_write_json.assert_called_once()
        args, _ = mock_write_json.call_args
        assert args[0] == output_path
        assert "fact_check_results" in args[1]
        assert len(args[1]["fact_check_results"]) == 2

    @pytest.mark.asyncio
    async def test_execute_with_no_chapter_path(self, mock_llm_client):
        """Test that execute logs an error when no chapter_path is provided."""
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = FactCheckerAgent(mock_llm_client, settings)
        with patch("rich.console.Console.print") as mock_print:
            await agent.execute(None)
            mock_print.assert_called_with("[red]Error: chapter_path is required[/red]")

    @pytest.mark.asyncio
    @patch("libriscribe2.agents.fact_checker.read_markdown_file", return_value=None)
    async def test_execute_with_empty_chapter(self, mock_read_markdown, mock_llm_client):
        """Test that execute handles an empty chapter."""
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = FactCheckerAgent(mock_llm_client, settings)
        with patch("builtins.print") as mock_print:
            await agent.execute(None, chapter_path="test_chapter.md")
            mock_print.assert_called_with("ERROR: Chapter file is empty or not found: test_chapter.md")
