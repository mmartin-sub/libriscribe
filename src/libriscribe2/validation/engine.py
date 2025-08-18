"""
Core validation engine implementation.

This module provides the main ValidationEngine implementation that orchestrates
validation processes and manages validator lifecycle.

The ValidationEngineImpl class is responsible for:
1. Managing validator registration and lifecycle
2. Orchestrating validation processes
3. Aggregating validation results
4. Handling configuration loading and saving
5. Auto-discovering validators from the validators package

Example usage:
    ```python
    from libriscribe2.validation import ValidationEngineImpl, ValidationConfig

    # Create configuration
    config = ValidationConfig(project_id="my_book")

    # Initialize engine
    engine = ValidationEngineImpl()
    await engine.initialize(config)

    # Register validators
    from libriscribe2.validation.validators import ContentValidator

    content_validator = ContentValidator()
    await engine.register_validator(content_validator)

    # Validate project
    result = await engine.validate_project(project_data, "my_book")
    ```
"""

import asyncio
import importlib
import inspect
import logging
import os
import pkgutil
from datetime import datetime
from typing import Any

import yaml

from .config import ValidationConfigManager
from .interfaces import (
    ConfigurationError,
    Finding,
    FindingType,
    Severity,
    ValidationConfig,
    ValidationEngine,
    ValidationError,
    ValidationResult,
    ValidationStatus,
    ValidatorBase,
    ValidatorResult,
)

logger = logging.getLogger(__name__)


class ValidationEngineImpl(ValidationEngine):
    """
    Implementation of the core validation engine.

    This class implements the ValidationEngine interface and provides comprehensive
    validation capabilities for both book content and system code. It manages validator
    lifecycle, orchestrates validation processes, and aggregates results.

    Attributes:
        config (ValidationConfig): Configuration for the validation engine
        validators (dict[str, ValidatorBase]): Dictionary of registered validators
        active_validations (dict[str, ValidationResult]): Currently active validation processes
        _initialized (bool): Whether the engine has been initialized
        config_manager (ValidationConfigManager): Manager for configuration loading/saving
    """

    def __init__(self) -> None:
        self.config: ValidationConfig | None = None
        self.validators: dict[str, ValidatorBase] = {}
        self.active_validations: dict[str, ValidationResult] = {}
        self._initialized = False
        self.config_manager = ValidationConfigManager()

    async def initialize(self, config: ValidationConfig) -> None:
        """
        Initialize the validation engine with configuration.

        This method must be called before using any other methods. It validates
        the configuration, initializes internal components, and optionally
        auto-discovers validators.

        Args:
            config: Configuration object for the validation engine

        Raises:
            ValidationError: If initialization fails
        """
        try:
            self.config = config
            logger.info(f"Initializing validation engine for project: {config.project_id}")

            # Validate configuration
            await self._validate_config(config)

            # Initialize internal components
            await self._initialize_components()

            # Auto-discover and register validators if enabled
            if getattr(config, "auto_discover_validators", True):
                await self._discover_validators()

            self._initialized = True
            logger.info("Validation engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize validation engine: {e}")
            raise ValidationError(f"Engine initialization failed: {e}") from e

    async def register_validator(self, validator: ValidatorBase) -> None:
        """
        Register a validator with the engine.

        Args:
            validator: Validator instance to register

        Raises:
            ValidationError: If registration fails or engine is not initialized
        """
        if not self._initialized:
            raise ValidationError("Engine not initialized")

        try:
            # Initialize validator with its specific config
            if self.config is None:
                raise ValidationError("Engine configuration is None")
            validator_config = self.config.validator_configs.get(validator.validator_id, {})
            await validator.initialize(validator_config)

            # Register validator
            self.validators[validator.validator_id] = validator
            logger.info(f"Registered validator: {validator.validator_id}")

        except Exception as e:
            logger.error(f"Failed to register validator {validator.validator_id}: {e}")
            raise ValidationError(f"Validator registration failed: {e}") from e

    async def register_validator_class(self, validator_class: type[ValidatorBase], **kwargs) -> None:
        """
        Register a validator class with the engine.

        Creates an instance of the specified validator class with the provided arguments
        and registers it with the engine.

        Args:
            validator_class: Validator class to instantiate and register
            **kwargs: Additional keyword arguments to pass to the validator constructor

        Raises:
            ValidationError: If registration fails or engine is not initialized
        """
        if not self._initialized:
            raise ValidationError("Engine not initialized")

        try:
            # Create validator instance
            validator = validator_class(**kwargs)

            # Register the validator
            await self.register_validator(validator)

        except Exception as e:
            logger.error(f"Failed to register validator class {validator_class.__name__}: {e}")
            raise ValidationError(f"Validator class registration failed: {e}") from e

    async def validate_project(self, project_data: Any, project_id: str) -> ValidationResult:
        """
        Validate a complete project.

        Validates a complete project using all enabled validators. The method runs validators
        either in parallel or sequentially based on configuration, aggregates results, and
        determines the final validation status.

        Args:
            project_data: Project data to validate (typically a ProjectKnowledgeBase instance)
            project_id: Unique identifier for the project

        Returns:
            ValidationResult: Complete validation result with findings and metrics

        Raises:
            ValidationError: If validation fails or engine is not initialized
        """
        if not self._initialized:
            raise ValidationError("Engine not initialized")

        validation_result = ValidationResult(project_id=project_id, status=ValidationStatus.IN_PROGRESS)

        # Store active validation
        self.active_validations[validation_result.validation_id] = validation_result

        try:
            start_time = datetime.now()
            logger.info(f"Starting project validation: {project_id}")

            # Get enabled validators
            enabled_validators = self._get_enabled_validators()

            if not enabled_validators:
                logger.warning("No validators enabled for validation")
                validation_result.status = ValidationStatus.COMPLETED
                return validation_result

            # Run validators
            if self.config is None:
                raise ValidationError("Engine configuration is None")
            if self.config.parallel_processing:
                validator_results = await self._run_validators_parallel(
                    enabled_validators, project_data, {"project_id": project_id}
                )
            else:
                validator_results = await self._run_validators_sequential(
                    enabled_validators, project_data, {"project_id": project_id}
                )

            # Aggregate results
            validation_result.validator_results = validator_results
            validation_result = await self._aggregate_results(validation_result)

            # Calculate execution time
            end_time = datetime.now()
            validation_result.total_execution_time = (end_time - start_time).total_seconds()

            # Determine final status
            validation_result.status = self._determine_final_status(validation_result)

            logger.info(f"Project validation completed: {project_id}, Status: {validation_result.status}")

            return validation_result

        except Exception as e:
            logger.error(f"Project validation failed: {e}")
            validation_result.status = ValidationStatus.ERROR
            validation_result.summary["error"] = str(e)
            return validation_result

        finally:
            # Remove from active validations
            self.active_validations.pop(validation_result.validation_id, None)

    async def validate_chapter(self, chapter_data: Any, project_context: dict[str, Any]) -> ValidationResult:
        """Validate individual chapter"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")

        validation_result = ValidationResult(
            project_id=project_context.get("project_id", ""),
            status=ValidationStatus.IN_PROGRESS,
        )

        try:
            start_time = datetime.now()
            logger.info(f"Starting chapter validation for project: {project_context.get('project_id')}")

            # Get validators that support chapter validation
            chapter_validators = [
                v for v in self._get_enabled_validators() if "chapter" in v.get_supported_content_types()
            ]

            if not chapter_validators:
                logger.warning("No chapter validators available")
                validation_result.status = ValidationStatus.COMPLETED
                return validation_result

            # Run chapter-specific validation
            validator_results = await self._run_validators_sequential(chapter_validators, chapter_data, project_context)

            # Aggregate results
            validation_result.validator_results = validator_results
            validation_result = await self._aggregate_results(validation_result)

            # Calculate execution time
            end_time = datetime.now()
            validation_result.total_execution_time = (end_time - start_time).total_seconds()

            # Determine final status
            validation_result.status = self._determine_final_status(validation_result)

            logger.info(f"Chapter validation completed, Status: {validation_result.status}")

            return validation_result

        except Exception as e:
            logger.error(f"Chapter validation failed: {e}")
            validation_result.status = ValidationStatus.ERROR
            validation_result.summary["error"] = str(e)
            return validation_result

    async def get_validation_status(self, validation_id: str) -> ValidationResult | None:
        """Get status of ongoing validation"""
        return self.active_validations.get(validation_id)

    async def get_registered_validators(self) -> list[dict[str, str]]:
        """Get list of registered validators"""
        return [validator.get_validator_info() for validator in self.validators.values()]

    async def load_config_from_file(self, config_path: str) -> ValidationConfig:
        """
        Load configuration from a file.

        Args:
            config_path: Path to the configuration file (YAML or JSON)

        Returns:
            ValidationConfig: Loaded configuration object

        Raises:
            ConfigurationError: If the configuration file is not found or invalid
        """
        if not os.path.exists(config_path):
            raise ConfigurationError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path) as f:
                if config_path.endswith(".json"):
                    import json

                    config_dict = json.load(f)
                else:
                    config_dict = yaml.safe_load(f)

            # Convert dictionary to ValidationConfig
            config = self.config_manager._dict_to_validation_config(config_dict, config_dict.get("project_id", ""))

            return config

        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise ConfigurationError(f"Configuration loading failed: {e}") from e

    async def save_config_to_file(self, config: ValidationConfig, config_path: str) -> None:
        """
        Save configuration to a file.

        Args:
            config: Configuration object to save
            config_path: Path where the configuration file should be saved

        Raises:
            ConfigurationError: If saving the configuration fails
        """
        try:
            # Convert ValidationConfig to dictionary
            config_dict = {
                "project_id": config.project_id,
                "validation_rules": config.validation_rules,
                "quality_thresholds": config.quality_thresholds,
                "human_review_threshold": config.human_review_threshold,
                "enabled_validators": config.enabled_validators,
                "validator_configs": config.validator_configs,
                "ai_settings": {
                    "mock_enabled": config.ai_mock_enabled,
                    "usage_tracking": config.ai_usage_tracking,
                    "litellm_config": config.litellm_config,
                },
                "processing": {
                    "parallel_processing": config.parallel_processing,
                    "max_parallel_requests": config.max_parallel_requests,
                    "request_timeout": config.request_timeout,
                    "chunk_size_tokens": config.chunk_size_tokens,
                },
                "output": {
                    "formats": config.output_formats,
                    "report_template": config.report_template,
                },
                "workflow": {
                    "auto_validate_chapters": config.auto_validate_chapters,
                    "auto_validate_manuscript": config.auto_validate_manuscript,
                    "fail_fast": config.fail_fast,
                },
                "resources": {
                    "temp_directory": config.temp_directory,
                    "cleanup_on_completion": config.cleanup_on_completion,
                },
                "monitoring": {
                    "health_check_enabled": config.health_check_enabled,
                    "metrics_collection": config.metrics_collection,
                },
            }

            # Write to file
            with open(config_path, "w") as f:
                if config_path.endswith(".json"):
                    import json

                    json.dump(config_dict, f, indent=2)
                else:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)

            logger.info(f"Configuration saved to {config_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            raise ConfigurationError(f"Configuration save failed: {e}") from e

    # Private methods

    async def _validate_config(self, config: ValidationConfig) -> None:
        """Validate the configuration"""
        if not config.project_id:
            raise ValidationError("Project ID is required")

        if config.max_parallel_requests <= 0:
            raise ValidationError("max_parallel_requests must be positive")

        if config.human_review_threshold < 0 or config.human_review_threshold > 100:
            raise ValidationError("human_review_threshold must be between 0 and 100")

    async def _initialize_components(self) -> None:
        """Initialize internal components"""
        # Don't reconfigure logging if it's already set up
        # The main application handles logging configuration
        # Initialize other components as needed
        pass

    async def _discover_validators(self) -> None:
        """
        Auto-discover validators in the validators package.

        This method automatically discovers and registers validator classes from the
        validators package. It uses reflection to find classes that inherit from
        ValidatorBase and are not abstract.
        """
        try:
            from . import validators

            # Get the package path
            package_path = validators.__path__
            prefix = validators.__name__ + "."

            for _, name, is_pkg in pkgutil.iter_modules(package_path, prefix):
                if not is_pkg:
                    try:
                        # Import the module
                        module = importlib.import_module(name)

                        # Find validator classes in the module
                        for _, obj in inspect.getmembers(module, inspect.isclass):
                            if (
                                issubclass(obj, ValidatorBase)
                                and obj is not ValidatorBase
                                and not inspect.isabstract(obj)
                            ):
                                # Create and register validator instance
                                try:
                                    # ValidatorBase requires validator_id, name, and version
                                    # We'll use the class name as a fallback
                                    validator = obj(
                                        validator_id=obj.__name__.lower(),
                                        name=obj.__name__,
                                        version="1.0.0",
                                    )
                                    await self.register_validator(validator)
                                    logger.info(f"Auto-discovered validator: {validator.validator_id}")
                                except Exception as e:
                                    logger.warning(f"Failed to register discovered validator {obj.__name__}: {e}")

                    except Exception as e:
                        logger.warning(f"Error importing validator module {name}: {e}")

            logger.info("Validator auto-discovery completed")

        except ImportError:
            logger.warning("Validators package not found, skipping auto-discovery")
        except Exception as e:
            logger.warning(f"Error during validator auto-discovery: {e}")

    def _get_enabled_validators(self) -> list[ValidatorBase]:
        """Get list of enabled validators"""
        if self.config is None:
            raise ValidationError("Engine configuration is None")
        if not self.config.enabled_validators:
            # If no specific validators enabled, return all registered
            return list(self.validators.values())

        enabled = []
        for validator_id in self.config.enabled_validators:
            if validator_id in self.validators:
                enabled.append(self.validators[validator_id])
            else:
                logger.warning(f"Enabled validator not found: {validator_id}")

        return enabled

    async def _run_validators_parallel(
        self, validators: list[ValidatorBase], content: Any, context: dict[str, Any]
    ) -> dict[str, ValidatorResult]:
        """Run validators in parallel"""
        tasks = []
        for validator in validators:
            task = asyncio.create_task(self._run_single_validator(validator, content, context))
            tasks.append((validator.validator_id, task))

        results = {}
        for validator_id, task in tasks:
            try:
                result = await task
                results[validator_id] = result
            except Exception as e:
                logger.error(f"Validator {validator_id} failed: {e}")
                results[validator_id] = ValidatorResult(
                    validator_id=validator_id,
                    status=ValidationStatus.ERROR,
                    findings=[
                        Finding(
                            validator_id=validator_id,
                            type=FindingType.SYSTEM_ERROR,
                            severity=Severity.CRITICAL,
                            title="Validator Error",
                            message=str(e),
                        )
                    ],
                )

        return results

    async def _run_validators_sequential(
        self, validators: list[ValidatorBase], content: Any, context: dict[str, Any]
    ) -> dict[str, ValidatorResult]:
        """Run validators sequentially"""
        results = {}

        for validator in validators:
            try:
                result = await self._run_single_validator(validator, content, context)
                results[validator.validator_id] = result

                # Check for fail-fast conditions
                if self.config is None:
                    raise ValidationError("Engine configuration is None")
                if self.config.fail_fast and result.status == ValidationStatus.ERROR:
                    logger.info(f"Fail-fast triggered by validator: {validator.validator_id}")
                    break

            except Exception as e:
                logger.error(f"Validator {validator.validator_id} failed: {e}")
                results[validator.validator_id] = ValidatorResult(
                    validator_id=validator.validator_id,
                    status=ValidationStatus.ERROR,
                    findings=[
                        Finding(
                            validator_id=validator.validator_id,
                            type=FindingType.SYSTEM_ERROR,
                            severity=Severity.CRITICAL,
                            title="Validator Error",
                            message=str(e),
                        )
                    ],
                )

                if self.config is None:
                    raise ValidationError("Engine configuration is None")
                if self.config.fail_fast:
                    break

        return results

    async def _run_single_validator(
        self, validator: ValidatorBase, content: Any, context: dict[str, Any]
    ) -> ValidatorResult:
        """Run a single validator"""
        start_time = datetime.now()

        try:
            result = await validator.validate(content, context)
            result.execution_time = (datetime.now() - start_time).total_seconds()
            return result

        except Exception as e:
            logger.error(f"Validator {validator.validator_id} execution failed: {e}")
            return ValidatorResult(
                validator_id=validator.validator_id,
                status=ValidationStatus.ERROR,
                execution_time=(datetime.now() - start_time).total_seconds(),
                findings=[
                    Finding(
                        validator_id=validator.validator_id,
                        type=FindingType.SYSTEM_ERROR,
                        severity=Severity.CRITICAL,
                        title="Validator Execution Error",
                        message=str(e),
                    )
                ],
            )

    async def _aggregate_results(self, validation_result: ValidationResult) -> ValidationResult:
        """Aggregate results from all validators"""
        all_findings = []
        total_ai_usage = {"tokens": 0, "cost": 0.0, "requests": 0}

        # Collect all findings and metrics
        for result in validation_result.validator_results.values():
            all_findings.extend(result.findings)

            # Aggregate AI usage
            if result.ai_usage:
                total_ai_usage["tokens"] += result.ai_usage.get("tokens", 0)
                total_ai_usage["cost"] += result.ai_usage.get("cost", 0.0)
                total_ai_usage["requests"] += result.ai_usage.get("requests", 0)

        # Calculate quality score
        validation_result.overall_quality_score = self._calculate_quality_score(all_findings)

        # Determine if human review is required
        if self.config is None:
            raise ValidationError("Engine configuration is None")
        validation_result.human_review_required = (
            validation_result.overall_quality_score < self.config.human_review_threshold
            or any(
                r.status == ValidationStatus.NEEDS_HUMAN_REVIEW for r in validation_result.validator_results.values()
            )
        )

        # Set AI usage
        validation_result.total_ai_usage = total_ai_usage

        # Generate summary
        validation_result.summary = {
            "total_findings": len(all_findings),
            "findings_by_severity": self._count_findings_by_severity(all_findings),
            "findings_by_type": self._count_findings_by_type(all_findings),
            "quality_score": validation_result.overall_quality_score,
            "human_review_required": validation_result.human_review_required,
            "validators_run": len(validation_result.validator_results),
            "ai_usage": total_ai_usage,
        }

        return validation_result

    def _calculate_quality_score(self, findings: list[Finding]) -> float:
        """Calculate overall quality score based on findings"""
        if not findings:
            return 100.0

        # Simple scoring algorithm - can be made more sophisticated
        severity_weights = {
            Severity.INFO: 0,
            Severity.LOW: 1,
            Severity.MEDIUM: 3,
            Severity.HIGH: 7,
            Severity.CRITICAL: 15,
        }

        total_penalty = sum(severity_weights.get(finding.severity, 0) for finding in findings)

        # Base score of 100, subtract penalties
        score = max(0.0, 100.0 - total_penalty)

        return score

    def _count_findings_by_severity(self, findings: list[Finding]) -> dict[str, int]:
        """Count findings by severity"""
        counts = {severity.value: 0 for severity in Severity}
        for finding in findings:
            counts[finding.severity.value] += 1
        return counts

    def _count_findings_by_type(self, findings: list[Finding]) -> dict[str, int]:
        """Count findings by type"""
        counts = {finding_type.value: 0 for finding_type in FindingType}
        for finding in findings:
            counts[finding.type.value] += 1
        return counts

    def _determine_final_status(self, validation_result: ValidationResult) -> ValidationStatus:
        """Determine the final validation status"""
        # Check for errors
        error_results = [r for r in validation_result.validator_results.values() if r.status == ValidationStatus.ERROR]

        if error_results:
            return ValidationStatus.ERROR

        # Check if any validator explicitly requested human review
        needs_review_results = [
            r for r in validation_result.validator_results.values() if r.status == ValidationStatus.NEEDS_HUMAN_REVIEW
        ]

        if needs_review_results:
            return ValidationStatus.NEEDS_HUMAN_REVIEW

        # Check for human review requirement based on quality score
        if validation_result.human_review_required:
            return ValidationStatus.NEEDS_HUMAN_REVIEW

        # Check for critical findings
        critical_findings = [
            f
            for result in validation_result.validator_results.values()
            for f in result.findings
            if f.severity == Severity.CRITICAL
        ]

        if critical_findings:
            return ValidationStatus.NEEDS_HUMAN_REVIEW

        return ValidationStatus.COMPLETED
