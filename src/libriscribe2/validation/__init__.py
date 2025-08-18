"""
LibriScribe Code Validation System

This module provides comprehensive validation of both generated book content
and the underlying LibriScribe system code before publishing.

Core interfaces that establish system boundaries for:
- Workflow integration (Requirements 6.1, 6.2)
- Customizable validation rules (Requirement 7.1)
- Validator lifecycle management (Requirement 4)
- Configuration management (Requirement 7)
- AI testing and mocking (Requirement 11)

The validation system includes:
- ValidationEngine: Core orchestration engine for validation processes
- ValidatorBase: Abstract base class for implementing custom validators
- ValidationConfig: Configuration management for validation rules
- AI Mock System: Comprehensive testing framework for AI components
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interfaces import (
        AIUsageTracker,
        ConfigurationError,
        ContentLocation,
        Finding,
        FindingType,
        HealthMonitor,
        ReportGenerator,
        ResourceError,
        ResourceManager,
        Severity,
        ValidationConfig,
        ValidationEngine,
        ValidationError,
        ValidationInterface,
        ValidationResult,
        ValidationStatus,
        ValidatorBase,
        ValidatorNotFoundError,
        ValidatorResult,
    )

# Import core interfaces
from .interfaces import (
    AIUsageTracker,
    ConfigurationError,
    ContentLocation,
    Finding,
    FindingType,
    HealthMonitor,
    ReportGenerator,
    ResourceError,
    ResourceManager,
    Severity,
    ValidationConfig,
    ValidationEngine,
    ValidationError,
    ValidationInterface,
    ValidationResult,
    ValidationStatus,
    ValidatorBase,
    ValidatorNotFoundError,
    ValidatorResult,
)

# Import implementations
try:
    from .ai_mock import AIMockManager, MockResponse, MockScenario, RecordedInteraction
    from .config import ValidationConfigManager
    from .engine import ValidationEngineImpl
    from .validation_engine import LibriScribeValidationEngine
except ImportError as e:
    # Handle import errors gracefully for mypy
    import logging

    logging.warning(f"Some validation modules could not be imported: {e}")

__version__ = "1.0.0"

__all__ = [
    # Core interfaces
    "ValidationInterface",
    "ValidatorBase",
    "ValidationEngine",
    "ValidationResult",
    "ValidatorResult",
    "ValidationConfig",
    "ValidationStatus",
    "Finding",
    "FindingType",
    "Severity",
    "ContentLocation",
    # Abstract interfaces
    "ResourceManager",
    "HealthMonitor",
    "AIUsageTracker",
    "ReportGenerator",
    # Exceptions
    "ConfigurationError",
    "ValidationError",
    "ValidatorNotFoundError",
    "ResourceError",
]

# Add implementations to __all__ if they were imported successfully
try:
    __all__.extend(
        [
            "AIMockManager",
            "LibriScribeValidationEngine",
            "MockResponse",
            "MockScenario",
            "RecordedInteraction",
            "ValidationConfigManager",
            "ValidationEngineImpl",
        ]
    )
except NameError:
    # Some implementations are not available
    pass
