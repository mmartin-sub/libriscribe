from unittest.mock import AsyncMock, MagicMock

import pytest

from libriscribe2.agents.title_generator import TitleGeneratorAgent
from libriscribe2.knowledge_base import ProjectKnowledgeBase


@pytest.fixture
def mock_llm_client():
    """Fixture for a mock LLM client."""
    client = MagicMock()
    client.generate_content = AsyncMock()
    return client


@pytest.fixture
def sample_knowledge_base():
    """Fixture for a sample ProjectKnowledgeBase."""
    kb = ProjectKnowledgeBase(
        project_name="Test Project",
        title="Untitled",
        genre="Fantasy",
        category="Fiction",
        language="English",
        description="A test project.",
    )
    return kb


class TestTitleGeneratorAgent:
    """Test cases for the TitleGeneratorAgent."""

    def test_build_title_prompt_with_basic_info(self, mock_llm_client, sample_knowledge_base):
        """Test that the prompt is built correctly with basic information."""
        agent = TitleGeneratorAgent(mock_llm_client)
        prompt = agent._build_title_prompt(sample_knowledge_base)

        assert "Genre: Fantasy" in prompt
        assert "Category: Fiction" in prompt
        assert "Language: en" in prompt
        assert "Description: A test project." in prompt
        assert "Main Characters" not in prompt
        assert "Worldbuilding Elements" not in prompt
        assert "Chapter Summaries" not in prompt
        assert "Full Manuscript Analysis" not in prompt
        assert "Keywords" not in prompt

    def test_build_title_prompt_with_all_info(self, mock_llm_client, sample_knowledge_base):
        """Test that the prompt is built correctly with all available information."""
        sample_knowledge_base.characters = {"Character 1": "A brave warrior."}
        sample_knowledge_base.worldbuilding = MagicMock()
        sample_knowledge_base.worldbuilding.geography = "A vast land."
        sample_knowledge_base.worldbuilding.culture_and_society = "A rich culture."
        sample_knowledge_base.worldbuilding.magic_system = "A powerful magic system."
        sample_knowledge_base.chapters = {1: MagicMock(summary="Chapter 1 summary.", title="Chapter 1", scenes=[])}
        sample_knowledge_base.keywords = ["keyword1", "keyword2"]
        agent = TitleGeneratorAgent(mock_llm_client)
        prompt = agent._build_title_prompt(sample_knowledge_base)

        assert "Main Characters: Character 1" in prompt
        assert "Worldbuilding Elements: geography, culture, magic" in prompt
        assert "Chapter Summaries:\nChapter 1: Chapter 1 summary." in prompt
        assert "Full Manuscript Analysis:\nChapter 1 Title: Chapter 1\nChapter 1 Summary: Chapter 1 summary." in prompt
        assert "Keywords: keyword1, keyword2" in prompt

    @pytest.mark.asyncio
    async def test_execute_with_valid_response(self, mock_llm_client, sample_knowledge_base):
        """Test the execute method with a valid response from the LLM."""
        mock_llm_client.generate_content.return_value = (
            '{"title": "The Crystal of Gondar", "subtitle": "A Fantasy Adventure", "reasoning": "It sounds epic."}'
        )
        agent = TitleGeneratorAgent(mock_llm_client)

        await agent.execute(sample_knowledge_base)

        mock_llm_client.generate_content.assert_called_once()
        assert sample_knowledge_base.title == "The Crystal of Gondar"

    @pytest.mark.asyncio
    async def test_execute_with_invalid_response(self, mock_llm_client, sample_knowledge_base):
        """Test the execute method with an invalid response from the LLM."""
        mock_llm_client.generate_content.return_value = "This is not a valid JSON response."
        agent = TitleGeneratorAgent(mock_llm_client)

        await agent.execute(sample_knowledge_base)

        mock_llm_client.generate_content.assert_called_once()
        assert sample_knowledge_base.title == "Untitled"  # Title should not be updated
