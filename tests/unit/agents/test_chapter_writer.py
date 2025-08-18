"""
Unit tests for ChapterWriterAgent.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from libriscribe2.agents.chapter_writer import ChapterWriterAgent
from libriscribe2.knowledge_base import Chapter, ProjectKnowledgeBase


def generate_large_chapter_content() -> str:
    """Generate a large mock chapter content response."""
    return """
    # Chapter 1: The Discovery

    Dr. Sarah Chen floated weightlessly in the observation module of the International Space Station, her eyes fixed on the holographic display that showed the latest data from the deep space probe. The station was quiet at this hour, with only the gentle hum of life support systems and the occasional creak of metal as the massive structure orbited Earth at seventeen thousand miles per hour.

    The data stream had been running for three days straight, and Sarah had been monitoring it almost continuously. As the lead astrophysicist on the deep space exploration project, she had grown accustomed to the long hours and the isolation that came with her work. But tonight was different. Tonight, she had found something that defied all her expectations.

    The energy signatures she was analyzing were unlike anything she had ever seen before. The patterns were too regular, too structured to be natural phenomena. Her heart rate increased as she double-checked her calculations, running the data through every filter and algorithm she could think of. The results remained the same: these signals were artificial in origin.

    "Commander Rodriguez," she called out, her voice echoing through the empty module. "You need to see this."

    Commander Marcus Rodriguez, the station's commanding officer, appeared at the doorway within minutes. A decorated astronaut with twenty years of experience, Rodriguez had seen his share of extraordinary discoveries, but the look on Sarah's face told him this was something special.

    "What have you found, Doctor?" he asked, floating over to join her at the display.

    Sarah pointed to the energy signatures on the screen. "Look at these patterns. They're repeating in cycles of exactly 1.618 seconds. That's the golden ratio, Commander. No natural phenomenon produces signals with that kind of mathematical precision."

    Rodriguez studied the data, his military training helping him assess the implications. "Are you saying what I think you're saying?"

    "I'm saying we've detected signs of intelligent life," Sarah replied, her voice barely above a whisper. "And they're coming from a region of space we've never explored before."

    The implications were staggering. Humanity had been searching for extraterrestrial life since the dawn of space exploration, but to actually find evidence of it was beyond anything they had imagined. The discovery would change everything—science, religion, politics, the very way humans thought about their place in the universe.

    "We need to report this immediately," Rodriguez said, his voice firm with military discipline. "This is going to require the highest levels of government attention."

    Sarah nodded, but her mind was already racing ahead. This was just the beginning. If there was intelligent life out there, what did they want? Were they peaceful, or hostile? And most importantly, how would humanity respond to the knowledge that they were not alone in the universe?

    As she prepared to make the most important call of her career, Sarah couldn't help but wonder if this was the moment that would define her generation. The moment when humanity took its first step into a much larger world.

    The station continued its orbit, a tiny speck of human technology in the vastness of space, while inside, two people prepared to change the course of history with a single discovery.
    """


class TestChapterWriterAgent:
    """Test cases for ChapterWriterAgent."""

    def test_initialization(self):
        """Test ChapterWriterAgent initialization."""
        # Arrange
        mock_llm = MagicMock()

        # Act
        agent = ChapterWriterAgent(mock_llm)

        # Assert
        assert agent.name == "ChapterWriterAgent"
        assert agent.llm_client == mock_llm

    @pytest.mark.asyncio
    async def test_execute_basic(self):
        """Test basic chapter writing execution."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.generate_content.return_value = generate_large_chapter_content()
        agent = ChapterWriterAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.set("concept", "A story about space exploration")
        chapter = Chapter(chapter_number=1, title="Chapter 1")
        kb.add_chapter(chapter)

        # Act
        await agent.execute(kb, chapter_number=0)

        # Assert
        mock_llm.generate_content.assert_called()

    @pytest.mark.asyncio
    async def test_execute_llm_error(self):
        """Test execution when LLM client raises an error."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.generate_content.side_effect = Exception("LLM error")
        agent = ChapterWriterAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert
        with pytest.raises(Exception, match="LLM error"):
            await agent.execute(kb, chapter_number=0)

    def test_format_scene(self):
        """Test formatting scene content."""
        # Arrange
        mock_llm = MagicMock()
        agent = ChapterWriterAgent(mock_llm)
        scene_title = "Scene 1: Opening"
        scene_content = "### **Scene 1: Opening**\n\nThis is the scene content."

        # Act
        formatted_content = agent.format_scene(scene_title, scene_content)

        # Assert
        # Scene title should be removed and no commented headers added
        assert "<!-- ### **Scene 1: Opening** -->" not in formatted_content
        assert "This is the scene content." in formatted_content
        # The original heading should be removed from the content
        assert "### **Scene 1: Opening**" not in formatted_content

    def test_format_scene_no_heading(self):
        """Test formatting scene content without heading."""
        # Arrange
        mock_llm = MagicMock()
        agent = ChapterWriterAgent(mock_llm)
        scene_title = "Scene 1: Opening"
        scene_content = "This is the scene content without a heading."

        # Act
        formatted_content = agent.format_scene(scene_title, scene_content)

        # Assert
        # No commented headers should be added
        assert "<!-- ### **Scene 1: Opening** -->" not in formatted_content
        assert "This is the scene content without a heading." in formatted_content

    def test_format_scene_variant_heading(self):
        """Test formatting scene content with variant heading format."""
        # Arrange
        mock_llm = MagicMock()
        agent = ChapterWriterAgent(mock_llm)
        scene_title = "Scene 1: Opening"
        scene_content = "**Scene 1: Opening**\n\nThis is the scene content."

        # Act
        formatted_content = agent.format_scene(scene_title, scene_content)

        # Assert
        # No commented headers should be added
        assert "<!-- ### **Scene 1: Opening** -->" not in formatted_content
        assert "This is the scene content." in formatted_content
        # The original heading should be removed from the content
        assert "**Scene 1: Opening**" not in formatted_content

    @pytest.mark.asyncio
    async def test_execute_with_invalid_chapter_number(self):
        """Test execution with invalid chapter number."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.generate_content.return_value = generate_large_chapter_content()
        agent = ChapterWriterAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        # No chapters added

        # Act
        await agent.execute(kb, chapter_number=0)

        # Assert
        # Should create a default chapter and continue
        assert len(kb.chapters) == 1

    @pytest.mark.asyncio
    async def test_execute_with_empty_scenes(self):
        """Test execution with chapter that has no scenes."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.generate_content.return_value = generate_large_chapter_content()
        agent = ChapterWriterAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        chapter = Chapter(chapter_number=1, title="Chapter 1")
        kb.add_chapter(chapter)
        # No scenes added to chapter

        # Act
        await agent.execute(kb, chapter_number=0)

        # Assert
        # Should create a default scene and continue
        assert len(kb.chapters[0].scenes) == 1
