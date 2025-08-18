# ValidationEngine API Documentation

## Overview

The `ValidationEngineImpl` class is the core implementation of the `ValidationEngine` interface in the LibriScribe validation system. It orchestrates validation processes, manages validator lifecycle, and provides comprehensive validation capabilities for both book content and system code.

## Class Definition

```python
class ValidationEngineImpl(ValidationEngine):
    """Implementation of the core validation engine"""
```

## Constructor

```python
def __init__(self):
    self.config: Optional[ValidationConfig] = None
    self.validators: Dict[str, ValidatorBase] = {}
    self.active_validations: Dict[str, ValidationResult] = {}
    self._initialized = False
    self.config_manager = ValidationConfigManager()
```

The constructor initializes the validation engine with empty state. No validation configuration is loaded at this point.

## Core Methods

### Initialize

```python
async def initialize(self, config: ValidationConfig) -> None:
    """Initialize the validation engine with configuration"""
```

**Parameters:**

- `config`: ValidationConfig - Configuration object for the validation engine

**Returns:** None

**Raises:**

- `ValidationError`: If initialization fails

**Description:**
Initializes the validation engine with the provided configuration. This method must be called before using any other methods. It validates the configuration, initializes internal components, and optionally auto-discovers validators.

**Example:**

```python
from libriscribe2.validation import ValidationEngineImpl, ValidationConfig

# Create configuration
config = ValidationConfig(
    project_id="my_book_project",
    enabled_validators=["content_validator", "publishing_standards_validator"],
    quality_thresholds={"overall": 80.0, "tone_consistency": 85.0}
)

# Initialize engine
engine = ValidationEngineImpl()
await engine.initialize(config)
```

### Register Validator

```python
async def register_validator(self, validator: ValidatorBase) -> None:
    """Register a validator with the engine"""
```

**Parameters:**

- `validator`: ValidatorBase - Validator instance to register

**Returns:** None

**Raises:**

- `ValidationError`: If registration fails or engine is not initialized

**Description:**
Registers a validator with the engine and initializes it with its specific configuration. The validator must implement the `ValidatorBase` interface.

**Example:**

```python
from libriscribe2.validation.validators import ContentValidator

# Create and register validator
content_validator = ContentValidator()
await engine.register_validator(content_validator)
```

### Register Validator Class

```python
async def register_validator_class(self, validator_class: Type[ValidatorBase], **kwargs) -> None:
    """Register a validator class with the engine"""
```

**Parameters:**

- `validator_class`: Type[ValidatorBase] - Validator class to instantiate and register
- `**kwargs`: Additional keyword arguments to pass to the validator constructor

**Returns:** None

**Raises:**

- `ValidationError`: If registration fails or engine is not initialized

**Description:**
Creates an instance of the specified validator class with the provided arguments and registers it with the engine. This is a convenience method for registering validators without manually creating instances.

**Example:**

```python
from libriscribe2.validation.validators import PublishingStandardsValidator

# Register validator class with arguments
await engine.register_validator_class(
    PublishingStandardsValidator,
    check_metadata=True,
    check_formatting=True
)
```

### Validate Project

```python
async def validate_project(self, project_data: Any, project_id: str) -> ValidationResult:
    """Validate a complete project"""
```

**Parameters:**

- `project_data`: Any - Project data to validate (typically a ProjectKnowledgeBase instance)
- `project_id`: str - Unique identifier for the project

**Returns:**

- `ValidationResult`: Complete validation result with findings and metrics

**Raises:**

- `ValidationError`: If validation fails or engine is not initialized

**Description:**
Validates a complete project using all enabled validators. The method runs validators either in parallel or sequentially based on configuration, aggregates results, and determines the final validation status.

**Example:**

```python
from libriscribe2.knowledge_base import ProjectKnowledgeBase

# Load project data
project_data = ProjectKnowledgeBase.load_from_file("projects/my_book/project_data.json")

# Validate project
validation_result = await engine.validate_project(project_data, "my_book_project")

# Check validation status
if validation_result.status == ValidationStatus.COMPLETED:
    print(f"Validation successful! Quality score: {validation_result.overall_quality_score}")
elif validation_result.status == ValidationStatus.NEEDS_HUMAN_REVIEW:
    print("Human review required. Check findings for details.")
else:
    print(f"Validation failed: {validation_result.status}")
```

### Validate Chapter

```python
async def validate_chapter(self, chapter_data: Any, project_context: Dict[str, Any]) -> ValidationResult:
    """Validate individual chapter"""
```

**Parameters:**

- `chapter_data`: Any - Chapter data to validate
- `project_context`: Dict[str, Any] - Context information about the project

**Returns:**

- `ValidationResult`: Validation result for the chapter

**Raises:**

- `ValidationError`: If validation fails or engine is not initialized

**Description:**
Validates an individual chapter using validators that support chapter validation. This method is useful for validating chapters as they are generated, before the complete manuscript is assembled.

**Example:**

```python
# Validate a single chapter
chapter_data = {
    "chapter_id": "chapter_1",
    "title": "The Beginning",
    "content": "Chapter content here...",
    "word_count": 2500
}

project_context = {
    "project_id": "my_book_project",
    "genre": "fantasy",
    "tone": "adventurous"
}

chapter_result = await engine.validate_chapter(chapter_data, project_context)
print(f"Chapter validation status: {chapter_result.status}")
```

### Get Validation Status

```python
async def get_validation_status(self, validation_id: str) -> Optional[ValidationResult]:
    """Get status of ongoing validation"""
```

**Parameters:**

- `validation_id`: str - Unique identifier for the validation process

**Returns:**

- `Optional[ValidationResult]`: Current validation result if found, None otherwise

**Description:**
Retrieves the current status of an ongoing validation process. This is useful for checking the progress of long-running validations.

**Example:**

```python
# Check status of ongoing validation
validation_status = await engine.get_validation_status("validation_123")
if validation_status:
    print(f"Validation status: {validation_status.status}")
else:
    print("Validation not found")
```

### Get Registered Validators

```python
async def get_registered_validators(self) -> List[Dict[str, str]]:
    """Get list of registered validators"""
```

**Parameters:** None

**Returns:**

- `List[Dict[str, str]]`: List of validator information dictionaries

**Description:**
Returns information about all registered validators, including their IDs, names, versions, and supported content types.

**Example:**

```python
# Get information about registered validators
validators = await engine.get_registered_validators()
for validator in validators:
    print(f"Validator: {validator['name']} (ID: {validator['id']}, Version: {validator['version']})")
    print(f"Supported content types: {', '.join(validator['supported_types'])}")
```

### Load Configuration from File

```python
async def load_config_from_file(self, config_path: str) -> ValidationConfig:
    """Load configuration from a file"""
```

**Parameters:**

- `config_path`: str - Path to the configuration file (YAML or JSON)

**Returns:**

- `ValidationConfig`: Loaded configuration object

**Raises:**

- `ConfigurationError`: If the configuration file is not found or invalid

**Description:**
Loads validation configuration from a YAML or JSON file. The file format is determined by the file extension.

**Example:**

```python
# Load configuration from file
config = await engine.load_config_from_file("configs/validation_config.yaml")

# Initialize engine with loaded config
await engine.initialize(config)
```

### Save Configuration to File

```python
async def save_config_to_file(self, config: ValidationConfig, config_path: str) -> None:
    """Save configuration to a file"""
```

**Parameters:**

- `config`: ValidationConfig - Configuration object to save
- `config_path`: str - Path where the configuration file should be saved

**Returns:** None

**Raises:**

- `ConfigurationError`: If saving the configuration fails

**Description:**
Saves a validation configuration to a YAML or JSON file. The file format is determined by the file extension.

**Example:**

```python
# Create custom configuration
config = ValidationConfig(
    project_id="custom_project",
    enabled_validators=["content_validator", "quality_validator"],
    quality_thresholds={"overall": 85.0, "tone_consistency": 90.0},
    human_review_threshold=75.0
)

# Save configuration to file
await engine.save_config_to_file(config, "configs/custom_validation_config.yaml")
```

## Private Methods

### _validate_config

```python
async def _validate_config(self, config: ValidationConfig) -> None:
    """Validate the configuration"""
```

Validates that the provided configuration meets requirements.

### _initialize_components

```python
async def _initialize_components(self) -> None:
    """Initialize internal components"""
```

Initializes internal components required by the validation engine.

### _discover_validators

```python
async def _discover_validators(self) -> None:
    """Auto-discover validators in the validators package"""
```

Automatically discovers and registers validator classes from the validators package.

### _get_enabled_validators

```python
def _get_enabled_validators(self) -> List[ValidatorBase]:
    """Get list of enabled validators"""
```

Returns a list of validators that are enabled in the current configuration.

### _run_validators_parallel

```python
async def _run_validators_parallel(self, validators: List[ValidatorBase],
                                 content: Any, context: Dict[str, Any]) -> Dict[str, ValidatorResult]:
    """Run validators in parallel"""
```

Runs multiple validators in parallel for improved performance.

### _run_validators_sequential

```python
async def _run_validators_sequential(self, validators: List[ValidatorBase],
                                   content: Any, context: Dict[str, Any]) -> Dict[str, ValidatorResult]:
    """Run validators sequentially"""
```

Runs validators sequentially, which allows for fail-fast behavior.

### _run_single_validator

```python
async def _run_single_validator(self, validator: ValidatorBase,
                              content: Any, context: Dict[str, Any]) -> ValidatorResult:
    """Run a single validator"""
```

Executes a single validator with error handling and timing.

### _aggregate_results

```python
async def _aggregate_results(self, validation_result: ValidationResult) -> ValidationResult:
    """Aggregate results from all validators"""
```

Combines results from multiple validators into a single comprehensive result.

### _calculate_quality_score

```python
def _calculate_quality_score(self, findings: List[Finding]) -> float:
    """Calculate overall quality score based on findings"""
```

Calculates an overall quality score based on validation findings.

### _count_findings_by_severity

```python
def _count_findings_by_severity(self, findings: List[Finding]) -> Dict[str, int]:
    """Count findings by severity"""
```

Counts validation findings by severity level.

### _count_findings_by_type

```python
def _count_findings_by_type(self, findings: List[Finding]) -> Dict[str, int]:
    """Count findings by type"""
```

Counts validation findings by finding type.

### _determine_final_status

```python
def _determine_final_status(self, validation_result: ValidationResult) -> ValidationStatus:
    """Determine the final validation status"""
```

Determines the final validation status based on validator results and findings.

## Complete Usage Example

```python
import asyncio
from libriscribe2.validation import ValidationEngineImpl, ValidationConfig
from libriscribe2.validation.validators import ContentValidator, PublishingStandardsValidator
from libriscribe2.knowledge_base import ProjectKnowledgeBase

async def validate_book_project():
    # Create validation configuration
    config = ValidationConfig(
        project_id="fantasy_novel",
        enabled_validators=["content_validator", "publishing_standards_validator"],
        quality_thresholds={
            "overall": 80.0,
            "tone_consistency": 85.0,
            "outline_adherence": 90.0
        },
        human_review_threshold=75.0,
        parallel_processing=True,
        fail_fast=True
    )

    # Initialize validation engine
    engine = ValidationEngineImpl()
    await engine.initialize(config)

    # Register validators
    content_validator = ContentValidator()
    publishing_validator = PublishingStandardsValidator()

    await engine.register_validator(content_validator)
    await engine.register_validator(publishing_validator)

    # Load project data
    project_data = ProjectKnowledgeBase.load_from_file("projects/fantasy_novel/project_data.json")

    # Validate project
    validation_result = await engine.validate_project(project_data, "fantasy_novel")

    # Process validation results
    if validation_result.status == ValidationStatus.COMPLETED:
        print(f"Validation successful! Quality score: {validation_result.overall_quality_score}")

        # Print findings by validator
        for validator_id, result in validation_result.validator_results.items():
            print(f"\n{validator_id} findings:")
            for finding in result.findings:
                print(f"- {finding.severity.value}: {finding.title}")
                print(f"  {finding.message}")

    elif validation_result.status == ValidationStatus.NEEDS_HUMAN_REVIEW:
        print(f"Human review required. Quality score: {validation_result.overall_quality_score}")
        print("Critical findings:")

        # Print critical findings
        for validator_id, result in validation_result.validator_results.items():
            critical_findings = [f for f in result.findings if f.severity == Severity.CRITICAL]
            for finding in critical_findings:
                print(f"- {finding.title}: {finding.message}")

    else:
        print(f"Validation failed: {validation_result.status}")

    # Save configuration for future use
    await engine.save_config_to_file(config, "projects/fantasy_novel/validation_config.yaml")

# Run validation
asyncio.run(validate_book_project())
```

## Integration with ValidationConfig

The `ValidationEngineImpl` works closely with the `ValidationConfig` class to manage validation settings:

```python
from libriscribe2.validation import ValidationConfig

# Create configuration with specific settings
config = ValidationConfig(
    project_id="my_project",
    validation_rules={
        "check_tone_consistency": True,
        "check_outline_adherence": True
    },
    quality_thresholds={
        "overall": 80.0,
        "tone_consistency": 85.0,
        "outline_adherence": 90.0
    },
    human_review_threshold=75.0,
    enabled_validators=["content_validator", "publishing_standards_validator"],
    validator_configs={
        "content_validator": {
            "check_tone_consistency": True,
            "check_outline_adherence": True
        },
        "publishing_standards_validator": {
            "check_metadata": True,
            "check_formatting": True
        }
    },
    ai_mock_enabled=False,
    parallel_processing=True,
    max_parallel_requests=100,
    request_timeout=1200,
    chunk_size_tokens=50000,
    output_formats=["json", "html"],
    fail_fast=True
)
```

## Auto-Discovery of Validators

The `ValidationEngineImpl` can automatically discover and register validators from the validators package:

```python
# Enable auto-discovery in configuration
config = ValidationConfig(
    project_id="my_project",
    # Auto-discovery is enabled by default
)

# Initialize engine with auto-discovery
engine = ValidationEngineImpl()
await engine.initialize(config)

# Check discovered validators
validators = await engine.get_registered_validators()
print(f"Discovered {len(validators)} validators:")
for validator in validators:
    print(f"- {validator['name']} (ID: {validator['id']})")
```

## Error Handling

The `ValidationEngineImpl` provides comprehensive error handling:

```python
try:
    # Initialize engine
    engine = ValidationEngineImpl()
    await engine.initialize(config)

    # Validate project
    result = await engine.validate_project(project_data, "my_project")

except ValidationError as e:
    print(f"Validation error: {e}")

except ConfigurationError as e:
    print(f"Configuration error: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```
