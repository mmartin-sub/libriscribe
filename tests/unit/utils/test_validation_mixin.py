from unittest.mock import patch

import pytest

from libriscribe2.utils.validation_mixin import ValidationMixin


class TestValidationMixin:
    def test_generate_random_chapter_count_single_value(self):
        """Test generating chapter count from a single value."""
        result = ValidationMixin.generate_random_chapter_count("10")
        assert result == 10

    def test_generate_random_chapter_count_range(self):
        """Test generating chapter count from a range."""
        with patch("secrets.randbelow") as mock_randbelow:
            # Mock randbelow to return 0, which should give us the minimum value
            mock_randbelow.return_value = 0
            result = ValidationMixin.generate_random_chapter_count("8-12")
            assert result == 8
            mock_randbelow.assert_called_once_with(5)  # range_size = 12 - 8 + 1 = 5

    def test_generate_random_chapter_count_range_max_value(self):
        """Test generating chapter count from a range with maximum value."""
        with patch("secrets.randbelow") as mock_randbelow:
            # Mock randbelow to return 4, which should give us the maximum value
            mock_randbelow.return_value = 4
            result = ValidationMixin.generate_random_chapter_count("8-12")
            assert result == 12
            mock_randbelow.assert_called_once_with(5)  # range_size = 12 - 8 + 1 = 5

    def test_generate_random_chapter_count_invalid_range(self):
        """Test generating chapter count with invalid range."""
        with pytest.raises(ValueError, match="Invalid chapter range"):
            ValidationMixin.generate_random_chapter_count("12-8")

    def test_generate_random_chapter_count_invalid_single_value(self):
        """Test generating chapter count with invalid single value."""
        with pytest.raises(ValueError, match="Invalid chapter count"):
            ValidationMixin.generate_random_chapter_count("0")

    def test_generate_random_chapter_count_invalid_format(self):
        """Test generating chapter count with invalid format."""
        with pytest.raises(ValueError, match="Invalid chapter range format"):
            ValidationMixin.generate_random_chapter_count("invalid")

    def test_validate_chapters_string_single_value(self):
        """Test validating chapters with string single value."""
        result = ValidationMixin.validate_chapters("10")
        assert result == 10

    def test_validate_chapters_string_range(self):
        """Test validating chapters with string range."""
        result = ValidationMixin.validate_chapters("8-12")
        assert result == (8, 12)

    def test_validate_chapters_integer(self):
        """Test validating chapters with integer value."""
        result = ValidationMixin.validate_chapters(10)
        assert result == 10

    def test_validate_chapters_tuple(self):
        """Test validating chapters with tuple range."""
        result = ValidationMixin.validate_chapters((8, 12))
        assert result == (8, 12)

    def test_validate_chapters_none(self):
        """Test validating chapters with None value."""
        result = ValidationMixin.validate_chapters(None)
        assert result is None

    def test_validate_chapters_invalid_string(self):
        """Test validating chapters with invalid string."""
        with pytest.raises(ValueError, match="Invalid chapter format"):
            ValidationMixin.validate_chapters("invalid")

    def test_validate_chapters_invalid_range(self):
        """Test validating chapters with invalid range."""
        with pytest.raises(ValueError, match="Invalid chapter range"):
            ValidationMixin.validate_chapters("12-8")

    def test_validate_chapters_invalid_type(self):
        """Test validating chapters with invalid type."""
        with pytest.raises(ValueError, match="Invalid chapter type"):
            ValidationMixin.validate_chapters(1.5)  # type: ignore[arg-type]

    def test_generate_random_character_count_single_value(self):
        """Test generating character count from a single value."""
        result = ValidationMixin.generate_random_character_count("5")
        assert result == 5

    def test_generate_random_character_count_range(self):
        """Test generating character count from a range."""
        with patch("secrets.randbelow") as mock_randbelow:
            # Mock randbelow to return 0, which should give us the minimum value
            mock_randbelow.return_value = 0
            result = ValidationMixin.generate_random_character_count("3-7")
            assert result == 3
            mock_randbelow.assert_called_once_with(5)  # range_size = 7 - 3 + 1 = 5

    def test_generate_random_character_count_range_max_value(self):
        """Test generating character count from a range with maximum value."""
        with patch("secrets.randbelow") as mock_randbelow:
            # Mock randbelow to return 4, which should give us the maximum value
            mock_randbelow.return_value = 4
            result = ValidationMixin.generate_random_character_count("3-7")
            assert result == 7
            mock_randbelow.assert_called_once_with(5)  # range_size = 7 - 3 + 1 = 5

    def test_generate_random_character_count_invalid_range(self):
        """Test generating character count with invalid range."""
        with pytest.raises(ValueError, match="Invalid character range"):
            ValidationMixin.generate_random_character_count("7-3")

    def test_generate_random_character_count_invalid_single_value(self):
        """Test generating character count with invalid single value."""
        with pytest.raises(ValueError, match="Invalid character range format"):
            ValidationMixin.generate_random_character_count("-1")

    def test_generate_random_character_count_invalid_format(self):
        """Test generating character count with invalid format."""
        with pytest.raises(ValueError, match="Invalid character range format"):
            ValidationMixin.generate_random_character_count("invalid")
