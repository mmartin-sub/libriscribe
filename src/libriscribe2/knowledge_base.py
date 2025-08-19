# src/libriscribe2/knowledge_base.py

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from libriscribe2.utils import project_state
from libriscribe2.utils.language import normalize_language
from libriscribe2.utils.timestamp_utils import (
    get_iso8601_utc_timestamp,
    iso_timestamp_to_utc_date,
)


class Character(BaseModel):
    name: str
    age: str = ""
    physical_description: str = ""
    personality_traits: str = ""
    background: str = ""
    motivations: str = ""
    relationships: dict[str, str] = {}  # Character name -> Relationship description
    role: str = ""
    internal_conflicts: str = ""
    external_conflicts: str = ""
    character_arc: str = ""


class Scene(BaseModel):
    scene_number: int
    summary: str = ""
    characters: list[str] = []  # List of character names
    setting: str = ""
    goal: str = ""  # What's the purpose of this scene?
    emotional_beat: str = ""  # What's the primary emotion conveyed?


class Chapter(BaseModel):
    chapter_number: int
    title: str = ""
    summary: str = ""
    scenes: list[Scene] = []
    # We don't store the full chapter text *here*, just metadata and scenes.


class Worldbuilding(BaseModel):
    # Keep this empty for now, and we will use it on the agents
    geography: str = ""
    culture_and_society: str = ""
    history: str = ""
    rules_and_laws: str = ""
    technology_level: str = ""
    magic_system: str = ""
    key_locations: str = ""
    important_organizations: str = ""
    flora_and_fauna: str = ""
    languages: str = ""
    religions_and_beliefs: str = ""
    economy: str = ""
    conflicts: str = ""
    # Non fiction
    setting_context: str = ""
    key_figures: str = ""
    major_events: str = ""
    underlying_causes: str = ""
    consequences: str = ""
    relevant_data: str = ""
    different_perspectives: str = ""
    key_concepts: str = ""
    # business
    industry_overview: str = ""
    target_audience: str = ""
    market_analysis: str = ""
    business_model: str = ""
    marketing_and_sales_strategy: str = ""
    operations: str = ""
    financial_projections: str = ""
    management_team: str = ""
    legal_and_regulatory_environment: str = ""
    risks_and_challenges: str = ""
    opportunities_for_growth: str = ""
    # research
    introduction: str = ""
    literature_review: str = ""
    methodology: str = ""
    results: str = ""
    discussion: str = ""
    conclusion: str = ""
    references: str = ""
    appendices: str = ""


class ProjectKnowledgeBase(BaseModel):
    project_name: str
    title: str = "Untitled"
    subtitle: str | None = None
    author: str | list[str] | None = None
    date: str | None = None
    publisher: str | None = None
    isbn: str | None = None
    rights: str | None = None
    subject: str | None = None
    koma_options: str | None = None
    dir: str | None = None
    fontsize: str | None = None
    classoption: list[str] | None = None
    genre: str = "Unknown Genre"
    description: str = "No description provided."
    category: str = "Unknown Category"
    language: str = "English"
    num_characters: int | tuple[int, int] | None = 0  # Keep, used by character generator
    num_characters_str: str = ""  # Keep for advanced
    worldbuilding_needed: bool = False  # Keep, used by worldbuilding generator
    review_preference: str = "AI"
    project_type: str = "novel"  # New field for project type
    book_length: str = ""
    auto_size: bool = True  # Track if auto-sizing is enabled
    logline: str = "No logline available"
    tone: str = "Informative"
    target_audience: str = "General"
    num_chapters: int | tuple[int, int] | None = 1  # Keep for chapter generation, advanced mode
    num_chapters_str: str = ""  # Keep for advanced
    chapters_str: str = ""  # Store original chapters specification (e.g., "8-12")
    scenes_per_chapter: str = "3-6"  # Scene range per chapter (e.g., "3-6", "2-4")
    config_file: str = "config.json"  # Name of the configuration file used
    dynamic_questions: dict[str, str] = {}  # Keep for advanced
    keywords: list[str] = Field(default_factory=list, description="A list of keywords for the book.")
    auto_title: bool = False  # Track if auto-title generation was enabled

    characters: dict[str, Character] = {}  # Character name -> Character object
    worldbuilding: Worldbuilding | None = None  # Make conditional on worldbuilding_needed
    chapters: dict[int, Chapter] = {}  # Chapter number -> Chapter object
    outline: str = ""  # Store outline as markdown
    project_dir: Path | None = None
    # Initial project creation timestamp (ISO 8601 UTC). This is the canonical stored value.
    # A global LLM datestamp (YYYY-MM-DD) is derived from this for tagging.
    initial_timestamp: str = Field(default_factory=get_iso8601_utc_timestamp)

    def model_post_init(self, __context: Any) -> None:  # pydantic v2 hook
        """Ensure global initial date is set when an instance is created."""
        try:
            ts = getattr(self, "initial_timestamp", None)
            if ts:
                # Derive date-only for global LLM tag state
                date_only = (
                    ts
                    if (isinstance(ts, str) and len(ts) == 10 and ts.count("-") == 2)
                    else iso_timestamp_to_utc_date(ts)
                )
                project_state.set_initial_date(date_only)
        except Exception:
            logging.getLogger(__name__).debug(
                "Failed to set initial date from timestamp in model_post_init; continuing",
                exc_info=True,
            )

    @field_validator("num_characters", "num_chapters", mode="before")
    @classmethod
    def parse_range_or_plus(cls, value: str | int | tuple[int, int]) -> int | tuple[int, int]:
        if isinstance(value, str):
            if "-" in value:
                try:
                    min_val, max_val = map(int, value.split("-"))
                    return (min_val, max_val)
                except ValueError:
                    return 0  # Default value
            elif "+" in value:
                try:
                    return int(value.replace("+", ""))
                except ValueError:
                    return 0  # Default
            else:
                try:
                    return int(value)
                except ValueError:
                    return 0
        return value

    @field_validator("language", mode="before")
    @classmethod
    def normalize_language_field(cls, value: str) -> str:
        if not value or len(value.strip()) == 0:
            return "en"
        return normalize_language(value)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def set(self, key: str, value: Any) -> None:
        if hasattr(self, key):
            setattr(self, key, value)

    def add_character(self, character: Character) -> None:
        self.characters[character.name] = character

    def get_character(self, character_name: str) -> Character | None:
        return self.characters.get(character_name)

    def add_chapter(self, chapter: Chapter) -> None:
        self.chapters[chapter.chapter_number] = chapter

    def get_chapter(self, chapter_number: int) -> Chapter | None:
        return self.chapters.get(chapter_number)

    def add_scene_to_chapter(self, chapter_number: int, scene: Scene) -> None:
        if chapter_number not in self.chapters:
            self.chapters[chapter_number] = Chapter(chapter_number=chapter_number)
        self.chapters[chapter_number].scenes.append(scene)

    def to_json(self) -> str:
        """Serializes the knowledge base to a JSON string."""
        json_data = self.model_dump_json(indent=4)  # Use model_dump_json
        return str(json_data)

    @classmethod
    def from_json(cls, json_str: str) -> ProjectKnowledgeBase:
        """Deserializes the knowledge base from a JSON string."""
        result: ProjectKnowledgeBase = cls.model_validate_json(json_str)
        return result

    def save_to_file(self, file_path: str) -> None:
        """Saves the knowledge base to a JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, file_path: str) -> ProjectKnowledgeBase | None:
        """Loads the knowledge base from a JSON file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                result = cls.from_json(f.read())
                # Ensure initial_timestamp exists (backward-compat for older files)
                if not getattr(result, "initial_timestamp", ""):
                    result.initial_timestamp = get_iso8601_utc_timestamp()
                # Update global project state for initial date used in tagging (date-only)
                try:
                    ts = result.initial_timestamp
                    date_only = (
                        ts
                        if (isinstance(ts, str) and len(ts) == 10 and ts.count("-") == 2)
                        else iso_timestamp_to_utc_date(ts)
                    )
                    prev = None
                    try:
                        prev = project_state.get_initial_date()
                    except Exception:
                        prev = None
                    # If we already had a startup datestamp, log the switch (continuing previous work)
                    if prev and prev != date_only:
                        logging.getLogger(__name__).info(
                            f"Continuing from existing project datestamp: KB={date_only}, startup={prev}. Using KB datestamp."
                        )
                    project_state.set_initial_date(date_only)
                except Exception:
                    # Don't fail loading if global state couldn't be set
                    logging.getLogger(__name__).debug(
                        "Failed to set global initial date from knowledge base; continuing",
                        exc_info=True,
                    )
                return result
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON in {file_path}")
            return None
        except Exception as e:
            print(f"ERROR loading knowledge base from {file_path}: {e}")
            return None
