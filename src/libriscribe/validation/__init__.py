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

from .interfaces import (
    ValidationInterface,
    ValidatorBase,
    ValidationEngine,
    ValidationResult,
    ValidatorResult,
    ValidationConfig,
    ValidationStatus,
    Finding,
    FindingType,
    Severity,
    ContentLocation,
    ResourceManager,
    HealthMonitor,
    AIUsageTracker,
    ReportGenerator,
    ConfigurationError,
    ValidationError,
    ValidatorNotFoundError,
    ResourceError
)

from .engine import ValidationEngineImpl
from .config import ValidationConfigManager
from .validation_engine import LibriScribeValidationEngine
from .ai_mock import (
    AIMockManager,
    MockScenario,
    MockResponse,
    RecordedInteraction
)

__version__ = "1.0.0"

__all__ = [
    # Core interfaces
    "ValidationInterface",
    "ValidatorBase", 
    "ValidationEngine",
    "ValidationEngineImpl",
    "ValidationResult",
    "ValidatorResult",
    "ValidationConfig",
    "ValidationConfigManager",
    
    # Concrete implementations
    "LibriScribeValidationEngine",
    
    # Data models
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
    
    # AI Mock System
    "AIMockManager",
    "MockScenario",
    "MockResponse",
    "RecordedInteraction"
]