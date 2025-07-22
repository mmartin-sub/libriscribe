# AI Mock System Documentation

## Overview

The AI Mock System provides seamless switching between real AI and mock responses for the LibriScribe validation system. It uses the **OpenAI SDK** with **LiteLLM configured via .env** (transparent to the service) and **API key-based switching** for automatic mode detection.

## 🔑 Key Features

1. **OpenAI SDK Integration**: Uses standard OpenAI SDK with LiteLLM proxy configured via environment variables
2. **API Key-Based Switching**: Empty `OPENAI_API_KEY` = mock mode, set key = real AI mode
3. **Live Response Recording**: Automatically records real AI responses for future mock use
4. **Transparent Operation**: Same code works in both mock and real AI modes
5. **Cost Tracking**: Monitors token usage and API costs
6. **Scenario Testing**: Comprehensive testing with different response scenarios

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Mock Mode (Development/Testing)
# Leave OPENAI_API_KEY empty or unset
unset OPENAI_API_KEY

# Real AI Mode (Production/Live Recording)
export OPENAI_API_KEY="your-openai-api-key"

# Optional: Configure LiteLLM Proxy
export OPENAI_BASE_URL="https://your-litellm-proxy.com/v1"
```

### 2. Basic Usage

```python
from src.libriscribe.validation.ai_mock import AIMockManager

# Create manager (automatically detects mode based on API key)
mock_manager = AIMockManager()

# Get AI response (works in both mock and real modes)
response = await mock_manager.get_ai_response(
    prompt="Analyze this chapter for content quality",
    validator_id="content_validator",
    content_type="chapter",
    model="gpt-4"
)

# Process response (same code for both modes)
print(f"Tokens used: {response.tokens_used}")
print(f"Cost: ${response.cost:.4f}")
print(f"Content: {response.content}")
```

## 🔄 How It Works

### Automatic Mode Detection

The system automatically determines whether to use mock or real AI based on the `OPENAI_API_KEY` environment variable:

```python
class AIMockManager:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.use_mock_mode = not bool(self.openai_api_key.strip())
        
        if not self.use_mock_mode:
            # Initialize OpenAI client with LiteLLM proxy
            self.openai_client = AsyncOpenAI(
                api_key=self.openai_api_key,
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            )
```

### Real AI Integration

When `OPENAI_API_KEY` is set, the system uses the OpenAI SDK:

```python
async def _call_real_ai(self, prompt, validator_id, content_type, model):
    response = await self.openai_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system", 
                "content": f"You are a {validator_id} for LibriScribe. Respond with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=2000
    )
    
    # Automatically record for future mock use
    await self._record_interaction(prompt, response, validator_id, content_type)
    
    return response
```

### Mock Response Generation

When `OPENAI_API_KEY` is empty, the system generates mock responses:

```python
async def _get_mock_response(self, prompt, validator_id, content_type, scenario):
    # First, try to find recorded interaction
    request_hash = self._generate_request_hash(prompt, validator_id, content_type)
    if request_hash in self.recorded_interactions:
        return self.recorded_interactions[request_hash].response
    
    # Otherwise, generate scenario-based response
    return await self._generate_scenario_response(scenario)
```

## 📹 Live Response Recording

### Automatic Recording

When using real AI, responses are automatically recorded for future mock use:

```python
# Real AI call automatically records response
response = await mock_manager.get_ai_response(
    prompt="Validate this content",
    validator_id="content_validator",
    content_type="chapter",
    model="gpt-4"
)
# Response is saved to .libriscribe/mock_data/recorded_interactions.json
```

### Bulk Recording

You can populate mock data from multiple live responses:

```python
# Define prompts to record
prompts = [
    {
        "prompt": "Analyze chapter for tone consistency",
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

# Record all prompts
results = await mock_manager.populate_mock_mappings_from_live(
    prompts=prompts,
    model="gpt-4"
)

print(f"Recorded {results['successful_recordings']} interactions")
print(f"Total cost: ${sum(r['cost'] for r in results['recordings']):.4f}")
```

### Recording Results

```json
{
  "total_prompts": 2,
  "successful_recordings": 2,
  "failed_recordings": 0,
  "recordings": [
    {
      "prompt": "Analyze chapter for tone consistency",
      "validator_id": "content_validator",
      "content_type": "chapter",
      "tokens_used": 245,
      "cost": 0.00735,
      "expected_scenario": "success",
      "recorded_at": "2024-01-15T10:30:00"
    }
  ]
}
```

## 🎭 Mock Scenarios

The system supports comprehensive scenario testing:

```python
from src.libriscribe.validation.ai_mock import MockScenario

scenarios = [
    MockScenario.SUCCESS,           # Normal successful validation
    MockScenario.HIGH_QUALITY,      # High quality content (>90% score)
    MockScenario.LOW_QUALITY,       # Low quality content (<70% score)
    MockScenario.FAILURE,           # Complete validation failure
    MockScenario.TIMEOUT,           # AI timeout simulation
    MockScenario.RATE_LIMIT,        # Rate limiting simulation
    MockScenario.INVALID_RESPONSE,  # Malformed JSON response
    MockScenario.PARTIAL_FAILURE,   # Some checks pass, some fail
    MockScenario.EDGE_CASE          # Edge cases (empty content, etc.)
]

# Test specific scenario
response = await mock_manager.get_ai_response(
    prompt="Test content",
    validator_id="content_validator",
    content_type="chapter",
    scenario=MockScenario.LOW_QUALITY  # Only used in mock mode
)
```

### Scenario Response Examples

**SUCCESS Scenario:**
```json
{
  "tone_consistency_score": 85.0,
  "outline_adherence_score": 90.0,
  "quality_score": 87.5,
  "findings": [
    {
      "type": "tone_consistency",
      "severity": "low",
      "message": "Minor tone variation in chapter 3"
    }
  ]
}
```

**LOW_QUALITY Scenario:**
```json
{
  "validation_score": 65.0,
  "quality_score": 62.0,
  "status": "needs_review",
  "findings": [
    {
      "type": "content_quality",
      "severity": "high",
      "message": "Content quality below threshold"
    }
  ]
}
```

**FAILURE Scenario:**
```json
{
  "error": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "status": "failed"
}
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required for real AI mode
OPENAI_API_KEY=your-openai-api-key

# Optional: LiteLLM proxy endpoint
OPENAI_BASE_URL=https://your-litellm-proxy.com/v1

# Optional: Default model
OPENAI_DEFAULT_MODEL=gpt-4
```

### LiteLLM Proxy Setup

The system works transparently with LiteLLM proxy. Configure your LiteLLM proxy and set the base URL:

```yaml
# litellm_config.yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: your-actual-openai-key
      
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: your-actual-openai-key
```

```bash
# Start LiteLLM proxy
litellm --config litellm_config.yaml --port 8000

# Configure LibriScribe to use proxy
export OPENAI_API_KEY="your-proxy-auth-key"
export OPENAI_BASE_URL="http://localhost:8000/v1"
```

### Validation Config Integration

```python
from src.libriscribe.validation import ValidationConfig

# Configuration automatically detects mock/real mode
config = ValidationConfig(
    project_id="my_project",
    validator_configs={
        "content_validator": {
            "openai_model": "gpt-4",
            "temperature": 0.1,
            "max_tokens": 2000
        }
    }
)
```

## 🧪 Testing Integration

### Test Framework Usage

```python
from src.libriscribe.validation.testing import ValidationTestFramework

# Create test framework
mock_manager = AIMockManager()
test_framework = ValidationTestFramework(mock_manager)

# Generate comprehensive test suite
test_cases = await test_framework.create_comprehensive_test_suite(
    validators=["content_validator", "publishing_standards_validator"],
    content_types=["chapter", "manuscript"]
)

# Run tests (automatically uses mock mode if no API key)
results = await test_framework.run_test_suite(test_cases)
```

### Validator Integration

```python
from src.libriscribe.validation.interfaces import ValidatorBase

class ContentValidator(ValidatorBase):
    def __init__(self, mock_manager):
        super().__init__("content_validator", "Content Validator", "1.0.0")
        self.mock_manager = mock_manager
        
    async def validate(self, content, context):
        # Call AI (automatically uses mock or real based on API key)
        ai_response = await self.mock_manager.get_ai_response(
            prompt=f"Analyze content quality: {content}",
            validator_id=self.validator_id,
            content_type="chapter",
            model="gpt-4"
        )
        
        # Process response (same code for mock or real)
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

## 📊 Monitoring and Statistics

### Usage Statistics

```python
# Get comprehensive usage statistics
stats = mock_manager.get_usage_stats()

print(f"Mock calls: {stats['mock_calls']}")
print(f"Real AI calls: {stats['real_calls']}")
print(f"Live recordings: {stats['live_recordings']}")
print(f"Total cost: ${sum(r.cost for r in recorded_responses):.4f}")
```

### Cost Tracking

The system automatically tracks costs for real AI calls:

```python
# Cost calculation based on model and tokens
def _calculate_cost(self, model: str, tokens_used: int) -> float:
    pricing = {
        "gpt-4": 0.03,           # $0.03 per 1K tokens
        "gpt-4-turbo": 0.01,     # $0.01 per 1K tokens
        "gpt-3.5-turbo": 0.002,  # $0.002 per 1K tokens
    }
    price_per_1k = pricing.get(model, 0.01)
    return (tokens_used / 1000) * price_per_1k
```

### Coverage Reporting

```python
from src.libriscribe.validation.testing import CoverageReporter

coverage_reporter = CoverageReporter()
coverage_report = await coverage_reporter.generate_coverage_report(test_results)

print(f"Overall coverage: {coverage_report.overall_coverage.coverage_percentage:.1f}%")
print(f"Validators tested: {len(coverage_report.validator_coverage)}")
print(f"Scenarios covered: {len(coverage_report.scenario_coverage)}")
```

## 🔧 Advanced Usage

### Custom Mock Responses

You can add custom mock responses for specific prompts:

```python
# Add custom mock response
custom_response = MockResponse(
    content=json.dumps({
        "validation_score": 95.0,
        "status": "excellent",
        "custom_field": "custom_value"
    }),
    model="gpt-4",
    tokens_used=150,
    cost=0.0045,
    scenario=MockScenario.SUCCESS
)

# Save to recorded interactions
await mock_manager._record_interaction(
    prompt="Your custom prompt",
    response=custom_response,
    validator_id="custom_validator",
    content_type="custom_type"
)
```

### Batch Processing

```python
# Process multiple prompts efficiently
prompts = [
    {"prompt": "Validate chapter 1", "validator_id": "content_validator"},
    {"prompt": "Validate chapter 2", "validator_id": "content_validator"},
    {"prompt": "Check manuscript", "validator_id": "publishing_validator"}
]

responses = []
for prompt_config in prompts:
    response = await mock_manager.get_ai_response(
        prompt=prompt_config["prompt"],
        validator_id=prompt_config["validator_id"],
        content_type="chapter",
        model="gpt-4"
    )
    responses.append(response)

total_cost = sum(r.cost for r in responses)
total_tokens = sum(r.tokens_used for r in responses)
```

### Error Handling

```python
try:
    response = await mock_manager.get_ai_response(
        prompt="Your prompt",
        validator_id="validator_id",
        content_type="chapter",
        model="gpt-4"
    )
except Exception as e:
    if "rate limit" in str(e).lower():
        # Handle rate limiting
        await asyncio.sleep(60)
        # Retry logic
    elif "timeout" in str(e).lower():
        # Handle timeout
        # Use cached response or fallback
    else:
        # Handle other errors
        logger.error(f"AI call failed: {e}")
```

## 🚀 Best Practices

### 1. Environment Management

```bash
# Development
export OPENAI_API_KEY=""  # Empty for mock mode

# Testing with live recording
export OPENAI_API_KEY="sk-test-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"

# Production with LiteLLM
export OPENAI_API_KEY="proxy-auth-key"
export OPENAI_BASE_URL="https://your-proxy.com/v1"
```

### 2. Cost Management

```python
# Monitor costs in real AI mode
if not mock_manager.use_mock_mode:
    stats = mock_manager.get_usage_stats()
    total_cost = sum(r.cost for r in recorded_responses)
    
    if total_cost > 10.0:  # $10 threshold
        logger.warning(f"High AI usage cost: ${total_cost:.2f}")
```

### 3. Recording Strategy

```python
# Record comprehensive test data
recording_prompts = [
    # Success cases
    {"prompt": "High quality content", "expected_scenario": "high_quality"},
    {"prompt": "Normal content", "expected_scenario": "success"},
    
    # Failure cases  
    {"prompt": "Poor quality content", "expected_scenario": "low_quality"},
    {"prompt": "Invalid content", "expected_scenario": "failure"},
    
    # Edge cases
    {"prompt": "", "expected_scenario": "edge_case"},
    {"prompt": "A" * 10000, "expected_scenario": "edge_case"}
]

# Record during development phase
if not mock_manager.use_mock_mode:
    await mock_manager.populate_mock_mappings_from_live(recording_prompts)
```

### 4. Testing Strategy

```python
# Comprehensive testing approach
async def test_validator_with_all_scenarios():
    scenarios = [MockScenario.SUCCESS, MockScenario.FAILURE, MockScenario.LOW_QUALITY]
    
    for scenario in scenarios:
        response = await mock_manager.get_ai_response(
            prompt="Test content",
            validator_id="content_validator",
            content_type="chapter",
            scenario=scenario
        )
        
        # Verify response matches scenario expectations
        assert_scenario_response(response, scenario)
```

## 🔍 Troubleshooting

### Common Issues

**1. "OpenAI client not initialized"**
```bash
# Solution: Set API key
export OPENAI_API_KEY="your-key-here"
```

**2. "Mock mode active - cannot record"**
```bash
# Solution: Provide API key for recording
export OPENAI_API_KEY="your-key-here"
python record_responses.py
unset OPENAI_API_KEY  # Return to mock mode
```

**3. "No recorded interactions found"**
```python
# Solution: Record some interactions first
await mock_manager.populate_mock_mappings_from_live(prompts)
```

**4. Rate limiting errors**
```python
# Solution: Add delays between calls
await asyncio.sleep(1.0)  # 1 second delay
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging
mock_manager = AIMockManager()
response = await mock_manager.get_ai_response(...)
```

## 📚 Examples

See the complete examples in:
- `examples/ai_mock_system_usage.py` - Comprehensive usage demonstration
- `examples/ai_testing_best_practices.py` - Testing best practices
- `docs/ai_testing_best_practices.md` - Detailed best practices guide

## 🎯 Summary

The AI Mock System provides:

1. **Seamless Integration**: Uses OpenAI SDK with LiteLLM proxy (transparent)
2. **Automatic Switching**: API key presence determines mock vs real mode
3. **Live Recording**: Real responses automatically recorded for mock use
4. **Cost Efficiency**: Free, fast mock responses for development/testing
5. **Comprehensive Testing**: Multiple scenarios and edge cases covered
6. **Production Ready**: Robust error handling and monitoring

This system enables efficient development and testing while maintaining compatibility with production AI services.