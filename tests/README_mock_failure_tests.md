# Mock LLM Client Failure Testing

## Overview

This document describes the mock LLM client failure testing implementation that allows testing CLI failure scenarios when the mock LLM client fails after a specific number of calls.

## Implementation

### FailingMockLLMClient

A specialized mock LLM client (`FailingMockLLMClient`) that extends the regular `MockLLMClient` to fail after a specified number of calls:

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

### Test Scenarios

The test suite includes the following failure scenarios:

1. **Fail after 1 call**: Tests that the CLI fails properly when the mock LLM fails on the second call (after succeeding on the first)
2. **Fail after 2 calls**: Tests failure on the third call (after two successful calls)
3. **Fail after 3 calls**: Tests failure on the fourth call (after three successful calls)
4. **Fail during chapter writing**: Tests failure during the chapter writing phase

### Test Structure

Each test follows this pattern:

1. **Mock Settings**: Creates a mock Settings instance with appropriate configuration
2. **Create Failing Client**: Instantiates a `FailingMockLLMClient` with the desired failure point
3. **Mock LLM Client Method**: Patches the `_generate_mock_content` method to use the failing client
4. **Execute Book Creation**: Calls the book creator service with specific arguments
5. **Assert Failure**: Verifies that the CLI fails with the expected error message

### Key Features

- **Call Counting**: Tracks the number of LLM calls made
- **Configurable Failure Point**: Can be set to fail after any number of calls
- **Proper Error Propagation**: Ensures errors are properly propagated through the CLI stack
- **Realistic Testing**: Tests actual CLI failure scenarios that could occur in production

### Usage Example

```python
def test_mock_fails_after_2_calls(self):
    # Create failing mock client that fails after 2 calls
    failing_client = FailingMockLLMClient(fail_after_calls=2)

    # Mock the LLM client to use our failing client
    with patch('libriscribe2.utils.llm_client.LLMClient._generate_mock_content') as mock_generate:
        async def mock_side_effect(prompt, temperature, **kwargs):
            prompt_type = kwargs.get("prompt_type", "general")
            return failing_client.generate_content(prompt, prompt_type, temperature, "English")

        mock_generate.side_effect = mock_side_effect

        # Test that CLI fails properly
        with pytest.raises(RuntimeError, match="Book creation failed"):
            book_creator.create_book(args)
```

## Benefits

1. **Comprehensive Testing**: Ensures CLI handles LLM failures gracefully at any point in the process
2. **Realistic Scenarios**: Tests actual failure conditions that could occur with real LLM providers
3. **Error Handling Validation**: Confirms that error messages are properly formatted and displayed
4. **Regression Prevention**: Prevents regressions in error handling code

## Test Results

All tests pass successfully, confirming that:

- The CLI properly handles LLM failures at different stages
- Error messages are appropriately formatted
- The failure scenarios are correctly simulated
- The mock client behavior is consistent and predictable
