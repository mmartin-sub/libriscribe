"""
LibriScribe Code Validation System

This module provides comprehensive validation of both generated book content 
and the underlying LibriScribe system code before publishing.

Core interfaces that establish system boundaries for:
- Workflow integration (Requirements 6.1, 6.2)
- Customizable validation rules (Requirement 7.1)
"""

from .interfaces import (
    ValidationInterface,
    ValidatorBase,
    ValidationEngine,
    ValidationResult,
    ValidationConfig,
    ValidationStatus,
    Finding,
    FindingType,
    Severity
)

from .engine import ValidationEngineImpl
from .config import ValidationConfigManager
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
    "ValidationConfig",
    "ValidationConfigManager",
    
    # Data models
    "ValidationStatus",
    "Finding",
    "FindingType", 
    "Severity",
    
    # AI Mock System
    "AIMockManager",
    "MockScenario",
    "MockResponse",
    "RecordedInteraction"
]