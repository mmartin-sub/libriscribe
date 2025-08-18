# Timestamp Utils API Documentation

## Overview

The `timestamp_utils` module provides standardized timestamp handling using **ISO 8601-2:2019 UTC format** for consistent timestamp generation and storage across LibriScribe2. This ensures international compatibility, proper timezone handling, and consistent data storage.

## Key Features

- **ISO 8601-2:2019 UTC Standard**: All timestamps follow international standards
- **Multiple Format Support**: Generate timestamps for different use cases
- **Timezone Consistency**: All timestamps are normalized to UTC
- **Cross-Platform Compatibility**: Consistent behavior across operating systems
- **Legacy Compatibility**: Deprecated functions for backward compatibility

## Module Location

```python
from libriscribe2.utils.timestamp_utils import (
    get_iso8601_utc_timestamp,
    get_iso8601_utc_datetime,
    convert_to_iso8601_utc,
    parse_iso8601_timestamp,
    # ... other functions
)
```

## Core Functions

### get_iso8601_utc_timestamp()

```python
def get_iso8601_utc_timestamp() -> str
```

Get current timestamp in ISO 8601-2:2019 UTC format.

**Returns:**
- `str`: ISO 8601-2:2019 UTC timestamp string (e.g., "2024-01-15T10:30:45.123456Z")

**Usage Example:**

```python
from libriscribe2.utils.timestamp_utils import get_iso8601_utc_timestamp

# Get current timestamp
timestamp = get_iso8601_utc_timestamp()
print(timestamp)  # "2024-01-15T10:30:45.123456Z"

# Use in data structures
project_data = {
    "created_at": get_iso8601_utc_timestamp(),
    "title": "My Book",
    "status": "active"
}
```

### get_iso8601_utc_datetime()

```python
def get_iso8601_utc_datetime() -> datetime
```

Get current datetime object in UTC timezone.

**Returns:**
- `datetime`: Current datetime in UTC timezone

**Usage Example:**

```python
from libriscribe2.utils.timestamp_utils import get_iso8601_utc_datetime

# Get current datetime object
dt = get_iso8601_utc_datetime()
print(dt)  # 2024-01-15 10:30:45.123456+00:00

# Use for calculations
from datetime import timedelta
future_time = get_iso8601_utc_datetime() + timedelta(hours=1)
```

### convert_to_iso8601_utc()

```python
def convert_to_iso8601_utc(timestamp: datetime | float | int | str) -> str
```

Convert various timestamp formats to ISO 8601-2:2019 UTC string.

**Parameters:**
- `timestamp` (datetime | float | int | str): Timestamp in various formats
  - `datetime`: Python datetime object (with or without timezone)
  - `float`: Unix timestamp (seconds since epoch)
  - `int`: Unix timestamp (seconds since epoch)
  - `str`: ISO 8601 timestamp string

**Returns:**
- `str`: ISO 8601-2:2019 UTC timestamp string

**Raises:**
- `ValueError`: If timestamp format is not supported

**Usage Examples:**

```python
from libriscribe2.utils.timestamp_utils import convert_to_iso8601_utc
from datetime import datetime, timezone
import time

# Convert datetime object
dt = datetime(2024, 1, 15, 10, 30, 45)
iso_str = convert_to_iso8601_utc(dt)
print(iso_str)  # "2024-01-15T10:30:45Z"

# Convert Unix timestamp
unix_ts = time.time()
iso_str = convert_to_iso8601_utc(unix_ts)
print(iso_str)  # "2024-01-15T10:30:45.123456Z"

# Convert ISO string (normalize to UTC)
iso_input = "2024-01-15T10:30:45+05:00"
iso_utc = convert_to_iso8601_utc(iso_input)
print(iso_utc)  # "2024-01-15T05:30:45Z"
```

### parse_iso8601_timestamp()

```python
def parse_iso8601_timestamp(timestamp_str: str) -> datetime
```

Parse ISO 8601 timestamp string to datetime object.

**Parameters:**
- `timestamp_str` (str): ISO 8601 timestamp string

**Returns:**
- `datetime`: Parsed datetime object

**Raises:**
- `ValueError`: If timestamp string is invalid

**Usage Example:**

```python
from libriscribe2.utils.timestamp_utils import parse_iso8601_timestamp

# Parse ISO 8601 timestamp
timestamp_str = "2024-01-15T10:30:45.123456Z"
dt = parse_iso8601_timestamp(timestamp_str)
print(dt)  # 2024-01-15 10:30:45.123456+00:00

# Handle parsing errors
try:
    invalid_dt = parse_iso8601_timestamp("invalid-timestamp")
except ValueError as e:
    print(f"Parsing failed: {e}")
```

### is_valid_iso8601_timestamp()

```python
def is_valid_iso8601_timestamp(timestamp_str: str) -> bool
```

Check if a string is a valid ISO 8601 timestamp.

**Parameters:**
- `timestamp_str` (str): String to validate

**Returns:**
- `bool`: True if valid ISO 8601 timestamp, False otherwise

**Usage Example:**

```python
from libriscribe2.utils.timestamp_utils import is_valid_iso8601_timestamp

# Validate timestamps
valid_ts = "2024-01-15T10:30:45.123456Z"
invalid_ts = "not-a-timestamp"

print(is_valid_iso8601_timestamp(valid_ts))    # True
print(is_valid_iso8601_timestamp(invalid_ts))  # False

# Use in validation
def validate_project_data(data):
    if "created_at" in data:
        if not is_valid_iso8601_timestamp(data["created_at"]):
            raise ValueError("Invalid timestamp format")
```

## Unix Timestamp Functions

### get_unix_timestamp()

```python
def get_unix_timestamp() -> float
```

Get current Unix timestamp (seconds since epoch).

**Returns:**
- `float`: Unix timestamp as float

**Usage Example:**

```python
from libriscribe2.utils.timestamp_utils import get_unix_timestamp

# Get Unix timestamp
unix_ts = get_unix_timestamp()
print(unix_ts)  # 1705315845.123456

# Use for performance timing
start_time = get_unix_timestamp()
# ... some operation ...
end_time = get_unix_timestamp()
duration = end_time - start_time
```

### get_unix_timestamp_int()

```python
def get_unix_timestamp_int() -> int
```

Get current Unix timestamp as integer (seconds since epoch).

**Returns:**
- `int`: Unix timestamp as int

**Usage Example:**

```python
from libriscribe2.utils.timestamp_utils import get_unix_timestamp_int

# Get integer Unix timestamp
unix_ts = get_unix_timestamp_int()
print(unix_ts)  # 1705315845

# Use for unique IDs
unique_id = f"project_{unix_ts}"
```

## Filename Formatting Functions

### format_timestamp_for_filename()

```python
def format_timestamp_for_filename() -> str
```

Get timestamp formatted for use in filenames (YYYYMMDD_HHMMSS).

**Returns:**
- `str`: Timestamp string formatted for filenames (e.g., "20240115_103045")

**Usage Example:**

```python
from libriscribe2.utils.timestamp_utils import format_timestamp_for_filename

# Create timestamped filename
timestamp = format_timestamp_for_filename()
filename = f"book_export_{timestamp}.pdf"
print(filename)  # "book_export_20240115_103045.pdf"
```

### format_timestamp_for_folder_name()

```python
def format_timestamp_for_folder_name() -> str
```

Get timestamp formatted for use in folder names (YYYYMMDDHHMMSS).

**Returns:**
- `str`: Timestamp string formatted for folder names (e.g., "20240115103045")

**Usage Example:**

```python
from libriscribe2.utils.timestamp_utils import format_timestamp_for_folder_name
import os

# Create timestamped folder
timestamp = format_timestamp_for_folder_name()
folder_name = f"project_{timestamp}"
os.makedirs(folder_name, exist_ok=True)
print(folder_name)  # "project_20240115103045"
```

### format_timestamp_for_folder_name_with_microseconds()

```python
def format_timestamp_for_folder_name_with_microseconds() -> str
```

Get timestamp formatted for use in folder names with microseconds (YYYYMMDDHHMMSS%f).

**Returns:**
- `str`: Timestamp string formatted for folder names with microseconds (e.g., "20240115103045123456")

**Usage Example:**

```python
from libriscribe2.utils.timestamp_utils import format_timestamp_for_folder_name_with_microseconds

# Create unique folder with microsecond precision
timestamp = format_timestamp_for_folder_name_with_microseconds()
unique_folder = f"temp_{timestamp}"
print(unique_folder)  # "temp_20240115103045123456"
```

## Legacy Functions (Deprecated)

### get_legacy_timestamp()

```python
def get_legacy_timestamp() -> float
```

**Deprecated**: Use `get_unix_timestamp()` instead for new code.

Get legacy Unix timestamp.

**Returns:**
- `float`: Unix timestamp as float

### get_legacy_datetime()

```python
def get_legacy_datetime() -> datetime
```

**Deprecated**: Use `get_iso8601_utc_datetime()` instead for new code.

Get legacy datetime without timezone.

**Returns:**
- `datetime`: Current datetime without timezone (deprecated)

## Complete Usage Examples

### Basic Timestamp Generation

```python
from libriscribe2.utils.timestamp_utils import (
    get_iso8601_utc_timestamp,
    get_iso8601_utc_datetime,
    format_timestamp_for_filename
)

# Standard ISO 8601 timestamp
iso_timestamp = get_iso8601_utc_timestamp()
print(f"ISO timestamp: {iso_timestamp}")

# Datetime object for calculations
dt = get_iso8601_utc_datetime()
print(f"Datetime object: {dt}")

# Filename-safe timestamp
filename_ts = format_timestamp_for_filename()
print(f"Filename timestamp: {filename_ts}")
```

### Data Storage with Timestamps

```python
from libriscribe2.utils.timestamp_utils import get_iso8601_utc_timestamp
import json

# Create project data with timestamp
project_data = {
    "id": "project_123",
    "title": "My Great Novel",
    "created_at": get_iso8601_utc_timestamp(),
    "updated_at": get_iso8601_utc_timestamp(),
    "status": "active"
}

# Save to JSON (timestamps are ISO 8601 compliant)
with open("project.json", "w") as f:
    json.dump(project_data, f, indent=2)
```

### Timestamp Conversion and Validation

```python
from libriscribe2.utils.timestamp_utils import (
    convert_to_iso8601_utc,
    is_valid_iso8601_timestamp,
    parse_iso8601_timestamp
)
import time

# Convert various formats to ISO 8601 UTC
unix_ts = time.time()
iso_from_unix = convert_to_iso8601_utc(unix_ts)
print(f"From Unix: {iso_from_unix}")

# Validate timestamp strings
timestamps_to_check = [
    "2024-01-15T10:30:45.123456Z",
    "2024-01-15T10:30:45+05:00",
    "invalid-timestamp"
]

for ts in timestamps_to_check:
    if is_valid_iso8601_timestamp(ts):
        parsed = parse_iso8601_timestamp(ts)
        normalized = convert_to_iso8601_utc(ts)
        print(f"Valid: {ts} -> {normalized}")
    else:
        print(f"Invalid: {ts}")
```

### Performance Timing

```python
from libriscribe2.utils.timestamp_utils import get_unix_timestamp
import time

def time_operation(func):
    """Decorator to time function execution"""
    def wrapper(*args, **kwargs):
        start_time = get_unix_timestamp()
        result = func(*args, **kwargs)
        end_time = get_unix_timestamp()
        duration = end_time - start_time
        print(f"{func.__name__} took {duration:.3f} seconds")
        return result
    return wrapper

@time_operation
def example_operation():
    time.sleep(1)  # Simulate work
    return "completed"

result = example_operation()
```

### File and Folder Management

```python
from libriscribe2.utils.timestamp_utils import (
    format_timestamp_for_filename,
    format_timestamp_for_folder_name_with_microseconds
)
import os
from pathlib import Path

# Create timestamped backup
def create_backup(source_file):
    timestamp = format_timestamp_for_filename()
    backup_name = f"{source_file}.backup_{timestamp}"
    # Copy file logic here
    return backup_name

# Create unique temporary directory
def create_temp_dir():
    timestamp = format_timestamp_for_folder_name_with_microseconds()
    temp_dir = Path(f"/tmp/libriscribe_{timestamp}")
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir

# Usage
backup_file = create_backup("important_data.json")
temp_directory = create_temp_dir()
```

## Integration with LibriScribe2

### Project Knowledge Base Integration

```python
from libriscribe2.utils.timestamp_utils import get_iso8601_utc_timestamp
from libriscribe2.knowledge_base import ProjectKnowledgeBase

# Create project with timestamps
project = ProjectKnowledgeBase(
    title="My Novel",
    created_at=get_iso8601_utc_timestamp(),
    updated_at=get_iso8601_utc_timestamp()
)

# Update project timestamp
def update_project(project):
    project.updated_at = get_iso8601_utc_timestamp()
    return project
```

### Logging Integration

```python
from libriscribe2.utils.timestamp_utils import get_iso8601_utc_timestamp
import logging

# Custom log formatter with ISO timestamps
class ISO8601Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return get_iso8601_utc_timestamp()

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(ISO8601Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger('libriscribe2')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Log with ISO timestamps
logger.info("Book generation started")
```

## Best Practices

### 1. Always Use UTC

```python
# ✅ Good - Always use UTC functions
from libriscribe2.utils.timestamp_utils import get_iso8601_utc_timestamp

timestamp = get_iso8601_utc_timestamp()

# ❌ Avoid - Don't use local timezone functions
from datetime import datetime
local_time = datetime.now()  # Timezone-dependent
```

### 2. Consistent Data Storage

```python
# ✅ Good - Use ISO 8601 for all stored timestamps
data = {
    "created_at": get_iso8601_utc_timestamp(),
    "updated_at": get_iso8601_utc_timestamp()
}

# ❌ Avoid - Mixed timestamp formats
data = {
    "created_at": time.time(),  # Unix timestamp
    "updated_at": str(datetime.now())  # String without timezone
}
```

### 3. Validation Before Processing

```python
# ✅ Good - Validate timestamps before use
def process_project_data(data):
    if "created_at" in data:
        if not is_valid_iso8601_timestamp(data["created_at"]):
            raise ValueError("Invalid created_at timestamp")

    # Process data...
```

### 4. Conversion for External APIs

```python
# ✅ Good - Convert to required format for external APIs
def send_to_external_api(project_data):
    # Convert ISO timestamp to Unix for API
    iso_timestamp = project_data["created_at"]
    dt = parse_iso8601_timestamp(iso_timestamp)
    unix_timestamp = dt.timestamp()

    api_data = {
        "title": project_data["title"],
        "created": int(unix_timestamp)  # API expects Unix timestamp
    }
    # Send to API...
```

## Error Handling

### Common Errors and Solutions

```python
from libriscribe2.utils.timestamp_utils import (
    parse_iso8601_timestamp,
    convert_to_iso8601_utc,
    is_valid_iso8601_timestamp
)

# Handle invalid timestamp strings
def safe_parse_timestamp(timestamp_str):
    try:
        return parse_iso8601_timestamp(timestamp_str)
    except ValueError as e:
        print(f"Invalid timestamp: {e}")
        return None

# Handle unsupported timestamp types
def safe_convert_timestamp(timestamp):
    try:
        return convert_to_iso8601_utc(timestamp)
    except ValueError as e:
        print(f"Conversion failed: {e}")
        return get_iso8601_utc_timestamp()  # Fallback to current time

# Validate before processing
def process_timestamps(data):
    for key, value in data.items():
        if key.endswith("_at") and isinstance(value, str):
            if not is_valid_iso8601_timestamp(value):
                print(f"Warning: Invalid timestamp in {key}: {value}")
                data[key] = get_iso8601_utc_timestamp()  # Fix with current time
    return data
```

## Type Annotations

The module uses modern Python type annotations:

```python
from typing import Union
from datetime import datetime

# Union types for flexibility
def convert_to_iso8601_utc(timestamp: datetime | float | int | str) -> str:
    # Implementation...

# Clear return types
def get_iso8601_utc_timestamp() -> str:
    # Implementation...

def get_iso8601_utc_datetime() -> datetime:
    # Implementation...
```

## Standards Compliance

This module follows **ISO 8601-2:2019** standards:

- **Format**: `YYYY-MM-DDTHH:MM:SS.fffffZ`
- **Timezone**: Always UTC (indicated by 'Z' suffix)
- **Precision**: Microsecond precision when available
- **Consistency**: Same format across all LibriScribe2 components

## See Also

- [Timestamp Standards Documentation](../development/timestamp-standards.md)
- [LibriScribe2 Development Guide](../development/)
- [Project Knowledge Base API](project-knowledge-base-api.md)
