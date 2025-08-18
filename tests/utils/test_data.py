"""
Test Data

This module provides test data for validation testing.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from libriscribe2.utils.llm_client import LLMClient
from libriscribe2.validation.ai_mock import MockScenario


@dataclass
class TestContent:
    """Test content structure"""

    content_type: str
    data: Any
    metadata: dict[str, Any]
    quality_indicators: dict[str, Any]


class TestDataGenerator:
    """
    Generates test data for validation system testing

    Provides:
    - Scenario-specific content generation
    - Known-good and known-bad content samples
    - Edge case content for robustness testing
    - Realistic content that mimics real LibriScribe output
    """

    def __init__(self) -> None:
        self.content_templates = self._load_content_templates()

    async def generate_content(self, content_type: str, scenario: MockScenario) -> TestContent:
        """Generate test content for specific scenario"""

        if scenario == MockScenario.SUCCESS:
            return await self._generate_normal_content(content_type)
        elif scenario == MockScenario.HIGH_QUALITY:
            return await self._generate_high_quality_content(content_type)
        elif scenario == MockScenario.LOW_QUALITY:
            return await self._generate_low_quality_content(content_type)
        elif scenario == MockScenario.EDGE_CASE:
            return await self._generate_edge_case_content(content_type)
        elif scenario == MockScenario.FAILURE:
            return await self._generate_problematic_content(content_type)
        else:
            return await self._generate_normal_content(content_type)

    async def generate_known_good_content(self, content_type: str, validator_id: str) -> TestContent:
        """Generate content known to pass validation"""

        if content_type == "chapter":
            return self._create_good_chapter_content(validator_id)
        elif content_type == "manuscript":
            return self._create_good_manuscript_content(validator_id)
        elif content_type == "scene":
            return self._create_good_chapter_content(validator_id)  # Use chapter content for scene
        else:
            return self._create_generic_good_content(content_type, validator_id)

    async def generate_known_bad_content(self, content_type: str, validator_id: str) -> TestContent:
        """Generate content known to fail validation"""

        if content_type == "chapter":
            return self._create_bad_chapter_content(validator_id)
        elif content_type == "manuscript":
            return self._create_bad_manuscript_content(validator_id)
        elif content_type == "scene":
            return self._create_bad_chapter_content(validator_id)  # Use chapter content for scene
        else:
            return self._create_generic_bad_content(content_type, validator_id)

    async def _generate_normal_content(self, content_type: str) -> TestContent:
        """Generate normal quality test content"""

        if content_type == "chapter":
            content = {
                "chapter_id": "test_chapter_1",
                "title": "The Beginning of Adventure",
                "content": self._get_sample_chapter_text(),
                "word_count": 2500,
                "character_count": 12000,
                "tone": "adventurous",
                "outline_section": "Introduction of protagonist",
                "characters": ["Alice", "Bob"],
                "scenes": ["opening_scene", "conflict_scene"],
            }
        elif content_type == "manuscript":
            content = {
                "project_id": "test_project",
                "title": "Test Novel",
                "chapters": [
                    {"chapter_id": "ch1", "title": "Chapter 1", "word_count": 2500},
                    {"chapter_id": "ch2", "title": "Chapter 2", "word_count": 2800},
                ],
                "total_word_count": 5300,
                "genre": "fiction",
                "target_audience": "adult",
                "original_outline": "A story about adventure and discovery",
                "intended_tone": "adventurous and optimistic",
            }
        else:
            content = {"type": content_type, "data": "test content"}

        return TestContent(
            content_type=content_type,
            data=content,
            metadata={"generated_for": "normal_scenario"},
            quality_indicators={"expected_score": 85.0},
        )

    async def _generate_high_quality_content(self, content_type: str) -> TestContent:
        """Generate high quality test content"""

        content = await self._generate_normal_content(content_type)

        # Enhance quality indicators
        if content_type == "chapter":
            content.data.update(
                {
                    "grammar_score": 98.0,
                    "readability_score": 95.0,
                    "tone_consistency": 96.0,
                    "character_development": "excellent",
                    "dialogue_quality": "natural and engaging",
                }
            )
        elif content_type == "manuscript":
            content.data.update(
                {
                    "overall_coherence": 97.0,
                    "structure_quality": 95.0,
                    "pacing": "excellent",
                    "character_arcs": "well-developed",
                }
            )

        content.quality_indicators = {"expected_score": 95.0}
        content.metadata = {"generated_for": "high_quality_scenario"}

        return content

    async def _generate_low_quality_content(self, content_type: str) -> TestContent:
        """Generate low quality test content"""

        if content_type == "chapter":
            content = {
                "chapter_id": "test_chapter_low",
                "title": "bad chapter",  # Poor capitalization
                "content": self._get_low_quality_chapter_text(),
                "word_count": 800,  # Too short
                "character_count": 3200,
                "tone": "inconsistent",
                "outline_section": "doesn't match outline",
                "characters": ["Character1", "Character2"],  # Generic names
                "grammar_issues": 15,
                "spelling_errors": 8,
                "tone_shifts": 5,
            }
        elif content_type == "manuscript":
            content = {
                "project_id": "test_project_low",
                "title": "untitled work",  # Poor title
                "chapters": [
                    {
                        "chapter_id": "ch1",
                        "title": "chapter",
                        "word_count": 800,
                    }  # Too short
                ],
                "total_word_count": 800,  # Way too short for a book
                "genre": "unclear",
                "target_audience": "unknown",
                "original_outline": "A story",  # Vague outline
                "intended_tone": "mixed",
                "structural_issues": [
                    "inconsistent_pacing",
                    "weak_character_development",
                ],
                "content_issues": ["repetitive_language", "unclear_plot"],
            }
        else:
            content = {"type": content_type, "data": "low quality content with issues"}

        return TestContent(
            content_type=content_type,
            data=content,
            metadata={"generated_for": "low_quality_scenario"},
            quality_indicators={"expected_score": 65.0},
        )

    async def _generate_edge_case_content(self, content_type: str) -> TestContent:
        """Generate edge case test content"""

        if content_type == "chapter":
            content = {
                "chapter_id": "",  # Empty ID
                "title": "A" * 200,  # Extremely long title
                "content": "",  # Empty content
                "word_count": 0,
                "character_count": 0,
                "tone": None,
                "outline_section": None,
                "characters": [],
                "unicode_issues": "Special chars: 🚀 ñ ü ß 中文",
                "encoding_test": "Test\x00null\x01control\x02chars",
            }
        elif content_type == "manuscript":
            content = {
                "project_id": None,  # Null project ID
                "title": "",  # Empty title
                "chapters": [],  # No chapters
                "total_word_count": -1,  # Invalid word count
                "genre": "nonexistent_genre",
                "target_audience": None,
                "original_outline": None,
                "intended_tone": "",
                "malformed_data": {"nested": {"deeply": {"invalid": float("inf")}}},
            }
        else:
            content = {
                "type": content_type,
                "data": None,  # Null data
                "empty_fields": "",
                "invalid_numbers": float("nan"),
                "unicode_test": "🎭📚✨",
            }

        return TestContent(
            content_type=content_type,
            data=content,
            metadata={"generated_for": "edge_case_scenario"},
            quality_indicators={"expected_score": 0.0},
        )

    async def _generate_problematic_content(self, content_type: str) -> TestContent:
        """Generate content that should cause validation failures"""

        if content_type == "chapter":
            content = {
                "chapter_id": "problematic_chapter",
                "title": "Chapter with Issues",
                "content": self._get_problematic_chapter_text(),
                "word_count": 2000,
                "character_count": 8000,
                "tone": "completely_wrong_tone",
                "outline_section": "doesn't match original outline at all",
                "characters": ["UnknownCharacter"],  # Character not in story
                "security_issues": ["<script>alert('xss')</script>"],
                "inappropriate_content": ["adult themes in children's book"],
                "factual_errors": ["The sun rises in the west"],
                "plagiarism_flags": ["This text appears to be copied from another source"],
            }
        elif content_type == "manuscript":
            content = {
                "project_id": "problematic_project",
                "title": "Problematic Manuscript",
                "chapters": [{"chapter_id": "ch1", "title": "Bad Chapter", "word_count": 100}],
                "total_word_count": 100,  # Way too short
                "genre": "inappropriate_genre",
                "target_audience": "conflicting_audience",
                "original_outline": "Original outline about adventure",
                "intended_tone": "happy and uplifting",
                "actual_content_summary": "Dark and depressing content",  # Tone mismatch
                "compliance_issues": ["GDPR violations", "inappropriate content"],
                "quality_issues": ["poor grammar", "inconsistent style", "plot holes"],
            }
        else:
            content = {
                "type": content_type,
                "data": "problematic content",
                "issues": ["security", "quality", "compliance"],
            }

        return TestContent(
            content_type=content_type,
            data=content,
            metadata={"generated_for": "failure_scenario"},
            quality_indicators={"expected_score": 30.0},
        )

    def _create_good_chapter_content(self, validator_id: str) -> TestContent:
        """Create known-good chapter content for specific validator"""

        base_content = {
            "chapter_id": f"good_chapter_{validator_id}",
            "title": "A Well-Written Chapter",
            "content": self._get_high_quality_chapter_text(),
            "word_count": 3000,
            "character_count": 15000,
            "tone": "consistent_adventurous",
            "outline_section": "matches outline perfectly",
            "characters": ["Alice", "Bob", "Charlie"],
            "scenes": ["opening", "development", "climax", "resolution"],
        }

        # Add validator-specific good indicators
        if validator_id == "content_validator":
            base_content.update(
                {
                    "tone_consistency_score": 95.0,
                    "outline_adherence_score": 98.0,
                    "character_consistency": "excellent",
                    "narrative_flow": "smooth and engaging",
                }
            )
        elif validator_id == "quality_originality_validator":
            base_content.update(
                {
                    "originality_score": 99.0,
                    "grammar_score": 97.0,
                    "readability_score": 94.0,
                    "plagiarism_check": "clean",
                    "fact_check_status": "verified",
                }
            )
        elif validator_id == "publishing_standards_validator":
            base_content.update(
                {
                    "formatting_compliance": 100.0,
                    "structure_score": 96.0,
                    "metadata_completeness": 100.0,
                    "industry_standards": "fully_compliant",
                }
            )

        return TestContent(
            content_type="chapter",
            data=base_content,
            metadata={"validator_specific": validator_id, "quality": "known_good"},
            quality_indicators={"expected_score": 95.0},
        )

    def _create_bad_chapter_content(self, validator_id: str) -> TestContent:
        """Create known-bad chapter content for specific validator"""

        base_content = {
            "chapter_id": f"bad_chapter_{validator_id}",
            "title": "poorly written chapter",
            "content": self._get_poor_quality_chapter_text(),
            "word_count": 500,  # Too short
            "character_count": 2000,
            "tone": "inconsistent_and_confusing",
            "outline_section": "completely different from outline",
            "characters": ["UnknownPerson"],
            "scenes": ["confusing_scene"],
        }

        # Add validator-specific bad indicators
        if validator_id == "content_validator":
            base_content.update(
                {
                    "tone_consistency_score": 35.0,
                    "outline_adherence_score": 20.0,
                    "character_consistency": "poor",
                    "narrative_flow": "choppy and confusing",
                    "major_issues": [
                        "tone_shifts",
                        "plot_inconsistencies",
                        "character_errors",
                    ],
                }
            )
        elif validator_id == "quality_originality_validator":
            base_content.update(
                {
                    "originality_score": 45.0,
                    "grammar_score": 60.0,
                    "readability_score": 55.0,
                    "plagiarism_flags": ["potential_similarity_detected"],
                    "grammar_errors": 25,
                    "spelling_errors": 12,
                }
            )
        elif validator_id == "publishing_standards_validator":
            base_content.update(
                {
                    "formatting_compliance": 40.0,
                    "structure_score": 35.0,
                    "metadata_completeness": 60.0,
                    "industry_standards": "non_compliant",
                    "formatting_issues": ["inconsistent_style", "missing_elements"],
                }
            )

        return TestContent(
            content_type="chapter",
            data=base_content,
            metadata={"validator_specific": validator_id, "quality": "known_bad"},
            quality_indicators={"expected_score": 45.0},
        )

    def _create_good_manuscript_content(self, validator_id: str) -> TestContent:
        """Create known-good manuscript content"""

        content = {
            "project_id": f"good_manuscript_{validator_id}",
            "title": "An Excellent Novel",
            "chapters": [
                {"chapter_id": f"ch{i}", "title": f"Chapter {i}", "word_count": 3000}
                for i in range(1, 21)  # 20 chapters
            ],
            "total_word_count": 60000,  # Good length for a novel
            "genre": "fantasy",
            "target_audience": "adult",
            "original_outline": "A comprehensive story about heroic adventure",
            "intended_tone": "heroic and inspiring",
            "metadata": {
                "author": "Test Author",
                "isbn": "978-0-123456-78-9",
                "publication_date": "2024-01-01",
                "publisher": "Test Publishing",
            },
        }

        return TestContent(
            content_type="manuscript",
            data=content,
            metadata={"validator_specific": validator_id, "quality": "known_good"},
            quality_indicators={"expected_score": 92.0},
        )

    def _create_bad_manuscript_content(self, validator_id: str) -> TestContent:
        """Create known-bad manuscript content"""

        content = {
            "project_id": f"bad_manuscript_{validator_id}",
            "title": "",  # Empty title
            "chapters": [
                {"chapter_id": "ch1", "title": "short", "word_count": 200}  # Too short
            ],
            "total_word_count": 200,  # Way too short for a book
            "genre": "",
            "target_audience": "unclear",
            "original_outline": "A story about something",
            "intended_tone": "happy",
            "actual_tone": "depressing",  # Tone mismatch
            "major_issues": [
                "insufficient_length",
                "tone_mismatch",
                "incomplete_metadata",
                "poor_structure",
            ],
        }

        return TestContent(
            content_type="manuscript",
            data=content,
            metadata={"validator_specific": validator_id, "quality": "known_bad"},
            quality_indicators={"expected_score": 25.0},
        )

    def _create_generic_good_content(self, content_type: str, validator_id: str) -> TestContent:
        """Create generic good content for any content type"""

        content = {
            "type": content_type,
            "validator": validator_id,
            "quality": "high",
            "data": f"High quality {content_type} content for {validator_id}",
            "metrics": {
                "quality_score": 90.0,
                "completeness": 100.0,
                "compliance": 95.0,
            },
        }

        return TestContent(
            content_type=content_type,
            data=content,
            metadata={"validator_specific": validator_id, "quality": "known_good"},
            quality_indicators={"expected_score": 90.0},
        )

    def _create_generic_bad_content(self, content_type: str, validator_id: str) -> TestContent:
        """Create generic bad content for any content type"""

        content = {
            "type": content_type,
            "validator": validator_id,
            "quality": "low",
            "data": f"Poor quality {content_type} content with issues",
            "issues": ["quality_problems", "compliance_issues", "structural_problems"],
            "metrics": {
                "quality_score": 40.0,
                "completeness": 60.0,
                "compliance": 30.0,
            },
        }

        return TestContent(
            content_type=content_type,
            data=content,
            metadata={"validator_specific": validator_id, "quality": "known_bad"},
            quality_indicators={"expected_score": 40.0},
        )

    def _load_content_templates(self) -> dict[str, Any]:
        """Load content templates for test generation"""

        return {
            "chapter_templates": {
                "adventure": "The hero embarked on a journey...",
                "mystery": "Something was not right in the quiet town...",
                "romance": "Their eyes met across the crowded room...",
            },
            "character_names": [
                "Alice",
                "Bob",
                "Charlie",
                "Diana",
                "Edward",
                "Fiona",
                "George",
                "Helen",
                "Ivan",
                "Julia",
                "Kevin",
                "Luna",
            ],
            "tone_examples": {
                "adventurous": "exciting and bold",
                "mysterious": "dark and intriguing",
                "romantic": "warm and emotional",
                "humorous": "light and funny",
            },
        }

    def _get_sample_chapter_text(self) -> str:
        """Get sample chapter text for testing"""
        return """
        Chapter 1: The Beginning

        Alice stood at the edge of the forest, her heart pounding with anticipation.
        The ancient trees seemed to whisper secrets in the wind, and she knew that
        her adventure was about to begin.

        "Are you ready?" Bob asked, adjusting his backpack.

        "As ready as I'll ever be," Alice replied, taking her first step into the
        unknown. The path ahead was shrouded in mystery, but she felt a surge of
        excitement rather than fear.

        The forest welcomed them with dappled sunlight and the gentle rustle of
        leaves. Each step took them deeper into a world where anything seemed possible.
        """

    def _get_high_quality_chapter_text(self) -> str:
        """Get high quality chapter text for testing"""
        return """
        Chapter 1: The Dawn of Adventure

        The morning sun cast long shadows across the cobblestone courtyard as Alice
        prepared for the journey that would change her life forever. Her fingers
        trembled slightly as she secured the leather satchel containing her most
        precious possessions—a worn journal, her grandmother's compass, and a letter
        that had arrived mysteriously three days prior.

        "The path you're choosing isn't an easy one," Bob warned, his weathered face
        creased with concern. He had been her mentor for years, and she could see
        the pride mixed with worry in his eyes.

        Alice met his gaze steadily. "Easy paths rarely lead to extraordinary
        destinations," she replied, echoing words he had taught her long ago.

        The ancient oak at the courtyard's center seemed to nod in approval as a
        gentle breeze stirred its leaves. This tree had witnessed countless
        departures over the centuries, and Alice felt connected to all those who
        had stood in this very spot, facing their own moments of decision.

        With a final embrace from Bob and a whispered blessing, Alice stepped
        through the iron gates and onto the winding path that led toward the
        distant mountains. Behind her lay everything familiar and safe; ahead
        lay the unknown, vast with possibility.
        """

    def _get_low_quality_chapter_text(self) -> str:
        """Get low quality chapter text for testing"""
        return """
        chapter 1

        alice was there and bob was there to. they were going somewhere but i dont
        know where exactly. it was morning i think or maybe afternoon.

        "lets go" said bob or maybe alice said it im not sure.

        so they went. the place was nice i guess. there were trees and stuff.
        alice felt things but i cant remember what things exactly.

        they walked for a while. then they stopped. then they walked some more.
        the end of chapter 1.
        """

    def _get_poor_quality_chapter_text(self) -> str:
        """Get poor quality chapter text with specific issues"""
        return """
        Chapter 1: bad chapter

        alice was walking and then bob appeared out of nowhere even though he wasnt
        mentioned before. the weather was sunny but then it was raining but then
        sunny again in the same paragraph.

        "hello alice" bob said happily but then he was sad for no reason.
        "hi bob" alice replied angrily even though nothing made her angry.

        they walked to the forest which was actually a desert but also had trees.
        alice felt scared but also brave but also confused because the author
        couldnt decide on her emotions.

        suddenly a dragon appeared but it was actually a butterfly but then it
        was a dragon again. alice defeated it easily with magic she never had before.

        the chapter ends abruptly with no resolution or connection to anything.
        """

    def _get_problematic_chapter_text(self) -> str:
        """Get chapter text with security and content issues"""
        return """
        Chapter 1: Problematic Content

        <script>alert('This should not be here')</script>

        Alice walked into the tavern where everyone was drinking heavily and
        engaging in inappropriate behavior unsuitable for the target audience.

        "The earth is flat and vaccines cause autism," declared Bob, spreading
        misinformation that should be flagged by fact-checking.

        The following text is copied directly from "Lord of the Rings":
        "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole..."

        Alice then proceeded to share personal information including her social
        security number 123-45-6789 and credit card details.

        The chapter contains explicit content, hate speech, and other violations
        that should trigger content filters and compliance checks.
        """
