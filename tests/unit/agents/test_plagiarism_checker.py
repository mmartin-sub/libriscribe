from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from libriscribe2.agents.plagiarism_checker import PlagiarismCheckerAgent


@pytest.fixture
def mock_llm_client():
    """Fixture for a mock LLM client."""
    client = MagicMock()
    client.generate_content = AsyncMock()
    return client


class TestPlagiarismCheckerAgent:
    """Test cases for the PlagiarismCheckerAgent."""

    def test_split_into_chunks(self):
        """Test that split_into_chunks correctly splits the text."""
        from libriscribe2.settings import Settings
        settings = Settings()
        agent = PlagiarismCheckerAgent(MagicMock(), settings)
        text = "word " * 1000
        chunks = agent.split_into_chunks(text, chunk_size=500)
        assert len(chunks) == 2
        assert len(chunks[0].split()) == 500
        assert len(chunks[1].split()) == 500

    def test_split_into_chunks_with_empty_text(self):
        """Test that split_into_chunks handles an empty string."""
        from libriscribe2.settings import Settings
        settings = Settings()
        agent = PlagiarismCheckerAgent(MagicMock(), settings)
        chunks = agent.split_into_chunks("", chunk_size=500)
        assert chunks == []

    @pytest.mark.asyncio
    async def test_check_plagiarism_with_valid_response(self, mock_llm_client):
        """Test that check_plagiarism returns a list of plagiarism results."""
        from libriscribe2.settings import Settings
        settings = Settings()
        mock_llm_client.generate_content.return_value = (
            '```json\n[{"text": "plagiarized text", "similarity_score": 0.9, "source": "http://example.com"}]\n```'
        )
        agent = PlagiarismCheckerAgent(mock_llm_client, settings)
        results = await agent.check_plagiarism("some text", "chapter_1.md")
        assert len(results) == 1
        assert results[0]["text"] == "plagiarized text"

    @pytest.mark.asyncio
    async def test_check_plagiarism_with_invalid_response(self, mock_llm_client):
        """Test that check_plagiarism returns an empty list."""
        from libriscribe2.settings import Settings
        settings = Settings()
        mock_llm_client.generate_content.return_value = "not a valid json"
        agent = PlagiarismCheckerAgent(mock_llm_client, settings)
        results = await agent.check_plagiarism("some text", "chapter_1.md")
        assert results == []

    @pytest.mark.asyncio
    @patch("libriscribe2.agents.plagiarism_checker.read_markdown_file", return_value="This is a test chapter.")
    @patch("libriscribe2.utils.file_utils.write_json_file")
    async def test_execute_with_valid_chapter(self, mock_write_json, mock_read_markdown, mock_llm_client, tmp_path):
        """Test the execute method with a valid chapter."""
        from libriscribe2.settings import Settings
        settings = Settings()
        mock_llm_client.generate_content.return_value = "[]"
        agent = PlagiarismCheckerAgent(mock_llm_client, settings)
        output_path = str(tmp_path / "plagiarism_check.json")
        await agent.execute(None, output_path=output_path, chapter_path="test_chapter.md")

        mock_llm_client.generate_content.assert_called_once()
        mock_write_json.assert_called_once()
        args, _ = mock_write_json.call_args
        assert args[0] == output_path
        assert "plagiarism_results" in args[1]
        assert len(args[1]["plagiarism_results"]) == 0

    @pytest.mark.asyncio
    async def test_execute_with_no_chapter_path(self, mock_llm_client):
        """Test that execute logs an error when no chapter_path is provided."""
        from libriscribe2.settings import Settings
        settings = Settings()
        agent = PlagiarismCheckerAgent(mock_llm_client, settings)
        with patch("rich.console.Console.print") as mock_print:
            await agent.execute(None)
            mock_print.assert_called_with("[red]Error: chapter_path is required[/red]")

    @pytest.mark.asyncio
    @patch("libriscribe2.agents.plagiarism_checker.read_markdown_file", return_value=None)
    async def test_execute_with_empty_chapter(self, mock_read_markdown, mock_llm_client):
        """Test that execute handles an empty chapter."""
        from libriscribe2.settings import Settings
        settings = Settings()
        agent = PlagiarismCheckerAgent(mock_llm_client, settings)
        with patch("builtins.print") as mock_print:
            await agent.execute(None, chapter_path="test_chapter.md")
            mock_print.assert_called_with("ERROR: Chapter file is empty or not found: test_chapter.md")
