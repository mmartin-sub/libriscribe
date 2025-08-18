#!/usr/bin/env python3
"""
Unit tests for ValidationEngine implementation.

This module contains comprehensive tests for the ValidationEngineImpl class,
covering initialization, validator registration, validation processes, and
configuration management.
"""

from pathlib import Path
from typing import Any

import pytest

from libriscribe2.validation import (
    Finding,
    FindingType,
    Severity,
    ValidationConfig,
    ValidationEngineImpl,
    ValidationStatus,
    ValidatorBase,
    ValidatorResult,
)


class MockValidator(ValidatorBase):
    """Mock validator for testing"""

    def __init__(self, validator_id: str, name: str = "Mock Validator", version: str = "1.0.0"):
        super().__init__(validator_id, name, version)
        self.initialized = False
        self.validate_called = False
        self.last_content = None
        self.last_context = None
        self.config = {}

    async def initialize(self, config: dict[str, Any]) -> None:
        """Initialize validator with configuration"""
        self.initialized = True
        self.config = config

    async def validate(self, content: Any, context: dict[str, Any]) -> ValidatorResult:
        """Perform validation on content"""
        self.validate_called = True
        self.last_content = content
        self.last_context = context

        findings = []
        if self.validator_id == "failing_validator":
            findings.append(
                Finding(
                    validator_id=self.validator_id,
                    type=FindingType.SYSTEM_ERROR,
                    severity=Severity.CRITICAL,
                    title="Test Error",
                    message="This validator always fails",
                )
            )

            return ValidatorResult(
                validator_id=self.validator_id,
                status=ValidationStatus.ERROR,
                findings=findings,
            )

        if self.validator_id == "review_validator":
            findings.append(
                Finding(
                    validator_id=self.validator_id,
                    type=FindingType.CONTENT_QUALITY,
                    severity=Severity.HIGH,
                    title="Review Required",
                    message="This content needs human review",
                )
            )

            return ValidatorResult(
                validator_id=self.validator_id,
                status=ValidationStatus.NEEDS_HUMAN_REVIEW,
                findings=findings,
                metrics={"test_metric": 100},
            )

        return ValidatorResult(
            validator_id=self.validator_id,
            status=ValidationStatus.COMPLETED,
            findings=findings,
            metrics={"test_metric": 100},
        )

    def get_supported_content_types(self) -> list[str]:
        """Return supported content types"""
        return ["chapter", "manuscript"]

    async def on_configuration_change(self, _old_config: dict[str, Any], new_config: dict[str, Any]) -> None:
        """Handle configuration changes"""
        self.config = new_config

    async def cleanup(self) -> None:
        """Cleanup validator resources"""
        self.initialized = False
        self.validate_called = False
        self.last_content = None
        self.last_context = None
        self.config = {}


@pytest.fixture
async def engine():
    """Create and initialize a ValidationEngineImpl instance"""
    config = ValidationConfig(project_id="test_project")
    engine = ValidationEngineImpl()
    await engine.initialize(config)
    return engine


@pytest.mark.asyncio
async def test_initialization():
    """Test engine initialization"""
    config = ValidationConfig(project_id="test_project")
    engine = ValidationEngineImpl()

    # Engine should not be initialized yet
    assert not engine._initialized

    # Initialize engine
    await engine.initialize(config)

    # Engine should now be initialized
    assert engine._initialized
    assert engine.config == config


@pytest.mark.asyncio
async def test_validator_registration(engine):
    """Test validator registration"""
    # Create validator
    validator = MockValidator("test_validator")

    # Register validator
    await engine.register_validator(validator)

    # Validator should be registered and initialized
    assert "test_validator" in engine.validators
    assert validator.initialized

    # Get registered validators
    validators = await engine.get_registered_validators()
    assert len(validators) == 1
    assert validators[0]["id"] == "test_validator"


@pytest.mark.asyncio
async def test_validator_class_registration(engine):
    """Test validator class registration"""
    # Register validator class
    await engine.register_validator_class(MockValidator, validator_id="class_validator", name="Class Validator")

    # Validator should be registered
    assert "class_validator" in engine.validators

    # Get registered validators
    validators = await engine.get_registered_validators()
    assert len(validators) == 1
    assert validators[0]["id"] == "class_validator"
    assert validators[0]["name"] == "Class Validator"


@pytest.mark.asyncio
async def test_project_validation(engine):
    """Test project validation"""
    # Register validators
    validator1 = MockValidator("validator1")
    validator2 = MockValidator("validator2")
    await engine.register_validator(validator1)
    await engine.register_validator(validator2)

    # Create test project data
    project_data = {"test": "data"}

    # Validate project
    result = await engine.validate_project(project_data, "test_project")

    # Check validation result
    assert result.status == ValidationStatus.COMPLETED
    assert result.project_id == "test_project"
    assert len(result.validator_results) == 2
    assert "validator1" in result.validator_results
    assert "validator2" in result.validator_results

    # Validators should have been called
    assert validator1.validate_called
    assert validator2.validate_called
    assert validator1.last_content == project_data
    assert validator2.last_content == project_data


@pytest.mark.asyncio
async def test_chapter_validation(engine):
    """Test chapter validation"""
    # Register validator
    validator = MockValidator("chapter_validator")
    await engine.register_validator(validator)

    # Create test chapter data and context
    chapter_data = {"chapter_id": "ch1", "content": "Test content"}
    context = {"project_id": "test_project"}

    # Validate chapter
    result = await engine.validate_chapter(chapter_data, context)

    # Check validation result
    assert result.status == ValidationStatus.COMPLETED
    assert result.project_id == "test_project"
    assert len(result.validator_results) == 1
    assert "chapter_validator" in result.validator_results

    # Validator should have been called
    assert validator.validate_called
    assert validator.last_content == chapter_data
    assert validator.last_context == context


@pytest.mark.asyncio
async def test_validation_status(engine):
    """Test validation status tracking"""
    # Register validator
    await engine.register_validator(MockValidator("test_validator"))

    # Start validation
    project_data = {"test": "data"}
    result = await engine.validate_project(project_data, "test_project")

    # Check validation ID
    validation_id = result.validation_id
    assert validation_id

    # Validation should not be active anymore
    status = await engine.get_validation_status(validation_id)
    assert status is None


@pytest.mark.asyncio
async def test_parallel_validation(engine):
    """Test parallel validation"""
    # Configure engine for parallel processing
    engine.config.parallel_processing = True

    # Register validators
    await engine.register_validator(MockValidator("validator1"))
    await engine.register_validator(MockValidator("validator2"))
    await engine.register_validator(MockValidator("validator3"))

    # Validate project
    project_data = {"test": "data"}
    result = await engine.validate_project(project_data, "test_project")

    # Check validation result
    assert result.status == ValidationStatus.COMPLETED
    assert len(result.validator_results) == 3


@pytest.mark.asyncio
async def test_sequential_validation(engine):
    """Test sequential validation"""
    # Configure engine for sequential processing
    engine.config.parallel_processing = False

    # Register validators
    await engine.register_validator(MockValidator("validator1"))
    await engine.register_validator(MockValidator("validator2"))
    await engine.register_validator(MockValidator("validator3"))

    # Validate project
    project_data = {"test": "data"}
    result = await engine.validate_project(project_data, "test_project")

    # Check validation result
    assert result.status == ValidationStatus.COMPLETED
    assert len(result.validator_results) == 3


@pytest.mark.asyncio
async def test_fail_fast_validation(engine):
    """Test fail-fast validation"""
    # Configure engine for fail-fast
    engine.config.fail_fast = True
    engine.config.parallel_processing = False

    # Register validators
    await engine.register_validator(MockValidator("validator1"))
    await engine.register_validator(MockValidator("failing_validator"))
    await engine.register_validator(MockValidator("validator3"))  # Should not be called

    # Validate project
    project_data = {"test": "data"}
    result = await engine.validate_project(project_data, "test_project")

    # Check validation result
    assert result.status == ValidationStatus.ERROR
    assert len(result.validator_results) == 2  # Only first two validators should be called
    assert "validator1" in result.validator_results
    assert "failing_validator" in result.validator_results
    assert "validator3" not in result.validator_results


@pytest.mark.asyncio
async def test_human_review_detection(engine):
    """Test human review detection"""
    # Configure engine
    engine.config.human_review_threshold = 80.0

    # Register validators
    validator = MockValidator("review_validator")
    await engine.register_validator(validator)

    # Validate project
    project_data = {"test": "data"}
    result = await engine.validate_project(project_data, "test_project")

    # Check validation result
    assert result.status == ValidationStatus.NEEDS_HUMAN_REVIEW
    assert result.human_review_required


@pytest.mark.asyncio
async def test_config_file_operations():
    """Test configuration file operations"""
    # Create temporary directory for test files
    test_dir = Path(".test_tmp")
    test_dir.mkdir(exist_ok=True)

    try:
        # Create configuration
        config = ValidationConfig(
            project_id="file_test",
            quality_thresholds={"overall": 85.0},
            enabled_validators=["test_validator"],
        )

        # Create engine
        engine = ValidationEngineImpl()
        await engine.initialize(config)

        # Save configuration to YAML file
        yaml_path = test_dir / "test_config.yaml"
        await engine.save_config_to_file(config, str(yaml_path))
        assert yaml_path.exists()

        # Save configuration to JSON file
        json_path = test_dir / "test_config.json"
        await engine.save_config_to_file(config, str(json_path))
        assert json_path.exists()

        # Load configuration from YAML file
        loaded_yaml_config = await engine.load_config_from_file(str(yaml_path))
        assert loaded_yaml_config.project_id == "file_test"
        assert loaded_yaml_config.quality_thresholds["overall"] == 85.0
        assert loaded_yaml_config.enabled_validators == ["test_validator"]

        # Load configuration from JSON file
        loaded_json_config = await engine.load_config_from_file(str(json_path))
        assert loaded_json_config.project_id == "file_test"
        assert loaded_json_config.quality_thresholds["overall"] == 85.0
        assert loaded_json_config.enabled_validators == ["test_validator"]

    finally:
        # Clean up test files
        if yaml_path.exists():
            yaml_path.unlink()
        if json_path.exists():
            json_path.unlink()
        if test_dir.exists():
            test_dir.rmdir()


@pytest.mark.asyncio
async def test_enabled_validators(engine):
    """Test enabled validators filtering"""
    # Register validators
    await engine.register_validator(MockValidator("validator1"))
    await engine.register_validator(MockValidator("validator2"))
    await engine.register_validator(MockValidator("validator3"))

    # Set enabled validators
    engine.config.enabled_validators = ["validator1", "validator3"]

    # Validate project
    project_data = {"test": "data"}
    result = await engine.validate_project(project_data, "test_project")

    # Check validation result
    assert len(result.validator_results) == 2
    assert "validator1" in result.validator_results
    assert "validator2" not in result.validator_results
    assert "validator3" in result.validator_results


@pytest.mark.asyncio
async def test_validator_config(engine):
    """Test validator configuration"""
    # Create validator
    validator = MockValidator("config_validator")

    # Set validator config
    engine.config.validator_configs = {"config_validator": {"test_option": True, "threshold": 90.0}}

    # Register validator
    await engine.register_validator(validator)

    # Check if validator received its config
    assert validator.config == {"test_option": True, "threshold": 90.0}


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
