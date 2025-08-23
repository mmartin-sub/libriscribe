"""
Unit tests for FormattingAgent.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from libriscribe2.agents.formatting import FormattingAgent
from libriscribe2.knowledge_base import Chapter, ProjectKnowledgeBase


def generate_large_formatting_response() -> str:
    """Generate a large mock formatting response."""
    return """
    # Book Formatting Results

    ## Formatted Manuscript: "The Discovery"

    # The Discovery
    *A Novel by Dr. Sarah Chen*

    ---

    ## Chapter 1: The Signal

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

    ---

    ## Chapter 2: The Mission

    Three weeks later, Sarah found herself in the cramped conference room of the United Nations Space Agency headquarters in Geneva. The room was filled with representatives from every major space-faring nation, all gathered to discuss the implications of her discovery.

    "Dr. Chen," said the UNSA Director, a stern woman with graying hair and the bearing of a military officer, "your discovery has been verified by multiple independent sources. We are now faced with a decision that will shape the future of humanity."

    Sarah nodded, feeling the weight of responsibility pressing down on her shoulders. "I understand the gravity of the situation, Director. But we have a moral obligation to respond to this signal."

    "And what if it's a trap?" asked the Russian representative, his accent thick with concern. "What if this is some kind of alien deception?"

    "That's a possibility we must consider," Sarah admitted. "But we can't let fear paralyze us. The signals are clearly artificial in origin, and they're coming from a region of space that would require technology far beyond our current capabilities to reach."

    The debate raged for hours, with representatives from different nations arguing for various approaches. Some wanted to send an immediate response, while others advocated for more study and preparation. Still others suggested keeping the discovery secret from the public.

    Finally, after a marathon session that lasted well into the night, a decision was reached. Humanity would respond to the signal, but with caution and preparation. A mission would be assembled, equipped with the best technology Earth could provide, and sent to investigate the source of the signals.

    Sarah would lead the scientific team, while Commander Rodriguez would handle the military and security aspects. It was a compromise that satisfied no one completely, but it was a start.

    As she left the conference room, Sarah couldn't help but think about the enormity of what they were about to attempt. They were about to make first contact with an alien civilization, an event that would change everything.

    The future of humanity hung in the balance, and she was at the center of it all.

    ---

    ## Formatting Notes

    **Structural Elements Added:**
    - Title page with author attribution
    - Chapter headings with consistent formatting
    - Proper paragraph spacing and indentation
    - Scene breaks with horizontal rules
    - Consistent typography throughout

    **Styling Improvements:**
    - Enhanced readability with proper spacing
    - Consistent formatting for dialogue
    - Clear visual hierarchy for headings
    - Professional manuscript layout
    - Proper quotation marks and punctuation

    **Technical Formatting:**
    - Standard manuscript format (1-inch margins, double spacing)
    - Consistent font usage and sizing
    - Proper page breaks and chapter divisions
    - Professional publishing standards
    - Accessibility considerations for digital formats

    **Content Organization:**
    - Logical chapter progression
    - Smooth transitions between scenes
    - Clear character introductions
    - Consistent narrative voice
    - Proper pacing and rhythm
    """


class TestFormattingAgent:
    """Test cases for FormattingAgent."""

    def test_initialization(self):
        """Test FormattingAgent initialization."""
        # Arrange
        mock_llm = MagicMock()
        from libriscribe2.settings import Settings

        settings = Settings()

        # Act
        agent = FormattingAgent(mock_llm, settings)

        # Assert
        assert agent.name == "FormattingAgent"
        assert agent.llm_client == mock_llm
        assert agent.settings == settings

    @pytest.mark.asyncio
    async def test_execute_basic(self):
        """Test basic formatting execution."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.generate_content.return_value = generate_large_formatting_response()
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = FormattingAgent(mock_llm, settings)

        # Create a unique temporary directory for this test in projects folder

        # Create projects directory in current working directory
        projects_dir = Path.cwd() / "projects"
        projects_dir.mkdir(exist_ok=True)

        # Create test project directory within projects
        test_dir = projects_dir / "test_project_formatting"
        test_dir.mkdir(exist_ok=True)

        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.project_dir = test_dir
        chapter = Chapter(chapter_number=1, title="Chapter 1")
        kb.add_chapter(chapter)

        # Create chapter files
        chapter_path = test_dir / "chapter_1.md"
        with open(chapter_path, "w") as f:
            f.write("# Chapter 1\n\nTest chapter content.")

        # Create project data file
        project_data_path = test_dir / settings.project_data_filename
        with open(project_data_path, "w") as f:
            f.write(kb.to_json())

        try:
            # Act
            await agent.execute(kb)

            # Assert
            mock_llm.generate_content.assert_called_once()
        finally:
            # Clean up
            import shutil

            shutil.rmtree(test_dir)

    @pytest.mark.asyncio
    async def test_execute_llm_error(self):
        """Test execution when LLM client raises an error."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.generate_content.side_effect = Exception("LLM error")
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = FormattingAgent(mock_llm, settings)

        # Create a unique temporary directory for this test in projects folder

        # Create projects directory in current working directory
        projects_dir = Path.cwd() / "projects"
        projects_dir.mkdir(exist_ok=True)

        # Create test project directory within projects
        test_dir = projects_dir / "test_project_formatting_error"
        test_dir.mkdir(exist_ok=True)

        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.project_dir = test_dir

        # Create chapter files
        chapter_path = test_dir / "chapter_1.md"
        with open(chapter_path, "w") as f:
            f.write("# Chapter 1\n\nTest chapter content.")

        # Create project data file
        project_data_path = test_dir / settings.project_data_filename
        with open(project_data_path, "w") as f:
            f.write(kb.to_json())

        try:
            # Act & Assert
            with pytest.raises(Exception, match="LLM error"):
                await agent.execute(kb)

            # Verify the mock was called
            mock_llm.generate_content.assert_called_once()
        finally:
            # Clean up
            import shutil

            shutil.rmtree(test_dir)

    def test_create_title_page(self):
        """Test creating title page."""
        # Arrange
        mock_llm = MagicMock()
        from libriscribe2.settings import Settings

        settings = Settings()
        agent = FormattingAgent(mock_llm, settings)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book", genre="Fiction")

        # Act
        title_page = agent.create_title_page(kb)

        # Assert
        assert "Test Book" in title_page
        assert "Fiction" in title_page

    @pytest.mark.asyncio
    async def test_execute_mock_mode_with_title_page(self, tmp_path):
        """Test that mock mode execution correctly adds a title page when enabled."""
        from libriscribe2.settings import Settings
        from libriscribe2.utils.mock_llm_client import MockLLMClient

        # Arrange
        settings = Settings()
        settings.formatting_add_title_page = True  # Enable title page

        mock_llm = MockLLMClient(settings=settings)
        agent = FormattingAgent(mock_llm, settings)

        # Create project structure in a temporary directory
        project_dir = tmp_path / "projects" / "test_project_mock_title"
        project_dir.mkdir(parents=True, exist_ok=True)

        kb = ProjectKnowledgeBase(
            project_name="test_project_mock_title", title="Mock Title", author="Mock Author", genre="Sci-Fi"
        )
        kb.project_dir = project_dir

        # Create a dummy chapter file
        (project_dir / "chapter_1.md").write_text("# Chapter 1\n\nHello world.")

        # Create a dummy project data file
        (project_dir / "project_data.json").write_text(kb.to_json())

        output_path = project_dir / "formatted_book.md"

        # Act
        with (
            patch.object(agent, "_validate_project_path", side_effect=lambda x: Path(x)),
            patch.object(agent, "_validate_output_path", side_effect=lambda x: Path(x)),
        ):
            print(f"Test project dir: {project_dir}")
            print(f"Files in dir: {list(project_dir.iterdir())}")
            await agent.execute(kb, output_path=str(output_path))

        # Assert
        assert output_path.exists()
        content = output_path.read_text()
        print(f"Final content:\n{content}")

        # Check for YAML frontmatter from the title page
        assert "---" in content
        assert 'title: "Mock Title"' in content
        assert 'author: "Mock Author"' in content
        assert 'genre: "Sci-Fi"' in content

        # Check for chapter content
        assert "# Chapter 1" in content
        assert "Hello world." in content
