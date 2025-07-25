"""
Core interfaces for the LibriScribe validation system.

This module defines the fundamental interfaces and data structures that establish
system boundaries and enable pluggable validation components.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class ValidationStatus(Enum):
    """Status of validation process or individual validator"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    ERROR = "error"


class FindingType(Enum):
    """Types of validation findings"""

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


class Severity(Enum):
    """Severity levels for validation findings"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ContentLocation:
    """Location information for validation findings"""

    content_type: str  # "chapter", "scene", "manuscript", "code_file", etc.
    content_id: str  # chapter_id, scene_id, file_path, etc.
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    character_range: Optional[Tuple[int, int]] = None


@dataclass
class Finding:
    """Individual validation finding"""

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


@dataclass
class ValidatorResult:
    """Result from a single validator"""

    validator_id: str
    status: ValidationStatus
    findings: List[Finding] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    ai_usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Complete validation result"""

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


@dataclass
class ValidationConfig:
    """Configuration for validation system"""

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


class ValidatorBase(ABC):
    """
    Base class for all validators with lifecycle hooks and common functionality.

    This class provides the foundation for all LibriScribe validators, including:
    - Lifecycle hooks for validation stages
    - Common validation functionality
    - Configuration management
    - Error handling and logging
    - Workflow integration support
    """

    def __init__(self, validator_id: str, name: str, version: str):
        self.validator_id = validator_id
        self.name = name
        self.version = version
        self.config: Optional[Dict[str, Any]] = None
        self.is_initialized = False
        self.validation_rules: Dict[str, Any] = {}
        self.quality_thresholds: Dict[str, float] = {}
        self._execution_context: Dict[str, Any] = {}

    # Core abstract methods that must be implemented by subclasses
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize validator with configuration"""
        pass

    @abstractmethod
    async def validate(self, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        """Perform validation on content"""
        pass

    @abstractmethod
    def get_supported_content_types(self) -> List[str]:
        """Return supported content types"""
        pass

    # Lifecycle hooks - can be overridden by subclasses
    async def pre_validation_hook(
        self, content: Any, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Hook called before validation starts.

        Args:
            content: Content to be validated
            context: Validation context

        Returns:
            Modified context or additional metadata
        """
        return context

    async def post_validation_hook(
        self, result: ValidatorResult, content: Any, context: Dict[str, Any]
    ) -> ValidatorResult:
        """
        Hook called after validation completes.

        Args:
            result: Validation result
            content: Original content
            context: Validation context

        Returns:
            Modified validation result
        """
        return result

    async def on_validation_error(
        self, error: Exception, content: Any, context: Dict[str, Any]
    ) -> Optional[ValidatorResult]:
        """
        Hook called when validation encounters an error.

        Args:
            error: Exception that occurred
            content: Content being validated
            context: Validation context

        Returns:
            Optional recovery result or None to re-raise
        """
        return None

    async def on_configuration_change(
        self, old_config: Dict[str, Any], new_config: Dict[str, Any]
    ) -> None:
        """
        Hook called when validator configuration changes.

        Args:
            old_config: Previous configuration
            new_config: New configuration
        """
        pass

    # Common validator functionality
    async def validate_with_lifecycle(
        self, content: Any, context: Dict[str, Any]
    ) -> ValidatorResult:
        """
        Main validation method that orchestrates lifecycle hooks.

        This method provides the complete validation workflow including:
        - Pre-validation hooks
        - Main validation logic
        - Post-validation hooks
        - Error handling
        """
        if not self.is_initialized:
            raise ValidationError(f"Validator {self.validator_id} not initialized")

        start_time = datetime.now()

        try:
            # Pre-validation hook
            modified_context = await self.pre_validation_hook(content, context)
            self._execution_context = modified_context

            # Main validation
            result = await self.validate(content, modified_context)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time

            # Post-validation hook
            final_result = await self.post_validation_hook(
                result, content, modified_context
            )

            return final_result

        except Exception as error:
            # Try error recovery hook
            recovery_result = await self.on_validation_error(error, content, context)

            if recovery_result is not None:
                return recovery_result

            # Create error result if no recovery
            execution_time = (datetime.now() - start_time).total_seconds()
            return ValidatorResult(
                validator_id=self.validator_id,
                status=ValidationStatus.ERROR,
                findings=[
                    Finding(
                        validator_id=self.validator_id,
                        type=FindingType.SYSTEM_ERROR,
                        severity=Severity.CRITICAL,
                        title=f"Validation Error in {self.name}",
                        message=str(error),
                        remediation="Check validator configuration and input data",
                    )
                ],
                execution_time=execution_time,
                metadata={"error": str(error), "error_type": type(error).__name__},
            )

    def configure_validation_rules(self, rules: Dict[str, Any]) -> None:
        """
        Configure validation rules for this validator.

        Args:
            rules: Dictionary of validation rules specific to this validator
        """
        old_rules = self.validation_rules.copy()
        self.validation_rules.update(rules)

        # Trigger configuration change hook if rules actually changed
        if old_rules != self.validation_rules:
            # Note: This is synchronous, but the hook is async
            # In practice, this would be handled by the validation engine
            pass

    def configure_quality_thresholds(self, thresholds: Dict[str, float]) -> None:
        """
        Configure quality thresholds for this validator.

        Args:
            thresholds: Dictionary of quality thresholds
        """
        self.quality_thresholds.update(thresholds)

    def get_validation_rule(self, rule_name: str, default: Any = None) -> Any:
        """
        Get a specific validation rule value.

        Args:
            rule_name: Name of the rule
            default: Default value if rule not found

        Returns:
            Rule value or default
        """
        return self.validation_rules.get(rule_name, default)

    def get_quality_threshold(
        self, threshold_name: str, default: float = 70.0
    ) -> float:
        """
        Get a specific quality threshold.

        Args:
            threshold_name: Name of the threshold
            default: Default threshold value

        Returns:
            Threshold value or default
        """
        return self.quality_thresholds.get(threshold_name, default)

    def should_flag_for_human_review(
        self, quality_score: float, threshold_name: str = "human_review"
    ) -> bool:
        """
        Determine if content should be flagged for human review based on quality score.

        Args:
            quality_score: Calculated quality score (0-100)
            threshold_name: Name of the threshold to check against

        Returns:
            True if content should be flagged for human review
        """
        threshold = self.get_quality_threshold(threshold_name)
        return quality_score < threshold

    def create_finding(
        self,
        finding_type: FindingType,
        severity: Severity,
        title: str,
        message: str,
        location: Optional[ContentLocation] = None,
        remediation: Optional[str] = None,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Finding:
        """
        Helper method to create a Finding with validator context.

        Args:
            finding_type: Type of finding
            severity: Severity level
            title: Finding title
            message: Detailed message
            location: Content location (optional)
            remediation: Suggested remediation (optional)
            confidence: Confidence score 0-1
            metadata: Additional metadata (optional)

        Returns:
            Configured Finding object
        """
        return Finding(
            validator_id=self.validator_id,
            type=finding_type,
            severity=severity,
            title=title,
            message=message,
            location=location,
            remediation=remediation,
            confidence=confidence,
            metadata=metadata or {},
        )

    def get_validator_info(self) -> Dict[str, Any]:
        """Get comprehensive validator information"""
        return {
            "id": self.validator_id,
            "name": self.name,
            "version": self.version,
            "supported_types": self.get_supported_content_types(),
            "is_initialized": self.is_initialized,
            "validation_rules": list(self.validation_rules.keys()),
            "quality_thresholds": list(self.quality_thresholds.keys()),
        }

    def get_execution_context(self) -> Dict[str, Any]:
        """Get current execution context"""
        return self._execution_context.copy()

    async def cleanup(self) -> None:
        """
        Cleanup validator resources.

        This method can be overridden by subclasses to perform cleanup
        when the validator is no longer needed.
        """
        pass


class ValidationEngine(ABC):
    """Core validation engine interface"""

    @abstractmethod
    async def initialize(self, config: ValidationConfig) -> None:
        """Initialize the validation engine"""
        pass

    @abstractmethod
    async def register_validator(self, validator: ValidatorBase) -> None:
        """Register a validator with the engine"""
        pass

    @abstractmethod
    async def validate_project(
        self, project_data: Any, project_id: str
    ) -> ValidationResult:
        """Validate a complete project"""
        pass

    @abstractmethod
    async def validate_chapter(
        self, chapter_data: Any, project_context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate individual chapter"""
        pass

    @abstractmethod
    async def get_validation_status(
        self, validation_id: str
    ) -> Optional[ValidationResult]:
        """Get status of ongoing validation"""
        pass

    @abstractmethod
    async def get_registered_validators(self) -> List[Dict[str, str]]:
        """Get list of registered validators"""
        pass


class ValidationInterface(ABC):
    """Main interface for external systems to interact with validation"""

    @abstractmethod
    async def validate_project(
        self, knowledge_base_path: str, project_id: Optional[str] = None
    ) -> ValidationResult:
        """Main API entry point for project validation"""
        pass

    @abstractmethod
    async def validate_chapter(
        self, chapter_path: str, project_context: str, project_id: str
    ) -> ValidationResult:
        """Validate individual chapter content"""
        pass

    @abstractmethod
    async def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        pass

    @abstractmethod
    async def get_validation_history(self, project_id: str) -> List[ValidationResult]:
        """Get validation history for a project"""
        pass

    @abstractmethod
    async def configure_validation_rules(
        self, project_id: str, rules: Dict[str, Any]
    ) -> bool:
        """Configure validation rules for a project"""
        pass


class ResourceManager(ABC):
    """Interface for managing validation resources"""

    @abstractmethod
    async def create_workspace(self, project_id: str) -> str:
        """Create unique workspace for validation process"""
        pass

    @abstractmethod
    async def cleanup_workspace(self, workspace_path: str) -> None:
        """Clean up workspace and temporary files"""
        pass

    @abstractmethod
    async def get_unique_temp_file(self, workspace: str, suffix: str = "") -> str:
        """Get unique temporary file path within workspace"""
        pass


class HealthMonitor(ABC):
    """Interface for system health monitoring"""

    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current system health"""
        pass

    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        pass

    @abstractmethod
    async def check_ai_connectivity(self) -> bool:
        """Check AI service connectivity"""
        pass


class AIUsageTracker(ABC):
    """Interface for tracking AI usage and costs"""

    @abstractmethod
    async def track_request(
        self,
        project_id: str,
        validator_id: str,
        tokens_used: int,
        cost: float,
        model: str,
    ) -> None:
        """Track AI request usage"""
        pass

    @abstractmethod
    async def get_project_usage(self, project_id: str) -> Dict[str, Any]:
        """Get AI usage for specific project"""
        pass

    @abstractmethod
    async def get_usage_report(self, project_id: str) -> Dict[str, Any]:
        """Generate usage report"""
        pass


class ReportGenerator(ABC):
    """Interface for generating validation reports"""

    @abstractmethod
    async def generate_report(
        self, result: ValidationResult, format: str
    ) -> Dict[str, Any]:
        """Generate validation report in specified format"""
        pass

    @abstractmethod
    async def get_supported_formats(self) -> List[str]:
        """Get supported report formats"""
        pass


# Exception classes
class ValidationError(Exception):
    """Base exception for validation errors"""

    pass


class ValidatorNotFoundError(ValidationError):
    """Raised when a validator is not found"""

    pass


class ConfigurationError(ValidationError):
    """Raised when configuration is invalid"""

    pass


class ResourceError(ValidationError):
    """Raised when resource management fails"""

    pass
