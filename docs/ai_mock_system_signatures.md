# AI Mock System - Function Signatures

## Complete API Reference

### AIMockManager Class

#### Constructor
```python
def __init__(self, mock_data_dir: Optional[str] = None) -> None
```
Initialize AI Mock Manager with automatic mode detection based on environment variables.

**Parameters:**
- `mock_data_dir` (Optional[str]): Directory for storing mock data files. Defaults to `.libriscribe/mock_data`

**Environment Variables Used:**
- `OPENAI_API_KEY`: If empty/unset, enables mock mode. If set, enables real AI mode.
- `OPENAI_BASE_URL`: Optional LiteLLM proxy URL. Defaults to `https://api.openai.com/v1`

#### Public Methods

##### get_ai_response()
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
Get AI response with automatic mock/real switching based on API key presence.

**Parameters:**
- `prompt` (str): The AI prompt text to send
- `validator_id` (str): Identifier of the validator making the request
- `content_type` (str): Type of content being validated (e.g., "chapter", "manuscript")
- `model` (str): OpenAI model to use. Defaults to "gpt-4"
- `scenario` (Optional[MockScenario]): Mock scenario to use (only applies in mock mode)

**Returns:**
- `MockResponse`: Standardized response structure with content, tokens, cost, etc.

**Raises:**
- `RuntimeError`: If real AI mode is requested but OpenAI client not initialized
- `TimeoutError`: If MockScenario.TIMEOUT is used
- `Exception`: For various mock scenarios (rate limit, etc.)

##### populate_mock_mappings_from_live()
```python
async def populate_mock_mappings_from_live(
    self, 
    prompts: List[Dict[str, Any]],
    model: str = "gpt-4"
) -> Dict[str, Any]
```
Record real AI responses for future mock playback.

**Parameters:**
- `prompts` (List[Dict[str, Any]]): List of prompt configurations, each containing:
  - `prompt` (str): The actual prompt text
  - `validator_id` (str): Validator making the request
  - `content_type` (str): Type of content being validated
  - `expected_scenario` (str): Expected mock scenario for this prompt
- `model` (str): OpenAI model to use for live calls. Defaults to "gpt-4"

**Returns:**
- `Dict[str, Any]`: Results dictionary containing:
  - `total_prompts` (int): Total number of prompts processed
  - `successful_recordings` (int): Number of successful recordings
  - `failed_recordings` (int): Number of failed recordings
  - `recordings` (List[Dict]): List of recording details
  - `errors` (List[str]): List of error messages

##### create_test_suite()
```python
async def create_test_suite(self, validators: List[str]) -> Dict[str, List[MockScenario]]
```
Create comprehensive test suite for specified validators.

**Parameters:**
- `validators` (List[str]): List of validator IDs to create tests for

**Returns:**
- `Dict[str, List[MockScenario]]`: Mapping of validator IDs to list of test scenarios

##### run_test_suite()
```python
async def run_test_suite(self, test_suite: Dict[str, List[MockScenario]]) -> Dict[str, Any]
```
Execute test suite and return comprehensive results.

**Parameters:**
- `test_suite` (Dict[str, List[MockScenario]]): Test suite from `create_test_suite()`

**Returns:**
- `Dict[str, Any]`: Test results containing:
  - `total_tests` (int): Total number of tests run
  - `passed_tests` (int): Number of tests that passed
  - `failed_tests` (int): Number of tests that failed
  - `validator_results` (Dict): Results by validator
  - `scenario_results` (Dict): Results by scenario
  - `coverage_report` (Dict): Coverage metrics

##### get_usage_stats()
```python
def get_usage_stats(self) -> Dict[str, Any]
```
Get comprehensive usage statistics for the mock system.

**Returns:**
- `Dict[str, Any]`: Statistics dictionary containing:
  - `mock_calls` (int): Number of mock AI calls made
  - `real_calls` (int): Number of real AI calls made
  - `scenarios_used` (Dict[str, int]): Count of each scenario used
  - `validators_tested` (List[str]): List of validators tested
  - `recorded_interactions` (int): Number of recorded interactions
  - `mock_coverage` (Dict[str, Any]): Coverage metrics

#### Private Methods

##### _get_mock_response()
```python
async def _get_mock_response(
    self, 
    prompt: str, 
    validator_id: str,
    content_type: str,
    scenario: Optional[MockScenario] = None
) -> MockResponse
```
Internal method to generate mock AI responses.

##### _call_real_ai()
```python
async def _call_real_ai(
    self, 
    prompt: str, 
    validator_id: str, 
    content_type: str, 
    model: str
) -> MockResponse
```
Internal method to call real AI through OpenAI SDK.

##### _generate_scenario_response()
```python
async def _generate_scenario_response(
    self, 
    prompt: str, 
    validator_id: str,
    content_type: str,
    scenario: MockScenario
) -> MockResponse
```
Generate mock response based on specific scenario.

##### _create_success_response()
```python
def _create_success_response(
    self, 
    prompt: str, 
    validator_id: str, 
    content_type: str
) -> MockResponse
```
Create a successful mock response with validator-specific content.

##### _create_high_quality_response()
```python
def _create_high_quality_response(
    self, 
    prompt: str, 
    validator_id: str, 
    content_type: str
) -> MockResponse
```
Create a high-quality mock response (scores > 90%).

##### _create_low_quality_response()
```python
def _create_low_quality_response(
    self, 
    prompt: str, 
    validator_id: str, 
    content_type: str
) -> MockResponse
```
Create a low-quality mock response (scores < 70%).

##### _create_failure_response()
```python
def _create_failure_response(
    self, 
    prompt: str, 
    validator_id: str, 
    content_type: str
) -> MockResponse
```
Create a failure mock response.

##### _create_invalid_response()
```python
def _create_invalid_response(
    self, 
    prompt: str, 
    validator_id: str, 
    content_type: str
) -> MockResponse
```
Create an invalid/malformed mock response for testing error handling.

##### _create_partial_failure_response()
```python
def _create_partial_failure_response(
    self, 
    prompt: str, 
    validator_id: str, 
    content_type: str
) -> MockResponse
```
Create a partial failure mock response.

##### _create_edge_case_response()
```python
def _create_edge_case_response(
    self, 
    prompt: str, 
    validator_id: str, 
    content_type: str
) -> MockResponse
```
Create an edge case mock response.

##### _record_interaction()
```python
async def _record_interaction(
    self, 
    prompt: str, 
    response: MockResponse, 
    validator_id: str,
    content_type: str
) -> None
```
Record AI interaction for future playback.

##### _generate_request_hash()
```python
def _generate_request_hash(
    self, 
    prompt: str, 
    validator_id: str, 
    content_type: str
) -> str
```
Generate consistent hash for request caching.

##### _load_mock_data()
```python
def _load_mock_data(self) -> None
```
Load existing mock data from disk.

##### _save_recorded_interaction()
```python
async def _save_recorded_interaction(self, interaction: RecordedInteraction) -> None
```
Save recorded interaction to disk.

##### _calculate_mock_coverage()
```python
def _calculate_mock_coverage(self) -> Dict[str, Any]
```
Calculate test coverage metrics.

##### _calculate_cost()
```python
def _calculate_cost(self, model: str, tokens_used: int) -> float
```
Calculate approximate cost based on model and token usage.

### Data Classes

#### MockResponse
```python
@dataclass
class MockResponse:
    content: str                     # AI response content (JSON string)
    model: str                       # Model used (e.g., "gpt-4")
    tokens_used: int                 # Token consumption
    cost: float                      # API cost in USD
    confidence: float = 1.0          # Response confidence (0.0-1.0)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
    timestamp: datetime = field(default_factory=datetime.now)  # Response timestamp
    scenario: MockScenario = MockScenario.SUCCESS  # Mock scenario used
```

#### RecordedInteraction
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

### Enums

#### MockScenario
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

## Usage Patterns

### Basic Usage
```python
# Initialize manager (auto-detects mode from environment)
mock_manager = AIMockManager()

# Get AI response (works in both mock and real modes)
response = await mock_manager.get_ai_response(
    prompt="Validate this content",
    validator_id="content_validator",
    content_type="chapter",
    model="gpt-4"
)
```

### Testing with Scenarios
```python
# Test specific scenario
response = await mock_manager.get_ai_response(
    prompt="Test content",
    validator_id="content_validator",
    content_type="chapter",
    scenario=MockScenario.LOW_QUALITY
)
```

### Recording Live Responses
```python
# Set environment variable for real AI mode
os.environ["OPENAI_API_KEY"] = "your-key"

# Record responses for later mock use
prompts = [
    {
        "prompt": "Validate chapter content",
        "validator_id": "content_validator",
        "content_type": "chapter",
        "expected_scenario": "success"
    }
]

results = await mock_manager.populate_mock_mappings_from_live(prompts)
```

### Comprehensive Testing
```python
# Create and run test suite
validators = ["content_validator", "quality_validator"]
test_suite = await mock_manager.create_test_suite(validators)
results = await mock_manager.run_test_suite(test_suite)

# Check coverage
stats = mock_manager.get_usage_stats()
print(f"Coverage: {stats['mock_coverage']['coverage_percentage']:.1f}%")
```

## Error Handling

The system handles various error conditions gracefully:

- **Missing API Key**: Automatically switches to mock mode
- **OpenAI SDK Unavailable**: Falls back to mock mode with warning
- **Network Errors**: Returns error response in standard format
- **Invalid JSON**: Handles malformed responses for testing
- **Timeout Scenarios**: Simulates AI timeouts for testing
- **Rate Limiting**: Simulates API rate limits for testing

## File System Integration

The system automatically manages files in the mock data directory:

- `recorded_interactions.json`: Stores recorded real AI interactions
- `mock_responses.json`: Stores custom mock responses
- Automatic cleanup and persistence of interaction data
- Thread-safe file operations for concurrent access