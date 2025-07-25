#!/usr/bin/env python3
"""
Validation Engine Usage Example

This example demonstrates how to use the ValidationEngine to validate content
and system code in LibriScribe.

Key features demonstrated:
1. Creating and configuring the validation engine
2. Registering validators
3. Validating projects and chapters
4. Processing validation results
5. Working with configuration files
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Import validation system components
from src.libriscribe.validation import (
    ValidationEngineImpl,
    ValidationConfig,
    ValidationStatus,
    Severity,
    Finding,
    FindingType,
    ValidatorResult
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockValidator:
    """Mock validator for demonstration purposes"""
    
    def __init__(self, validator_id: str, name: str, version: str = "1.0.0"):
        self.validator_id = validator_id
        self.name = name
        self.version = version
        self.config = {}
        
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize validator with configuration"""
        self.config = config
        logger.info(f"Initialized {self.name} with config: {config}")
        
    async def validate(self, content: Any, context: Dict[str, Any]):
        """Perform validation on content"""
        
        # Simulate validation logic
        findings = []
        
        # Add some sample findings
        if self.validator_id == "content_validator":
            findings.append(Finding(
                validator_id=self.validator_id,
                type=FindingType.CONTENT_QUALITY,
                severity=Severity.LOW,
                title="Minor content issue",
                message="Consider revising for clarity"
            ))
        elif self.validator_id == "publishing_validator":
            findings.append(Finding(
                validator_id=self.validator_id,
                type=FindingType.PUBLISHING_STANDARD,
                severity=Severity.MEDIUM,
                title="Formatting inconsistency",
                message="Chapter headings have inconsistent formatting"
            ))
            
        return ValidatorResult(
            validator_id=self.validator_id,
            status=ValidationStatus.COMPLETED,
            findings=findings,
            metrics={
                "quality_score": 85.0,
                "execution_time": 0.5
            }
        )
        
    def get_supported_content_types(self) -> list:
        """Return supported content types"""
        return ["chapter", "manuscript"]
        
    def get_validator_info(self) -> Dict[str, str]:
        """Get validator information"""
        return {
            "id": self.validator_id,
            "name": self.name,
            "version": self.version,
            "supported_types": self.get_supported_content_types()
        }


async def demonstrate_basic_usage():
    """Demonstrate basic usage of the validation engine"""
    
    print("\n1. 🚀 Basic ValidationEngine Usage")
    print("-" * 50)
    
    # Create validation configuration
    config = ValidationConfig(
        project_id="demo_project",
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
        enabled_validators=["content_validator", "publishing_validator"],
        validator_configs={
            "content_validator": {
                "check_tone_consistency": True,
                "check_outline_adherence": True
            },
            "publishing_validator": {
                "check_metadata": True,
                "check_formatting": True
            }
        }
    )
    
    print("✅ Created validation configuration")
    
    # Initialize validation engine
    engine = ValidationEngineImpl()
    await engine.initialize(config)
    print("✅ Initialized validation engine")
    
    # Register validators
    content_validator = MockValidator("content_validator", "Content Validator")
    publishing_validator = MockValidator("publishing_validator", "Publishing Standards Validator")
    
    await engine.register_validator(content_validator)
    await engine.register_validator(publishing_validator)
    print("✅ Registered validators")
    
    # Get registered validators
    validators = await engine.get_registered_validators()
    print(f"✅ Registered validators: {len(validators)}")
    for validator in validators:
        print(f"   - {validator['name']} (ID: {validator['id']}, Version: {validator['version']})")
    
    # Create sample project data
    project_data = {
        "title": "Sample Book",
        "author": "Demo Author",
        "chapters": [
            {"chapter_id": "ch1", "title": "Chapter 1", "content": "Chapter 1 content..."},
            {"chapter_id": "ch2", "title": "Chapter 2", "content": "Chapter 2 content..."}
        ],
        "metadata": {
            "genre": "fiction",
            "target_audience": "adult",
            "word_count": 50000
        }
    }
    
    # Validate project
    print("\n📝 Validating project...")
    validation_result = await engine.validate_project(project_data, "demo_project")
    
    # Process validation results
    print(f"✅ Validation completed with status: {validation_result.status}")
    print(f"✅ Overall quality score: {validation_result.overall_quality_score}")
    print(f"✅ Human review required: {validation_result.human_review_required}")
    
    # Print findings
    print("\n📋 Validation findings:")
    for validator_id, result in validation_result.validator_results.items():
        print(f"\n   {validator_id} findings:")
        if not result.findings:
            print("   - No findings")
        for finding in result.findings:
            print(f"   - {finding.severity.value}: {finding.title}")
            print(f"     {finding.message}")
    
    # Print summary
    print("\n📊 Validation summary:")
    for key, value in validation_result.summary.items():
        print(f"   - {key}: {value}")


async def demonstrate_configuration_management():
    """Demonstrate configuration management features"""
    
    print("\n2. ⚙️ Configuration Management")
    print("-" * 50)
    
    # Create a temporary directory for config files
    config_dir = Path(".demo/configs")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create validation configuration
    config = ValidationConfig(
        project_id="config_demo",
        validation_rules={
            "check_tone_consistency": True,
            "check_outline_adherence": True
        },
        quality_thresholds={
            "overall": 85.0,
            "tone_consistency": 90.0
        },
        human_review_threshold=80.0,
        enabled_validators=["content_validator", "quality_validator"],
        validator_configs={
            "content_validator": {
                "check_character_consistency": True,
                "check_narrative_flow": True
            },
            "quality_validator": {
                "check_grammar": True,
                "check_readability": True
            }
        },
        parallel_processing=True,
        output_formats=["json", "html"]
    )
    
    # Initialize engine
    engine = ValidationEngineImpl()
    await engine.initialize(config)
    
    # Save configuration to YAML file
    yaml_path = config_dir / "validation_config.yaml"
    await engine.save_config_to_file(config, str(yaml_path))
    print(f"✅ Saved configuration to YAML: {yaml_path}")
    
    # Save configuration to JSON file
    json_path = config_dir / "validation_config.json"
    await engine.save_config_to_file(config, str(json_path))
    print(f"✅ Saved configuration to JSON: {json_path}")
    
    # Load configuration from YAML file
    loaded_yaml_config = await engine.load_config_from_file(str(yaml_path))
    print(f"✅ Loaded configuration from YAML")
    print(f"   - Project ID: {loaded_yaml_config.project_id}")
    print(f"   - Enabled validators: {loaded_yaml_config.enabled_validators}")
    
    # Load configuration from JSON file
    loaded_json_config = await engine.load_config_from_file(str(json_path))
    print(f"✅ Loaded configuration from JSON")
    print(f"   - Project ID: {loaded_json_config.project_id}")
    print(f"   - Quality thresholds: {loaded_json_config.quality_thresholds}")
    
    # Modify and save updated configuration
    loaded_yaml_config.human_review_threshold = 70.0
    loaded_yaml_config.enabled_validators.append("publishing_validator")
    loaded_yaml_config.validator_configs["publishing_validator"] = {
        "check_metadata": True,
        "check_formatting": True
    }
    
    updated_yaml_path = config_dir / "updated_config.yaml"
    await engine.save_config_to_file(loaded_yaml_config, str(updated_yaml_path))
    print(f"✅ Saved updated configuration to: {updated_yaml_path}")


async def demonstrate_validator_registration():
    """Demonstrate validator registration methods"""
    
    print("\n3. 🔌 Validator Registration")
    print("-" * 50)
    
    # Create configuration
    config = ValidationConfig(project_id="registration_demo")
    
    # Initialize engine
    engine = ValidationEngineImpl()
    await engine.initialize(config)
    
    # Register validator instance
    content_validator = MockValidator("content_validator", "Content Validator")
    await engine.register_validator(content_validator)
    print("✅ Registered validator instance")
    
    # Define validator class
    class QualityValidator(MockValidator):
        def __init__(self, check_grammar=True, check_readability=True):
            super().__init__("quality_validator", "Quality Validator")
            self.check_grammar = check_grammar
            self.check_readability = check_readability
            
        async def validate(self, content, context):
            result = await super().validate(content, context)
            result.metrics["grammar_checked"] = self.check_grammar
            result.metrics["readability_checked"] = self.check_readability
            return result
    
    # Register validator class with arguments
    await engine.register_validator_class(
        QualityValidator,
        check_grammar=True,
        check_readability=True
    )
    print("✅ Registered validator class with arguments")
    
    # Get registered validators
    validators = await engine.get_registered_validators()
    print(f"✅ Registered validators: {len(validators)}")
    for validator in validators:
        print(f"   - {validator['name']} (ID: {validator['id']})")


async def demonstrate_chapter_validation():
    """Demonstrate chapter validation"""
    
    print("\n4. 📖 Chapter Validation")
    print("-" * 50)
    
    # Create configuration
    config = ValidationConfig(project_id="chapter_demo")
    
    # Initialize engine
    engine = ValidationEngineImpl()
    await engine.initialize(config)
    
    # Register validators
    content_validator = MockValidator("content_validator", "Content Validator")
    await engine.register_validator(content_validator)
    
    # Create sample chapter data
    chapter_data = {
        "chapter_id": "chapter_1",
        "title": "The Beginning",
        "content": "Once upon a time in a land far away...",
        "word_count": 2500,
        "scene_count": 3
    }
    
    # Create project context
    project_context = {
        "project_id": "chapter_demo",
        "genre": "fantasy",
        "tone": "adventurous",
        "target_audience": "young adult"
    }
    
    # Validate chapter
    print("📝 Validating chapter...")
    chapter_result = await engine.validate_chapter(chapter_data, project_context)
    
    # Process validation results
    print(f"✅ Chapter validation completed with status: {chapter_result.status}")
    print(f"✅ Quality score: {chapter_result.overall_quality_score}")
    
    # Print findings
    print("\n📋 Chapter validation findings:")
    for validator_id, result in chapter_result.validator_results.items():
        print(f"\n   {validator_id} findings:")
        if not result.findings:
            print("   - No findings")
        for finding in result.findings:
            print(f"   - {finding.severity.value}: {finding.title}")
            print(f"     {finding.message}")


async def demonstrate_error_handling():
    """Demonstrate error handling"""
    
    print("\n5. ⚠️ Error Handling")
    print("-" * 50)
    
    # Create engine
    engine = ValidationEngineImpl()
    
    # Try to use engine without initialization
    try:
        validators = await engine.get_registered_validators()
        print("❌ This should have failed!")
    except Exception as e:
        print(f"✅ Caught expected error: {e}")
    
    # Try to load non-existent configuration file
    try:
        config = await engine.load_config_from_file("non_existent_config.yaml")
        print("❌ This should have failed!")
    except Exception as e:
        print(f"✅ Caught expected error: {e}")
    
    # Initialize with invalid configuration
    try:
        from src.libriscribe.validation import ValidationConfig
        invalid_config = ValidationConfig(
            project_id="",  # Empty project ID
            human_review_threshold=150.0  # Invalid threshold (> 100)
        )
        await engine.initialize(invalid_config)
        print("❌ This should have failed!")
    except Exception as e:
        print(f"✅ Caught expected error: {e}")


if __name__ == "__main__":
    # Create demo directory
    Path(".demo").mkdir(exist_ok=True)
    
    # Run demonstrations
    asyncio.run(demonstrate_basic_usage())
    asyncio.run(demonstrate_configuration_management())
    asyncio.run(demonstrate_validator_registration())
    asyncio.run(demonstrate_chapter_validation())
    asyncio.run(demonstrate_error_handling())
    
    print("\n🎉 ValidationEngine demonstration completed!")