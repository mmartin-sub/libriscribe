# tests/test_character_generator_refactored.py
"""Refactored tests for CharacterGeneratorAgent using base classes."""

from unittest.mock import AsyncMock

import pytest

from libriscribe2.agents.character_generator import CharacterGeneratorAgent


class TestCharacterGeneratorRefactored:
    """Refactored tests for CharacterGeneratorAgent."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client for testing."""
        mock_client = AsyncMock()
        mock_client.generate_content.return_value = "Mock response"
        return mock_client

    @pytest.fixture
    def sample_knowledge_base(self):
        """Create a sample knowledge base for testing."""
        from libriscribe2.knowledge_base import ProjectKnowledgeBase

        return ProjectKnowledgeBase(
            project_name="test_project",
            title="Test Book",
            genre="Fantasy",
            description="A test book for unit testing",
            category="Fiction",
            language="English",
            num_characters=3,
            num_chapters=5,
            worldbuilding_needed=True,
            book_length="Novel",
        )

    def test_character_generator_initialization(self, mock_llm_client):
        """Test that CharacterGeneratorAgent initializes correctly."""
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = CharacterGeneratorAgent(mock_llm_client, settings)
        assert agent.name == "CharacterGeneratorAgent"
        assert agent.llm_client == mock_llm_client

    @pytest.mark.asyncio
    async def test_execute_success(self, sample_knowledge_base, mock_llm_client, tmp_path):
        """Test successful character generation."""
        # Setup mock response
        mock_response = """
        ```json
        [
            {
                "name": "John Doe",
                "age": "25",
                "physical_description": "Tall and athletic",
                "personality_traits": "Brave, loyal, curious",
                "background": "Orphan raised by wolves",
                "motivations": "Find his true identity",
                "relationships": {"Jane": "Best friend"},
                "role": "Protagonist",
                "internal_conflicts": "Fear of abandonment",
                "external_conflicts": "Evil empire",
                "character_arc": "From orphan to hero"
            }
        ]
        ```"""

        mock_llm_client.generate_content.return_value = mock_response

        from libriscribe2.settings import Settings

        settings = Settings()
        agent = CharacterGeneratorAgent(mock_llm_client, settings)
        output_path = str(tmp_path / "characters.json")

        # Execute
        await agent.execute(sample_knowledge_base, output_path)

        # Verify
        assert len(sample_knowledge_base.characters) == 1
        character = sample_knowledge_base.characters["John Doe"]
        assert character.name == "John Doe"
        assert character.age == "25"
        assert character.role == "Protagonist"

    @pytest.mark.asyncio
    async def test_execute_no_response(self, sample_knowledge_base, mock_llm_client):
        """Test character generation with no LLM response."""
        mock_llm_client.generate_content.return_value = None

        from libriscribe2.settings import Settings

        settings = Settings()
        agent = CharacterGeneratorAgent(mock_llm_client, settings)
        initial_count = len(sample_knowledge_base.characters)

        await agent.execute(sample_knowledge_base)

        # Should not add any characters
        assert len(sample_knowledge_base.characters) == initial_count

    @pytest.mark.asyncio
    async def test_execute_invalid_json(self, sample_knowledge_base, mock_llm_client):
        """Test character generation with invalid JSON response."""
        mock_llm_client.generate_content.return_value = "Invalid JSON response"

        from libriscribe2.settings import Settings

        settings = Settings()
        agent = CharacterGeneratorAgent(mock_llm_client, settings)
        initial_count = len(sample_knowledge_base.characters)

        await agent.execute(sample_knowledge_base)

        # Should not add any characters
        assert len(sample_knowledge_base.characters) == initial_count

    @pytest.mark.asyncio
    async def test_execute_empty_character_list(self, sample_knowledge_base, mock_llm_client):
        """Test character generation with empty character list."""
        mock_response = "```json\n[]\n```"
        mock_llm_client.generate_content.return_value = mock_response

        from libriscribe2.settings import Settings

        settings = Settings()
        agent = CharacterGeneratorAgent(mock_llm_client, settings)
        initial_count = len(sample_knowledge_base.characters)

        await agent.execute(sample_knowledge_base)

        # Should not add any characters
        assert len(sample_knowledge_base.characters) == initial_count

    @pytest.mark.asyncio
    async def test_execute_partial_character_data(self, sample_knowledge_base, mock_llm_client):
        """Test character generation with partial character data."""
        mock_response = """
        ```json
        [
            {
                "name": "Jane Smith",
                "age": "30"
            }
        ]
        ```"""

        mock_llm_client.generate_content.return_value = mock_response

        from libriscribe2.settings import Settings

        settings = Settings()
        agent = CharacterGeneratorAgent(mock_llm_client, settings)

        await agent.execute(sample_knowledge_base)

        # Should add character with default values for missing fields
        assert len(sample_knowledge_base.characters) == 1
        character = sample_knowledge_base.characters["Jane Smith"]
        assert character.name == "Jane Smith"
        assert character.age == "30"
        assert character.physical_description == ""  # Default empty string

    @pytest.mark.asyncio
    async def test_execute_save_to_file(self, sample_knowledge_base, mock_llm_client, tmp_path):
        """Test that characters are saved to file when output_path is provided."""
        mock_response = """
        ```json
        [
            {
                "name": "Test Character",
                "age": "25",
                "role": "Supporting"
            }
        ]
        ```"""

        mock_llm_client.generate_content.return_value = mock_response

        from libriscribe2.settings import Settings

        settings = Settings()
        agent = CharacterGeneratorAgent(mock_llm_client, settings)
        output_path = str(tmp_path / "test_characters.json")

        await agent.execute(sample_knowledge_base, output_path)

        # Verify file was created
        import os

        assert os.path.exists(output_path)

    @pytest.mark.asyncio
    async def test_execute_exception_handling(self, sample_knowledge_base, mock_llm_client):
        """Test that exceptions are properly handled."""
        mock_llm_client.generate_content.side_effect = Exception("LLM Error")

        from libriscribe2.settings import Settings

        settings = Settings()
        agent = CharacterGeneratorAgent(mock_llm_client, settings)
        initial_count = len(sample_knowledge_base.characters)

        # Should not raise exception
        await agent.execute(sample_knowledge_base)

        # Should not add any characters
        assert len(sample_knowledge_base.characters) == initial_count

    @pytest.mark.asyncio
    async def test_character_creation_with_relationships(self, sample_knowledge_base, mock_llm_client):
        """Test character creation with relationship data."""
        mock_response = """
        ```json
        [
            {
                "name": "Alice",
                "relationships": "Close to family"
            }
        ]
        ```"""

        mock_llm_client.generate_content.return_value = mock_response

        from libriscribe2.settings import Settings

        settings = Settings()
        agent = CharacterGeneratorAgent(mock_llm_client, settings)

        await agent.execute(sample_knowledge_base)

        # Verify character with relationships was created
        assert len(sample_knowledge_base.characters) == 1
        character = sample_knowledge_base.characters["Alice"]
        assert character.relationships == {"general": "Close to family"}

    @pytest.mark.asyncio
    async def test_character_creation_with_string_relationships(self, sample_knowledge_base, mock_llm_client):
        """Test character creation with string relationship data."""
        mock_response = """
        ```json
        [
            {
                "name": "Bob",
                "relationships": "Close to family"
            }
        ]
        ```"""

        mock_llm_client.generate_content.return_value = mock_response

        from libriscribe2.settings import Settings

        settings = Settings()
        agent = CharacterGeneratorAgent(mock_llm_client, settings)

        await agent.execute(sample_knowledge_base)

        # Verify character with string relationships was converted to dict
        assert len(sample_knowledge_base.characters) == 1
        character = sample_knowledge_base.characters["Bob"]
        assert character.relationships == {"general": "Close to family"}
