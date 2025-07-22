# AI Mock System Documentation

## Overview

The AI Mock System provides comprehensive mocking capabilities for AI interactions in the LibriScribe validation system. It enables testing without consuming expensive AI resources while maintaining interface consistency with real AI calls.

## Key Features

- **Interface Consistency**: Same response format as real AI calls
- **Scenario-based Testing**: Multiple test scenarios (success, failure, edge cases)
- **Record and Playback**: Deterministic testing with real AI interaction data
- **Configuration-driven**: Easy switching between mock and real AI via configuration
- **Test Coverage Metrics**: Comprehensive tracking of test coverage and accuracy

## Core Classes

### MockScenario (Enum)

Available mock scenarios for testing different conditions:

```python
class MockScenario(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    INVALID_RESPONSE = "invalid_response"
    PARTIAL_FAILURE = "partial_failure"
    HIGH_QUALITY = "high_quality"
    LOW_QUALITY = "low_quality"
    EDGE_CASE = "edge_case"
```

### MockResponse

Data structure for mock AI responses:

```python
@dataclass
class MockResponse:
    content: str                    # AI response content (usually JSON)
    model: str                      # Model name used
    tokens_used: int               # Number of tokens consumed
    cost: float                    # Cost of the request
    confidence: float = 1.0        # Confidence score (0.0-1.0)
    metadata: Dict[str, Any]       # Additional metadata
    timestamp: datetime            # Response timestamp
    scenario: MockScenario         # Scenario used to generate response
```

### RecordedInteraction

Structure for recorded AI interactions that can be played back:

```python
@dataclass
class RecordedInteraction:
    interaction_id: str            # Unique interaction identifier
    request_hash: str             # Hash of request for caching
    prompt: str                   # Original AI prompt
    response: MockResponse        # AI response
    validator_id: str             # Validator that made the request
    content_type: str             # Type of content being validated
    timestamp: datetime           # Interaction timestamp
    real_ai_used: bool = True     # Whether real AI was used
```

### AIMockManager

Main class for managing AI mocking with record/playback capabilities.

#### Constructor

```python
def __init__(self, mock_data_dir: Optional[str] = None)
```

**Parameters:**
- `mock_data_dir`: Directory to store mock data (default: `.libriscribe/mock_data`)

#### Key Methods

##### get_ai_response

```python
async def get_ai_response(
    prompt: str, 
    validator_id: str,
    content_type: str,
    scenario: Optional[MockScenario] = None,
    use_mock: bool = True
) -> MockResponse
```

Get AI response - either mock or real based on configuration.

**Parameters:**
- `prompt`: The AI prompt
- `validator_id`: ID of the validator making the request
- `content_type`: Type of content being validated
- `scenario`: Specific mock scenario to use (optional)
- `use_mock`: Whether to use mock (True) or real AI (False)

**Returns:** MockResponse object

##### create_test_suite

```python
async def create_test_suite(self, validators: List[str]) -> Dict[str, List[MockScenario]]
```

Create comprehensive test suite for validators.

**Parameters:**
- `validators`: List of validator IDs to test

**Returns:** Dictionary mapping validator IDs to test scenarios

##### run_test_suite

```python
async def run_test_suite(self, test_suite: Dict[str, List[MockScenario]]) -> Dict[str, Any]
```

Run comprehensive test suite and return results.

**Parameters:**
- `test_suite`: Test suite created by `create_test_suite`

**Returns:** Dictionary with test results including:
- `total_tests`: Total number of tests run
- `passed_tests`: Number of passed tests
- `failed_tests`: Number of failed tests
- `validator_results`: Results by validator
- `coverage_report`: Coverage metrics

##### get_usage_stats

```python
def get_usage_stats(self) -> Dict[str, Any]
```

Get mock system usage statistics.

**Returns:** Dictionary with usage statistics including:
- `mock_calls`: Number of mock calls made
- `real_calls`: Number of real AI calls made
- `scenarios_used`: Count of each scenario used
- `validators_tested`: List of validators tested
- `mock_coverage`: Coverage metrics

## Usage Examples

### Basic Mock Usage

```python
from libriscribe.validation.ai_mock import AIMockManager, MockScenario

# Initialize mock manager
mock_manager = AIMockManager()

# Get mock response for content validation
response = await mock_manager.get_ai_response(
    prompt="Validate this chapter content...",
    validator_id="content_validator",
    content_type="chapter",
    scenario=MockScenario.SUCCESS,
    use_mock=True
)

print(f"Validation score: {response.content}")
print(f"Tokens used: {response.tokens_used}")
print(f"Cost: ${response.cost}")
```

### Testing Different Scenarios

```python
# Test high quality scenario
high_quality_response = await mock_manager.get_ai_response(
    prompt="Validate high quality content",
    validator_id="quality_validator",
    content_type="manuscript",
    scenario=MockScenario.HIGH_QUALITY
)

# Test low quality scenario
low_quality_response = await mock_manager.get_ai_response(
    prompt="Validate low quality content",
    validator_id="quality_validator", 
    content_type="manuscript",
    scenario=MockScenario.LOW_QUALITY
)

# Test failure scenario
try:
    failure_response = await mock_manager.get_ai_response(
        prompt="Test failure",
        validator_id="test_validator",
        content_type="test",
        scenario=MockScenario.TIMEOUT
    )
except TimeoutError:
    print("Timeout scenario triggered successfully")
```

### Comprehensive Test Suite

```python
# Create test suite for multiple validators
validators = [
    "content_validator",
    "publishing_standards_validator", 
    "quality_originality_validator"
]

test_suite = await mock_manager.create_test_suite(validators)

# Run the test suite
results = await mock_manager.run_test_suite(test_suite)

print(f"Total tests: {results['total_tests']}")
print(f"Passed: {results['passed_tests']}")
print(f"Failed: {results['failed_tests']}")
print(f"Coverage: {results['coverage_report']['coverage_percentage']:.1f}%")

# Check results by validator
for validator_id, validator_results in results['validator_results'].items():
    print(f"\n{validator_id}:")
    print(f"  Passed: {validator_results['passed']}")
    print(f"  Failed: {validator_results['failed']}")
    for scenario, result in validator_results['scenarios'].items():
        print(f"  {scenario}: {result}")
```

### Record and Playback

```python
# Record real AI interactions for later playback
response = await mock_manager.get_ai_response(
    prompt="Real validation prompt",
    validator_id="content_validator",
    content_type="chapter",
    use_mock=False  # Use real AI and record interaction
)

# Later, the same request will use recorded response
cached_response = await mock_manager.get_ai_response(
    prompt="Real validation prompt",  # Same prompt
    validator_id="content_validator", # Same validator
    content_type="chapter",          # Same content type
    use_mock=True  # Will use recorded response
)
```

### Configuration Integration

```python
from libriscribe.validation.ai_mock import create_mock_manager, get_mock_config_for_testing

# Get recommended configuration
config = get_mock_config_for_testing()
print(config)
# Output:
# {
#     "ai_mock_enabled": True,
#     "mock_data_dir": ".libriscribe/mock_data",
#     "default_scenario": "success",
#     "record_real_interactions": True,
#     "test_coverage_required": 80.0,
#     "scenarios_to_test": [
#         "success", "high_quality", "low_quality",
#         "failure", "partial_failure", "edge_case"
#     ]
# }

# Create mock manager with configuration
mock_manager = await create_mock_manager(config)
```

## Mock Response Examples

### Content Validator Success Response

```json
{
    "tone_consistency_score": 85.0,
    "outline_adherence_score": 90.0,
    "quality_score": 87.5,
    "findings": [
        {
            "type": "tone_consistency",
            "severity": "low",
            "message": "Minor tone variation in chapter 3",
            "confidence": 0.8
        }
    ],
    "recommendations": [
        "Consider reviewing tone consistency in chapter 3"
    ]
}
```

### Publishing Standards Validator Response

```json
{
    "formatting_score": 95.0,
    "metadata_completeness": 100.0,
    "structure_score": 92.0,
    "findings": [],
    "publishing_ready": true
}
```

### Quality Originality Validator Response

```json
{
    "originality_score": 98.0,
    "grammar_score": 94.0,
    "readability_score": 88.0,
    "plagiarism_detected": false,
    "findings": [
        {
            "type": "grammar",
            "severity": "low",
            "message": "Minor grammar issue on page 45",
            "confidence": 0.9
        }
    ]
}
```

### Low Quality Response

```json
{
    "validation_score": 65.0,
    "quality_score": 62.0,
    "status": "needs_review",
    "findings": [
        {
            "type": "content_quality",
            "severity": "high",
            "message": "Content quality below threshold",
            "confidence": 0.9
        },
        {
            "type": "tone_consistency",
            "severity": "medium",
            "message": "Inconsistent tone throughout",
            "confidence": 0.8
        }
    ],
    "recommendations": [
        "Human review required",
        "Consider regenerating content",
        "Review tone consistency"
    ]
}
```

## Integration with Validation System

### Using Mock in Validators

```python
from libriscribe.validation.ai_mock import AIMockManager
from libriscribe.validation.interfaces import ValidatorBase

class ContentValidator(ValidatorBase):
    def __init__(self, mock_manager: AIMockManager = None):
        super().__init__("content_validator", "Content Validator", "1.0.0")
        self.mock_manager = mock_manager
        
    async def validate(self, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        # Use mock manager if available
        if self.mock_manager:
            response = await self.mock_manager.get_ai_response(
                prompt=self._build_validation_prompt(content),
                validator_id=self.validator_id,
                content_type=context.get("content_type", "unknown"),
                use_mock=context.get("use_mock", True)
            )
        else:
            # Use real AI through LiteLLM
            response = await self._call_real_ai(content, context)
            
        return self._process_ai_response(response)
```

### Configuration-Driven Testing

```python
from libriscribe.validation.config import ValidationConfig

# Enable mock in configuration
config = ValidationConfig(
    project_id="test_project",
    ai_mock_enabled=True,
    validator_configs={
        "content_validator": {
            "mock_scenario": "success",
            "mock_data_dir": ".libriscribe/test_data"
        }
    }
)

# Mock manager will be used automatically based on configuration
```

## File Structure

The mock system creates the following file structure:

```
.libriscribe/
└── mock_data/
    ├── recorded_interactions.json    # Recorded AI interactions
    └── mock_responses.json          # Custom mock responses
```

### recorded_interactions.json Format

```json
[
    {
        "interaction_id": "uuid-string",
        "request_hash": "md5-hash",
        "prompt": "AI prompt text",
        "response": {
            "content": "AI response content",
            "model": "gpt-4",
            "tokens_used": 150,
            "cost": 0.003,
            "confidence": 0.9,
            "metadata": {},
            "timestamp": "2025-01-22T10:30:00",
            "scenario": "success"
        },
        "validator_id": "content_validator",
        "content_type": "chapter",
        "timestamp": "2025-01-22T10:30:00",
        "real_ai_used": true
    }
]
```

## Best Practices

### 1. Use Appropriate Scenarios

```python
# Use HIGH_QUALITY for testing optimal conditions
response = await mock_manager.get_ai_response(
    prompt="Test optimal content",
    validator_id="validator",
    content_type="test",
    scenario=MockScenario.HIGH_QUALITY
)

# Use LOW_QUALITY for testing human review triggers
response = await mock_manager.get_ai_response(
    prompt="Test poor content",
    validator_id="validator", 
    content_type="test",
    scenario=MockScenario.LOW_QUALITY
)
```

### 2. Record Real Interactions for Realistic Testing

```python
# Record real interactions during development
real_response = await mock_manager.get_ai_response(
    prompt="Real validation prompt",
    validator_id="content_validator",
    content_type="chapter",
    use_mock=False  # Record real AI interaction
)

# Use recorded interactions in tests
test_response = await mock_manager.get_ai_response(
    prompt="Real validation prompt",  # Same prompt will use recording
    validator_id="content_validator",
    content_type="chapter",
    use_mock=True
)
```

### 3. Monitor Test Coverage

```python
# Check coverage regularly
stats = mock_manager.get_usage_stats()
coverage = stats["mock_coverage"]["coverage_percentage"]

if coverage < 80.0:
    print(f"Warning: Test coverage is {coverage:.1f}%, below 80% threshold")
    
# Identify untested scenarios
total_scenarios = len(MockScenario)
tested_scenarios = stats["mock_coverage"]["scenarios_covered"]
print(f"Tested {tested_scenarios}/{total_scenarios} scenarios")
```

### 4. Handle Exceptions in Tests

```python
# Test timeout scenarios
try:
    response = await mock_manager.get_ai_response(
        prompt="Test timeout",
        validator_id="test_validator",
        content_type="test",
        scenario=MockScenario.TIMEOUT
    )
except TimeoutError:
    # Expected behavior
    pass

# Test rate limiting
try:
    response = await mock_manager.get_ai_response(
        prompt="Test rate limit",
        validator_id="test_validator",
        content_type="test", 
        scenario=MockScenario.RATE_LIMIT
    )
except Exception as e:
    assert "Rate limit exceeded" in str(e)
```

## Utility Functions

### create_mock_manager

```python
async def create_mock_manager(config: Dict[str, Any]) -> AIMockManager
```

Create and configure AI mock manager from configuration dictionary.

### get_mock_config_for_testing

```python
def get_mock_config_for_testing() -> Dict[str, Any]
```

Get recommended mock configuration for testing with sensible defaults.

## Error Handling

The mock system handles various error scenarios:

- **TimeoutError**: Raised for TIMEOUT scenario
- **Exception**: Raised for RATE_LIMIT scenario with appropriate message
- **JSON parsing errors**: For INVALID_RESPONSE scenario
- **File I/O errors**: Gracefully handled when loading/saving mock data

## Performance Considerations

- Mock responses include simulated processing delays (0.1s for most scenarios)
- Real AI calls include realistic delays (2.0s simulation)
- File I/O is performed asynchronously where possible
- Memory usage is managed through request hashing and caching

## Integration Testing

The mock system supports comprehensive integration testing:

```python
# Test all validators with all scenarios
validators = ["content_validator", "quality_validator", "publishing_validator"]
test_suite = await mock_manager.create_test_suite(validators)
results = await mock_manager.run_test_suite(test_suite)

# Verify all tests passed
assert results["failed_tests"] == 0
assert results["coverage_report"]["coverage_percentage"] >= 80.0
```

This documentation provides comprehensive coverage of the AI Mock System, enabling developers to effectively use it for testing validation components without consuming expensive AI resources.