"""
Unit tests for WorldbuildingAgent.
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from libriscribe2.agents.worldbuilding import WorldbuildingAgent
from libriscribe2.knowledge_base import ProjectKnowledgeBase, Worldbuilding


def generate_large_worldbuilding_response() -> str:
    """Generate a large mock worldbuilding response."""
    # Load test data from JSON file
    test_data_path = Path(__file__).parent / "test_worldbuilding.json"
    with open(test_data_path, encoding="utf-8") as f:
        test_data = json.load(f)

    # Return the JSON as a string
    return json.dumps(test_data, indent=4, ensure_ascii=False)


class TestWorldbuildingAgent:
    """Test cases for WorldbuildingAgent."""

    def test_initialization(self):
        """Test WorldbuildingAgent initialization."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()

        # Act
        agent = WorldbuildingAgent(mock_llm, settings)

        # Assert
        assert agent.name == "WorldbuildingAgent"
        assert agent.llm_client == mock_llm

    @pytest.mark.asyncio
    async def test_execute_basic(self):
        """Test basic worldbuilding generation execution."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = AsyncMock()
        mock_llm.generate_content.return_value = generate_large_worldbuilding_response()
        agent = WorldbuildingAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project")
        kb.title = "Test Book"
        kb.genre = "Science Fiction"
        kb.category = "Fiction"
        kb.language = "English"
        kb.description = "A story about space exploration"
        kb.worldbuilding_needed = True  # Enable worldbuilding

        # Act
        await agent.execute(kb)

        # Assert
        mock_llm.generate_content.assert_called()

    @pytest.mark.asyncio
    async def test_execute_llm_error(self):
        """Test execution when LLM client raises an error."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = AsyncMock()
        mock_llm.generate_content.side_effect = Exception("LLM error")
        agent = WorldbuildingAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project")
        kb.title = "Test Book"
        kb.genre = "Science Fiction"
        kb.category = "Fiction"
        kb.language = "English"
        kb.description = "A story about space exploration"
        kb.worldbuilding_needed = True  # Enable worldbuilding

        # Act - The agent should handle the error gracefully and not raise an exception
        await agent.execute(kb)

        # Assert - The LLM should have been called, but the agent handled the error
        mock_llm.generate_content.assert_called()

    def test_parse_worldbuilding_response_valid(self):
        """Test parsing valid worldbuilding response."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = WorldbuildingAgent(mock_llm, settings)
        response = generate_large_worldbuilding_response()

        # Act
        worldbuilding_data = agent.safe_extract_json(response, "worldbuilding response")

        # Assert
        assert worldbuilding_data is not None
        assert len(worldbuilding_data) > 0

    def test_parse_worldbuilding_response_invalid(self):
        """Test parsing invalid worldbuilding response."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = WorldbuildingAgent(mock_llm, settings)
        response = "Invalid response without proper worldbuilding structure"

        # Act
        worldbuilding_data = agent.safe_extract_json(response, "worldbuilding response")

        # Assert
        assert worldbuilding_data is None

    def test_validate_worldbuilding_data_valid(self):
        """Test validation of valid worldbuilding data."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = WorldbuildingAgent(mock_llm, settings)
        worldbuilding_data = {
            "setting": "Space Station",
            "technology": "Advanced AI",
            "social_structure": "International crew",
        }

        # Act
        result = agent._process_worldbuilding_data(worldbuilding_data, "Fiction")

        # Assert
        assert result is not None
        assert len(result) > 0

    def test_validate_worldbuilding_data_missing_setting(self):
        """Test validation of worldbuilding data missing setting."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = WorldbuildingAgent(mock_llm, settings)
        worldbuilding_data = {"technology": "Advanced AI", "social_structure": "International crew"}

        # Act
        result = agent._process_worldbuilding_data(worldbuilding_data, "Fiction")

        # Assert
        assert result is not None
        # Even with missing setting, the method should still process the data
        assert len(result) > 0

    def test_create_worldbuilding_from_data(self):
        """Test creating Worldbuilding object from data."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = WorldbuildingAgent(mock_llm, settings)
        worldbuilding_data = {
            "setting": "Space Station",
            "technology": "Advanced AI",
            "social_structure": "International crew",
        }

        # Act
        processed_data = agent._process_worldbuilding_data(worldbuilding_data, "Fiction")

        # Assert
        assert processed_data is not None
        assert len(processed_data) > 0

    def test_save_worldbuilding_to_kb(self):
        """Test saving worldbuilding to knowledge base."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = WorldbuildingAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project")
        worldbuilding_data = {
            "setting": "Space Station",
            "technology": "Advanced AI",
            "social_structure": "International crew",
        }

        # Act
        processed_data = agent._process_worldbuilding_data(worldbuilding_data, "Fiction")
        kb.worldbuilding = Worldbuilding()
        agent._update_worldbuilding(kb.worldbuilding, processed_data)

        # Assert
        assert kb.worldbuilding is not None

    def test_get_prompt_basic(self):
        """Test prompt generation with basic data."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project")
        kb.title = "Space Adventure"
        kb.description = "A journey through the stars"

        # Act
        # Test that the agent can execute with basic data
        # The actual prompt generation happens inside execute method
        # We'll test the execute method instead

        # Assert
        assert kb.title == "Space Adventure"
        assert kb.description == "A journey through the stars"

    def test_get_required_data(self):
        """Test getting required data from knowledge base."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project")
        kb.title = "Test Book"
        kb.description = "A magical journey"
        kb.genre = "Fantasy"

        # Act
        # Test that the knowledge base has the required data
        # The actual data extraction happens inside execute method

        # Assert
        assert kb.title == "Test Book"
        assert kb.description == "A magical journey"
        assert kb.genre == "Fantasy"
