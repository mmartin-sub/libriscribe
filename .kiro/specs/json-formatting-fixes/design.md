# Design Document: JSON Formatting Fixes

## Overview

This design addresses the issue where LibriScribe generates JSON files with Unicode escape sequences instead of readable Unicode characters. We have two potential approaches:

1. **Simple Fix**: Add `ensure_ascii=False` to existing JSON serialization calls
2. **Enhanced Approach**: Consider JSON5 for better human readability and editability

## JSON5 vs Standard JSON Analysis

### JSON5 Benefits

- **Comments**: Users could add comments to configuration files
- **Trailing commas**: More forgiving syntax for manual editing
- **Unquoted keys**: Cleaner appearance for simple keys
- **Multi-line strings**: Better for long descriptions
- **Hexadecimal numbers**: More flexible number formats

### JSON5 Constraints and Considerations

**Compatibility Issues:**

- JSON5 files cannot be read by standard `json.load()` - requires `json5` library
- External tools expecting standard JSON would break
- API integrations expecting JSON would need updates
- Backup/restore tools might not handle JSON5

**Library Dependencies:**

- Adds new dependency (`json5` package)
- Need to handle both JSON and JSON5 files during transition
- Pydantic models use standard JSON serialization by default

**Use Case Analysis:**

- **Project data files**: Rarely edited by users manually - JSON is fine
- **Configuration files**: Could benefit from JSON5 comments and readability
- **Agent outputs**: Machine-generated, rarely edited - JSON is sufficient
- **Concept files**: Sometimes edited by users - could benefit from JSON5

### Recommendation

**Hybrid Approach**: Use JSON5 only for user-editable configuration files, keep standard JSON for data files.

**Files that could use JSON5:**

- Configuration files (`.config.json` → `.config.json5`)
- User-customizable templates
- Project settings that users might want to comment

**Files that should stay JSON:**

- `project_data.json` (machine-managed)
- Agent output files (machine-generated)
- Concept files (for API compatibility)

## Architecture

The fix involves updating the JSON serialization functions in the LibriScribe codebase to preserve Unicode characters in their readable form. This is a minimal change that affects only the JSON output formatting without changing any data structures or business logic.

### Current State

Currently, JSON files are generated with code like:

```python
json.dump(data, f, indent=4)
```

This results in output like:

```json
{
    "title": "The Map Between Us",
    "logline": "When an earthquake in Seoul shatters the fragile distance between them, estranged sisters Isa and Caro must cross continents\u2014one by air, one by spirit\u2014to heal their fractured family before the next aftershock tears them apart forever."
}
```

### Target State

After the fix, JSON files will be generated with:

```python
json.dump(data, f, indent=4, ensure_ascii=False)
```

This will result in output like:

```json
{
    "title": "The Map Between Us",
    "logline": "When an earthquake in Seoul shatters the fragile distance between them, estranged sisters Isa and Caro must cross continents—one by air, one by spirit—to heal their fractured family before the next aftershock tears them apart forever."
}
```

## Components and Interfaces

### Primary Component: File Utils Module

The main change occurs in `src/libriscribe2/utils/file_utils.py` in the `write_json_file()` function.

**Current Implementation:**

```python
def write_json_file(file_path: str, data: dict[str, Any] | BaseModel) -> None:
    """Writes data (dict or Pydantic model) to a JSON file."""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            if isinstance(data, BaseModel):
                json.dump(data.model_dump(), f, indent=4)
            else:
                json.dump(data, f, indent=4)
        logger.info(f"Data written to {_get_relative_path(file_path)}")
    except Exception as e:
        logger.exception(f"Error writing to JSON file {file_path}: {e}")
        print(f"ERROR: Failed to write to {file_path}. See log.")
```

**Updated Implementation:**

```python
def write_json_file(file_path: str, data: dict[str, Any] | BaseModel) -> None:
    """Writes data (dict or Pydantic model) to a JSON file."""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            if isinstance(data, BaseModel):
                json.dump(data.model_dump(), f, indent=4, ensure_ascii=False)
            else:
                json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Data written to {_get_relative_path(file_path)}")
    except Exception as e:
        logger.exception(f"Error writing to JSON file {file_path}: {e}")
        print(f"ERROR: Failed to write to {file_path}. See log.")
```

### Secondary Components: Direct JSON Calls

A search through the codebase will identify any direct `json.dump()` or `json.dumps()` calls that need to be updated with the `ensure_ascii=False` parameter.

## Data Models

No changes to data models are required. This is purely a formatting change that affects how existing data is serialized to JSON.

## Error Handling

The error handling remains the same. The `ensure_ascii=False` parameter is a standard JSON serialization option and doesn't introduce new error conditions.

## Testing Strategy

### Unit Tests

1. **JSON Formatting Test**: Create a test that verifies Unicode characters are preserved in JSON output
2. **Round-trip Test**: Ensure data can be written and read back correctly
3. **Backward Compatibility Test**: Verify that existing JSON files with escape sequences can still be read

### Integration Tests

1. **Concept Generation Test**: Verify that concept.json files are generated with readable Unicode characters
2. **Project Data Test**: Ensure project_data.json files maintain Unicode characters
3. **Agent Output Test**: Confirm that all agent-generated JSON files use the new formatting

### Test Implementation

```python
def test_json_unicode_preservation():
    """Test that Unicode characters are preserved in JSON output"""
    test_data = {
        "title": "Test—Title",
        "description": "Text with 'curly quotes' and—em dashes"
    }

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        write_json_file(temp_path, test_data)

        # Read raw file content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify Unicode characters are not escaped
        assert '\\u2014' not in content  # em dash should not be escaped
        assert '\\u2018' not in content  # left single quote should not be escaped
        assert '\\u2019' not in content  # right single quote should not be escaped
        assert '—' in content  # em dash should be present
        assert ''' in content  # curly quote should be present

        # Verify JSON is still valid and data is preserved
        loaded_data = read_json_file(temp_path)
        assert loaded_data == test_data

    finally:
        os.unlink(temp_path)
```

## Implementation Plan

1. **Update `write_json_file()` function** in `src/libriscribe2/utils/file_utils.py`
2. **Search for direct JSON calls** throughout the codebase using grep/search
3. **Update any direct `json.dump()` and `json.dumps()` calls** to include `ensure_ascii=False`
4. **Add unit tests** to verify Unicode preservation
5. **Run integration tests** to ensure no regressions
6. **Update documentation** if needed

## Backward Compatibility

This change is fully backward compatible:

- Existing JSON files with escape sequences will continue to be read correctly
- The JSON reading functions (`read_json_file()`, `json.load()`, `json.loads()`) handle both escaped and unescaped Unicode characters
- No changes to data structures or APIs are required

## Performance Impact

The performance impact is negligible:

- `ensure_ascii=False` may actually be slightly faster since it skips the ASCII encoding step
- File sizes may be slightly smaller since escape sequences are longer than the actual Unicode characters
- No impact on JSON parsing performance

## Security Considerations

No security implications:

- UTF-8 encoding is maintained
- JSON structure and validation remain the same
- No new attack vectors are introduced
