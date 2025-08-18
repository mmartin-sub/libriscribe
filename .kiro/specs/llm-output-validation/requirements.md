# Requirements Document

## Introduction

The LibriScribe2 system currently has issues with LLM output processing where raw responses containing markdown code blocks (```json) are being saved instead of clean JSON data. This creates problems for downstream processing and makes the output files inconsistent and harder to parse. We need to implement proper LLM output validation and cleanup to ensure consistent, clean JSON output across all agents.

## Requirements

### Requirement 1

**User Story:** As a developer, I want LLM responses to be properly validated and cleaned before being saved, so that output files contain only clean JSON data without markdown formatting artifacts.

#### Acceptance Criteria

1. WHEN an LLM returns content with markdown code blocks THEN the system SHALL extract only the JSON content and discard the markdown formatting
2. WHEN an LLM returns content with ```json markers THEN the system SHALL detect this as a formatting issue and extract the clean JSON
3. WHEN saving concept.json or other JSON output files THEN the system SHALL contain only the clean JSON structure without raw_content wrappers
4. WHEN an LLM response contains malformed JSON within code blocks THEN the system SHALL log an error and attempt to fix common JSON formatting issues

### Requirement 2

**User Story:** As a developer, I want to be notified when LLM responses contain problematic formatting, so that I can identify and address content generation issues.

#### Acceptance Criteria

1. WHEN an LLM response contains ```json code blocks THEN the system SHALL log a warning about markdown formatting in JSON responses
2. WHEN JSON extraction fails due to malformed content THEN the system SHALL log detailed error information including the problematic content
3. WHEN content filtering triggers are detected THEN the system SHALL log specific indicators that caused the issue
4. WHEN fallback content generation is used THEN the system SHALL log which fallback method was applied

### Requirement 3

**User Story:** As a developer, I want consistent JSON output format across all agents, so that downstream processing and file parsing works reliably.

#### Acceptance Criteria

1. WHEN any agent saves JSON output THEN the system SHALL use a consistent format without metadata wrappers
2. WHEN concept.json is generated THEN it SHALL contain only the concept data structure: {"concept": {...}, "keywords": {...}}
3. WHEN debug information is needed THEN it SHALL be saved to separate debug files, not mixed with production output
4. WHEN JSON validation fails THEN the system SHALL provide clear error messages and not save malformed output

### Requirement 4

**User Story:** As a developer, I want robust JSON extraction that handles various LLM response formats, so that the system works reliably with different LLM providers and response styles.

#### Acceptance Criteria

1. WHEN an LLM response contains JSON in code blocks THEN the system SHALL extract it correctly
2. WHEN an LLM response contains JSON without code blocks THEN the system SHALL extract it correctly
3. WHEN an LLM response contains multiple JSON objects THEN the system SHALL extract the first valid one
4. WHEN an LLM response contains no valid JSON THEN the system SHALL return null and log appropriate error messages
5. WHEN JSON contains escape sequences or special characters THEN the system SHALL handle them correctly without corruption
