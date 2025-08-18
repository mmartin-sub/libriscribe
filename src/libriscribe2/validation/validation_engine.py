"""
ValidationEngine factory and concrete implementation.

This module provides a concrete implementation of the ValidationEngine interface
that can be used directly by client code.
"""

import logging
import os
from typing import Any

from .config import ValidationConfigManager
from .engine import ValidationEngineImpl
from .interfaces import (
    ValidationConfig,
    ValidationEngine,
    ValidationError,
    ValidationResult,
    ValidatorBase,
)

logger = logging.getLogger(__name__)


class LibriScribeValidationEngine:
    """
    Concrete ValidationEngine implementation for libriscribe2.

    This class serves as a factory for creating and configuring ValidationEngineImpl
    instances with appropriate configuration and validators.
    """

    def __init__(self, config_path: str | None = None, project_id: str | None = None):
        """
        Initialize the validation engine.

        Args:
            config_path: Optional path to configuration file
            project_id: Optional project ID for loading project-specific configuration
        """
        self.engine = ValidationEngineImpl()
        self.config_manager = ValidationConfigManager()
        self.config_path = config_path
        self.project_id = project_id
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the validation engine with configuration"""
        try:
            # Load configuration
            if self.config_path and os.path.exists(self.config_path):
                # Load from specified file
                config = await self.engine.load_config_from_file(self.config_path)
                if not config.project_id and self.project_id:
                    config.project_id = self.project_id
            elif self.project_id:
                # Load project-specific configuration
                config = self.config_manager.load_config(self.project_id)
            else:
                # Create default configuration
                config = ValidationConfig(project_id="default")

            # Initialize engine with configuration
            await self.engine.initialize(config)

            # Register built-in validators
            await self._register_builtin_validators()

            self._initialized = True
            logger.info("LibriScribe validation engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LibriScribe validation engine: {e}")
            raise ValidationError(f"Engine initialization failed: {e}") from e

    async def _register_builtin_validators(self) -> None:
        """Register built-in validators"""
        # This will be populated as validators are implemented
        pass

    def get_engine(self) -> ValidationEngine:
        """Get the underlying ValidationEngine implementation"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")
        return self.engine

    async def register_validator(self, validator: ValidatorBase) -> None:
        """Register a validator with the engine"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")
        await self.engine.register_validator(validator)

    async def register_validator_class(self, validator_class: type[ValidatorBase], **kwargs) -> None:
        """Register a validator class with the engine"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")
        await self.engine.register_validator_class(validator_class, **kwargs)

    async def validate_project(self, project_data: Any, project_id: str | None = None) -> ValidationResult:
        """Validate a complete project"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")

        # Use provided project_id or fall back to the one from initialization
        project_id = project_id or self.project_id
        if not project_id:
            raise ValidationError("Project ID is required")

        return await self.engine.validate_project(project_data, project_id)

    async def validate_chapter(self, chapter_data: Any, project_context: dict[str, Any]) -> ValidationResult:
        """Validate individual chapter"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")
        return await self.engine.validate_chapter(chapter_data, project_context)

    async def get_validation_status(self, validation_id: str) -> ValidationResult | None:
        """Get status of ongoing validation"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")
        return await self.engine.get_validation_status(validation_id)

    async def get_registered_validators(self) -> list[dict[str, str]]:
        """Get list of registered validators"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")
        return await self.engine.get_registered_validators()

    @classmethod
    async def create(
        cls, config_path: str | None = None, project_id: str | None = None
    ) -> "LibriScribeValidationEngine":
        """
        Factory method to create and initialize a validation engine.

        Args:
            config_path: Optional path to configuration file
            project_id: Optional project ID for loading project-specific configuration

        Returns:
            Initialized LibriScribeValidationEngine instance
        """
        engine = cls(config_path, project_id)
        await engine.initialize()
        return engine
