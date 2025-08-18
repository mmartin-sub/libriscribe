"""
Unit tests for timestamp utilities.

Tests the timestamp utility functions to ensure they generate correct
ISO 8601-2:2019 UTC timestamps and handle various edge cases properly.
"""

import time
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from libriscribe2.utils.timestamp_utils import (
    convert_to_iso8601_utc,
    format_timestamp_for_filename,
    format_timestamp_for_folder_name,
    format_timestamp_for_folder_name_with_microseconds,
    get_iso8601_utc_datetime,
    get_iso8601_utc_timestamp,
    get_unix_timestamp,
    get_unix_timestamp_int,
    is_valid_iso8601_timestamp,
    parse_iso8601_timestamp,
)


class TestTimestampGeneration:
    """Test timestamp generation functions."""

    def test_get_iso8601_utc_timestamp_format(self):
        """Test that ISO 8601 UTC timestamp has correct format."""
        timestamp = get_iso8601_utc_timestamp()

        # Check format: YYYY-MM-DDTHH:MM:SS.ssssssZ
        assert len(timestamp) == 27  # 27 characters
        assert timestamp.count("-") == 2  # Two hyphens for date
        assert timestamp.count(":") == 2  # Two colons for time
        assert timestamp.count(".") == 1  # One dot for microseconds
        assert timestamp.endswith("Z")  # Ends with Z for UTC

        # Check that it's a valid datetime
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert parsed.tzinfo == UTC

    def test_get_iso8601_utc_timestamp_utc_timezone(self):
        """Test that timestamp is always in UTC timezone."""
        timestamp = get_iso8601_utc_timestamp()

        # Parse and verify timezone
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert parsed.tzinfo == UTC

        # Verify it's actually UTC (not local time)
        utc_now = datetime.now(UTC)
        time_diff = abs((parsed - utc_now).total_seconds())
        assert time_diff < 1.0  # Should be within 1 second

    def test_get_iso8601_utc_datetime(self):
        """Test that UTC datetime object is returned."""
        dt = get_iso8601_utc_datetime()

        assert isinstance(dt, datetime)
        assert dt.tzinfo == UTC

        # Verify it's recent
        utc_now = datetime.now(UTC)
        time_diff = abs((dt - utc_now).total_seconds())
        assert time_diff < 1.0

    def test_get_unix_timestamp(self):
        """Test Unix timestamp generation."""
        timestamp = get_unix_timestamp()

        assert isinstance(timestamp, float)
        assert timestamp > 0

        # Verify it's recent
        current_time = time.time()
        time_diff = abs(timestamp - current_time)
        assert time_diff < 1.0

    def test_get_unix_timestamp_int(self):
        """Test integer Unix timestamp generation."""
        timestamp = get_unix_timestamp_int()

        assert isinstance(timestamp, int)
        assert timestamp > 0

        # Verify it's recent
        current_time = int(time.time())
        time_diff = abs(timestamp - current_time)
        assert time_diff <= 1  # Should be within 1 second


class TestTimestampFormatting:
    """Test timestamp formatting functions."""

    def test_format_timestamp_for_filename(self):
        """Test filename timestamp formatting."""
        timestamp = format_timestamp_for_filename()

        # Format: YYYYMMDD_HHMMSS
        assert len(timestamp) == 15  # 15 characters
        assert timestamp.count("_") == 1  # One underscore separator
        assert timestamp.count("-") == 0  # No hyphens

        # Verify it's a valid date/time
        date_part = timestamp[:8]  # YYYYMMDD
        time_part = timestamp[9:]  # HHMMSS

        # Check date format
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        assert 2020 <= year <= 2030  # Reasonable year range
        assert 1 <= month <= 12
        assert 1 <= day <= 31

        # Check time format
        hour = int(time_part[:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        assert 0 <= hour <= 23
        assert 0 <= minute <= 59
        assert 0 <= second <= 59

    def test_format_timestamp_for_folder_name(self):
        """Test folder name timestamp formatting."""
        timestamp = format_timestamp_for_folder_name()

        # Format: YYYYMMDDHHMMSS
        assert len(timestamp) == 14  # 14 characters
        assert timestamp.count("_") == 0  # No underscores
        assert timestamp.count("-") == 0  # No hyphens

        # Verify it's a valid date/time
        date_part = timestamp[:8]  # YYYYMMDD
        time_part = timestamp[8:]  # HHMMSS

        # Check date format
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        assert 2020 <= year <= 2030
        assert 1 <= month <= 12
        assert 1 <= day <= 31

        # Check time format
        hour = int(time_part[:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        assert 0 <= hour <= 23
        assert 0 <= minute <= 59
        assert 0 <= second <= 59

    def test_format_timestamp_for_folder_name_with_microseconds(self):
        """Test folder name timestamp formatting with microseconds."""
        timestamp = format_timestamp_for_folder_name_with_microseconds()

        # Format: YYYYMMDDHHMMSS%f (microseconds)
        assert len(timestamp) >= 20  # At least 20 characters (14 + 6 for microseconds)
        assert timestamp.count("_") == 0  # No underscores
        assert timestamp.count("-") == 0  # No hyphens

        # Verify it's a valid date/time
        date_part = timestamp[:8]  # YYYYMMDD
        time_part = timestamp[8:14]  # HHMMSS

        # Check date format
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        assert 2020 <= year <= 2030
        assert 1 <= month <= 12
        assert 1 <= day <= 31

        # Check time format
        hour = int(time_part[:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        assert 0 <= hour <= 23
        assert 0 <= minute <= 59
        assert 0 <= second <= 59


class TestTimestampParsing:
    """Test timestamp parsing functions."""

    def test_parse_iso8601_timestamp_valid(self):
        """Test parsing valid ISO 8601 timestamps."""
        test_cases = [
            "2024-01-15T10:30:45.123456Z",
            "2024-01-15T10:30:45Z",
            "2024-01-15T10:30:45.123Z",
            "2024-01-15T10:30:45.123456Z",
        ]

        for timestamp_str in test_cases:
            dt = parse_iso8601_timestamp(timestamp_str)
            assert isinstance(dt, datetime)
            assert dt.tzinfo == UTC

    def test_parse_iso8601_timestamp_invalid(self):
        """Test parsing invalid ISO 8601 timestamps."""
        invalid_timestamps = [
            "invalid",
            "2024-01-15 10:30:45",
            "2024-01-15T10:30:45",
            "2024-01-15T10:30:45+00:00",
            "",
            None,
        ]

        for timestamp_str in invalid_timestamps:
            if timestamp_str is not None:
                with pytest.raises(ValueError):
                    parse_iso8601_timestamp(timestamp_str)

    def test_parse_iso8601_timestamp_edge_cases(self):
        """Test parsing edge case timestamps."""
        # Test with different precision levels
        test_cases = [
            ("2024-01-15T10:30:45Z", 0),  # No microseconds
            ("2024-01-15T10:30:45.1Z", 1),  # 1 decimal place
            ("2024-01-15T10:30:45.12Z", 2),  # 2 decimal places
            ("2024-01-15T10:30:45.123Z", 3),  # 3 decimal places
            ("2024-01-15T10:30:45.1234Z", 4),  # 4 decimal places
            ("2024-01-15T10:30:45.12345Z", 5),  # 5 decimal places
            ("2024-01-15T10:30:45.123456Z", 6),  # 6 decimal places
        ]

        for timestamp_str, _expected_precision in test_cases:
            dt = parse_iso8601_timestamp(timestamp_str)
            assert isinstance(dt, datetime)
            assert dt.tzinfo == UTC


class TestTimestampValidation:
    """Test timestamp validation functions."""

    def test_is_valid_iso8601_timestamp_valid(self):
        """Test validation of valid ISO 8601 timestamps."""
        valid_timestamps = [
            "2024-01-15T10:30:45.123456Z",
            "2024-01-15T10:30:45Z",
            "2024-01-15T10:30:45.123Z",
            "2024-01-15T10:30:45.123456Z",
        ]

        for timestamp_str in valid_timestamps:
            assert is_valid_iso8601_timestamp(timestamp_str) is True

    def test_is_valid_iso8601_timestamp_invalid(self):
        """Test validation of invalid ISO 8601 timestamps."""
        invalid_timestamps = [
            "invalid",
            "2024-01-15 10:30:45",
            "2024-01-15T10:30:45",
            "2024-01-15T10:30:45+00:00",
            "",
            None,
        ]

        for timestamp_str in invalid_timestamps:
            assert is_valid_iso8601_timestamp(timestamp_str) is False


class TestTimestampConversion:
    """Test timestamp conversion functions."""

    def test_convert_to_iso8601_utc_from_datetime(self):
        """Test conversion from datetime object."""
        # Test with timezone-aware datetime
        dt_utc = datetime.now(UTC)
        result = convert_to_iso8601_utc(dt_utc)

        assert isinstance(result, str)
        assert result.endswith("Z")
        assert is_valid_iso8601_timestamp(result)

        # Test with timezone-naive datetime (should assume UTC)
        dt_naive = datetime.now()
        result = convert_to_iso8601_utc(dt_naive)

        assert isinstance(result, str)
        assert result.endswith("Z")
        assert is_valid_iso8601_timestamp(result)

    def test_convert_to_iso8601_utc_from_unix_timestamp(self):
        """Test conversion from Unix timestamp."""
        # Test with float timestamp
        unix_ts = time.time()
        result = convert_to_iso8601_utc(unix_ts)

        assert isinstance(result, str)
        assert result.endswith("Z")
        assert is_valid_iso8601_timestamp(result)

        # Test with integer timestamp
        unix_ts_int = int(time.time())
        result = convert_to_iso8601_utc(unix_ts_int)

        assert isinstance(result, str)
        assert result.endswith("Z")
        assert is_valid_iso8601_timestamp(result)

    def test_convert_to_iso8601_utc_from_iso_string(self):
        """Test conversion from ISO string."""
        # Test with valid ISO string
        iso_string = "2024-01-15T10:30:45.123456Z"
        result = convert_to_iso8601_utc(iso_string)

        assert isinstance(result, str)
        assert result.endswith("Z")
        assert is_valid_iso8601_timestamp(result)
        assert result == iso_string  # Should remain the same

    def test_convert_to_iso8601_utc_invalid_type(self):
        """Test conversion with invalid type."""
        invalid_inputs = [
            [],
            {},
            True,
            False,
            object(),
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError):
                convert_to_iso8601_utc(invalid_input)


class TestTimestampConsistency:
    """Test timestamp consistency and accuracy."""

    def test_timestamp_consistency(self):
        """Test that multiple calls generate consistent timestamps."""
        # Test that timestamps are monotonically increasing
        timestamps = []
        for _ in range(10):
            timestamps.append(get_iso8601_utc_timestamp())
            time.sleep(0.001)  # Small delay to ensure different timestamps

        # Verify timestamps are in ascending order
        for i in range(1, len(timestamps)):
            assert timestamps[i] > timestamps[i - 1]

    def test_timestamp_precision(self):
        """Test that timestamps have microsecond precision."""
        timestamp = get_iso8601_utc_timestamp()

        # Extract microseconds part
        microseconds_part = timestamp.split(".")[1].replace("Z", "")

        # Should have 6 decimal places
        assert len(microseconds_part) == 6

        # Should be a valid number
        microseconds = int(microseconds_part)
        assert 0 <= microseconds <= 999999

    def test_utc_timezone_consistency(self):
        """Test that all timestamps are consistently in UTC."""
        # Test multiple timestamp functions
        timestamp_functions = [
            get_iso8601_utc_timestamp,
            get_iso8601_utc_datetime,
        ]

        for func in timestamp_functions:
            result = func()
            if isinstance(result, str):
                # Parse string timestamp
                dt = parse_iso8601_timestamp(result)
            else:
                # Direct datetime object
                dt = result

            assert dt.tzinfo == UTC


class TestTimestampEdgeCases:
    """Test timestamp edge cases and error handling."""

    def test_timestamp_at_midnight(self):
        """Test timestamp generation at midnight."""
        with patch("libriscribe2.utils.timestamp_utils.datetime") as mock_datetime:
            # Mock datetime to return midnight UTC
            mock_now = datetime(2024, 1, 15, 0, 0, 0, 0, tzinfo=UTC)
            mock_datetime.now.return_value = mock_now

            timestamp = get_iso8601_utc_timestamp()
            assert timestamp == "2024-01-15T00:00:00.000000Z"

    def test_timestamp_at_year_boundary(self):
        """Test timestamp generation at year boundary."""
        with patch("libriscribe2.utils.timestamp_utils.datetime") as mock_datetime:
            # Mock datetime to return year boundary
            mock_now = datetime(2024, 12, 31, 23, 59, 59, 999999, tzinfo=UTC)
            mock_datetime.now.return_value = mock_now

            timestamp = get_iso8601_utc_timestamp()
            assert timestamp == "2024-12-31T23:59:59.999999Z"

    def test_timestamp_with_leap_year(self):
        """Test timestamp generation during leap year."""
        with patch("libriscribe2.utils.timestamp_utils.datetime") as mock_datetime:
            # Mock datetime to return leap year date
            mock_now = datetime(2024, 2, 29, 12, 0, 0, 0, tzinfo=UTC)
            mock_datetime.now.return_value = mock_now

            timestamp = get_iso8601_utc_timestamp()
            assert timestamp == "2024-02-29T12:00:00.000000Z"

    def test_timestamp_parsing_with_different_formats(self):
        """Test parsing timestamps with different ISO 8601 formats."""
        test_cases = [
            ("2024-01-15T10:30:45Z", "2024-01-15T10:30:45.000000Z"),
            ("2024-01-15T10:30:45.1Z", "2024-01-15T10:30:45.100000Z"),
            ("2024-01-15T10:30:45.12Z", "2024-01-15T10:30:45.120000Z"),
            ("2024-01-15T10:30:45.123Z", "2024-01-15T10:30:45.123000Z"),
            ("2024-01-15T10:30:45.1234Z", "2024-01-15T10:30:45.123400Z"),
            ("2024-01-15T10:30:45.12345Z", "2024-01-15T10:30:45.123450Z"),
            ("2024-01-15T10:30:45.123456Z", "2024-01-15T10:30:45.123456Z"),
        ]

        for input_timestamp, expected_output in test_cases:
            result = convert_to_iso8601_utc(input_timestamp)
            assert result == expected_output


class TestTimestampPerformance:
    """Test timestamp generation performance."""

    def test_timestamp_generation_speed(self):
        """Test that timestamp generation is fast."""
        import time

        # Generate 1000 timestamps and measure time
        start_time = time.perf_counter()
        for _ in range(1000):
            get_iso8601_utc_timestamp()
        end_time = time.perf_counter()

        total_time = end_time - start_time
        avg_time = total_time / 1000

        # Should be very fast (less than 1 millisecond per timestamp)
        assert avg_time < 0.001

    def test_timestamp_parsing_speed(self):
        """Test that timestamp parsing is fast."""
        import time

        test_timestamp = "2024-01-15T10:30:45.123456Z"

        # Parse 1000 times and measure time
        start_time = time.perf_counter()
        for _ in range(1000):
            parse_iso8601_timestamp(test_timestamp)
        end_time = time.perf_counter()

        total_time = end_time - start_time
        avg_time = total_time / 1000

        # Should be very fast (less than 1 millisecond per parse)
        assert avg_time < 0.001
