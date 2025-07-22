# AI Mock System API Documentation

## Overview

The AI Mock System provides comprehensive mocking capabilities for AI interactions in the LibriScribe validation system. It enables testing without consuming expensive AI resources while maintaining identical interfaces to real AI calls.

## Key Features

- **OpenAI SDK Integration**: Uses standard OpenAI SDK with LiteLLM proxy configured via environment variables
- **API Key-Based Switching**: Empty `OPENAI_API_KEY` = mock mode, set key = real AI mode
- **Live Response Recording**: Automatically records real AI responses for future mock use
- **Scenario-Based Testing**: Comprehensive testing with different response scenarios
- **Deterministic Testing**: Consistent, repeatable test results with recorded interactions

## Classes and Enums

### MockScenario (Enum)

Available mock scenarios for testing different AI response conditions.

```python
class MockScenario(Enum):
    SUCCESS = "success"              # Normal successful validation
    FAILURE = "failure"              # Complete validation failure
    TIMEOUT = "timeout"              # AI timeout simulation
    RATE_LIMIT = "rate_limit"        # Rate limiting simulation
    INVALID_RESPONSE = "invalid_response"  # Malformed JSON response
    PARTIAL_FAILURE = "partial_failure"    # Some checks pass, some fail
    HIGH_QUALITY = "high_quality"    # High quality content (>90% score)
    LOW_QUALITY = "low_quality"      # Low quality content (<70% score)
    EDGE_CASE = "edge_case"          # Edge cases (empty content, etc.)
```

### MockResponse (Dataclass)

Standardized response structure for both mock and real AI responses.

```python
@dataclass
class MockResponse:
    content: str                     # AI response content (JSON string)
    model: str                       # Model used (e.g., "gpt-4")
    tokens_used: int                 # Token consumption
    cost: float                      # API cost in USD
    confidence: float = 1.0          # Response confidence (0.0-1.0)
    metadata: Dict[str, Any]         # Additional metadata
    timestamp: datetime              # Response timestamp
    scenario: MockScenario           # Mock scenario used
```

### RecordedInteraction (Dataclass)

Recorded AI interaction for deterministic playback.

```python
@dataclass
class RecordedInteraction:
    interaction_id: str              # Unique interaction identifier
    request_hash: str                # Hash of prompt + context for caching
    prompt: str                      # Original prompt text
    response: MockResponse           # AI response
    validator_id: str                # Validator that made the request
    content_type: str                # Type of content validated
    timestamp: datetime              # Recording timestamp
    real_ai_used: bool = True        # Whether real AI was used
```

## Main Class: AIMockManager

The central class that manages AI interactions with automatic mock/real switching.

### Constructor

```python
def __init__(self, mock_data_dir: Optional[str] = None)
```

**Parameters:**
- `mock_data_dir` (Optional[str]): Directory for storing mock data. Defaults to `.libriscribe/mock_data`

**Behavior:**
- Automatically detects mock vs real mode based on `OPENAI_API_KEY` environment variable
- Initializes OpenAI client if API key is present and SDK is available
- Loads existing recorded interactions and mock responses from disk

### Core Methods

#### get_ai_response()

Main method for getting AI responses with automatic mock/real switching.

```python
async def get_ai_response(
    self, 
    prompt: str, 
    validator_id: str,
    content_type: str,
    model: str = "gpt-4",
    scenario: Optional[MockScenario] = None
) -> MockResponse
```

**Parameters:**
- `prompt` (str): The AI prompt text
- `validator_id` (str): ID of the validator making the request
- `content_type` (str): Type of content being validated ("chapter", "manuscript", etc.)
- `model` (str): OpenAI model to use (default: "gpt-4")
- `scenario` (Optional[MockScenario]): Specific mock scenario (only used in mock mode)

**Returns:**
- `MockResponse`: Standardized response structure

**Usage Example:**
```python
mock_manager = AIMockManager()

# Automatically uses mock or real AI based on OPENAI_API_KEY
response = await mock_manager.get_ai_response(
    prompt="Validate this chapter content",
    validator_id="content_validator",
    content_type="chapter",
    model="gpt-4",
    scenario=MockScenario.SUCCESS  # Only used if in mock mode
)

print(f"Response: {response.content}")
print(f"Tokens used: {response.tokens_used}")
print(f"Cost: ${response.cost:.4f}")
```

#### populate_mock_mappings_from_live()

Populate mock input/output mappings from live AI responses for testing.

```python
async def populate_mock_mappings_from_live(
    self, 
    prompts: List[Dict[str, Any]],
    model: str = "gpt-4"
) -> Dict[str, Any]
```

**Parameters:**
- `prompts` (List[Dict[str, Any]]): List of prompt configurations with keys:
  - `prompt` (str): The actual prompt text
  - `validator_id` (str): Validator making the request
  - `content_type` (str): Type of content being validated
  - `expected_scenario` (str): Expected mock scenario for this prompt
- `model` (str): OpenAI model to use for live calls (default: "gpt-4")

**Returns:**
- `Dict[str, Any]`: Results of the mapping population process

**Usage Example:**
```python
# Define prompts to record from live AI
prompts = [
    {
        "prompt": "Analyze this chapter for tone consistency",
        "validator_id": "content_validator",
        "content_type": "chapter",
        "expected_scenario": "success"
    },
    {
        "prompt": "Check manuscript publishing standards",
        "validator_id": "publishing_standards_validator",
        "content_type": "manuscript",
        "expected_scenario": "success"
    }
]

# Record from live AI (requires OPENAI_API_KEY)
results = await mock_manager.populate_mock_mappings_from_live(
    prompts=prompts,
    model="gpt-4"
)

print(f"Recorded {results['successful_recordings']} interactions")
print(f"Total cost: ${sum(r['cost'] for r in results['recordings']):.4f}")
```

#### create_test_suite()

Create comprehensive test suite for validators.

```python
async def create_test_suite(self, validators: List[str]) -> Dict[str, List[MockScenario]]
```

**Parameters:**
- `validators` (List[str]): List of validator IDs to test

**Returns:**
- `Dict[str, List[MockScenario]]`: Test suite mapping validators to scenarios

**Usage Example:**
```python
validators = ["content_validator", "quality_validator", "publishing_validator"]
test_suite = await mock_manager.create_test_suite(validators)

# Returns:
# {
#     "content_validator": [MockScenario.SUCCESS, MockScenario.HIGH_QUALITY, ...],
#     "quality_validator": [MockScenario.SUCCESS, MockScenario.HIGH_QUALITY, ...],
#     ...
# }
```

#### run_test_suite()

Run comprehensive test suite and return results.

```python
async def run_test_suite(self, test_suite: Dict[str, List[MockScenario]]) -> Dict[str, Any]
```

**Parameters:**
- `test_suite` (Dict[str, List[MockScenario]]): Test suite from `create_test_suite()`

**Returns:**
- `Dict[str, Any]`: Comprehensive test results

**Usage Example:**
```python
test_suite = await mock_manager.create_test_suite(["content_validator"])
results = await mock_manager.run_test_suite(test_suite)

print(f"Total tests: {results['total_tests']}")
print(f"Passed: {results['passed_tests']}")
print(f"Failed: {results['failed_tests']}")
print(f"Coverage: {results['coverage_report']['coverage_percentage']:.1f}%")
```

#### get_usage_stats()

Get mock system usage statistics.

```python
def get_usage_stats(self) -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Usage statistics including:
  - `mock_calls` (int): Number of mock AI calls made
  - `real_calls` (int): Number of real AI calls made
  - `validators_tested` (List[str]): List of validators that have been tested
  - `scenarios_used` (Dict[str, int]): Count of each scenario used
  - `recorded_interactions` (int): Number of recorded interactions
  - `mock_coverage` (Dict[str, Any]): Coverage metrics

**Usage Example:**
```python
stats = mock_manager.get_usage_stats()

print(f"Mock calls: {stats['mock_calls']}")
print(f"Real AI calls: {stats['real_calls']}")
print(f"Validators tested: {len(stats['validators_tested'])}")
print(f"Coverage: {stats['mock_coverage']['coverage_percentage']:.1f}%")
```

## Environment Configuration

The system uses environment variables for configuration:

```bash
# Mock Mode (Development/Testing)
# Leave OPENAI_API_KEY empty or unset
unset OPENAI_API_KEY

# Real AI Mode (Production/Recording)
export OPENAI_API_KEY="your-openai-api-key"

# Optional: Configure LiteLLM Proxy
export OPENAI_BASE_URL="https://your-litellm-proxy.com/v1"
```

## Mock Response Examples

### Success Response (content_validator)
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

### High Quality Response
```json
{
  "validation_score": 95.0,
  "quality_score": 96.0,
  "status": "excellent",
  "findings": [],
  "recommendations": ["Content meets high quality standards"]
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
    }
  ],
  "recommendations": [
    "Human review required",
    "Consider regenerating content"
  ]
}
```

## File Storage

The system stores data in the following files:

- `.libriscribe/mock_data/recorded_interactions.json`: Recorded real AI interactions
- `.libriscribe/mock_data/mock_responses.json`: Custom mock responses

## Error Handling

The system handles various error conditions:

- **TimeoutError**: Raised for `MockScenario.TIMEOUT`
- **Exception**: Raised for `MockScenario.RATE_LIMIT`
- **RuntimeError**: Raised when OpenAI client is not initialized
- **JSON parsing errors**: Handled gracefully with error responses

## Integration with Validation System

```python
from src.libriscribe.validation.ai_mock import AIMockManager, MockScenario
from src.libriscribe.validation.interfaces import ValidatorBase, ValidatorResult

class ContentValidator(ValidatorBase):
    def __init__(self, mock_manager: AIMockManager):
        super().__init__("content_validator", "Content Validator", "1.0.0")
        self.mock_manager = mock_manager
        
    async def validate(self, content, context):
        # Use AI mock system for validation
        ai_response = await self.mock_manager.get_ai_response(
            prompt=f"Validate content: {str(content)[:100]}...",
            validator_id=self.validator_id,
            content_type="chapter",
            scenario=MockScenario.SUCCESS
        )
        
        # Process AI response into validation result
        response_data = json.loads(ai_response.content)
        
        return ValidatorResult(
            validator_id=self.validator_id,
            status=ValidationStatus.COMPLETED,
            findings=self._parse_findings(response_data),
            metrics={
                "quality_score": response_data.get("validation_score", 0),
                "ai_tokens": ai_response.tokens_used,
                "ai_cost": ai_response.cost
            }
        )
```

## Best Practices

1. **Environment Management**: Use environment variables to switch between mock and real AI modes
2. **Cost Monitoring**: Track AI usage and costs in real AI mode
3. **Recording Strategy**: Record comprehensive test data during development
4. **Testing Strategy**: Test all scenarios for comprehensive coverage
5. **Error Handling**: Handle all mock scenarios including timeouts and failures

## See Also

- [AI Testing Best Practices](ai_testing_best_practices.md)
- [AI Mock System Usage Examples](../examples/ai_mock_system_usage.py)
- [Validation System Documentation](validation_system.md)