"""
Unit tests for CharacterGeneratorAgent.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from libriscribe2.agents.character_generator import CharacterGeneratorAgent
from libriscribe2.knowledge_base import ProjectKnowledgeBase


def generate_large_character_response() -> str:
    """Generate a large mock character generation response."""
    return """
    # Character Generation Results

    ## Main Characters

    ### Protagonist: Dr. Sarah Chen
    **Role:** Lead Astrophysicist
    **Age:** 34
    **Background:** Born in San Francisco to immigrant parents, Sarah showed an early aptitude for science. She earned her PhD in Astrophysics from MIT and has spent the last decade working on deep space exploration projects.

    **Personality Traits:**
    - Brilliant but socially awkward
    - Driven by curiosity and the desire to understand the universe
    - Struggles with the weight of responsibility that comes with her discoveries
    - Has a dry sense of humor that emerges under stress

    **Physical Description:**
    - Average height with a slight build
    - Dark hair often pulled back in a practical bun
    - Intelligent brown eyes that light up when discussing her work
    - Moves with the careful precision of someone used to working in zero gravity

    **Motivations:**
    - Primary: To understand the nature of the alien signals and their implications for humanity
    - Secondary: To prove that her discovery is real and not a false positive
    - Personal: To make her parents proud and justify their sacrifices for her education

    **Internal Conflicts:**
    - Balancing scientific objectivity with the emotional impact of her discovery
    - Fear that her discovery will be used for military purposes
    - Guilt over the attention and pressure her discovery brings to her colleagues

    **External Conflicts:**
    - Skepticism from the scientific community
    - Government interference in her research
    - The physical and psychological challenges of space travel

    **Character Arc:**
    - Begins as a dedicated scientist focused purely on her research
    - Gradually realizes the broader implications of her discovery
    - Must learn to navigate political and social complexities
    - Ultimately becomes a voice for peaceful exploration and cooperation

    ### Antagonist: General Marcus Rodriguez
    **Role:** Military Commander
    **Age:** 52
    **Background:** A decorated military officer with thirty years of service, Rodriguez has seen combat in multiple conflicts. He's been assigned to oversee the space station's security and the mission's military aspects.

    **Personality Traits:**
    - Disciplined and methodical
        - Follows protocols strictly
        - Values order and hierarchy
        - Makes decisions based on risk assessment
    - Protective of his crew and mission
        - Willing to make difficult decisions for the greater good
        - Prioritizes safety and security
        - Has a strong sense of duty
    - Struggles with the unknown
        - Uncomfortable with situations he can't control
        - Tends to view new discoveries as potential threats
        - Has difficulty trusting alien intentions

    **Physical Description:**
    - Tall and physically fit despite his age
    - Short-cropped gray hair
    - Piercing blue eyes that miss nothing
    - Carries himself with military bearing even in civilian clothes

    **Motivations:**
    - Primary: To protect Earth and humanity from potential threats
    - Secondary: To maintain order and discipline within the mission
    - Personal: To prove that military oversight is necessary for scientific missions

    **Internal Conflicts:**
    - Balancing his duty to protect with the need for scientific discovery
    - Fear that his military background makes him unsuitable for peaceful contact
    - Guilt over past decisions that resulted in casualties

    **External Conflicts:**
    - Clashes with civilian scientists over mission priorities
        - Wants to arm the mission for self-defense
        - Scientists want to emphasize peaceful intentions
        - Must find compromise between security and diplomacy
    - Disagreements with mission control over protocols
        - Insists on military-style chain of command
        - Mission control prefers collaborative decision-making
        - Creates tension within the crew

    **Character Arc:**
    - Begins as a strict military commander focused on security
    - Gradually learns to trust the scientific process
    - Must overcome his prejudices about alien life
    - Ultimately becomes a bridge between military and civilian perspectives

    ## Supporting Characters

    ### Dr. Elena Petrov
    **Role:** Communications Specialist
    **Age:** 28
    **Background:** Born in Moscow, Elena is a linguistics expert specializing in first contact protocols. She's designed communication systems for potential alien encounters.

    **Personality Traits:**
    - Optimistic and enthusiastic about first contact
    - Skilled at reading body language and cultural cues
    - Sometimes naive about the potential dangers
    - Forms strong emotional bonds with her colleagues

    **Motivations:**
    - To establish peaceful communication with alien life
    - To prove that language can bridge any cultural divide
    - To make her family proud of her achievements

    **Character Arc:**
    - Begins as an idealistic communicator
    - Learns that not all differences can be resolved through language
    - Must adapt her communication strategies to reality
    - Becomes more pragmatic while maintaining hope

    ### Alex Thompson
    **Role:** Engineer
    **Age:** 31
    **Background:** A mechanical genius from Texas, Alex designed many of the systems that keep the space station running. He's practical, resourceful, and has a knack for solving problems under pressure.

    **Personality Traits:**
    - Practical and hands-on
    - Quick to adapt to new situations
    - Has a folksy sense of humor that helps relieve tension
    - Sometimes acts before thinking through consequences

    **Motivations:**
    - To keep the mission running smoothly
    - To prove that human ingenuity can solve any problem
    - To return home safely to his family

    **Character Arc:**
    - Begins as a practical problem-solver
    - Learns that some problems require more than technical solutions
    - Must balance his desire to help with the need to follow protocols
    - Becomes a voice of common sense in difficult situations
    """


class TestCharacterGeneratorAgent:
    """Test cases for CharacterGeneratorAgent."""

    def test_initialization(self):
        """Test CharacterGeneratorAgent initialization."""
        # Arrange
        mock_llm = MagicMock()

        # Act
        agent = CharacterGeneratorAgent(mock_llm)

        # Assert
        assert agent.name == "CharacterGeneratorAgent"
        assert agent.llm_client == mock_llm

    @pytest.mark.asyncio
    async def test_execute_basic(self):
        """Test basic character generation execution."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.generate_content.return_value = generate_large_character_response()
        agent = CharacterGeneratorAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.set("concept", "A story about space exploration")

        # Act
        await agent.execute(kb)

        # Assert
        mock_llm.generate_content.assert_called()

    @pytest.mark.asyncio
    async def test_execute_llm_error(self):
        """Test execution when LLM client raises an error."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.generate_content.side_effect = Exception("LLM error")
        agent = CharacterGeneratorAgent(mock_llm)
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act
        await agent.execute(kb)

        # Assert
        # The agent should handle the error gracefully and not raise an exception
        # The error should be logged but execution should continue

    def test_basic_functionality(self):
        """Test basic CharacterGeneratorAgent functionality."""
        # Arrange
        mock_llm = MagicMock()
        agent = CharacterGeneratorAgent(mock_llm)

        # Assert
        assert agent.name == "CharacterGeneratorAgent"
        assert agent.llm_client == mock_llm
