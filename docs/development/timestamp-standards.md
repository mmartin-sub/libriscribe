# Timestamp Standards in LibriScribe2

## Overview

LibriScribe2 uses **ISO 8601-2:2019 UTC** as the standard timestamp format for all data storage and API responses. This ensures consistency, international compatibility, and proper timezone handling across the application.

## Standard Format

### ISO 8601-2:2019 UTC Format
- **Format**: `YYYY-MM-DDTHH:MM:SS.ssssssZ`
- **Example**: `2024-01-15T10:30:45.123456Z`
- **Timezone**: Always UTC (indicated by `Z` suffix)
- **Precision**: Microsecond precision (6 decimal places)

### Key Characteristics
- **Human-readable**: Clear date and time representation
- **Sortable**: Lexicographical sorting matches chronological order
- **Timezone-aware**: Explicitly UTC to avoid ambiguity
- **Precise**: Microsecond precision for accurate timing
- **Standards-compliant**: Follows international ISO 8601 standard

## Implementation

### Timestamp Utility Module

All timestamp generation is centralized in `src/libriscribe2/utils/timestamp_utils.py`:

```python
from libriscribe2.utils.timestamp_utils import get_iso8601_utc_timestamp

# Get current timestamp in ISO 8601-2:2019 UTC format
timestamp = get_iso8601_utc_timestamp()
# Returns: "2024-01-15T10:30:45.123456Z"
```

### Available Functions

#### Core Timestamp Functions
- `get_iso8601_utc_timestamp()` - Current timestamp in ISO 8601-2:2019 UTC
- `get_iso8601_utc_datetime()` - Current datetime object in UTC timezone
- `get_unix_timestamp()` - Current Unix timestamp (float)
- `get_unix_timestamp_int()` - Current Unix timestamp (integer)

#### Formatting Functions
- `format_timestamp_for_filename()` - `YYYYMMDD_HHMMSS` for filenames
- `format_timestamp_for_folder_name()` - `YYYYMMDDHHMMSS` for folder names
- `format_timestamp_for_folder_name_with_microseconds()` - `YYYYMMDDHHMMSS%f` with microseconds

#### Utility Functions
- `parse_iso8601_timestamp(timestamp_str)` - Parse ISO string to datetime
- `is_valid_iso8601_timestamp(timestamp_str)` - Validate ISO timestamp
- `convert_to_iso8601_utc(timestamp)` - Convert various formats to ISO UTC

## Usage Guidelines

### 1. Data Storage
Always use ISO 8601-2:2019 UTC format for storing timestamps in:
- JSON files (concept.json, chapter files, etc.)
- Database records
- API responses
- Log files

```python
# ✅ Correct
{
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "content": "..."
}

# ❌ Incorrect
{
    "timestamp": 1705315845.123456,
    "content": "..."
}
```

### 2. File and Folder Naming
Use appropriate formatting functions for different naming contexts:

```python
# For log files
from libriscribe2.utils.timestamp_utils import format_timestamp_for_filename
log_file = f"libriscribe_{format_timestamp_for_filename()}.log"
# Result: libriscribe_20240115_103045.log

# For project folders
from libriscribe2.utils.timestamp_utils import format_timestamp_for_folder_name
folder_name = f"project-{format_timestamp_for_folder_name()}"
# Result: project-20240115103045
```

### 3. API Responses
All API responses should include timestamps in ISO 8601-2:2019 UTC format:

```python
response = {
    "status": "success",
    "timestamp": get_iso8601_utc_timestamp(),
    "data": {...}
}
```

### 4. Logging
Use ISO 8601-2:2019 UTC format for all log entries:

```python
logger.info(f"Operation completed at {get_iso8601_utc_timestamp()}")
```

## Migration from Legacy Formats

### Previous Formats
- **Unix timestamps**: `1705315845.123456`
- **Local datetime**: `2024-01-15 10:30:45`
- **Custom formats**: `20240115_103045`

### Migration Strategy
1. **New code**: Always use `get_iso8601_utc_timestamp()`
2. **Existing data**: Convert using `convert_to_iso8601_utc()`
3. **Legacy functions**: Marked as deprecated, use new equivalents

### Conversion Examples

```python
from libriscribe2.utils.timestamp_utils import convert_to_iso8601_utc

# Convert Unix timestamp
unix_ts = 1705315845.123456
iso_ts = convert_to_iso8601_utc(unix_ts)
# Result: "2024-01-15T10:30:45.123456Z"

# Convert datetime object
dt = datetime.now()
iso_ts = convert_to_iso8601_utc(dt)
# Result: "2024-01-15T10:30:45.123456Z"
```

## Testing

### Timestamp Validation
Use the built-in validation function:

```python
from libriscribe2.utils.timestamp_utils import is_valid_iso8601_timestamp

# Test valid timestamp
assert is_valid_iso8601_timestamp("2024-01-15T10:30:45.123456Z") == True

# Test invalid timestamp
assert is_valid_iso8601_timestamp("invalid") == False
```

### Unit Tests
All timestamp utilities include comprehensive unit tests in `tests/unit/utils/test_timestamp_utils.py`.

## Benefits

### 1. Consistency
- Uniform timestamp format across all components
- Eliminates format confusion and parsing errors
- Standardized API responses

### 2. Internationalization
- ISO 8601 is an international standard
- UTC timezone eliminates local timezone confusion
- Proper handling of daylight saving time

### 3. Debugging and Monitoring
- Human-readable timestamps in logs
- Easy chronological sorting and filtering
- Precise timing for performance analysis

### 4. Future-Proofing
- Standards-compliant format
- Extensible for additional precision
- Compatible with modern tools and databases

## Compliance

### ISO 8601-2:2019 Requirements
- ✅ Date format: `YYYY-MM-DD`
- ✅ Time format: `HH:MM:SS.ssssss`
- ✅ Timezone indicator: `Z` (UTC)
- ✅ Separator: `T` between date and time
- ✅ Microsecond precision: 6 decimal places

### UTC Timezone
- ✅ Always uses Coordinated Universal Time
- ✅ No daylight saving time complications
- ✅ Consistent across all geographic locations
- ✅ Standard for international applications

## Examples

### Complete Usage Example

```python
from libriscribe2.utils.timestamp_utils import (
    get_iso8601_utc_timestamp,
    format_timestamp_for_filename,
    convert_to_iso8601_utc
)

# Generate new content with ISO timestamp
content = {
    "title": "Sample Chapter",
    "created_at": get_iso8601_utc_timestamp(),
    "modified_at": get_iso8601_utc_timestamp(),
    "content": "Chapter content..."
}

# Save to file with timestamped filename
filename = f"chapter_{format_timestamp_for_filename()}.json"
save_content(filename, content)

# Convert legacy timestamp
legacy_timestamp = 1705315845.123456
iso_timestamp = convert_to_iso8601_utc(legacy_timestamp)
```

### Database Schema Example

```sql
CREATE TABLE content_versions (
    id SERIAL PRIMARY KEY,
    content_id UUID NOT NULL,
    version_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    modified_at TIMESTAMP WITH TIME ZONE NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    metadata JSONB
);

-- Insert with ISO timestamp
INSERT INTO content_versions (
    content_id, version_number, created_at, modified_at, content_hash
) VALUES (
    '123e4567-e89b-12d3-a456-426614174000',
    1,
    '2024-01-15T10:30:45.123456Z',
    '2024-01-15T10:30:45.123456Z',
    'abc123...'
);
```

## Troubleshooting

### Common Issues

#### 1. Invalid ISO Format
```python
# ❌ Problem: Missing timezone indicator
timestamp = "2024-01-15T10:30:45.123456"

# ✅ Solution: Use utility function
timestamp = get_iso8601_utc_timestamp()
```

#### 2. Timezone Confusion
```python
# ❌ Problem: Local timezone ambiguity
timestamp = datetime.now().isoformat()

# ✅ Solution: Explicit UTC
timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
```

#### 3. Precision Loss
```python
# ❌ Problem: Integer timestamp loses precision
timestamp = int(time.time())

# ✅ Solution: Use appropriate precision
timestamp = get_iso8601_utc_timestamp()  # Microsecond precision
```

### Debug Commands

```python
# Validate timestamp format
from libriscribe2.utils.timestamp_utils import is_valid_iso8601_timestamp
print(f"Valid: {is_valid_iso8601_timestamp('2024-01-15T10:30:45.123456Z')}")

# Parse and display timestamp
from libriscribe2.utils.timestamp_utils import parse_iso8601_timestamp
dt = parse_iso8601_timestamp('2024-01-15T10:30:45.123456Z')
print(f"Parsed: {dt}")
print(f"UTC: {dt.utctimetuple()}")
```

## References

- [ISO 8601-2:2019 Standard](https://www.iso.org/standard/70907.html)
- [UTC Time Standard](https://en.wikipedia.org/wiki/Coordinated_Universal_Time)
- [Python datetime Documentation](https://docs.python.org/3/library/datetime.html)
- [RFC 3339 (Internet Timestamp Format)](https://tools.ietf.org/html/rfc3339)
