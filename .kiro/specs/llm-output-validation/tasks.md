# Implementation Plan

- [ ] 1. Enhance JSONProcessor with markdown detection and cleanup using existing libraries
  - Add `detect_markdown_artifacts()` method to identify ```json code blocks and other formatting issues
  - Add `clean_llm_response()` method to remove markdown artifacts from LLM responses using regex patterns
  - Add `extract_json_from_llm_response()` method with enhanced extraction logic for various response formats
  - Leverage existing `safe_json_loads()` method and enhance error reporting
  - _Requirements: 1.1, 1.2, 4.1, 4.2_

- [ ] 2. Create Pydantic models for JSON validation instead of custom schemas
  - Create `ConceptModel` Pydantic model with required fields (title, logline, description) and validation rules
  - Create `KeywordsModel` Pydantic model for keyword structure validation
  - Use Pydantic's built-in validation capabilities instead of custom schema validation
  - Add `validate_json_with_pydantic()` method in JSONProcessor to use these models
  - _Requirements: 3.2, 1.4_

- [ ] 3. Enhance Agent base class JSON extraction methods using Rich for logging
  - Update `safe_extract_json()` to use enhanced JSONProcessor methods with Pydantic validation
  - Add `_detect_llm_formatting_issues()` method to identify common LLM response problems
  - Add `_validate_and_clean_json_output()` method for pre-save validation using Pydantic models
  - Use Rich console for enhanced logging with color-coded warnings and errors
  - _Requirements: 2.1, 2.2, 1.1, 1.2_

- [ ] 4. Update ConceptGeneratorAgent to use clean JSON output
  - Remove raw_content wrapper from saved JSON files
  - Update file saving logic to save only clean concept and keywords data
  - Modify `_dump_raw_response()` to save debug info separately from production output
  - Update validation to use new schema-based validation methods
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 5. Implement enhanced error handling and logging using Rich and Tenacity
  - Use Rich console for color-coded log messages for markdown detection (JSON_EXTRACTION_WARNING)
  - Add detailed error logging for Pydantic validation failures with Rich formatting (JSON_VALIDATION_ERROR)
  - Add content filtering detection logging with Rich panels (CONTENT_FILTERING_DETECTED)
  - Use Tenacity for retry logic with exponential backoff when JSON extraction fails
  - Add fallback generation logging with Rich progress indicators (FALLBACK_GENERATION_USED)
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 6. Create comprehensive unit tests using pytest fixtures and parametrize
  - Test `detect_markdown_artifacts()` with various markdown patterns using pytest.mark.parametrize
  - Test `clean_llm_response()` with different response formats using pytest fixtures
  - Test `extract_json_from_llm_response()` with valid and invalid JSON using existing pytest setup
  - Test Pydantic model validation with valid and invalid concept structures
  - Test edge cases with special characters and escape sequences using pytest-asyncio for async tests
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 7. Create integration tests using existing pytest-asyncio framework
  - Test ConceptGeneratorAgent produces clean JSON output without raw_content using existing test patterns
  - Test that debug information is saved separately from production output using pytest tmp_path fixtures
  - Test error handling when LLM returns malformed JSON using existing mock LLM client
  - Test fallback mechanisms when content filtering occurs using pytest-asyncio for async testing
  - _Requirements: 3.1, 3.2, 3.3, 1.3_

- [ ] 8. Update existing agents to use enhanced JSON processing
  - Review other agents that use JSON extraction (CharacterGeneratorAgent, etc.)
  - Update them to use the new enhanced JSON processing methods
  - Ensure consistent output format across all agents
  - _Requirements: 3.1, 3.2_

- [ ] 9. Add performance monitoring and validation
  - Add timing measurements for JSON extraction and validation
  - Monitor memory usage with large LLM responses
  - Add metrics tracking for extraction success rates and validation failures
  - _Requirements: 2.2, 2.3_

- [ ] 10. Create documentation and migration guide
  - Document the new JSON processing methods and their usage
  - Create migration guide for any breaking changes
  - Update agent development guidelines to use new validation methods
  - _Requirements: 3.1, 3.2_
