# LibriScribe Validation Interfaces API Documentation

## Overview

The `src/libriscribe/validation/interfaces.py` module defines the core interfaces and data structures for the LibriScribe validation system. This module establishes system boundaries and enables pluggable validation components with comprehensive lifecycle management.

## Core Classes and Interfaces

### Enums

#### ValidationStatus
```python
class ValidationStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    ERROR = "error"
```

Status enumeration for validation processes and individual validators.

#### FindingType
```python
class FindingType(Enum):
    CONTENT_QUALITY = "content_quality"
    TONE_CONSISTENCY = "tone_consistency"
    OUTLINE_ADHERENCE = "outline_adherence"
    SECURITY_VULNERABILITY = "security_vulnerability"
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    COMPLIANCE = "compliance"
    PUBLISHING_STANDARD = "publishing_standard"
    AI_OUTPUT_QUALITY = "ai_output_quality"
    SYSTEM_ERROR = "system_error"
    LANGUAGE_UNICODE = "language_unicode"
    CHARACTER_COMPATIBILITY = "character_compatibility"
```

Types of validation findings that can be reported by validators.

#### Severity
```python
class Severity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

Severity levels for validation findings.

### Data Classes

#### ContentLocation
```python
@dataclass
class ContentLocation:
    content_type: str  # "chapter", "scene", "manuscript", "code_file", etc.
    content_id: str    # chapter_id, scene_id, file_path, etc.
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    character_range: Optional[Tuple[int, int]] = None
```

Location information for validation findings within content.

**Parameters:**
- `content_type`: Type of content being referenced
- `content_id`: Unique identifier for the content
- `line_number`: Optional line number within the content
- `column_number`: Optional column number within the line
- `character_range`: Optional character range as (start, end) tuple

#### Finding
```python
@dataclass
class Finding:
    finding_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    validator_id: str = ""
    type: FindingType = FindingType.CONTENT_QUALITY
    severity: Severity = Severity.MEDIUM
    title: str = ""
    message: str = ""
    location: Optional[ContentLocation] = None
    remediation: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
```

Individual validation finding with detailed information and context.

**Parameters:**
- `finding_id`: Unique identifier for the finding
- `validator_id`: ID of the validator that generated this finding
- `type`: Type of finding from FindingType enum
- `severity`: Severity level from Severity enum
- `title`: Short descriptive title
- `message`: Detailed finding message
- `location`: Optional location information
- `remediation`: Optional suggested remediation
- `confidence`: Confidence score (0.0-1.0)
- `metadata`: Additional metadata dictionary
- `timestamp`: When the finding was created

#### ValidatorResult
```python
@dataclass
class ValidatorResult:
    validator_id: str
    status: ValidationStatus
    findings: List[Finding] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    ai_usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

Result from a single validator execution.

**Parameters:**
- `validator_id`: ID of the validator that produced this result
- `status`: Validation status from ValidationStatus enum
- `findings`: List of findings discovered during validation
- `metrics`: Performance and quality metrics
- `execution_time`: Time taken to execute validation in seconds
- `ai_usage`: AI usage statistics (tokens, cost, etc.)
- `metadata`: Additional result metadata

#### ValidationResult
```python
@dataclass
class ValidationResult:
    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    status: ValidationStatus = ValidationStatus.NOT_STARTED
    overall_quality_score: float = 0.0
    human_review_required: bool = False
    validator_results: Dict[str, ValidatorResult] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)
    total_execution_time: float = 0.0
    total_ai_usage: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

Complete validation result containing all validator outputs and aggregated metrics.

**Parameters:**
- `validation_id`: Unique identifier for this validation run
- `project_id`: Project identifier
- `status`: Overall validation status
- `overall_quality_score`: Aggregated quality score (0-100)
- `human_review_required`: Whether human review is needed
- `validator_results`: Results from each validator
- `summary`: Aggregated summary metrics
- `total_execution_time`: Total validation time in seconds
- `total_ai_usage`: Aggregated AI usage metrics
- `timestamp`: Validation timestamp
- `metadata`: Additional validation metadata

#### ValidationConfig
```python
@dataclass
class ValidationConfig:
    # Core settings
    project_id: str = ""
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    quality_thresholds: Dict[str, float] = field(default_factory=dict)
    human_review_threshold: float = 70.0

    # Validator settings
    enabled_validators: List[str] = field(default_factory=list)
    validator_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # AI settings
    ai_mock_enabled: bool = False
    ai_usage_tracking: bool = True
    litellm_config: Dict[str, Any] = field(default_factory=dict)

    # Processing settings
    parallel_processing: bool = True
    max_parallel_requests: int = 100
    request_timeout: int = 1200  # 20 minutes
    chunk_size_tokens: int = 50000

    # Output settings
    output_formats: List[str] = field(default_factory=lambda: ["json", "html"])
    report_template: Optional[str] = None

    # Workflow integration
    auto_validate_chapters: bool = True
    auto_validate_manuscript: bool = True
    fail_fast: bool = True

    # Resource management
    temp_directory: Optional[str] = None
    cleanup_on_completion: bool = True

    # Monitoring
    health_check_enabled: bool = True
    metrics_collection: bool = True
```

Configuration object for customizing validation behavior.

## ValidatorBase Class

The `ValidatorBase` class is the foundation for all LibriScribe validators, providing comprehensive lifecycle management and common functionality.

### Constructor

```python
def __init__(self, validator_id: str, name: str, version: str):
```

**Parameters:**
- `validator_id`: Unique identifier for the validator
- `name`: Human-readable validator name
- `version`: Validator version string

**Attributes:**
- `validator_id`: Unique validator identifier
- `name`: Validator display name
- `version`: Version string
- `config`: Optional configuration dictionary
- `is_initialized`: Whether validator has been initialized
- `validation_rules`: Dictionary of validation rules
- `quality_thresholds`: Dictionary of quality thresholds
- `_execution_context`: Current execution context

### Abstract Methods

These methods must be implemented by all validator subclasses:

#### initialize
```python
@abstractmethod
async def initialize(self, config: Dict[str, Any]) -> None:
```

Initialize validator with configuration.

**Parameters:**
- `config`: Configuration dictionary specific to this validator

#### validate
```python
@abstractmethod
async def validate(self, content: Any, context: Dict[str, Any]) -> ValidatorResult:
```

Perform validation on content.

**Parameters:**
- `content`: Content to be validated
- `context`: Validation context dictionary

**Returns:**
- `ValidatorResult`: Validation result with findings and metrics

#### get_supported_content_types
```python
@abstractmethod
def get_supported_content_types(self) -> List[str]:
```

Return supported content types.

**Returns:**
- `List[str]`: List of supported content type strings

### Lifecycle Hooks

These methods can be overridden by subclasses to customize validation behavior:

#### pre_validation_hook
```python
async def pre_validation_hook(self, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
```

Hook called before validation starts.

**Parameters:**
- `content`: Content to be validated
- `context`: Validation context

**Returns:**
- `Dict[str, Any]`: Modified context or additional metadata

#### post_validation_hook
```python
async def post_validation_hook(self, result: ValidatorResult, content: Any, context: Dict[str, Any]) -> ValidatorResult:
```

Hook called after validation completes.

**Parameters:**
- `result`: Validation result
- `content`: Original content
- `context`: Validation context

**Returns:**
- `ValidatorResult`: Modified validation result

#### on_validation_error
```python
async def on_validation_error(self, error: Exception, content: Any, context: Dict[str, Any]) -> Optional[ValidatorResult]:
```

Hook called when validation encounters an error.

**Parameters:**
- `error`: Exception that occurred
- `content`: Content being validated
- `context`: Validation context

**Returns:**
- `Optional[ValidatorResult]`: Recovery result or None to re-raise

#### on_configuration_change
```python
async def on_configuration_change(self, old_config: Dict[str, Any], new_config: Dict[str, Any]) -> None:
```

Hook called when validator configuration changes.

**Parameters:**
- `old_config`: Previous configuration
- `new_config`: New configuration

### Core Methods

#### validate_with_lifecycle
```python
async def validate_with_lifecycle(self, content: Any, context: Dict[str, Any]) -> ValidatorResult:
```

Main validation method that orchestrates lifecycle hooks.

This method provides the complete validation workflow including:
- Pre-validation hooks
- Main validation logic
- Post-validation hooks
- Error handling

**Parameters:**
- `content`: Content to be validated
- `context`: Validation context

**Returns:**
- `ValidatorResult`: Complete validation result

**Raises:**
- `ValidationError`: If validator is not initialized

#### configure_validation_rules
```python
def configure_validation_rules(self, rules: Dict[str, Any]) -> None:
```

Configure validation rules for this validator.

**Parameters:**
- `rules`: Dictionary of validation rules specific to this validator

#### configure_quality_thresholds
```python
def configure_quality_thresholds(self, thresholds: Dict[str, float]) -> None:
```

Configure quality thresholds for this validator.

**Parameters:**
- `thresholds`: Dictionary of quality thresholds

#### get_validation_rule
```python
def get_validation_rule(self, rule_name: str, default: Any = None) -> Any:
```

Get a specific validation rule value.

**Parameters:**
- `rule_name`: Name of the rule
- `default`: Default value if rule not found

**Returns:**
- `Any`: Rule value or default

#### get_quality_threshold
```python
def get_quality_threshold(self, threshold_name: str, default: float = 70.0) -> float:
```

Get a specific quality threshold.

**Parameters:**
- `threshold_name`: Name of the threshold
- `default`: Default threshold value

**Returns:**
- `float`: Threshold value or default

#### should_flag_for_human_review
```python
def should_flag_for_human_review(self, quality_score: float, threshold_name: str = "human_review") -> bool:
```

Determine if content should be flagged for human review based on quality score.

**Parameters:**
- `quality_score`: Calculated quality score (0-100)
- `threshold_name`: Name of the threshold to check against

**Returns:**
- `bool`: True if content should be flagged for human review

#### create_finding
```python
def create_finding(self, 
                  finding_type: FindingType,
                  severity: Severity,
                  title: str,
                  message: str,
                  location: Optional[ContentLocation] = None,
                  remediation: Optional[str] = None,
                  confidence: float = 1.0,
                  metadata: Optional[Dict[str, Any]] = None) -> Finding:
```

Helper method to create a Finding with validator context.

**Parameters:**
- `finding_type`: Type of finding
- `severity`: Severity level
- `title`: Finding title
- `message`: Detailed message
- `location`: Content location (optional)
- `remediation`: Suggested remediation (optional)
- `confidence`: Confidence score 0-1
- `metadata`: Additional metadata (optional)

**Returns:**
- `Finding`: Configured Finding object

#### get_validator_info
```python
def get_validator_info(self) -> Dict[str, Any]:
```

Get comprehensive validator information.

**Returns:**
- `Dict[str, Any]`: Dictionary containing validator metadata

#### get_execution_context
```python
def get_execution_context(self) -> Dict[str, Any]:
```

Get current execution context.

**Returns:**
- `Dict[str, Any]`: Copy of current execution context

#### cleanup
```python
async def cleanup(self) -> None:
```

Cleanup validator resources. Can be overridden by subclasses.

## Abstract Interfaces

### ValidationEngine
```python
class ValidationEngine(ABC):
```

Core validation engine interface for orchestrating validation processes.

**Methods:**
- `initialize(config: ValidationConfig) -> None`: Initialize the engine
- `register_validator(validator: ValidatorBase) -> None`: Register a validator
- `validate_project(project_data: Any, project_id: str) -> ValidationResult`: Validate complete project
- `validate_chapter(chapter_data: Any, project_context: Dict[str, Any]) -> ValidationResult`: Validate individual chapter
- `get_validation_status(validation_id: str) -> Optional[ValidationResult]`: Get validation status
- `get_registered_validators() -> List[Dict[str, str]]`: Get registered validators

### ValidationInterface
```python
class ValidationInterface(ABC):
```

Main interface for external systems to interact with validation.

**Methods:**
- `validate_project(knowledge_base_path: str, project_id: Optional[str]) -> ValidationResult`: Main validation entry point
- `validate_chapter(chapter_path: str, project_context: str, project_id: str) -> ValidationResult`: Validate chapter
- `get_system_health() -> Dict[str, Any]`: Get system health status
- `get_validation_history(project_id: str) -> List[ValidationResult]`: Get validation history
- `configure_validation_rules(project_id: str, rules: Dict[str, Any]) -> bool`: Configure validation rules

### ResourceManager
```python
class ResourceManager(ABC):
```

Interface for managing validation resources.

**Methods:**
- `create_workspace(project_id: str) -> str`: Create unique workspace
- `cleanup_workspace(workspace_path: str) -> None`: Clean up workspace
- `get_unique_temp_file(workspace: str, suffix: str) -> str`: Get unique temp file

### HealthMonitor
```python
class HealthMonitor(ABC):
```

Interface for system health monitoring.

**Methods:**
- `get_health_status() -> Dict[str, Any]`: Get current system health
- `get_metrics() -> Dict[str, Any]`: Get system metrics
- `check_ai_connectivity() -> bool`: Check AI service connectivity

### AIUsageTracker
```python
class AIUsageTracker(ABC):
```

Interface for tracking AI usage and costs.

**Methods:**
- `track_request(project_id: str, validator_id: str, tokens_used: int, cost: float, model: str) -> None`: Track AI request
- `get_project_usage(project_id: str) -> Dict[str, Any]`: Get project usage
- `get_usage_report(project_id: str) -> Dict[str, Any]`: Generate usage report

### ReportGenerator
```python
class ReportGenerator(ABC):
```

Interface for generating validation reports.

**Methods:**
- `generate_report(result: ValidationResult, format: str) -> Dict[str, Any]`: Generate report
- `get_supported_formats() -> List[str]`: Get supported formats

## Exception Classes

### ValidationError
```python
class ValidationError(Exception):
```

Base exception for validation errors.

### ValidatorNotFoundError
```python
class ValidatorNotFoundError(ValidationError):
```

Raised when a validator is not found.

### ConfigurationError
```python
class ConfigurationError(ValidationError):
```

Raised when configuration is invalid.

### ResourceError
```python
class ResourceError(ValidationError):
```

Raised when resource management fails.

## Usage Examples

### Creating a Custom Validator

```python
from libriscribe.validation import ValidatorBase, ValidatorResult, Finding, FindingType, Severity

class CustomContentValidator(ValidatorBase):
    def __init__(self):
        super().__init__("custom_content", "Custom Content Validator", "1.0.0")
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize validator with configuration"""
        self.config = config
        self.is_initialized = True
        
        # Configure validation rules
        self.configure_validation_rules({
            "min_word_count": config.get("min_word_count", 1000),
            "check_grammar": config.get("check_grammar", True)
        })
        
        # Configure quality thresholds
        self.configure_quality_thresholds({
            "grammar_score": config.get("grammar_threshold", 80.0),
            "readability_score": config.get("readability_threshold", 70.0)
        })
    
    async def validate(self, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        """Perform validation on content"""
        findings = []
        
        # Check word count
        word_count = len(content.split()) if isinstance(content, str) else 0
        min_words = self.get_validation_rule("min_word_count", 1000)
        
        if word_count < min_words:
            finding = self.create_finding(
                finding_type=FindingType.CONTENT_QUALITY,
                severity=Severity.HIGH,
                title="Insufficient Word Count",
                message=f"Content has {word_count} words, minimum required is {min_words}",
                remediation="Add more content to meet minimum word count requirement",
                confidence=1.0
            )
            findings.append(finding)
        
        # Calculate quality score
        quality_score = max(0, 100 - len(findings) * 20)
        
        return ValidatorResult(
            validator_id=self.validator_id,
            status=ValidationStatus.COMPLETED,
            findings=findings,
            metrics={
                "word_count": word_count,
                "quality_score": quality_score
            }
        )
    
    def get_supported_content_types(self) -> List[str]:
        """Return supported content types"""
        return ["chapter", "manuscript", "scene"]
    
    async def pre_validation_hook(self, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-validation processing"""
        # Add preprocessing logic here
        context["preprocessed"] = True
        return context
    
    async def post_validation_hook(self, result: ValidatorResult, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        """Post-validation processing"""
        # Add post-processing logic here
        result.metadata["post_processed"] = True
        return result
```

### Using Lifecycle Validation

```python
async def validate_with_lifecycle_example():
    # Create validator
    validator = CustomContentValidator()
    
    # Initialize with configuration
    config = {
        "min_word_count": 1500,
        "check_grammar": True,
        "grammar_threshold": 85.0
    }
    await validator.initialize(config)
    
    # Validate content using lifecycle method
    content = "This is sample content to validate..."
    context = {"project_id": "my_book", "chapter_id": "chapter_1"}
    
    result = await validator.validate_with_lifecycle(content, context)
    
    # Process results
    print(f"Validation Status: {result.status}")
    print(f"Findings: {len(result.findings)}")
    for finding in result.findings:
        print(f"  - {finding.title}: {finding.message}")
```

### Error Handling with Recovery

```python
class RobustValidator(ValidatorBase):
    async def on_validation_error(self, error: Exception, content: Any, context: Dict[str, Any]) -> Optional[ValidatorResult]:
        """Handle validation errors with recovery"""
        if isinstance(error, ConnectionError):
            # Retry with fallback logic
            return ValidatorResult(
                validator_id=self.validator_id,
                status=ValidationStatus.COMPLETED,
                findings=[self.create_finding(
                    finding_type=FindingType.SYSTEM_ERROR,
                    severity=Severity.LOW,
                    title="Connection Issue Recovered",
                    message="Validation completed using fallback method",
                    confidence=0.8
                )]
            )
        
        # Let other errors propagate
        return None
```

### Configuration Management

```python
# Configure validator rules dynamically
validator = CustomContentValidator()
await validator.initialize({})

# Update validation rules
validator.configure_validation_rules({
    "min_word_count": 2000,
    "check_spelling": True,
    "require_citations": True
})

# Update quality thresholds
validator.configure_quality_thresholds({
    "overall_quality": 85.0,
    "grammar_score": 90.0,
    "readability_score": 75.0
})

# Check if human review is needed
quality_score = 65.0
needs_review = validator.should_flag_for_human_review(quality_score)
print(f"Human review required: {needs_review}")
```

## Best Practices

1. **Initialization**: Always call `initialize()` before using a validator
2. **Error Handling**: Implement `on_validation_error()` for robust error recovery
3. **Lifecycle Hooks**: Use hooks for preprocessing and postprocessing
4. **Configuration**: Use `configure_validation_rules()` and `configure_quality_thresholds()` for dynamic configuration
5. **Findings**: Use `create_finding()` helper for consistent finding creation
6. **Cleanup**: Implement `cleanup()` for resource management
7. **Context**: Use execution context for sharing data between hooks
8. **Quality Scores**: Implement consistent quality scoring across validators
9. **Human Review**: Use `should_flag_for_human_review()` for consistent review thresholds
10. **Metadata**: Include relevant metadata in results for debugging and analysis