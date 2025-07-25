# LibriScribe Validation System Documentation

## Overview

The LibriScribe Validation System provides comprehensive validation of both generated book content and the underlying LibriScribe system code before publishing. The system ensures that AI-generated books meet quality standards, the LibriScribe platform maintains code quality, and the publishing process adheres to industry best practices.

## Architecture

The validation system follows a modular, plugin-based architecture with the following key components:

- **ValidationEngine**: Core orchestration engine that manages validation workflows
- **ValidatorBase**: Abstract base class for all validators
- **ValidationInterface**: Main API interface for external systems
- **ValidationConfig**: Configuration management system
- **ResourceManager**: Handles workspace isolation and resource management
- **AIUsageTracker**: Tracks AI consumption and costs

## Core Interfaces

### ValidationInterface

The main entry point for external systems to interact with the validation system.

```python
from libriscribe.validation import ValidationInterface, ValidationConfig

# Initialize validation interface
config = ValidationConfig(project_id="my_book_project")
validator = ValidationInterface(config)

# Validate a complete project
result = await validator.validate_project(
    knowledge_base_path="projects/my_book/project_data.json",
    project_id="my_book_project"
)

# Check validation status
if result.status == ValidationStatus.NEEDS_HUMAN_REVIEW:
    print(f"Human review required. Quality score: {result.overall_quality_score}")
    print(f"Findings: {len(result.validator_results)}")
```

### ValidationEngine

Core engine that orchestrates validation processes and manages validator lifecycle.

```python
from libriscribe.validation import ValidationEngineImpl, ValidationConfig

# Initialize engine
engine = ValidationEngineImpl()
config = ValidationConfig(project_id="my_project")
await engine.initialize(config)

# Register validators
from libriscribe.validation.validators import ContentValidator
content_validator = ContentValidator()
await engine.register_validator(content_validator)

# Run validation
result = await engine.validate_project(project_data, "my_project")
```

### ValidatorBase

Abstract base class for implementing custom validators with comprehensive lifecycle management.

```python
from libriscribe.validation import ValidatorBase, ValidatorResult, ValidationStatus, Finding, FindingType, Severity

class CustomValidator(ValidatorBase):
    def __init__(self):
        super().__init__("custom_validator", "Custom Validator", "1.0.0")
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize validator with configuration"""
        self.config = config
        self.is_initialized = True
        
        # Configure validation rules
        self.configure_validation_rules({
            "min_quality_score": config.get("min_quality_score", 70.0),
            "check_grammar": config.get("check_grammar", True)
        })
        
        # Configure quality thresholds
        self.configure_quality_thresholds({
            "human_review": config.get("human_review_threshold", 75.0),
            "grammar_score": config.get("grammar_threshold", 80.0)
        })
    
    async def validate(self, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        """Perform validation on content"""
        findings = []
        
        # Perform validation logic
        quality_score = self._calculate_quality_score(content)
        
        if quality_score < self.get_validation_rule("min_quality_score", 70.0):
            finding = self.create_finding(
                finding_type=FindingType.CONTENT_QUALITY,
                severity=Severity.MEDIUM,
                title="Quality Below Threshold",
                message=f"Content quality score {quality_score} below minimum {self.get_validation_rule('min_quality_score')}",
                remediation="Review and improve content quality",
                confidence=0.9
            )
            findings.append(finding)
        
        return ValidatorResult(
            validator_id=self.validator_id,
            status=ValidationStatus.COMPLETED,
            findings=findings,
            metrics={"quality_score": quality_score}
        )
    
    def get_supported_content_types(self) -> List[str]:
        """Return supported content types"""
        return ["chapter", "manuscript"]
    
    async def pre_validation_hook(self, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-validation processing"""
        # Add preprocessing logic
        context["preprocessed_at"] = datetime.now()
        return context
    
    async def post_validation_hook(self, result: ValidatorResult, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        """Post-validation processing"""
        # Check if human review is needed
        if result.metrics.get("quality_score", 100) < self.get_quality_threshold("human_review"):
            result.metadata["human_review_recommended"] = True
        return result
    
    def _calculate_quality_score(self, content: Any) -> float:
        """Calculate quality score for content"""
        # Implementation specific logic
        return 85.0
```

## Data Models

### ValidationResult

Complete validation result containing all validator outputs and aggregated metrics.

```python
@dataclass
class ValidationResult:
    validation_id: str              # Unique validation identifier
    project_id: str                 # Project identifier
    status: ValidationStatus        # Overall validation status
    overall_quality_score: float    # Aggregated quality score (0-100)
    human_review_required: bool     # Whether human review is needed
    validator_results: Dict[str, ValidatorResult]  # Results from each validator
    summary: Dict[str, Any]         # Aggregated summary metrics
    total_execution_time: float     # Total validation time in seconds
    total_ai_usage: Dict[str, Any]  # Aggregated AI usage metrics
    timestamp: datetime             # Validation timestamp
    metadata: Dict[str, Any]        # Additional metadata
```

### Finding

Individual validation finding with location and remediation information.

```python
@dataclass
class Finding:
    finding_id: str                 # Unique finding identifier
    validator_id: str               # Validator that generated the finding
    type: FindingType              # Type of finding (content_quality, security, etc.)
    severity: Severity             # Severity level (info, low, medium, high, critical)
    title: str                     # Short finding title
    message: str                   # Detailed finding message
    location: Optional[ContentLocation]  # Location in content
    remediation: Optional[str]     # Suggested remediation
    confidence: float              # Confidence score (0.0-1.0)
    metadata: Dict[str, Any]       # Additional finding metadata
    timestamp: datetime            # Finding timestamp
```

### ValidationConfig

Configuration object for customizing validation behavior.

```python
@dataclass
class ValidationConfig:
    # Core settings
    project_id: str                           # Project identifier
    validation_rules: Dict[str, Any]          # Custom validation rules
    quality_thresholds: Dict[str, float]      # Quality score thresholds
    human_review_threshold: float = 70.0      # Threshold for human review
    
    # Validator settings
    enabled_validators: List[str]             # List of enabled validators
    validator_configs: Dict[str, Dict[str, Any]]  # Per-validator configuration
    
    # AI settings
    ai_mock_enabled: bool = False             # Enable AI mocking for testing
    ai_usage_tracking: bool = True            # Track AI usage and costs
    litellm_config: Dict[str, Any]           # LiteLLM configuration
    
    # Processing settings
    parallel_processing: bool = True          # Enable parallel validation
    max_parallel_requests: int = 100         # Maximum parallel requests
    request_timeout: int = 1200              # Request timeout (20 minutes)
    chunk_size_tokens: int = 50000           # Token chunk size for large content
    
    # Output settings
    output_formats: List[str]                # Report output formats
    report_template: Optional[str]           # Custom report template
    
    # Workflow integration
    auto_validate_chapters: bool = True      # Auto-validate chapters
    auto_validate_manuscript: bool = True    # Auto-validate full manuscript
    fail_fast: bool = True                   # Stop on first critical error
    
    # Resource management
    temp_directory: Optional[str]            # Custom temp directory
    cleanup_on_completion: bool = True       # Cleanup temp files
    
    # Monitoring
    health_check_enabled: bool = True        # Enable health checks
    metrics_collection: bool = True          # Collect performance metrics
```

## Configuration Management

### ValidationConfigManager

Manages loading and customization of validation configurations with support for genre-specific settings and project overrides.

```python
from libriscribe.validation import ValidationConfigManager

# Initialize config manager
config_manager = ValidationConfigManager(config_dir=".libriscribe")

# Load configuration for a project
config = config_manager.load_config(
    project_id="my_book",
    genre="fiction"  # Apply fiction-specific settings
)

# Update validation rules
updated_config = config_manager.update_validation_rules(
    project_id="my_book",
    rules={
        "quality_thresholds": {
            "tone_consistency": 85.0,
            "content_quality": 80.0
        },
        "validator_configs": {
            "content_validator": {
                "check_character_consistency": True,
                "max_chunk_size": 40000
            }
        }
    }
)

# Save project-specific configuration
config_manager.save_project_config("my_book", updated_config)

# Get available genre configurations
genre_configs = config_manager.get_genre_configs()
print("Available genres:", list(genre_configs.keys()))
```

### Genre-Specific Configurations

The system supports genre-specific validation rules:

- **Fiction**: Enhanced character consistency and narrative flow validation
- **Non-Fiction**: Strict fact-checking and citation validation
- **Children**: Age-appropriate content filtering and reading level checks
- **Technical**: Code example validation and technical accuracy checks

## Validator Lifecycle Management

The enhanced `ValidatorBase` class provides comprehensive lifecycle management with hooks for customizing validation behavior:

### Lifecycle Hooks

```python
class AdvancedValidator(ValidatorBase):
    async def pre_validation_hook(self, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Called before validation starts"""
        # Preprocess content, add context
        context["start_time"] = datetime.now()
        context["content_length"] = len(str(content))
        return context
    
    async def post_validation_hook(self, result: ValidatorResult, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        """Called after validation completes"""
        # Post-process results, add metadata
        execution_time = (datetime.now() - context["start_time"]).total_seconds()
        result.metadata["execution_time"] = execution_time
        
        # Check if human review is needed
        if self.should_flag_for_human_review(result.metrics.get("quality_score", 100)):
            result.metadata["human_review_required"] = True
        
        return result
    
    async def on_validation_error(self, error: Exception, content: Any, context: Dict[str, Any]) -> Optional[ValidatorResult]:
        """Called when validation encounters an error"""
        if isinstance(error, ConnectionError):
            # Implement fallback validation
            return ValidatorResult(
                validator_id=self.validator_id,
                status=ValidationStatus.COMPLETED,
                findings=[self.create_finding(
                    finding_type=FindingType.SYSTEM_ERROR,
                    severity=Severity.LOW,
                    title="Fallback Validation Used",
                    message="Primary validation failed, used fallback method"
                )]
            )
        return None  # Re-raise other errors
```

### Configuration Management

```python
# Dynamic configuration
validator = CustomValidator()
await validator.initialize({})

# Configure validation rules
validator.configure_validation_rules({
    "min_word_count": 1000,
    "check_spelling": True,
    "require_citations": False
})

# Configure quality thresholds
validator.configure_quality_thresholds({
    "human_review": 70.0,
    "grammar_score": 85.0,
    "readability_score": 75.0
})

# Use configuration in validation
min_words = validator.get_validation_rule("min_word_count", 500)
grammar_threshold = validator.get_quality_threshold("grammar_score", 80.0)
```

### Helper Methods

```python
class ContentValidator(ValidatorBase):
    async def validate(self, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        findings = []
        
        # Use helper method to create findings
        if self._has_grammar_issues(content):
            finding = self.create_finding(
                finding_type=FindingType.CONTENT_QUALITY,
                severity=Severity.MEDIUM,
                title="Grammar Issues Detected",
                message="Multiple grammar issues found in content",
                remediation="Review and correct grammar errors",
                confidence=0.85,
                metadata={"issue_count": 5}
            )
            findings.append(finding)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(content)
        
        # Check if human review is needed
        if self.should_flag_for_human_review(quality_score):
            findings.append(self.create_finding(
                finding_type=FindingType.CONTENT_QUALITY,
                severity=Severity.HIGH,
                title="Human Review Required",
                message=f"Quality score {quality_score} below threshold",
                remediation="Content requires human review before publishing"
            ))
        
        return ValidatorResult(
            validator_id=self.validator_id,
            status=ValidationStatus.COMPLETED,
            findings=findings,
            metrics={"quality_score": quality_score}
        )
```

## Usage Examples

### Basic Project Validation

```python
import asyncio
from libriscribe.validation import ValidationInterface, ValidationConfig

async def validate_book_project():
    # Configure validation
    config = ValidationConfig(
        project_id="my_fantasy_novel",
        enabled_validators=[
            "content_validator",
            "publishing_standards_validator",
            "quality_originality_validator"
        ],
        quality_thresholds={
            "overall": 75.0,
            "tone_consistency": 80.0,
            "outline_adherence": 85.0
        },
        human_review_threshold=70.0
    )
    
    # Initialize validation interface
    validator = ValidationInterface(config)
    
    # Validate project
    result = await validator.validate_project(
        knowledge_base_path="projects/my_fantasy_novel/project_data.json"
    )
    
    # Process results
    print(f"Validation Status: {result.status}")
    print(f"Quality Score: {result.overall_quality_score}")
    print(f"Human Review Required: {result.human_review_required}")
    
    # Check findings by severity
    for validator_id, validator_result in result.validator_results.items():
        critical_findings = [
            f for f in validator_result.findings 
            if f.severity == Severity.CRITICAL
        ]
        if critical_findings:
            print(f"Critical issues in {validator_id}: {len(critical_findings)}")
            for finding in critical_findings:
                print(f"  - {finding.title}: {finding.message}")

# Run validation
asyncio.run(validate_book_project())
```

### Chapter-Level Validation

```python
async def validate_chapter():
    config = ValidationConfig(project_id="my_book")
    validator = ValidationInterface(config)
    
    # Validate individual chapter
    result = await validator.validate_chapter(
        chapter_path="projects/my_book/chapter_1.md",
        project_context="projects/my_book/project_data.json",
        project_id="my_book"
    )
    
    # Check chapter-specific issues
    if result.status == ValidationStatus.NEEDS_HUMAN_REVIEW:
        print("Chapter needs review:")
        for validator_id, validator_result in result.validator_results.items():
            for finding in validator_result.findings:
                if finding.location and finding.location.content_type == "chapter":
                    print(f"  Line {finding.location.line_number}: {finding.message}")

asyncio.run(validate_chapter())
```

### Custom Validator Implementation

```python
from libriscribe.validation import ValidatorBase, ValidatorResult, Finding, FindingType, Severity

class DialogueQualityValidator(ValidatorBase):
    """Custom validator for dialogue quality in fiction"""
    
    def __init__(self):
        super().__init__(
            validator_id="dialogue_quality_validator",
            name="Dialogue Quality Validator",
            version="1.0.0"
        )
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        self.min_dialogue_ratio = config.get("min_dialogue_ratio", 0.2)
        self.check_dialogue_tags = config.get("check_dialogue_tags", True)
    
    async def validate(self, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        findings = []
        
        # Analyze dialogue content
        dialogue_ratio = self._calculate_dialogue_ratio(content)
        
        if dialogue_ratio < self.min_dialogue_ratio:
            findings.append(Finding(
                validator_id=self.validator_id,
                type=FindingType.CONTENT_QUALITY,
                severity=Severity.MEDIUM,
                title="Low Dialogue Ratio",
                message=f"Dialogue ratio is {dialogue_ratio:.1%}, below recommended {self.min_dialogue_ratio:.1%}",
                remediation="Consider adding more dialogue to improve reader engagement"
            ))
        
        # Check dialogue tag variety
        if self.check_dialogue_tags:
            tag_issues = self._check_dialogue_tags(content)
            findings.extend(tag_issues)
        
        return ValidatorResult(
            validator_id=self.validator_id,
            status=ValidationStatus.COMPLETED,
            findings=findings,
            metrics={
                "dialogue_ratio": dialogue_ratio,
                "dialogue_tags_checked": self.check_dialogue_tags
            }
        )
    
    def get_supported_content_types(self) -> List[str]:
        return ["chapter", "scene", "manuscript"]
    
    def _calculate_dialogue_ratio(self, content: str) -> float:
        # Implementation for calculating dialogue ratio
        pass
    
    def _check_dialogue_tags(self, content: str) -> List[Finding]:
        # Implementation for checking dialogue tag variety
        pass

# Register custom validator
async def use_custom_validator():
    engine = ValidationEngineImpl()
    config = ValidationConfig(project_id="fiction_book")
    await engine.initialize(config)
    
    # Register custom validator
    dialogue_validator = DialogueQualityValidator()
    await engine.register_validator(dialogue_validator)
    
    # Use in validation
    result = await engine.validate_project(project_data, "fiction_book")
```

### AI Usage Tracking

```python
from libriscribe.validation import AIUsageTracker

async def track_ai_usage():
    tracker = AIUsageTracker()
    
    # Track AI request
    await tracker.track_request(
        project_id="my_book",
        validator_id="content_validator",
        tokens_used=1500,
        cost=0.03,
        model="gpt-4"
    )
    
    # Get usage report
    usage_report = await tracker.get_usage_report("my_book")
    print(f"Total tokens used: {usage_report['total_tokens']}")
    print(f"Total cost: ${usage_report['total_cost']:.2f}")
    print(f"Requests by validator: {usage_report['by_validator']}")
```

### Health Monitoring

```python
from libriscribe.validation import HealthMonitor

async def check_system_health():
    monitor = HealthMonitor()
    
    # Get health status
    health = await monitor.get_health_status()
    print(f"System Status: {health['status']}")
    print(f"AI Connectivity: {health['ai_connectivity']}")
    
    # Get detailed metrics
    metrics = await monitor.get_metrics()
    print(f"Active validations: {metrics['active_validations']}")
    print(f"Memory usage: {metrics['memory_usage_mb']} MB")
    print(f"CPU usage: {metrics['cpu_usage_percent']}%")
```

## Error Handling

The validation system provides comprehensive error handling with specific exception types:

```python
from libriscribe.validation import (
    ValidationError,
    ValidatorNotFoundError,
    ConfigurationError,
    ResourceError
)

async def handle_validation_errors():
    try:
        config = ValidationConfig(project_id="test_project")
        validator = ValidationInterface(config)
        result = await validator.validate_project("invalid_path.json")
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        # Handle configuration issues
        
    except ValidatorNotFoundError as e:
        print(f"Validator not found: {e}")
        # Handle missing validator
        
    except ResourceError as e:
        print(f"Resource error: {e}")
        # Handle resource management issues
        
    except ValidationError as e:
        print(f"General validation error: {e}")
        # Handle general validation errors
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle unexpected errors
```

## Integration with LibriScribe Workflow

The validation system integrates seamlessly with the LibriScribe book generation workflow:

```python
# In your LibriScribe workflow
from libriscribe.validation import ValidationInterface, ValidationConfig

async def integrated_book_generation():
    # Generate book content using LibriScribe agents
    project = generate_book_project()
    
    # Configure validation
    config = ValidationConfig(
        project_id=project.id,
        auto_validate_chapters=True,
        auto_validate_manuscript=True,
        human_review_threshold=75.0
    )
    
    validator = ValidationInterface(config)
    
    # Validate each chapter as it's generated
    for chapter_num in range(1, project.num_chapters + 1):
        chapter_result = await validator.validate_chapter(
            chapter_path=f"projects/{project.id}/chapter_{chapter_num}.md",
            project_context=f"projects/{project.id}/project_data.json",
            project_id=project.id
        )
        
        if chapter_result.status == ValidationStatus.NEEDS_HUMAN_REVIEW:
            # Pause for human review
            await request_human_review(chapter_result)
    
    # Final manuscript validation
    final_result = await validator.validate_project(
        knowledge_base_path=f"projects/{project.id}/project_data.json",
        project_id=project.id
    )
    
    if final_result.status == ValidationStatus.COMPLETED:
        print("Book ready for publishing!")
    else:
        print("Additional review required before publishing")
```

## Testing and Development

### AI Mock System

The validation system includes a comprehensive AI Mock System for testing without consuming expensive AI resources. See [AI Mock System Documentation](ai_mock_system.md) for complete details.

#### Basic Mock Usage

```python
from libriscribe.validation.ai_mock import AIMockManager, MockScenario

# Initialize mock manager
mock_manager = AIMockManager()

# Get mock response for testing
response = await mock_manager.get_ai_response(
    prompt="Validate this content...",
    validator_id="content_validator",
    content_type="chapter",
    scenario=MockScenario.SUCCESS,
    use_mock=True
)
```

#### Configuration-Driven Mocking

```python
# Enable AI mocking in configuration
config = ValidationConfig(
    project_id="test_project",
    ai_mock_enabled=True,
    validator_configs={
        "content_validator": {
            "mock_scenario": "success",  # or "failure", "timeout", "high_quality", "low_quality"
            "mock_data_dir": ".libriscribe/test_data"
        }
    }
)

# Run validation with mocked AI responses
validator = ValidationInterface(config)
result = await validator.validate_project("test_project.json")
```

#### Comprehensive Test Suite

```python
# Create and run comprehensive test suite
validators = ["content_validator", "quality_validator", "publishing_validator"]
test_suite = await mock_manager.create_test_suite(validators)
results = await mock_manager.run_test_suite(test_suite)

print(f"Tests run: {results['total_tests']}")
print(f"Coverage: {results['coverage_report']['coverage_percentage']:.1f}%")
```

#### Record and Playback

```python
# Record real AI interactions for later playback
real_response = await mock_manager.get_ai_response(
    prompt="Real validation prompt",
    validator_id="content_validator",
    content_type="chapter",
    use_mock=False  # Record real AI interaction
)

# Later, same request uses recorded response
cached_response = await mock_manager.get_ai_response(
    prompt="Real validation prompt",  # Same prompt
    validator_id="content_validator",
    content_type="chapter", 
    use_mock=True  # Uses recorded response
)
```

### Unit Testing

```python
import pytest
from libriscribe.validation import ValidationEngineImpl, ValidationConfig

@pytest.mark.asyncio
async def test_validation_engine():
    engine = ValidationEngineImpl()
    config = ValidationConfig(project_id="test")
    
    await engine.initialize(config)
    
    # Test validator registration
    validator = MockValidator()
    await engine.register_validator(validator)
    
    validators = await engine.get_registered_validators()
    assert len(validators) == 1
    assert validators[0]["id"] == "mock_validator"

@pytest.mark.asyncio
async def test_validation_result_aggregation():
    # Test result aggregation logic
    pass
```

## Performance Considerations

- **Parallel Processing**: Enable `parallel_processing=True` for better performance
- **Chunking**: Large manuscripts are automatically chunked based on `chunk_size_tokens`
- **Resource Management**: Temporary files are automatically cleaned up
- **AI Usage Optimization**: Track and optimize AI API calls to minimize costs

## Best Practices

1. **Configuration Management**: Use project-specific configurations for different book types
2. **Error Handling**: Always handle validation errors gracefully in your workflow
3. **Human Review**: Set appropriate thresholds for human review based on your quality standards
4. **Testing**: Use the mock AI system for development and testing
5. **Monitoring**: Enable health checks and metrics collection for production use
6. **Resource Cleanup**: Ensure temporary resources are properly cleaned up

## Troubleshooting

### Common Issues

1. **Configuration Errors**: Check that all required configuration values are set
2. **Validator Registration**: Ensure validators are properly registered before use
3. **AI Connectivity**: Verify LiteLLM configuration and API keys
4. **Resource Limits**: Monitor memory and disk usage for large projects
5. **Timeout Issues**: Adjust `request_timeout` for complex validations

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run validation with debug output
result = await validator.validate_project("project.json")
```

## API Reference

For complete API documentation, see the individual module documentation:

- [Interfaces](src/libriscribe/validation/interfaces.py)
- [Engine](src/libriscribe/validation/engine.py)
- [Configuration](src/libriscribe/validation/config.py)
- [Validators](src/libriscribe/validation/validators/)
- [Utilities](src/libriscribe/validation/utils/)