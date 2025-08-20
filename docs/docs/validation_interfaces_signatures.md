# LibriScribe Validation Interfaces - Function and Class Signatures

## Overview

This document provides a comprehensive reference of all function and class signatures in the `src/libriscribe2/validation/interfaces.py` module.

## Enums

### ValidationStatus

```python
class ValidationStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    ERROR = "error"
```

### FindingType

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

### Severity

```python
class Severity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

## Data Classes

### ContentLocation

```python
@dataclass
class ContentLocation:
    content_type: str
    content_id: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    character_range: Optional[Tuple[int, int]] = None
```

### Finding

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
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
```

### ValidatorResult

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

### ValidationResult

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

### ValidationConfig

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
    request_timeout: int = 1200
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

## ValidatorBase Class

### Constructor

```python
def __init__(self, validator_id: str, name: str, version: str) -> None
```

### Abstract Methods

```python
@abstractmethod
async def initialize(self, config: Dict[str, Any]) -> None

@abstractmethod
async def validate(self, content: Any, context: Dict[str, Any]) -> ValidatorResult

@abstractmethod
def get_supported_content_types(self) -> List[str]
```

### Lifecycle Hooks

```python
async def pre_validation_hook(self, content: Any, context: Dict[str, Any]) -> Dict[str, Any]

async def post_validation_hook(self, result: ValidatorResult, content: Any, context: Dict[str, Any]) -> ValidatorResult

async def on_validation_error(self, error: Exception, content: Any, context: Dict[str, Any]) -> Optional[ValidatorResult]

async def on_configuration_change(self, old_config: Dict[str, Any], new_config: Dict[str, Any]) -> None
```

### Core Methods

```python
async def validate_with_lifecycle(self, content: Any, context: Dict[str, Any]) -> ValidatorResult

def configure_validation_rules(self, rules: Dict[str, Any]) -> None

def configure_quality_thresholds(self, thresholds: Dict[str, float]) -> None

def get_validation_rule(self, rule_name: str, default: Any = None) -> Any

def get_quality_threshold(self, threshold_name: str, default: float = 70.0) -> float

def should_flag_for_human_review(self, quality_score: float, threshold_name: str = "human_review") -> bool

def create_finding(self,
                  finding_type: FindingType,
                  severity: Severity,
                  title: str,
                  message: str,
                  location: Optional[ContentLocation] = None,
                  remediation: Optional[str] = None,
                  confidence: float = 1.0,
                  metadata: Optional[Dict[str, Any]] = None) -> Finding

def get_validator_info(self) -> Dict[str, Any]

def get_execution_context(self) -> Dict[str, Any]

async def cleanup(self) -> None
```

## Abstract Interfaces

### ValidationEngine

```python
class ValidationEngine(ABC):
    @abstractmethod
    async def initialize(self, config: ValidationConfig) -> None

    @abstractmethod
    async def register_validator(self, validator: ValidatorBase) -> None

    @abstractmethod
    async def validate_project(self, project_data: Any, project_id: str) -> ValidationResult

    @abstractmethod
    async def validate_chapter(self, chapter_data: Any, project_context: Dict[str, Any]) -> ValidationResult

    @abstractmethod
    async def get_validation_status(self, validation_id: str) -> Optional[ValidationResult]

    @abstractmethod
    async def get_registered_validators(self) -> List[Dict[str, str]]
```

### ValidationInterface

```python
class ValidationInterface(ABC):
    @abstractmethod
    async def validate_project(self, knowledge_base_path: str, project_id: Optional[str] = None) -> ValidationResult

    @abstractmethod
    async def validate_chapter(self, chapter_path: str, project_context: str, project_id: str) -> ValidationResult

    @abstractmethod
    async def get_system_health(self) -> Dict[str, Any]

    @abstractmethod
    async def get_validation_history(self, project_id: str) -> List[ValidationResult]

    @abstractmethod
    async def configure_validation_rules(self, project_id: str, rules: Dict[str, Any]) -> bool
```

### ResourceManager

```python
class ResourceManager(ABC):
    @abstractmethod
    async def create_workspace(self, project_id: str) -> str

    @abstractmethod
    async def cleanup_workspace(self, workspace_path: str) -> None

    @abstractmethod
    async def get_unique_temp_file(self, workspace: str, suffix: str = "") -> str
```

### HealthMonitor

```python
class HealthMonitor(ABC):
    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]

    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]

    @abstractmethod
    async def check_ai_connectivity(self) -> bool
```

### AIUsageTracker

```python
class AIUsageTracker(ABC):
    @abstractmethod
    async def track_request(self, project_id: str, validator_id: str, tokens_used: int, cost: float, model: str) -> None

    @abstractmethod
    async def get_project_usage(self, project_id: str) -> Dict[str, Any]

    @abstractmethod
    async def get_usage_report(self, project_id: str) -> Dict[str, Any]
```

### ReportGenerator

```python
class ReportGenerator(ABC):
    @abstractmethod
    async def generate_report(self, result: ValidationResult, format: str) -> Dict[str, Any]

    @abstractmethod
    async def get_supported_formats(self) -> List[str]
```

## Exception Classes

### ValidationError

```python
class ValidationError(Exception):
    pass
```

### ValidatorNotFoundError

```python
class ValidatorNotFoundError(ValidationError):
    pass
```

### ConfigurationError

```python
class ConfigurationError(ValidationError):
    pass
```

### ResourceError

```python
class ResourceError(ValidationError):
    pass
```

## Type Annotations Summary

### Common Type Patterns

```python
# Content types
content: Any
context: Dict[str, Any]
config: Dict[str, Any]

# Result types
ValidatorResult
ValidationResult
Optional[ValidationResult]

# Collection types
List[Finding]
List[str]
Dict[str, ValidatorResult]
Dict[str, Any]

# Identifier types
validator_id: str
project_id: str
validation_id: str

# Numeric types
quality_score: float
execution_time: float
confidence: float

# Optional types
Optional[ContentLocation]
Optional[str]
Optional[Dict[str, Any]]
```

### Function Return Types

```python
# Async methods
-> None                           # Initialization, configuration
-> ValidatorResult               # Validation operations
-> ValidationResult              # Complete validation
-> Dict[str, Any]               # Information retrieval
-> List[str]                    # Content types, formats
-> bool                         # Status checks
-> Optional[ValidatorResult]    # Error recovery

# Sync methods
-> None                         # Configuration updates
-> Any                          # Rule retrieval
-> float                        # Threshold retrieval
-> bool                         # Review checks
-> Finding                      # Finding creation
-> Dict[str, Any]              # Information retrieval
```

### Parameter Patterns

```python
# Required parameters
validator_id: str
name: str
version: str
content: Any
context: Dict[str, Any]

# Optional parameters with defaults
default: Any = None
threshold_name: str = "human_review"
confidence: float = 1.0
suffix: str = ""

# Optional parameters
location: Optional[ContentLocation] = None
remediation: Optional[str] = None
metadata: Optional[Dict[str, Any]] = None
```

## Import Requirements

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
```

## Usage Pattern Examples

### Basic Validator Implementation

```python
class MyValidator(ValidatorBase):
    def __init__(self):
        super().__init__("my_validator", "My Validator", "1.0.0")

    async def initialize(self, config: Dict[str, Any]) -> None:
        # Implementation
        pass

    async def validate(self, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        # Implementation
        return ValidatorResult(...)

    def get_supported_content_types(self) -> List[str]:
        return ["chapter", "manuscript"]
```

### Finding Creation Pattern

```python
finding = validator.create_finding(
    finding_type=FindingType.CONTENT_QUALITY,
    severity=Severity.MEDIUM,
    title="Issue Title",
    message="Detailed message",
    remediation="How to fix",
    confidence=0.8
)
```

### Configuration Pattern

```python
validator.configure_validation_rules({
    "rule_name": "rule_value"
})

validator.configure_quality_thresholds({
    "threshold_name": 75.0
})

rule_value = validator.get_validation_rule("rule_name", default_value)
threshold = validator.get_quality_threshold("threshold_name", 70.0)
```

### Lifecycle Usage Pattern

```python
result = await validator.validate_with_lifecycle(content, context)

# Or implement hooks
async def pre_validation_hook(self, content, context):
    # Preprocessing
    return modified_context

async def post_validation_hook(self, result, content, context):
    # Postprocessing
    return modified_result
```
