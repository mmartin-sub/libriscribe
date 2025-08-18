"""
Unit tests for OutlinerAgent.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from libriscribe2.agents.outliner import OutlinerAgent
from libriscribe2.knowledge_base import Chapter, ProjectKnowledgeBase


def create_test_project_dir(project_name: str = "test_project") -> Path:
    """Create a test project directory with proper naming convention."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    process_id = os.getpid()
    test_dir_name = f"{project_name}-{timestamp}-{process_id}"
    test_dir = Path(tempfile.gettempdir()) / test_dir_name
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


def generate_large_outline_response() -> str:
    """Generate a large mock outline response."""
    return """
    # Book Outline: Space Adventure

    ## Chapter 1: The Discovery
    In the year 2150, Dr. Sarah Chen, a brilliant astrophysicist working at the International Space Station, makes a groundbreaking discovery. While analyzing data from a deep space probe, she detects unusual energy signatures emanating from a previously unexplored region of the galaxy. The signals suggest the presence of intelligent life, something humanity has been searching for since the dawn of space exploration.

    ## Chapter 2: The Mission
    The United Nations Space Agency hastily assembles a crew for humanity's first interstellar mission. Commander Marcus Rodriguez, a decorated astronaut with years of experience, is chosen to lead the expedition. The crew includes Dr. Chen, engineer Alex Thompson, and communications specialist Dr. Elena Petrov. Their mission: make first contact with the alien civilization and establish peaceful relations.

    ## Chapter 3: The Journey
    The crew embarks on their journey aboard the experimental starship Odyssey, equipped with the latest in propulsion technology. The three-year voyage tests not only their physical endurance but also their psychological resilience. As they travel deeper into space, they encounter cosmic phenomena that challenge their understanding of the universe and force them to confront their own humanity.

    ## Chapter 4: First Contact
    The Odyssey finally reaches its destination: a planet orbiting a binary star system. What they discover exceeds all expectations. The alien civilization, known as the Zephyrians, has been monitoring Earth for centuries. They reveal that humanity stands at a crucial crossroads in its development, and their guidance could help Earth avoid the same mistakes that nearly destroyed their own world.

    ## Chapter 5: The Choice
    The crew must decide whether to accept the Zephyrians' offer of advanced technology and knowledge. While this could solve many of Earth's problems, it also raises questions about humanity's independence and the potential consequences of such rapid advancement. The decision will shape not only their own future but the destiny of all humankind.

    ## Chapter 6: Return to Earth
    The crew returns to Earth with their findings, but they discover that their three-year absence has changed the world they left behind. Political tensions have escalated, and the revelation of alien contact threatens to destabilize global order. The crew must navigate the complex political landscape while sharing their extraordinary experiences.

    ## Chapter 7: The Aftermath
    As Earth grapples with the implications of first contact, the crew faces personal challenges. Dr. Chen struggles with the weight of her discovery and its impact on human society. Commander Rodriguez must reconcile his military training with the peaceful nature of their mission. Each crew member must find their place in a world that has been forever changed.

    ## Chapter 8: New Horizons
    The story concludes with humanity's first steps toward a new era of interstellar cooperation. The crew's mission has opened the door to unprecedented possibilities, but it has also revealed the challenges that lie ahead. The final chapter explores the hope and uncertainty that accompany humanity's entry into a larger galactic community.
    """


def generate_large_scene_outline_response() -> str:
    """Generate a large mock scene outline response."""
    return """
    # Chapter 1 Scene Breakdown

    Scene 1:
        * Summary: Dr. Sarah Chen makes her groundbreaking discovery while working late at the International Space Station.
        * Characters: Dr. Sarah Chen, Commander Rodriguez, Mission Control
        * Setting: International Space Station, Earth orbit
        * Goal: Establish the discovery that sets the plot in motion
        * Emotional Beat: Excitement and wonder at the possibility of alien life

    Scene 2:
        * Summary: The crew must report their findings to Earth authorities and face the bureaucratic challenges of their discovery.
        * Characters: Full crew, Mission Control, Government officials
        * Setting: Space Station communications center
        * Goal: Navigate the political implications of their discovery
        * Emotional Beat: Tension and uncertainty about how Earth will react

    Scene 3:
        * Summary: The crew learns about the mission to make first contact and must decide whether to volunteer.
        * Characters: Crew members, Mission Control, UN representatives
        * Setting: Space Station conference room
        * Goal: Establish the crew's commitment to the mission
        * Emotional Beat: Determination mixed with apprehension about the unknown

    Scene 4:
        * Summary: The crew prepares for their historic mission by undergoing final training and equipment checks.
        * Characters: Full crew, Training officers, Technical specialists
        * Setting: Space Station training module
        * Goal: Ensure all crew members are prepared for the mission
        * Emotional Beat: Focus and determination as they prepare for the unknown

    Scene 5:
        * Summary: The crew receives their final briefing and makes their last communications with Earth before departure.
        * Characters: Crew members, Mission Control, Family members
        * Setting: Space Station communications center
        * Goal: Complete final preparations and say farewell to Earth
        * Emotional Beat: Bittersweet farewell mixed with anticipation

    Scene 6:
        * Summary: The crew boards their spacecraft and begins the countdown to launch, marking the beginning of their historic journey.
        * Characters: Full crew, Mission Control, Launch specialists
        * Setting: Spacecraft cockpit and launch facility
        * Goal: Successfully launch the mission
        * Emotional Beat: Nervous excitement as they embark on humanity's greatest adventure
    """


def generate_flexible_scene_outline_response(num_scenes: int = 6) -> str:
    """Generate a flexible mock scene outline response with the specified number of scenes."""
    scene_templates = [
        {
            "summary": "Dr. Sarah Chen makes her groundbreaking discovery while working late at the International Space Station.",
            "characters": "Dr. Sarah Chen, Commander Rodriguez, Mission Control",
            "setting": "International Space Station, Earth orbit",
            "goal": "Establish the discovery that sets the plot in motion",
            "emotional_beat": "Excitement and wonder at the possibility of alien life",
        },
        {
            "summary": "The crew must report their findings to Earth authorities and face the bureaucratic challenges of their discovery.",
            "characters": "Full crew, Mission Control, Government officials",
            "setting": "Space Station communications center",
            "goal": "Navigate the political implications of their discovery",
            "emotional_beat": "Tension and uncertainty about how Earth will react",
        },
        {
            "summary": "The crew learns about the mission to make first contact and must decide whether to volunteer.",
            "characters": "Crew members, Mission Control, UN representatives",
            "setting": "Space Station conference room",
            "goal": "Establish the crew's commitment to the mission",
            "emotional_beat": "Determination mixed with apprehension about the unknown",
        },
        {
            "summary": "The crew prepares for their historic mission by undergoing final training and equipment checks.",
            "characters": "Full crew, Training officers, Technical specialists",
            "setting": "Space Station training module",
            "goal": "Ensure all crew members are prepared for the mission",
            "emotional_beat": "Focus and determination as they prepare for the unknown",
        },
        {
            "summary": "The crew receives their final briefing and makes their last communications with Earth before departure.",
            "characters": "Crew members, Mission Control, Family members",
            "setting": "Space Station communications center",
            "goal": "Complete final preparations and say farewell to Earth",
            "emotional_beat": "Bittersweet farewell mixed with anticipation",
        },
        {
            "summary": "The crew boards their spacecraft and begins the countdown to launch, marking the beginning of their historic journey.",
            "characters": "Full crew, Mission Control, Launch specialists",
            "setting": "Spacecraft cockpit and launch facility",
            "goal": "Successfully launch the mission",
            "emotional_beat": "Nervous excitement as they embark on humanity's greatest adventure",
        },
    ]

    # Use only the requested number of scenes
    scenes_to_use = scene_templates[:num_scenes]

    scene_sections = []
    for i, scene in enumerate(scenes_to_use, 1):
        scene_section = f"""
    Scene {i}:
        * Summary: {scene["summary"]}
        * Characters: {scene["characters"]}
        * Setting: {scene["setting"]}
        * Goal: {scene["goal"]}
        * Emotional Beat: {scene["emotional_beat"]}
"""
        scene_sections.append(scene_section)

    return f"""
    # Chapter 1 Scene Breakdown
{"".join(scene_sections)}
    """


class TestOutlinerAgent:
    """Test cases for OutlinerAgent."""

    def test_initialization(self):
        """Test OutlinerAgent initialization."""
        # Arrange
        mock_llm = MagicMock()

        # Act
        agent = OutlinerAgent(mock_llm)

        # Assert
        assert agent.name == "OutlinerAgent"
        assert agent.llm_client == mock_llm

    @pytest.mark.asyncio
    async def test_execute_basic(self):
        """Test basic outline generation execution."""
        # Arrange
        mock_llm = AsyncMock()

        # Create a flexible mock that returns appropriate responses for any number of calls
        call_count = 0

        def mock_generate_content(*args, **kwargs):
            # First call is always for outline generation
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                return generate_large_outline_response()
            else:
                # For scene generation calls, detect the number of scenes from the prompt
                prompt = args[0] if args else ""

                # Look for "EXACTLY X scenes" in the prompt to determine scene count
                import re

                scene_match = re.search(r"EXACTLY (\d+) scenes", prompt)
                if scene_match:
                    num_scenes = int(scene_match.group(1))
                    return generate_flexible_scene_outline_response(num_scenes)
                else:
                    # Default to 6 scenes if we can't detect the count
                    return generate_flexible_scene_outline_response(6)

        mock_llm.generate_content.side_effect = mock_generate_content

        agent = OutlinerAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.description = "A story about space exploration"
        kb.num_chapters = 5

        # Create test project directory with proper naming convention
        test_project_dir = create_test_project_dir("test_project")
        kb.project_dir = test_project_dir

        try:
            # Act
            await agent.execute(kb)

            # Assert
            mock_llm.generate_content.assert_called()
        finally:
            # Clean up test directory
            import shutil

            if test_project_dir.exists():
                shutil.rmtree(test_project_dir)

    @pytest.mark.asyncio
    async def test_execute_llm_error(self):
        """Test execution when LLM client raises an error."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.generate_content.side_effect = Exception("LLM error")
        agent = OutlinerAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert
        with pytest.raises(Exception):
            await agent.execute(kb)

    def test_process_outline(self):
        """Test processing outline."""
        # Arrange
        mock_llm = MagicMock()
        agent = OutlinerAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        outline_markdown = generate_large_outline_response()
        max_chapters = 8

        # Act
        agent.process_outline(kb, outline_markdown, max_chapters)

        # Assert
        assert len(kb.chapters) > 0

    def test_enforce_chapter_limit(self):
        """Test enforcing chapter limit."""
        # Arrange
        mock_llm = MagicMock()
        agent = OutlinerAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.add_chapter(Chapter(chapter_number=1, title="Chapter 1", summary="Introduction"))
        kb.add_chapter(Chapter(chapter_number=2, title="Chapter 2", summary="Development"))
        kb.add_chapter(Chapter(chapter_number=3, title="Chapter 3", summary="Climax"))
        kb.add_chapter(Chapter(chapter_number=4, title="Chapter 4", summary="Conclusion"))
        max_chapters = 2

        # Act
        agent._enforce_chapter_limit(kb, max_chapters)

        # Assert
        assert len(kb.chapters) == 2

    def test_update_outline_markdown(self):
        """Test updating outline markdown."""
        # Arrange
        mock_llm = MagicMock()
        agent = OutlinerAgent(mock_llm)
        original_outline = generate_large_outline_response()
        max_chapters = 3

        # Act
        updated_outline = agent._update_outline_markdown(original_outline, max_chapters)

        # Assert
        assert "Chapter 1" in updated_outline
        assert "Chapter 2" in updated_outline
        assert "Chapter 3" in updated_outline
        assert "Chapter 4" not in updated_outline
        assert "Chapter 5" not in updated_outline

    def test_get_project_type_chapters(self):
        """Test getting project type chapters."""
        # Arrange
        mock_llm = MagicMock()
        agent = OutlinerAgent(mock_llm)

        # Act & Assert
        assert agent._get_project_type_chapters("short_story") == 1
        assert agent._get_project_type_chapters("novella") == 5
        assert agent._get_project_type_chapters("book") == 8
        assert agent._get_project_type_chapters("novel") == 12
        assert agent._get_project_type_chapters("epic") == 20
        assert agent._get_project_type_chapters("unknown") == 12

    @pytest.mark.asyncio
    async def test_generate_scene_outline(self):
        """Test generating scene outline."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.generate_content.return_value = generate_large_scene_outline_response()
        agent = OutlinerAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        chapter = Chapter(chapter_number=1, title="Chapter 1", summary="Introduction")

        # Act
        result = await agent.generate_scene_outline(kb, chapter)

        # Assert
        assert result is True
        mock_llm.generate_content.assert_called()

    def test_split_into_scene_sections(self):
        """Test splitting into scene sections."""
        # Arrange
        mock_llm = MagicMock()
        agent = OutlinerAgent(mock_llm)
        scene_outline_md = generate_large_scene_outline_response()

        # Act
        sections = agent._split_into_scene_sections(scene_outline_md)

        # Assert
        assert len(sections) >= 2
        assert "Scene 1" in sections[0]
        assert "Scene 2" in sections[1]

    def test_extract_scene_data(self):
        """Test extracting scene data."""
        # Arrange
        mock_llm = MagicMock()
        agent = OutlinerAgent(mock_llm)
        scene_section = """
        Scene 1: Opening
        Summary: The story begins
        Characters: John, Mary
        Setting: Space station
        Goal: Establish characters
        Emotional Beat: Curiosity
        """

        # Act
        scene_data = agent._extract_scene_data(scene_section, 1)

        # Assert
        assert scene_data is not None
        assert scene_data["scene_number"] == 1
        assert scene_data["summary"] == "The story begins"

    def test_extract_scene_data_invalid(self):
        """Test extracting scene data from invalid section."""
        # Arrange
        mock_llm = MagicMock()
        agent = OutlinerAgent(mock_llm)
        scene_section = "Invalid scene section without proper format"

        # Act
        scene_data = agent._extract_scene_data(scene_section, 1)

        # Assert
        assert scene_data is None

    def test_process_scene_outline(self):
        """Test processing scene outline."""
        # Arrange
        mock_llm = MagicMock()
        agent = OutlinerAgent(mock_llm)
        chapter = Chapter(chapter_number=1, title="Chapter 1", summary="Introduction")
        scene_outline_md = generate_large_scene_outline_response()

        # Act
        agent.process_scene_outline(chapter, scene_outline_md)

        # Assert
        assert len(chapter.scenes) > 0
