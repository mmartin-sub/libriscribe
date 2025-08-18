"""
Timestamp utilities for LibriScribe2.

This module provides standardized timestamp handling using ISO 8601-2:2019 UTC format
for consistent timestamp generation and storage across the application.
"""

import time
from datetime import UTC, datetime


def get_iso8601_utc_timestamp() -> str:
    """
    Get current timestamp in ISO 8601-2:2019 UTC format.

    Returns:
        ISO 8601-2:2019 UTC timestamp string (e.g., "2024-01-15T10:30:45.123456Z")
    """
    dt = datetime.now(UTC)
    # Ensure microseconds are always included (6 digits)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def get_utc_date_str() -> str:
    """
    Get current UTC date as YYYY-MM-DD (no time component).

    Returns:
        Date string in UTC formatted as "YYYY-MM-DD"
    """
    return datetime.now(UTC).strftime("%Y-%m-%d")


def iso_timestamp_to_utc_date(timestamp_str: str) -> str:
    """
    Convert an ISO 8601 (UTC) timestamp to a UTC date string (YYYY-MM-DD).

    Args:
        timestamp_str: ISO 8601 timestamp string (e.g., "2024-01-15T10:30:45.123456Z")

    Returns:
        Date string in UTC formatted as "YYYY-MM-DD"
    """
    dt = parse_iso8601_timestamp(timestamp_str)
    return dt.astimezone(UTC).strftime("%Y-%m-%d")


def get_iso8601_utc_datetime() -> datetime:
    """
    Get current datetime object in UTC timezone.

    Returns:
        Current datetime in UTC timezone
    """
    return datetime.now(UTC)


def get_unix_timestamp() -> float:
    """
    Get current Unix timestamp (seconds since epoch).

    Returns:
        Unix timestamp as float
    """
    return time.time()


def get_unix_timestamp_int() -> int:
    """
    Get current Unix timestamp as integer (seconds since epoch).

    Returns:
        Unix timestamp as int
    """
    return int(time.time())


def format_timestamp_for_filename() -> str:
    """
    Get timestamp formatted for use in filenames (YYYYMMDD_HHMMSS).

    Returns:
        Timestamp string formatted for filenames (e.g., "20240115_103045")
    """
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def format_timestamp_for_folder_name() -> str:
    """
    Get timestamp formatted for use in folder names (YYYYMMDDHHMMSS).

    Returns:
        Timestamp string formatted for folder names (e.g., "20240115103045")
    """
    return datetime.now(UTC).strftime("%Y%m%d%H%M%S")


def format_timestamp_for_folder_name_with_microseconds() -> str:
    """
    Get timestamp formatted for use in folder names with microseconds (YYYYMMDDHHMMSS%f).

    Returns:
        Timestamp string formatted for folder names with microseconds (e.g., "20240115103045123456")
    """
    return datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")


def parse_iso8601_timestamp(timestamp_str: str) -> datetime:
    """
    Parse ISO 8601 timestamp string to datetime object.

    Args:
        timestamp_str: ISO 8601 timestamp string

    Returns:
        Parsed datetime object

    Raises:
        ValueError: If timestamp string is invalid
    """
    if not isinstance(timestamp_str, str) or not timestamp_str:
        raise ValueError(f"Invalid ISO 8601 timestamp: {timestamp_str}")

    # Check if it ends with Z (UTC indicator)
    if not timestamp_str.endswith("Z"):
        raise ValueError(f"Invalid ISO 8601 timestamp: {timestamp_str}")

    # Remove 'Z' suffix and replace with '+00:00' for parsing
    timestamp_str = timestamp_str[:-1] + "+00:00"

    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError as e:
        raise ValueError(f"Invalid ISO 8601 timestamp: {timestamp_str}") from e


def is_valid_iso8601_timestamp(timestamp_str: str | None) -> bool:
    """
    Check if a string is a valid ISO 8601 timestamp.

    Args:
        timestamp_str: String to validate

    Returns:
        True if valid ISO 8601 timestamp, False otherwise
    """
    if timestamp_str is None or not isinstance(timestamp_str, str):
        return False

    try:
        parse_iso8601_timestamp(timestamp_str)
        return True
    except (ValueError, TypeError):
        return False


def convert_to_iso8601_utc(timestamp: datetime | float | int | str) -> str:
    """
    Convert various timestamp formats to ISO 8601-2:2019 UTC string.

    Args:
        timestamp: Timestamp in various formats (datetime, Unix timestamp, ISO string)

    Returns:
        ISO 8601-2:2019 UTC timestamp string

    Raises:
        ValueError: If timestamp format is not supported
    """
    if isinstance(timestamp, datetime):
        # If datetime has no timezone, assume UTC
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        dt_utc = timestamp.astimezone(UTC)
        # Ensure microseconds are always included (6 digits)
        return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    elif isinstance(timestamp, bool):
        # Boolean values should not be treated as timestamps
        raise ValueError(f"Unsupported timestamp type: {type(timestamp)}")

    elif isinstance(timestamp, int | float):
        # Unix timestamp
        dt = datetime.fromtimestamp(timestamp, tz=UTC)
        # Ensure microseconds are always included (6 digits)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    elif isinstance(timestamp, str):
        # Try to parse as ISO 8601
        dt = parse_iso8601_timestamp(timestamp)
        dt_utc = dt.astimezone(UTC)
        # Ensure microseconds are always included (6 digits)
        return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    else:
        raise ValueError(f"Unsupported timestamp type: {type(timestamp)}")


# Legacy compatibility functions (deprecated)
def get_legacy_timestamp() -> float:
    """
    Get legacy Unix timestamp (deprecated, use get_unix_timestamp instead).

    Returns:
        Unix timestamp as float

    Deprecated:
        Use get_unix_timestamp() instead for new code
    """
    return get_unix_timestamp()


def get_legacy_datetime() -> datetime:
    """
    Get legacy datetime without timezone (deprecated, use get_iso8601_utc_datetime instead).

    Returns:
        Current datetime without timezone (deprecated)

    Deprecated:
        Use get_iso8601_utc_datetime() instead for new code
    """
    return datetime.now()
