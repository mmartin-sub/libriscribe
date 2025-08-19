from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from libriscribe2.agents.researcher import ResearcherAgent
from libriscribe2.knowledge_base import ProjectKnowledgeBase


@pytest.fixture
def mock_llm_client():
    """Fixture for a mock LLM client."""
    client = MagicMock()
    client.generate_content = AsyncMock()
    return client


class TestResearcherAgent:
    """Test cases for the ResearcherAgent."""

    def test_get_project_language_with_file(self, tmp_path):
        """Test that _get_project_language returns the correct language."""
        kb = ProjectKnowledgeBase(
            project_name="Test Project",
            language="French",
        )
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        from libriscribe2.settings import Settings

        settings = Settings()
        kb.save_to_file(str(project_dir / settings.project_data_filename))
        agent = ResearcherAgent(MagicMock(), settings)
        language = agent._get_project_language(str(project_dir / "output.md"))
        assert language == "fr"

    def test_get_project_language_without_file(self, tmp_path):
        """Test that _get_project_language returns the default language."""
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = ResearcherAgent(MagicMock(), settings)
        language = agent._get_project_language(str(tmp_path / "output.md"))
        assert language == settings.default_language

    def test_format_search_results(self):
        """Test that _format_search_results correctly formats search results."""
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = ResearcherAgent(MagicMock(), settings)
        results = [
            {"title": "Title 1", "url": "http://example.com/1", "snippet": "Snippet 1"},
            {"title": "Title 2", "url": "http://example.com/2", "snippet": "Snippet 2"},
        ]
        formatted_results = agent._format_search_results(results)
        assert "### [Title 1](http://example.com/1)" in formatted_results
        assert "Snippet 1" in formatted_results
        assert "### [Title 2](http://example.com/2)" in formatted_results
        assert "Snippet 2" in formatted_results

    def test_format_search_results_with_no_results(self):
        """Test that _format_search_results returns the correct message for no results."""
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = ResearcherAgent(MagicMock(), settings)
        formatted_results = agent._format_search_results([])
        assert formatted_results == "No search results found."

    @patch("requests.get")
    def test_scrape_google_search_with_success(self, mock_get):
        """Test that scrape_google_search returns a list of search results."""
        mock_response = MagicMock()
        mock_response.text = """
        <div class="tF2Cxc">
            <a href="http://example.com/1"><h3>Title 1</h3></a>
            <div class="VwiC3b">Snippet 1</div>
        </div>
        """
        mock_get.return_value = mock_response
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = ResearcherAgent(MagicMock(), settings)
        results = agent.scrape_google_search("test query")
        assert len(results) == 1
        assert results[0]["title"] == "Title 1"

    @patch("requests.get", side_effect=Exception("Test exception"))
    def test_scrape_google_search_with_failure(self, mock_get):
        """Test that scrape_google_search returns an empty list on failure."""
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = ResearcherAgent(MagicMock(), settings)
        results = agent.scrape_google_search("test query")
        assert results == []

    def test_extract_search_result(self):
        """Test that _extract_search_result correctly extracts data."""
        html = """
        <div class="tF2Cxc">
            <a href="http://example.com/1"><h3>Title 1</h3></a>
            <div class="VwiC3b">Snippet 1</div>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div", class_="tF2Cxc")
        from bs4 import Tag

        from libriscribe2.settings import Settings

        settings = Settings()

        assert isinstance(element, Tag)
        agent = ResearcherAgent(MagicMock(), settings)
        result = agent._extract_search_result(element)
        assert result == {"title": "Title 1", "url": "http://example.com/1", "snippet": "Snippet 1"}

    @pytest.mark.asyncio
    async def test_execute_with_valid_query(self, mock_llm_client, tmp_path):
        """Test the execute method with a valid query."""
        mock_llm_client.generate_content.return_value = "AI summary"
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = ResearcherAgent(mock_llm_client, settings)
        output_path = str(tmp_path / "research.md")

        with patch.object(agent, "scrape_google_search", return_value=[]):
            await agent.execute(None, output_path=output_path, query="test query")

        mock_llm_client.generate_content.assert_called_once()
        with open(output_path) as f:
            content = f.read()
            assert "# Research Report: test query" in content
            assert "## AI-Generated Summary" in content
            assert "AI summary" in content
            assert "## Web Search Results" in content

    @pytest.mark.asyncio
    async def test_execute_with_no_query(self, mock_llm_client):
        """Test that execute logs an error when no query is provided."""
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = ResearcherAgent(mock_llm_client, settings)
        with patch.object(agent, "log_error") as mock_log_error:
            await agent.execute(None)
            mock_log_error.assert_called_with("Error: query is required")
