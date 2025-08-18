# Design Document

## Overview

This design addresses the failing timestamp utility tests by implementing proper validation, error handling, and format consistency in the timestamp utilities module. The fixes ensure full compliance with ISO 8601-2:2019 UTC standards as defined in the timestamp standards document.

## Architecture

The timestamp utilities module follows a layered architecture:

1. **Core Generation Layer**: Functions that generate timestamps (`get_iso8601_utc_timestamp`, `get_iso8601_utc_datetime`)
2. **Validation Layer**: Functions that validate timestamp formats (`is_valid_iso8601_timestamp`, `parse_iso8601_timestamp`)
3. **Conversion Layer**: Functions that convert between formats (`convert_to_iso8601_utc`)
4. **Formatting Layer**: Functions that format timestamps for specific use cases

## Components and Interfaces

### Enhanced Validation Component

**Purpose**: Provide robust validation for ISO 8601-2:2019 UTC timestamps

**Key Functions**:

- `parse_iso8601_timestamp()`: Enhanced with strict validation
- `is_valid_iso8601_timestamp()`: Improved error handling for edge cases

**Validation Rules**:

- Must end with 'Z' (UTC timezone indicator)
- Must follow ISO 8601 format: `YYYY-MM-DDTHH:MM:SS[.ffffff]Z`
- Must handle None and empty string inputs
- Must reject non-UTC timezone indicators (+00:00, etc.)

### Microsecond Precision Component

**Purpose**: Ensure consistent 6-digit microsecond precision across all timestamp operations

**Key Functions**:

- `get_iso8601_utc_timestamp()`: Always returns 6-digit microseconds
- `convert_to_iso8601_utc()`: Normalizes input to 6-digit microseconds

**Precision Rules**:

- Always pad microseconds to 6 digits (e.g., ".1" becomes ".100000")
- Handle zero microseconds as ".000000"
- Maintain precision during conversions

### Type Safety Component

**Purpose**: Provide proper type validation and error handling

**Key Functions**:

- `convert_to_iso8601_utc()`: Enhanced type checking
- Input validation for all public functions

**Type Handling**:

- `datetime`: Convert to UTC and format with microseconds
- `int/float`: Treat as Unix timestamp and convert
- `str`: Parse as ISO 8601 and validate
- Other types: Raise ValueError with descriptive message

## Data Models

### Timestamp Format Model

```python
# Standard ISO 8601-2:2019 UTC format
TIMESTAMP_FORMAT = "YYYY-MM-DDTHH:MM:SS.ffffffZ"

# Validation patterns
ISO_8601_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$'
```

### Error Response Model

```python
class TimestampValidationError(ValueError):
    """Specific error for timestamp validation failures"""
    pass
```

## Error Handling

### Validation Errors

1. **Invalid Format**: Clear error messages indicating expected format
2. **Type Errors**: Specific messages for unsupported types
3. **None/Empty Handling**: Explicit handling with appropriate error messages

### Error Message Standards

- Include expected format in error messages
- Provide specific reason for rejection
- Reference ISO 8601-2:2019 standard when appropriate

## Testing Strategy

### Unit Test Coverage

1. **Validation Tests**:
   - Test all invalid format combinations
   - Test None and empty string handling
   - Test edge cases (midnight, year boundaries, leap years)

2. **Precision Tests**:
   - Test microsecond padding and normalization
   - Test conversion between different precision levels
   - Test format consistency across all functions

3. **Type Safety Tests**:
   - Test all supported types (datetime, int, float, str)
   - Test all unsupported types (bool, list, dict, object)
   - Test error message quality and specificity

4. **Integration Tests**:
   - Test interaction between validation and conversion functions
   - Test consistency across the entire timestamp utilities module

### Test Data Strategy

- Use fixed test timestamps for predictable results
- Mock datetime.now() for consistent edge case testing
- Test with various microsecond precision levels (0-6 digits)

## Implementation Details

### Enhanced `parse_iso8601_timestamp()` Function

```python
def parse_iso8601_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO 8601 timestamp with strict validation"""
    # Input validation
    if timestamp_str is None:
        raise ValueError("Timestamp string cannot be None")

    if not isinstance(timestamp_str, str):
        raise ValueError(f"Expected string, got {type(timestamp_str)}")

    if not timestamp_str:
        raise ValueError("Timestamp string cannot be empty")

    # Format validation
    if not timestamp_str.endswith('Z'):
        raise ValueError("ISO 8601-2:2019 UTC timestamp must end with 'Z'")

    # Parse and validate
    try:
        # Convert Z to +00:00 for parsing
        iso_str = timestamp_str[:-1] + '+00:00'
        dt = datetime.fromisoformat(iso_str)
        return dt.astimezone(timezone.utc)
    except ValueError as e:
        raise ValueError(f"Invalid ISO 8601 timestamp format: {timestamp_str}") from e
```

### Enhanced `get_iso8601_utc_timestamp()` Function

```python
def get_iso8601_utc_timestamp() -> str:
    """Get current timestamp with guaranteed 6-digit microseconds"""
    dt = datetime.now(timezone.utc)
    # Ensure 6-digit microsecond precision
    iso_str = dt.isoformat()

    # Handle microsecond padding
    if '.' not in iso_str:
        iso_str += '.000000'
    else:
        # Pad microseconds to 6 digits
        parts = iso_str.split('.')
        microseconds = parts[1].replace('+00:00', '')
        microseconds = microseconds.ljust(6, '0')[:6]  # Pad or truncate to 6 digits
        iso_str = f"{parts[0]}.{microseconds}+00:00"

    return iso_str.replace('+00:00', 'Z')
```

### Enhanced `convert_to_iso8601_utc()` Function

```python
def convert_to_iso8601_utc(timestamp: Union[datetime, float, int, str]) -> str:
    """Convert with strict type validation and microsecond normalization"""
    if isinstance(timestamp, datetime):
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        result = timestamp.astimezone(timezone.utc).isoformat()
    elif isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        result = dt.isoformat()
    elif isinstance(timestamp, str):
        dt = parse_iso8601_timestamp(timestamp)
        result = dt.isoformat()
    else:
        raise ValueError(f"Unsupported timestamp type: {type(timestamp).__name__}. "
                        f"Supported types: datetime, int, float, str")

    # Normalize microsecond precision
    if '.' not in result:
        result = result.replace('+00:00', '.000000+00:00')
    else:
        parts = result.split('.')
        microseconds = parts[1].replace('+00:00', '')
        microseconds = microseconds.ljust(6, '0')[:6]
        result = f"{parts[0]}.{microseconds}+00:00"

    return result.replace('+00:00', 'Z')
```

## Performance Considerations

- Minimize regex usage for better performance
- Cache compiled patterns if regex is needed
- Use string operations instead of complex parsing where possible
- Maintain existing performance characteristics while adding validation

## Backward Compatibility

- All existing function signatures remain unchanged
- Enhanced error handling provides better debugging information
- Stricter validation may catch previously undetected issues
- Legacy functions remain available but deprecated

## Security Considerations

- Input validation prevents injection attacks through timestamp strings
- Type checking prevents unexpected behavior from malicious inputs
- Clear error messages don't expose internal implementation details
