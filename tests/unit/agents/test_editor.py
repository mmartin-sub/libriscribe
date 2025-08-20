"""
Unit tests for EditorAgent.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from libriscribe2.agents.editor import EditorAgent
from libriscribe2.knowledge_base import Chapter, ProjectKnowledgeBase


def generate_large_editing_response() -> str:
    """Generate a large mock editing response."""
    return """
    # Chapter Editing Results

    ## Chapter 1: The Discovery - Edited Version

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

    ## Editing Notes

    **Structural Improvements:**
    - Enhanced the opening paragraph to better establish the setting and atmosphere
    - Improved the pacing by adding more descriptive details about the space station environment
    - Strengthened the dialogue between Sarah and Commander Rodriguez to show their different perspectives
    - Added more internal monologue to reveal Sarah's thoughts and motivations

    **Character Development:**
    - Expanded Sarah's background and personality traits
    - Added more detail about Commander Rodriguez's military background and decision-making process
    - Enhanced the contrast between scientific curiosity and military caution

    **Technical Accuracy:**
    - Verified the scientific details about space station operations
    - Ensured the dialogue reflects the characters' expertise and backgrounds
    - Maintained consistency with the established worldbuilding

    **Narrative Flow:**
    - Improved the transition from discovery to reporting
    - Enhanced the sense of urgency and importance
    - Better established the stakes and implications of the discovery

    **Language and Style:**
    - Refined sentence structure for better readability
    - Improved word choice for more precise and engaging prose
    - Enhanced the emotional impact of key moments
    """


class TestEditorAgent:
    """Test cases for EditorAgent."""

    def test_initialization(self):
        """Test EditorAgent initialization."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()

        # Act
        agent = EditorAgent(mock_llm, settings)

        # Assert
        assert agent.name == "EditorAgent"
        assert agent.llm_client == mock_llm

    @pytest.mark.asyncio
    async def test_execute_basic(self):
        """Test basic editing execution."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = AsyncMock()
        mock_llm.generate_content.return_value = generate_large_editing_response()
        agent = EditorAgent(mock_llm, settings)
        # Create a unique temporary directory for this test
        import os
        import tempfile

        test_dir = tempfile.mkdtemp(prefix="test_project_")

        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.project_dir = Path(test_dir)
        chapter = Chapter(chapter_number=1, title="Chapter 1")
        kb.add_chapter(chapter)

        # Create the chapter file in the test directory
        chapter_path = os.path.join(test_dir, "chapter_1.md")
        with open(chapter_path, "w") as f:
            f.write("# Chapter 1\n\nTest content")

        try:
            # Act & Assert
            with (
                patch("libriscribe2.utils.file_utils.write_markdown_file"),
                patch("libriscribe2.agents.editor.ContentReviewerAgent") as mock_reviewer_class,
            ):
                # Mock the ContentReviewerAgent with proper async setup
                mock_reviewer = AsyncMock()
                mock_reviewer.execute = AsyncMock(return_value=None)
                mock_reviewer.last_review_results = {"review": "Test review"}
                mock_reviewer_class.return_value = mock_reviewer

                await agent.execute(kb, chapter_number=1)

                # Assert
                mock_llm.generate_content.assert_called()
                mock_reviewer.execute.assert_called_once()
        finally:
            # Clean up
            import shutil

            shutil.rmtree(test_dir)

    @pytest.mark.asyncio
    async def test_execute_llm_error(self):
        """Test execution when LLM client raises an error."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = AsyncMock()
        mock_llm.generate_content.side_effect = Exception("LLM error")
        agent = EditorAgent(mock_llm, settings)

        # Create a unique temporary directory for this test
        import os
        import tempfile

        test_dir = tempfile.mkdtemp(prefix="test_project_")

        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.project_dir = Path(test_dir)
        chapter = Chapter(chapter_number=1, title="Chapter 1")
        kb.add_chapter(chapter)

        # Create the chapter file in the test directory
        chapter_path = os.path.join(test_dir, "chapter_1.md")
        with open(chapter_path, "w") as f:
            f.write("# Chapter 1\n\nTest content")

        try:
            # Act & Assert
            with (
                patch("libriscribe2.utils.file_utils.write_markdown_file"),
                patch("libriscribe2.agents.editor.ContentReviewerAgent") as mock_reviewer_class,
            ):
                # Mock the ContentReviewerAgent with proper async setup
                mock_reviewer = AsyncMock()
                mock_reviewer.execute = AsyncMock(return_value=None)
                mock_reviewer.last_review_results = {"review": "Test review"}
                mock_reviewer_class.return_value = mock_reviewer

                await agent.execute(kb, chapter_number=1)
                # The agent should handle the error gracefully and not raise an exception
                # The error should be logged but execution should continue
        finally:
            # Clean up
            import shutil

            shutil.rmtree(test_dir)

    @pytest.mark.asyncio
    async def test_execute_invalid_chapter_index(self):
        """Test execution with invalid chapter index."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = AsyncMock()
        # Configure the mock to return a valid response
        mock_llm.generate_content.return_value = "# Chapter 1\n\nEdited content"
        agent = EditorAgent(mock_llm, settings)

        # Create a unique temporary directory for this test
        import os
        import tempfile

        test_dir = tempfile.mkdtemp(prefix="test_project_")

        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.project_dir = Path(test_dir)
        # No chapters added

        # Create the chapter file in the test directory
        chapter_path = os.path.join(test_dir, "chapter_1.md")
        with open(chapter_path, "w") as f:
            f.write("# Chapter 1\n\nTest content")

        try:
            # Act & Assert
            with (
                patch("libriscribe2.utils.file_utils.write_markdown_file"),
                patch("libriscribe2.agents.editor.ContentReviewerAgent") as mock_reviewer_class,
            ):
                # Mock the ContentReviewerAgent with proper async setup
                mock_reviewer = AsyncMock()
                mock_reviewer.execute = AsyncMock(return_value=None)
                mock_reviewer.last_review_results = {"review": "Test review"}
                mock_reviewer_class.return_value = mock_reviewer

                await agent.execute(kb, chapter_number=1)
                # Should handle gracefully without raising IndexError
                # Verify the mock was called (once for editor)
                assert mock_llm.generate_content.call_count == 1
                # Verify the reviewer was called
                mock_reviewer.execute.assert_called_once()
        finally:
            # Clean up
            import shutil

            shutil.rmtree(test_dir)

    def test_extract_chapter_title(self):
        """Test extracting chapter title from content."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = EditorAgent(mock_llm, settings)
        content = "# Chapter 1: The Discovery\n\nThis is the chapter content."

        # Act
        title = agent.extract_chapter_title(content)

        # Assert
        assert title == "Chapter 1: The Discovery"

    def test_extract_scene_titles(self):
        """Test extracting scene titles from content."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = EditorAgent(mock_llm, settings)
        content = "# Chapter 1\n\n## Scene 1: Opening\nContent here.\n\n## Scene 2: Discovery\nMore content."

        # Act
        titles = agent.extract_scene_titles(content)

        # Assert
        assert len(titles) > 0
        assert any("Scene 1" in title for title in titles)

    def test_extract_chapter_number(self):
        """Test extracting chapter number from path."""
        # Arrange
        from libriscribe2.settings import Settings

        settings = Settings()
        mock_llm = MagicMock()
        agent = EditorAgent(mock_llm, settings)
        chapter_path = "chapter_1.md"

        # Act
        number = agent.extract_chapter_number(chapter_path)

        # Assert
        assert number == 1
