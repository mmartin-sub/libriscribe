"""
Unit tests for ConceptGeneratorAgent.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from libriscribe2.agents.concept_generator import ConceptGeneratorAgent
from libriscribe2.knowledge_base import ProjectKnowledgeBase


def generate_large_mock_response(base_text: str, target_length: int = 2000) -> str:
    """Generate a large mock response by repeating and expanding the base text."""
    if len(base_text) >= target_length:
        return base_text

    # Expand the text by repeating and adding variations
    expanded = base_text
    while len(expanded) < target_length:
        expanded += f"\n\n{base_text} with additional details and elaboration. "
        expanded += "This concept explores deep themes and complex character dynamics. "
        expanded += "The narrative structure provides multiple layers of meaning and engagement. "
        expanded += "Readers will find themselves drawn into a world of rich possibilities and unexpected developments."

    return expanded[:target_length]


class TestConceptGeneratorAgent:
    """Test cases for ConceptGeneratorAgent."""

    def test_initialization(self):
        """Test ConceptGeneratorAgent initialization."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()

        # Act
        agent = ConceptGeneratorAgent(mock_llm, settings)

        # Assert
        assert agent.name == "ConceptGeneratorAgent"
        assert agent.llm_client == mock_llm

    @pytest.mark.asyncio
    async def test_execute_basic(self):
        """Test basic concept generation execution."""
        # Arrange
        mock_llm = AsyncMock()
        # Mock responses for all the generate_content calls
        initial_concept_response = (
            "Here is the book concept:\n\n"
            "```json\n"
            '{"title": "The Discovery", "logline": "A brave astronaut discovers an ancient alien civilization", "description": "A fascinating concept about space exploration and human discovery. '
            "This story follows the journey of a brave astronaut who discovers "
            "an ancient alien civilization on a distant planet. The narrative "
            "explores themes of first contact, cultural exchange, and the human "
            "spirit's drive to explore the unknown.\"}\n"
            "```"
        )
        critique_response = "This is a good concept with strong potential."
        refined_concept_response = (
            "Here is the refined concept:\n\n"
            "```json\n"
            '{"title": "The Discovery", "logline": "A brave astronaut discovers an ancient alien civilization", "description": "A refined concept about space exploration and human discovery. '
            "This story follows the journey of a brave astronaut who discovers "
            "an ancient alien civilization on a distant planet. The narrative "
            "explores themes of first contact, cultural exchange, and the human "
            "spirit's drive to explore the unknown.\"}\n"
            "```"
        )
        keywords_response = (
            "Here are the keywords:\n\n"
            "```json\n"
            '{"keywords": ["space", "exploration", "alien", "civilization", "discovery"]}\n'
            "```"
        )
        # Mock the async generate_content (initial concept) call to yield a string
        mock_llm.generate_content = AsyncMock(
            side_effect=[
                initial_concept_response,
            ]
        )
        # Mock content-filtering fallback calls for critique, refine, keywords
        mock_llm.generate_content_with_content_filtering_fallback = AsyncMock(
            side_effect=[
                critique_response,
                refined_concept_response,
                keywords_response,
            ]
        )
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = ConceptGeneratorAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.set("genre", "Science Fiction")

        # Act
        await agent.execute(kb)

        # Assert
        # Ensure all async mock calls are awaited
        for call in mock_llm.generate_content.call_args_list:
            assert call[0][0] is not None  # Ensure prompt is provided
            assert call[1].get("prompt_type") is not None  # Ensure prompt_type is provided

    @pytest.mark.asyncio
    async def test_execute_llm_error(self):
        """Test execution when LLM client raises an error."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = AsyncMock()
        mock_llm.generate_content.side_effect = Exception("LLM error")
        agent = ConceptGeneratorAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert
        with pytest.raises(RuntimeError, match="Failed to generate book concept"):
            await agent.execute(kb)

    @pytest.mark.asyncio
    async def test_execute_null_content(self):
        """Test execution when LLM returns null content."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = AsyncMock()
        # Mock all generate_content calls to return None
        mock_llm.generate_content = AsyncMock(side_effect=[None, None, None, None])
        agent = ConceptGeneratorAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert: the agent raises RuntimeError when no content is generated
        with pytest.raises(RuntimeError, match="Failed to generate book concept"):
            await agent.execute(kb)

    def test_build_initial_prompt(self):
        """Test building initial prompt."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = ConceptGeneratorAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Space Adventure")
        kb.set("genre", "Science Fiction")

        # Act
        prompt = agent._build_initial_prompt(kb)

        # Assert
        assert "Science Fiction" in prompt
        assert "Unknown Category" in prompt

    def test_build_critique_prompt(self):
        """Test building critique prompt."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = ConceptGeneratorAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        concept_json = {"title": "Test Concept", "description": "A test concept"}

        # Act
        prompt = agent._build_critique_prompt(concept_json, kb)

        # Assert
        assert "Test Concept" in prompt
        assert "A test concept" in prompt

    def test_build_refine_prompt(self):
        """Test building refine prompt."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = ConceptGeneratorAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        concept_json = {"title": "Test Concept", "description": "A test concept"}
        critique = "This concept needs improvement"

        # Act
        prompt = agent._build_refine_prompt(concept_json, critique, kb)

        # Assert
        assert "Test Concept" in prompt
        assert "This concept needs improvement" in prompt

    def test_build_keywords_prompt(self):
        """Test building keywords prompt."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = ConceptGeneratorAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        concept_json = {"title": "Test Concept", "description": "A test concept"}

        # Act
        prompt = agent._build_keywords_prompt(concept_json, kb)

        # Assert
        assert "Test Concept" in prompt
        assert "A test concept" in prompt

    def test_format_concept_as_markdown(self):
        """Test formatting concept as markdown."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = ConceptGeneratorAgent(mock_llm, settings)
        concept_json = {"title": "Test Concept", "description": "A test concept"}
        keywords_json = {"keywords": ["space", "adventure"]}
        critique_response = "This is a good concept"

        # Act
        markdown = agent._format_concept_as_markdown(concept_json, keywords_json, critique_response)

        # Assert
        assert "Test Concept" in markdown
        assert "A test concept" in markdown
        assert "space" in markdown
        assert "adventure" in markdown

    def test_update_knowledge_base(self):
        """Test updating knowledge base with concept data."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = ConceptGeneratorAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        concept_json = {"title": "Test Concept", "description": "A test concept"}
        keywords_json = {
            "primary_keywords": ["space", "exploration"],
            "secondary_keywords": ["adventure", "discovery"],
            "genre_keywords": ["science fiction", "futuristic"],
        }

        # Act
        agent._update_knowledge_base(kb, concept_json, keywords_json)

        # Assert
        assert kb.title == "Test Concept"
        assert kb.description == "A test concept"
        assert len(kb.keywords) > 0

    @pytest.mark.asyncio
    async def test_execute_creates_correct_file_names(self, tmp_path):
        """Test that concept generator creates files with correct numbered names."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = AsyncMock()
        # Mock responses for all the generate_content calls
        initial_concept_response = (
            "Here is the book concept:\n\n"
            "```json\n"
            '{"title": "The Discovery", "logline": "A brave astronaut discovers an ancient alien civilization", "description": "A fascinating concept about space exploration."}\n'
            "```"
        )
        critique_response = "This is a good concept with strong potential."
        refined_concept_response = (
            "Here is the refined concept:\n\n"
            "```json\n"
            '{"title": "The Discovery", "logline": "A brave astronaut discovers an ancient alien civilization", "description": "A refined concept about space exploration."}\n'
            "```"
        )
        keywords_response = 'Here are the keywords:\n\n```json\n{"keywords": ["space", "exploration"]}\n```'

        # Mock initial concept generation
        mock_llm.generate_content = AsyncMock(
            side_effect=[
                initial_concept_response,
            ]
        )
        # Mock content-filtering fallback calls for critique, refine, keywords
        mock_llm.generate_content_with_content_filtering_fallback = AsyncMock(
            side_effect=[
                critique_response,
                refined_concept_response,
                keywords_response,
            ]
        )
        agent = ConceptGeneratorAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.set("genre", "Science Fiction")

        output_path = str(tmp_path / "concept.json")

        # Act
        await agent.execute(kb, output_path=output_path)

        # Assert - Check that the correct files were created
        expected_files = ["1-concept.json", "2-concept_revised.json", "2-concept_revised.md"]

        for filename in expected_files:
            file_path = tmp_path / filename
            assert file_path.exists(), f"Expected file {filename} was not created"
