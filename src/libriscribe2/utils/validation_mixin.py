"""
Validation Mixin

This module provides validation utilities.
"""

import logging
import secrets
from pathlib import Path
from typing import Any


class ValidationMixin:
    """Mixin providing common validation methods."""

    @staticmethod
    def validate_title(title: str) -> str:
        """Validate and clean a book title."""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        return title.strip()

    @staticmethod
    def validate_language(language: str) -> str:
        """Validate and clean a language string."""
        if not language or not language.strip():
            raise ValueError("Language cannot be empty")
        return language.strip()

    @staticmethod
    def validate_description(description: str) -> str:
        """Validate and clean a description."""
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")
        return description.strip()

    @staticmethod
    def validate_output_dir(output_dir: str | None) -> str | None:
        """Validate and create output directory if needed."""
        if output_dir is None:
            return None

        path = Path(output_dir)
        if path.exists() and not path.is_dir():
            raise ValueError(f"Output path exists but is not a directory: {output_dir}")

        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    @staticmethod
    def validate_chapters(
        chapters: int | str | tuple[int, int] | None,
    ) -> int | tuple[int, int] | None:
        """Validate chapter count."""
        if chapters is None:
            return None
        elif isinstance(chapters, str):
            try:
                if "-" in chapters:
                    min_chapters, max_chapters = map(int, chapters.split("-"))
                    if min_chapters < 1 or max_chapters < min_chapters:
                        raise ValueError(f"Invalid chapter range: {chapters}")
                    return (min_chapters, max_chapters)
                else:
                    chapter_count = int(chapters)
                    if chapter_count < 1:
                        raise ValueError(f"Invalid chapter count: {chapters}")
                    return chapter_count
            except ValueError as err:
                raise ValueError(f"Invalid chapter format '{chapters}': {err}") from err
        elif isinstance(chapters, int):
            if chapters < 1:
                raise ValueError("Chapter count must be at least 1")
            return chapters
        elif isinstance(chapters, tuple):
            if len(chapters) != 2 or chapters[0] < 1 or chapters[1] < chapters[0]:
                raise ValueError("Invalid chapter range")
            return chapters
        else:
            raise ValueError(f"Invalid chapter type: {type(chapters)}")

    @staticmethod
    def validate_characters(
        characters: int | str | tuple[int, int] | None,
    ) -> int | tuple[int, int] | None:
        """Validate character count."""
        if characters is None:
            return None
        elif isinstance(characters, str):
            try:
                if "-" in characters:
                    min_characters, max_characters = map(int, characters.split("-"))
                    if min_characters < 0 or max_characters < min_characters:
                        raise ValueError(f"Invalid character range: {characters}")
                    return (min_characters, max_characters)
                else:
                    character_count = int(characters)
                    if character_count < 0:
                        raise ValueError(f"Invalid character count: {characters}")
                    return character_count
            except ValueError as err:
                raise ValueError(f"Invalid character format '{characters}': {err}") from err
        elif isinstance(characters, int):
            if characters < 0:
                raise ValueError("Character count must be non-negative")
            return characters
        elif isinstance(characters, tuple):
            if len(characters) != 2 or characters[0] < 0 or characters[1] < characters[0]:
                raise ValueError("Invalid character range")
            return characters
        else:
            raise ValueError(f"Invalid character type: {type(characters)}")

    @staticmethod
    def validate_scenes_per_chapter(
        scenes: int | str | tuple[int, int],
    ) -> int | tuple[int, int]:
        """Validate scenes per chapter count."""
        if isinstance(scenes, str):
            try:
                return int(scenes)
            except ValueError as err:
                raise ValueError(f"Invalid scenes per chapter count: {scenes}") from err
        elif isinstance(scenes, int):
            if scenes < 1:
                raise ValueError("Scenes per chapter must be at least 1")
            return scenes
        elif isinstance(scenes, tuple):
            if len(scenes) != 2 or scenes[0] < 1 or scenes[1] < scenes[0]:
                raise ValueError("Invalid scenes per chapter range")
            return scenes
        else:
            raise ValueError(f"Invalid scenes per chapter type: {type(scenes)}")

    @staticmethod
    def generate_random_scene_count(scene_range: str) -> int:
        """Generate a random scene count within the specified range."""
        try:
            if "-" in scene_range:
                min_scenes, max_scenes = map(int, scene_range.split("-"))
                if min_scenes < 1 or max_scenes < min_scenes:
                    raise ValueError(f"Invalid scene range: {scene_range}")
                # Use secrets.randbelow() for better randomness
                # randbelow(n) returns [0, n), so we need to adjust for [min, max]
                range_size = max_scenes - min_scenes + 1
                return min_scenes + secrets.randbelow(range_size)
            else:
                scene_count = int(scene_range)
                if scene_count < 1:
                    raise ValueError(f"Invalid scene count: {scene_range}")
                return scene_count
        except ValueError as e:
            raise ValueError(f"Invalid scene range format '{scene_range}': {e}")

    @staticmethod
    def generate_random_chapter_count(chapter_range: str) -> int:
        """Generate a random chapter count within the specified range."""
        try:
            if "-" in chapter_range:
                min_chapters, max_chapters = map(int, chapter_range.split("-"))
                if min_chapters < 1 or max_chapters < min_chapters:
                    raise ValueError(f"Invalid chapter range: {chapter_range}")
                # Use secrets.randbelow() for better randomness
                # randbelow(n) returns [0, n), so we need to adjust for [min, max]
                range_size = max_chapters - min_chapters + 1
                return min_chapters + secrets.randbelow(range_size)
            else:
                chapter_count = int(chapter_range)
                if chapter_count < 1:
                    raise ValueError(f"Invalid chapter count: {chapter_range}")
                return chapter_count
        except ValueError as e:
            raise ValueError(f"Invalid chapter range format '{chapter_range}': {e}")

    @staticmethod
    def generate_random_character_count(character_range: str) -> int:
        """Generate a random character count within the specified range."""
        try:
            if "-" in character_range:
                min_characters, max_characters = map(int, character_range.split("-"))
                if min_characters < 0 or max_characters < min_characters:
                    raise ValueError(f"Invalid character range: {character_range}")
                # Use secrets.randbelow() for better randomness
                # randbelow(n) returns [0, n), so we need to adjust for [min, max]
                range_size = max_characters - min_characters + 1
                return min_characters + secrets.randbelow(range_size)
            else:
                character_count = int(character_range)
                if character_count < 0:
                    raise ValueError(f"Invalid character count: {character_range}")
                return character_count
        except ValueError as e:
            raise ValueError(f"Invalid character range format '{character_range}': {e}")

    @staticmethod
    def validate_category(category: str) -> str:
        """Validate book category."""
        valid_categories = [
            "Fiction",
            "Non-Fiction",
            "Business",
            "Research Paper",
            "Academic",
            "Technical",
            "Biography",
            "History",
            "Science",
        ]
        if category not in valid_categories:
            # Allow custom categories but log as info
            logging.getLogger(__name__).info(f"Custom category used: {category}")
        return category

    @staticmethod
    def validate_genre(genre: str | None) -> str:
        """Validate book genre."""
        if genre is None:
            return "General"
        return genre.strip()

    @staticmethod
    def validate_target_audience(target_audience: str | None) -> str:
        """Validate target audience."""
        if target_audience is None:
            return "General"

        audience = target_audience.strip()
        if not audience:
            return "General"

        # Common target audiences (for reference, but allow any value)
        common_audiences = [
            "General",
            "Young Adult",
            "Adult",
            "Children",
            "Teen",
            "Middle Grade",
            "New Adult",
            "Senior",
            "Academic",
            "Professional",
        ]

        # Log as info if using a non-common audience (but don't reject it)
        if audience not in common_audiences:
            logging.getLogger(__name__).info(f"Custom target audience used: {audience}")

        return audience

    @staticmethod
    def validate_llm_provider(provider: str | None) -> str:
        """Validate LLM provider."""
        valid_providers = ["openai", "mock"]
        if provider is None:
            return "openai"
        if provider not in valid_providers:
            raise ValueError(f"Invalid LLM provider: {provider}")
        return provider

    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = False) -> str:
        """Validate file path."""
        path = Path(file_path)
        if must_exist and not path.exists():
            raise ValueError(f"File does not exist: {file_path}")
        return str(path)

    @staticmethod
    def validate_json_data(data: Any, expected_type: type = dict) -> bool:
        """Validate JSON data structure."""
        if not isinstance(data, expected_type):
            return False
        if expected_type is dict and not data:
            return False
        return True
