# Design Document

## Overview

This design addresses the LLM output validation and cleanup issues in LibriScribe2. The current system saves raw LLM responses containing markdown code blocks instead of clean JSON data, causing downstream processing problems. The solution involves implementing a robust JSON extraction and validation pipeline that ensures consistent, clean output across all agents.

## Architecture

The solution will be implemented as a layered approach:

1. **Enhanced JSON Extraction Layer**: Improved JSON extraction methods in `JSONProcessor` and `Agent` base class
2. **Output Validation Layer**: New validation methods to ensure JSON structure compliance
3. **Content Cleanup Layer**: Methods to detect and clean markdown formatting artifacts
4. **Logging and Monitoring Layer**: Enhanced logging for debugging LLM response issues

## Components and Interfaces

### Enhanced JSONProcessor

**Location**: `src/libriscribe2/utils/json_utils.py`

**New Methods**:

- `extract_json_from_llm_response(response: str) -> dict[str, Any] | None`: Enhanced JSON extraction with markdown detection
- `validate_json_with_pydantic(data: dict, model_class: BaseModel) -> tuple[bool, list[str]]`: Validate JSON using Pydantic models
- `clean_llm_response(response: str) -> str`: Remove markdown artifacts and clean response
- `detect_markdown_artifacts(response: str) -> list[str]`: Detect problematic formatting patterns

**Enhanced Methods**:

- `extract_json_from_response()`: Add markdown detection and warning logging
- `safe_json_loads()`: Add better error reporting with content preview

### Enhanced Agent Base Class

**Location**: `src/libriscribe2/agents/agent_base.py`

**Modified Methods**:

- `safe_extract_json()`: Use enhanced JSONProcessor methods and add validation
- `_dump_raw_response()`: Separate debug output from production output
- Add new method `_validate_and_clean_json_output()`: Validate JSON before saving

**New Methods**:

- `_detect_llm_formatting_issues(content: str) -> list[str]`: Detect common LLM formatting problems
- `_log_json_extraction_warning(issues: list[str])`: Log formatting issues for debugging

### ConceptGeneratorAgent Updates

**Location**: `src/libriscribe2/agents/concept_generator.py`

**Modified Methods**:

- `execute()`: Use clean JSON extraction and remove raw_content from output
- `_validate_concept_json()`: Enhanced validation with schema checking
- File saving logic: Save only clean JSON structure without metadata wrappers

## Data Models

### Clean JSON Output Format

```json
{
  "concept": {
    "title": "Book Title",
    "logline": "One sentence summary",
    "description": "Detailed description"
  },
  "keywords": {
    "primary_keywords": ["keyword1", "keyword2"],
    "secondary_keywords": ["keyword3", "keyword4"],
    "genre_keywords": ["keyword5", "keyword6"]
  }
}
```

### Debug Output Format (separate file)

```json
{
  "debug_info": {
    "agent_name": "ConceptGeneratorAgent",
    "timestamp": "2025-01-12T10:30:00Z",
    "raw_response": "```json\n{...}\n```",
    "formatting_issues": ["markdown_code_blocks", "unicode_escapes"],
    "extraction_method": "markdown_block_extraction"
  }
}
```

### Pydantic Models for Validation

```python
from pydantic import BaseModel, Field, validator
from typing import List

class ConceptModel(BaseModel):
    title: str = Field(..., min_length=1, description="Book title")
    logline: str = Field(..., min_length=1, description="One sentence summary")
    description: str = Field(..., min_length=1, description="Detailed description")

    @validator('title', 'logline', 'description')
    def validate_non_empty_strings(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()

class KeywordsModel(BaseModel):
    primary_keywords: List[str] = Field(default_factory=list)
    secondary_keywords: List[str] = Field(default_factory=list)
    genre_keywords: List[str] = Field(default_factory=list)

    @validator('*', pre=True)
    def validate_keyword_lists(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v or []
```

## Error Handling

### Markdown Detection and Cleanup

1. **Detection**: Scan for ````json`, `````, and other markdown patterns
2. **Extraction**: Extract JSON content from within code blocks
3. **Validation**: Validate extracted JSON structure
4. **Logging**: Log warnings about markdown formatting issues
5. **Fallback**: If extraction fails, attempt alternative parsing methods

### JSON Validation Pipeline

1. **Structure Validation**: Check for required fields and correct types
2. **Content Validation**: Ensure non-empty strings and valid data
3. **Schema Compliance**: Validate against predefined schemas
4. **Error Reporting**: Provide detailed error messages with context

### Content Filtering Handling

1. **Detection**: Identify content filtering triggers in responses
2. **Logging**: Log specific indicators that may have caused filtering
3. **Fallback**: Use simplified prompts when filtering is detected
4. **Recovery**: Attempt to generate alternative content

## Testing Strategy

### Unit Tests

1. **JSON Extraction Tests**: Test various LLM response formats
   - Responses with markdown code blocks
   - Responses without markdown formatting
   - Malformed JSON responses
   - Multiple JSON objects in response
   - Empty or null responses

2. **Validation Tests**: Test JSON structure validation
   - Valid concept JSON structures
   - Invalid or incomplete structures
   - Edge cases with special characters
   - Schema compliance testing

3. **Cleanup Tests**: Test markdown artifact removal
   - Various markdown patterns
   - Mixed content with JSON
   - Unicode and escape sequence handling

### Integration Tests

1. **Agent Output Tests**: Test complete agent execution pipeline
   - ConceptGeneratorAgent with clean output
   - Other agents using JSON extraction
   - File saving with correct format

2. **Error Handling Tests**: Test error scenarios
   - LLM returns malformed JSON
   - Content filtering scenarios
   - Network or API failures

### Performance Tests

1. **JSON Processing Performance**: Measure extraction and validation speed
2. **Memory Usage**: Monitor memory consumption with large responses
3. **Error Recovery Time**: Measure fallback mechanism performance

## Implementation Plan

### Phase 1: Core JSON Processing Enhancement

- Enhance JSONProcessor with markdown detection using regex
- Add robust JSON extraction methods leveraging existing safe_json_loads
- Create Pydantic models for validation instead of custom schemas

### Phase 2: Agent Base Class Updates

- Update safe_extract_json method
- Add validation pipeline
- Enhance error logging

### Phase 3: ConceptGeneratorAgent Fixes

- Remove raw_content from output
- Use clean JSON extraction
- Update file saving logic

### Phase 4: Testing and Validation

- Comprehensive test suite
- Integration testing
- Performance validation

## Migration Strategy

### Backward Compatibility

- Existing JSON files will continue to work
- New format will be cleaner and more consistent
- Debug information moved to separate files

### Rollout Plan

1. Deploy enhanced JSON processing utilities
2. Update agent base class with new methods
3. Update ConceptGeneratorAgent to use clean output
4. Monitor for any issues and adjust as needed

## Monitoring and Logging

### New Log Messages

- `JSON_EXTRACTION_WARNING`: When markdown artifacts are detected
- `JSON_VALIDATION_ERROR`: When JSON structure validation fails
- `CONTENT_FILTERING_DETECTED`: When content filtering indicators are found
- `FALLBACK_GENERATION_USED`: When fallback content generation is triggered

### Metrics to Track

- JSON extraction success rate
- Validation failure rate
- Content filtering occurrence rate
- Response cleanup effectiveness
