# Systematic Mock LLM Failure Testing

## Overview

This document describes the systematic failure testing framework implemented for the LibriScribe2 project to ensure robust error handling throughout the book creation process.

## Problem Statement

The book creation process involves multiple sequential LLM calls. It's critical to verify that the CLI handles failures gracefully at any point in this sequence. Previously, we only tested a few specific failure scenarios, but we needed comprehensive coverage.

## Solution: Parametrized Failure Testing

### Implementation

The test framework uses a `FailingMockLLMClient` that extends the standard `MockLLMClient` with failure injection capabilities:

```python
class FailingMockLLMClient(MockLLMClient):
    """Mock LLM client that fails after a specified number of calls."""

    def __init__(self, fail_after_calls: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_after_calls = fail_after_calls
        self.call_count = 0

    def generate_content(self, prompt: str, prompt_type: str = "default",
                        temperature: float = 0.7, language: str = "English",
                        timeout: int | None = None) -> str:
        """Generate content but fail after specified number of calls."""
        self.call_count += 1

        if self.call_count > self.fail_after_calls:
            raise RuntimeError(f"Mock LLM client failed after {self.fail_after_calls} calls")

        # Return normal mock content for successful calls
        return super().generate_content(prompt=prompt, prompt_type=prompt_type,
                                      temperature=temperature, language=language,
                                      timeout=timeout)
```

### Test Coverage

The main test uses pytest parametrization to systematically test failures at each call position:

```python
@pytest.mark.parametrize("fail_after_calls", range(1, 20))  # Test failures from call 1 to 19
def test_mock_fails_at_specific_call(self, mock_settings_class, mock_generate_content, fail_after_calls):
    """Test that CLI fails properly when mock LLM fails at specific call position."""
```

## Call Sequence Analysis

Based on analysis of a typical book creation process (3 chapters, 2 characters), the LLM call sequence is:

| Call # | Stage | Purpose |
|--------|-------|---------|
| 1-4 | Concept Generation | concept, critique, refine, keywords |
| 5 | Outline Generation | Main outline |
| 6-8 | Scene Outlines | Scene breakdowns for 3 chapters |
| 9 | Character Generation | Character profiles |
| 10-18 | Scene Writing | 3 scenes × 3 chapters = 9 scenes |

**Total Expected Calls: 18**

## Test Scenarios

### Failure Tests (Calls 1-18)
- **Purpose**: Verify that failures at any point in the sequence are handled gracefully
- **Expected Behavior**: CLI should raise `RuntimeError` with message "Book creation failed"
- **Verification**: Confirms the failure occurred at the expected call number

### Success Test (Call 19+)
- **Purpose**: Verify that when no failure is programmed, the process completes successfully
- **Expected Behavior**: All 18 calls complete successfully
- **Verification**: Confirms exactly 18 calls were made

## Benefits

1. **Comprehensive Coverage**: Tests every possible failure point in the book creation process
2. **Regression Prevention**: Ensures new changes don't break error handling
3. **Systematic Approach**: Uses parametrization to avoid code duplication
4. **Precise Verification**: Confirms failures occur at the exact expected call position
5. **Boundary Testing**: Verifies both failure and success scenarios

## Usage

Run the systematic failure tests:

```bash
# Run all failure scenario tests
hatch run test tests/test_mock_failure_scenarios.py -v

# Run specific failure position
hatch run test tests/test_mock_failure_scenarios.py::TestMockFailureScenarios::test_mock_fails_at_specific_call[5] -v

# Run success scenario
hatch run test tests/test_mock_failure_scenarios.py::TestMockFailureScenarios::test_mock_succeeds_with_no_failure -v
```

## Key Implementation Details

1. **Unique Project Names**: Each test uses a unique suffix to avoid directory conflicts
2. **Proper Cleanup**: Tests use temporary directories that are cleaned up automatically
3. **Mock Settings**: Each test creates isolated mock settings to avoid interference
4. **Call Counting**: The failing client accurately tracks and reports call counts
5. **Error Message Matching**: Tests verify the specific error message format expected by users

This systematic approach ensures that LibriScribe2's error handling is robust and reliable across all stages of the book creation process.
