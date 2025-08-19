"""
Unit tests for ContentReviewerAgent.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from libriscribe2.agents.content_reviewer import ContentReviewerAgent
from libriscribe2.knowledge_base import Chapter, ProjectKnowledgeBase


def generate_large_review_response() -> str:
    """Generate a large mock content review response."""
    return """
    # Content Review Report

    ## Overall Assessment: B+ (85/100)

    **Strengths:**
    - Compelling opening that immediately draws the reader into the story
    - Strong character development for both Dr. Sarah Chen and Commander Rodriguez
    - Excellent pacing that maintains reader engagement throughout the chapter
    - Authentic dialogue that reflects the characters' backgrounds and expertise
    - Vivid descriptions that create a strong sense of place and atmosphere
    - Effective use of scientific details that enhance credibility without overwhelming the reader
    - Emotional stakes are clearly established and compelling

    **Areas for Improvement:**
    - Some technical jargon could be simplified for broader audience appeal
    - The transition between the discovery and the reporting decision could be smoother
    - Consider adding more sensory details to enhance the space station environment
    - The ending could be strengthened to create more anticipation for the next chapter

    **Technical Accuracy:**
    - Space station operations and terminology are generally accurate
    - Scientific concepts are well-integrated and accessible
    - Military protocol and chain of command are realistically portrayed
    - The golden ratio reference adds an interesting mathematical element

    **Character Development:**
    - Dr. Sarah Chen: Well-developed protagonist with clear motivations and expertise
    - Commander Rodriguez: Effective supporting character with distinct personality and role
    - Both characters have believable reactions to the extraordinary discovery
    - Character interactions feel natural and serve the plot effectively

    **Plot and Structure:**
    - Strong central conflict with clear stakes
    - Logical progression from discovery to decision-making
    - Effective use of tension and suspense
    - Good balance between action and reflection

    **Writing Quality:**
    - Clear, engaging prose that flows well
    - Varied sentence structure maintains reader interest
    - Effective use of both dialogue and narration
    - Professional manuscript quality with few technical issues

    **Recommendations:**
    1. Consider expanding the description of the space station environment in the opening
    2. Add more specific details about the energy signatures to enhance scientific credibility
    3. Strengthen the emotional impact of the discovery on both characters
    4. Include more sensory details to immerse the reader in the space environment
    5. Consider adding a brief moment of doubt or uncertainty before the decision to report

    **Market Readiness:**
    - This chapter demonstrates strong commercial potential
    - Appeals to both science fiction and thriller audiences
    - Professional quality suitable for traditional publishing consideration
    - Engaging enough to maintain reader interest across multiple chapters

    **Specific Line Edits:**
    - Page 2, paragraph 3: Consider adding more detail about the data stream analysis
    - Page 4, dialogue: Commander Rodriguez's response could be more specific about military protocol
    - Page 6, final paragraph: The ending could be strengthened with more specific implications

    **Overall Recommendation:**
    This is a strong chapter that effectively establishes the story's premise and characters. With minor revisions to enhance sensory details and smooth transitions, this chapter would be ready for publication. The scientific elements are well-integrated, and the character dynamics are compelling. The discovery of extraterrestrial life is handled with appropriate gravity and scientific rigor.
    """


class TestContentReviewerAgent:
    """Test cases for ContentReviewerAgent."""

    def test_initialization(self):
        """Test ContentReviewerAgent initialization."""
        # Arrange
        from libriscribe2.settings import Settings
        settings = Settings()
        mock_llm = MagicMock()

        # Act
        agent = ContentReviewerAgent(mock_llm, settings)

        # Assert
        assert agent.name == "ContentReviewerAgent"
        assert agent.llm_client == mock_llm

    @pytest.mark.asyncio
    async def test_execute_basic(self):
        """Test basic content review execution."""
        # Arrange
        from libriscribe2.settings import Settings
        settings = Settings()
        mock_llm = AsyncMock()
        mock_llm.generate_content.return_value = generate_large_review_response()
        agent = ContentReviewerAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        chapter = Chapter(chapter_number=1, title="Chapter 1")
        kb.add_chapter(chapter)

        # Mock the read_markdown_file function
        with patch("libriscribe2.agents.content_reviewer.read_markdown_file", return_value="Test chapter content"):
            # Act
            await agent.execute(kb, chapter_path="test_chapter.md")

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
        agent = ContentReviewerAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        chapter = Chapter(chapter_number=1, title="Chapter 1")
        kb.add_chapter(chapter)

        # Act
        with patch("libriscribe2.agents.content_reviewer.read_markdown_file", return_value="Test chapter content"):
            await agent.execute(kb, chapter_path="test_chapter.md")

        # Assert
        # The agent should handle the error gracefully and not raise an exception
        # The error should be logged but execution should continue

    @pytest.mark.asyncio
    async def test_execute_invalid_chapter_index(self):
        """Test execution with invalid chapter index."""
        # Arrange
        from libriscribe2.settings import Settings
        settings = Settings()
        mock_llm = AsyncMock()
        agent = ContentReviewerAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        # No chapters added

        # Act & Assert
        with patch("libriscribe2.agents.content_reviewer.read_markdown_file", return_value="Test chapter content"):
            await agent.execute(kb, chapter_path="test_chapter.md")
            # Should handle gracefully without raising IndexError

    def test_basic_functionality(self):
        """Test basic ContentReviewerAgent functionality."""
        # Arrange
        from libriscribe2.settings import Settings
        settings = Settings()
        mock_llm = MagicMock()
        agent = ContentReviewerAgent(mock_llm, settings)

        # Assert
        assert agent.name == "ContentReviewerAgent"
        assert agent.llm_client == mock_llm
