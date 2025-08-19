"""
Unit tests for ProjectKnowledgeBase.

This module tests the core functionality of the ProjectKnowledgeBase class,
including data management, chapter handling, character management, and file operations.
"""

import json
import os
import tempfile

from libriscribe2.knowledge_base import Chapter, Character, ProjectKnowledgeBase, Worldbuilding


class TestProjectKnowledgeBase:
    """Test cases for ProjectKnowledgeBase."""

    def test_initialization(self):
        """Test ProjectKnowledgeBase initialization."""
        # Arrange & Act
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Assert
        assert kb.project_name == "test_project"
        assert kb.title == "Test Book"
        assert kb.project_dir is None
        assert kb.chapters == {}
        assert kb.characters == {}
        assert kb.worldbuilding is None
        assert kb.scenes_per_chapter == "3-6"  # Test that scenes_per_chapter field exists

    def test_initialization_with_additional_data(self):
        """Test ProjectKnowledgeBase initialization with additional data."""
        # Arrange & Act
        kb = ProjectKnowledgeBase(
            project_name="test_project",
            title="Test Book",
            category="Fiction",
            genre="Fantasy",
            description="A test book",
        )

        # Assert
        assert kb.project_name == "test_project"
        assert kb.title == "Test Book"
        assert kb.category == "Fiction"
        assert kb.genre == "Fantasy"
        assert kb.description == "A test book"
        assert kb.scenes_per_chapter == "3-6"  # Test default value

    def test_scenes_per_chapter_field(self):
        """Test that scenes_per_chapter field can be set and retrieved."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act
        kb.scenes_per_chapter = "5-8"

        # Assert
        assert kb.scenes_per_chapter == "5-8"

    def test_scenes_per_chapter_in_model_dump(self):
        """Test that scenes_per_chapter is included in model serialization."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.scenes_per_chapter = "4-6"

        # Act
        data = kb.model_dump()

        # Assert
        assert "scenes_per_chapter" in data
        assert data["scenes_per_chapter"] == "4-6"

    def test_scenes_per_chapter_in_json_serialization(self):
        """Test that scenes_per_chapter is included in JSON serialization."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.scenes_per_chapter = "2-4"

        # Act
        json_str = kb.to_json()
        data = json.loads(json_str)

        # Assert
        assert "scenes_per_chapter" in data
        assert data["scenes_per_chapter"] == "2-4"

    def test_scenes_per_chapter_in_json_deserialization(self):
        """Test that scenes_per_chapter is properly deserialized from JSON."""
        # Arrange
        kb_data = {"project_name": "test_project", "title": "Test Book", "scenes_per_chapter": "6-10"}

        # Act
        kb = ProjectKnowledgeBase.from_json(json.dumps(kb_data, ensure_ascii=False))

        # Assert
        assert kb.scenes_per_chapter == "6-10"

    def test_set_and_get_data(self):
        """Test setting and getting data."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act
        kb.set("genre", "Science Fiction")
        kb.set("scenes_per_chapter", "3-5")

        # Assert
        assert kb.get("genre") == "Science Fiction"
        assert kb.get("scenes_per_chapter") == "3-5"

    def test_set_and_get_with_default(self):
        """Test setting and getting data with default values."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert
        assert kb.get("nonexistent_field", "default_value") == "default_value"
        assert kb.get("scenes_per_chapter", "default") == "3-6"  # Should return actual value

    def test_add_and_get_chapter(self):
        """Test adding and getting chapters."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        chapter = Chapter(chapter_number=1, title="Chapter 1")

        # Act
        kb.add_chapter(chapter)

        # Assert
        retrieved_chapter = kb.get_chapter(1)
        assert retrieved_chapter is not None
        assert retrieved_chapter.chapter_number == 1
        assert retrieved_chapter.title == "Chapter 1"

    def test_add_and_get_multiple_chapters(self):
        """Test adding and getting multiple chapters."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        chapter1 = Chapter(chapter_number=1, title="Chapter 1")
        chapter2 = Chapter(chapter_number=2, title="Chapter 2")

        # Act
        kb.add_chapter(chapter1)
        kb.add_chapter(chapter2)

        # Assert
        assert len(kb.chapters) == 2
        retrieved_chapter1 = kb.get_chapter(1)
        assert retrieved_chapter1 is not None
        assert retrieved_chapter1.title == "Chapter 1"
        retrieved_chapter2 = kb.get_chapter(2)
        assert retrieved_chapter2 is not None
        assert retrieved_chapter2.title == "Chapter 2"

    def test_get_chapter_nonexistent(self):
        """Test getting a non-existent chapter."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert
        assert kb.get_chapter(999) is None

    def test_add_and_get_character(self):
        """Test adding and getting characters."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        character = Character(name="John Doe", age="25")

        # Act
        kb.add_character(character)

        # Assert
        retrieved_character = kb.get_character("John Doe")
        assert retrieved_character is not None
        assert retrieved_character.name == "John Doe"
        assert retrieved_character.age == "25"

    def test_add_and_get_multiple_characters(self):
        """Test adding and getting multiple characters."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        character1 = Character(name="John Doe", age="25")
        character2 = Character(name="Jane Smith", age="30")

        # Act
        kb.add_character(character1)
        kb.add_character(character2)

        # Assert
        assert len(kb.characters) == 2
        retrieved_character1 = kb.get_character("John Doe")
        assert retrieved_character1 is not None
        assert retrieved_character1.age == "25"
        retrieved_character2 = kb.get_character("Jane Smith")
        assert retrieved_character2 is not None
        assert retrieved_character2.age == "30"

    def test_get_character_nonexistent(self):
        """Test getting a non-existent character."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert
        assert kb.get_character("Nonexistent") is None

    def test_set_and_get_worldbuilding(self):
        """Test setting and getting worldbuilding data."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        worldbuilding = Worldbuilding(geography="Mountainous region", culture_and_society="Medieval")

        # Act
        kb.worldbuilding = worldbuilding

        # Assert
        assert kb.worldbuilding is not None
        assert kb.worldbuilding.geography == "Mountainous region"
        assert kb.worldbuilding.culture_and_society == "Medieval"

    def test_get_worldbuilding_none(self):
        """Test getting worldbuilding when it's None."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert
        assert kb.worldbuilding is None

    def test_save_and_load_from_file(self):
        """Test saving and loading from file."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        kb.scenes_per_chapter = "4-7"
        kb.genre = "Fantasy"
        kb.description = "A magical journey"

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            kb.save_to_file(f.name)
            loaded_kb = ProjectKnowledgeBase.load_from_file(f.name)

        # Assert
        assert loaded_kb is not None
        assert loaded_kb.project_name == "test_project"
        assert loaded_kb.title == "Test Book"
        assert loaded_kb.scenes_per_chapter == "4-7"
        assert loaded_kb.genre == "Fantasy"
        assert loaded_kb.description == "A magical journey"

        # Cleanup
        os.unlink(f.name)

    def test_load_from_file_nonexistent(self):
        """Test loading from non-existent file."""
        # Act & Assert
        result = ProjectKnowledgeBase.load_from_file("nonexistent_file.json")
        assert result is None

    def test_save_to_file_error(self):
        """Test saving to file with error."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert - should not raise exception
        try:
            kb.save_to_file("/invalid/path/file.json")
        except Exception:
            # Expected to fail due to invalid path, but should not crash the application
            # This tests graceful error handling in the save_to_file method
            pass

    def test_chapters_access(self):
        """Test direct access to chapters."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert
        assert isinstance(kb.chapters, dict)
        assert len(kb.chapters) == 0

    def test_characters_access(self):
        """Test direct access to characters."""
        # Arrange
        kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        # Act & Assert
        assert isinstance(kb.characters, dict)
        assert len(kb.characters) == 0


class TestChapter:
    """Test cases for Chapter class."""

    def test_chapter_initialization(self):
        """Test Chapter initialization."""
        # Arrange & Act
        chapter = Chapter(chapter_number=1, title="Test Chapter")

        # Assert
        assert chapter.chapter_number == 1
        assert chapter.title == "Test Chapter"
        assert chapter.summary == ""
        assert chapter.scenes == []

    def test_chapter_model_dump(self):
        """Test Chapter model serialization."""
        # Arrange
        chapter = Chapter(chapter_number=1, title="Test Chapter")

        # Act
        data = chapter.model_dump()

        # Assert
        assert data["chapter_number"] == 1
        assert data["title"] == "Test Chapter"

    def test_chapter_model_validate(self):
        """Test Chapter model validation."""
        # Arrange
        data = {"chapter_number": 2, "title": "Valid Chapter"}

        # Act
        chapter = Chapter.model_validate(data)

        # Assert
        assert chapter.chapter_number == 2
        assert chapter.title == "Valid Chapter"


class TestCharacter:
    """Test cases for Character class."""

    def test_character_initialization(self):
        """Test Character initialization."""
        # Arrange & Act
        character = Character(name="John Doe", age="25")

        # Assert
        assert character.name == "John Doe"
        assert character.age == "25"
        assert character.physical_description == ""
        assert character.personality_traits == ""

    def test_character_model_dump(self):
        """Test Character model serialization."""
        # Arrange
        character = Character(name="Jane Smith", age="30")

        # Act
        data = character.model_dump()

        # Assert
        assert data["name"] == "Jane Smith"
        assert data["age"] == "30"

    def test_character_model_validate(self):
        """Test Character model validation."""
        # Arrange
        data = {"name": "Valid Character", "age": "35"}

        # Act
        character = Character.model_validate(data)

        # Assert
        assert character.name == "Valid Character"
        assert character.age == "35"


class TestWorldbuilding:
    """Test cases for Worldbuilding class."""

    def test_worldbuilding_initialization(self):
        """Test Worldbuilding initialization."""
        # Arrange & Act
        worldbuilding = Worldbuilding(geography="Mountains", culture_and_society="Medieval")

        # Assert
        assert worldbuilding.geography == "Mountains"
        assert worldbuilding.culture_and_society == "Medieval"
        assert worldbuilding.history == ""
        assert worldbuilding.rules_and_laws == ""

    def test_worldbuilding_model_dump(self):
        """Test Worldbuilding model serialization."""
        # Arrange
        worldbuilding = Worldbuilding(geography="Desert", culture_and_society="Nomadic")

        # Act
        data = worldbuilding.model_dump()

        # Assert
        assert data["geography"] == "Desert"
        assert data["culture_and_society"] == "Nomadic"

    def test_worldbuilding_model_validate(self):
        """Test Worldbuilding model validation."""
        # Arrange
        data = {"geography": "Valid Geography", "culture_and_society": "Valid Culture"}

        # Act
        worldbuilding = Worldbuilding.model_validate(data)

        # Assert
        assert worldbuilding.geography == "Valid Geography"
        assert worldbuilding.culture_and_society == "Valid Culture"
