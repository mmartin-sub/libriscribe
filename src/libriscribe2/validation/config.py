"""
Configuration management for the LibriScribe validation system.

This module handles loading, validation, and management of validation configurations
including support for customizable validation rules and project-specific settings.
"""

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, ClassVar

import yaml

from .interfaces import ConfigurationError, ValidationConfig

logger = logging.getLogger(__name__)


class ValidationConfigManager:
    """Manages validation configuration loading and customization"""

    DEFAULT_CONFIG: ClassVar[dict[str, Any]] = {
        "quality_thresholds": {
            "overall": 70.0,
            "content_quality": 75.0,
            "tone_consistency": 80.0,
            "outline_adherence": 85.0,
            "security": 90.0,
            "code_quality": 80.0,
            "documentation": 70.0,
        },
        "enabled_validators": [
            "content_validator",
            "publishing_standards_validator",
            "quality_originality_validator",
            "ai_output_validator",
        ],
        "validator_configs": {
            "content_validator": {
                "check_tone_consistency": True,
                "check_outline_adherence": True,
                "detect_hallucinations": True,
                "max_chunk_size": 50000,
            },
            "publishing_standards_validator": {
                "check_formatting": True,
                "check_metadata": True,
                "check_length": True,
                "check_structure": True,
            },
            "quality_originality_validator": {
                "check_plagiarism": True,
                "check_grammar": True,
                "check_readability": True,
                "check_facts": True,
            },
            "ai_output_validator": {
                "check_coherence": True,
                "check_cross_agent_consistency": True,
                "validate_prompts": True,
            },
        },
        "ai_settings": {
            "mock_enabled": False,
            "usage_tracking": True,
            "litellm_config": {"timeout": 300, "max_retries": 3},
        },
        "processing": {
            "parallel_processing": True,
            "max_parallel_requests": 100,
            "request_timeout": 1200,
            "chunk_size_tokens": 50000,
        },
        "output": {"formats": ["json", "html"], "report_template": None},
        "workflow": {
            "auto_validate_chapters": True,
            "auto_validate_manuscript": True,
            "fail_fast": True,
        },
        "resources": {"temp_directory": None, "cleanup_on_completion": True},
        "monitoring": {"health_check_enabled": True, "metrics_collection": True},
    }

    GENRE_SPECIFIC_CONFIGS: ClassVar[dict[str, dict[str, Any]]] = {
        "fiction": {
            "quality_thresholds": {
                "tone_consistency": 85.0,
                "outline_adherence": 80.0,
                "content_quality": 75.0,
            },
            "validator_configs": {
                "content_validator": {
                    "check_character_consistency": True,
                    "check_narrative_flow": True,
                    "check_dialogue_quality": True,
                }
            },
        },
        "non_fiction": {
            "quality_thresholds": {
                "factual_accuracy": 90.0,
                "citation_quality": 85.0,
                "content_quality": 80.0,
            },
            "validator_configs": {
                "quality_originality_validator": {
                    "check_facts": True,
                    "check_citations": True,
                    "fact_checking_strict": True,
                }
            },
        },
        "children": {
            "quality_thresholds": {
                "content_appropriateness": 95.0,
                "language_complexity": 70.0,
            },
            "validator_configs": {
                "content_validator": {
                    "check_age_appropriateness": True,
                    "max_reading_level": 8,
                    "content_filters": ["violence", "adult_themes"],
                }
            },
        },
        "technical": {
            "quality_thresholds": {
                "accuracy": 90.0,
                "code_examples": 95.0,
                "documentation": 85.0,
            },
            "validator_configs": {
                "system_code_validator": {
                    "validate_code_examples": True,
                    "check_technical_accuracy": True,
                }
            },
        },
    }

    def __init__(self, config_dir: str | None = None):
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / ".libriscribe2"
        self.config_dir.mkdir(exist_ok=True)

    def load_config(self, project_id: str, genre: str | None = None) -> ValidationConfig:
        """Load validation configuration for a project"""
        try:
            # Start with default configuration
            config_dict = self.DEFAULT_CONFIG.copy()

            # Apply genre-specific configuration if specified
            if genre and genre in self.GENRE_SPECIFIC_CONFIGS:
                config_dict = self._merge_configs(config_dict, self.GENRE_SPECIFIC_CONFIGS[genre])
                logger.info(f"Applied genre-specific config for: {genre}")

            # Load global configuration file if exists
            global_config_path = self.config_dir / "validation_config.yaml"
            if global_config_path.exists():
                global_config = self._load_config_file(global_config_path)
                config_dict = self._merge_configs(config_dict, global_config)
                logger.info("Applied global configuration")

            # Load project-specific configuration if exists
            project_config_path = self.config_dir / f"validation_config_{project_id}.yaml"
            if project_config_path.exists():
                project_config = self._load_config_file(project_config_path)
                config_dict = self._merge_configs(config_dict, project_config)
                logger.info(f"Applied project-specific config for: {project_id}")

            # Create ValidationConfig object
            validation_config = self._dict_to_validation_config(config_dict, project_id)

            # Validate configuration
            self._validate_config(validation_config)

            logger.info(f"Configuration loaded successfully for project: {project_id}")
            return validation_config

        except Exception as e:
            logger.error(f"Failed to load configuration for project {project_id}: {e}")
            raise ConfigurationError(f"Configuration loading failed: {e}") from e

    def save_project_config(self, project_id: str, config: ValidationConfig) -> None:
        """Save project-specific configuration"""
        try:
            config_path = self.config_dir / f"validation_config_{project_id}.yaml"
            config_dict = asdict(config)

            # Remove project_id from saved config
            config_dict.pop("project_id", None)

            with open(config_path, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)

            logger.info(f"Project configuration saved: {project_id}")

        except Exception as e:
            logger.error(f"Failed to save project configuration {project_id}: {e}")
            raise ConfigurationError(f"Configuration save failed: {e}") from e

    def update_validation_rules(self, project_id: str, rules: dict[str, Any]) -> ValidationConfig:
        """Update validation rules for a project"""
        try:
            # Load current configuration
            current_config = self.load_config(project_id)

            # Update validation rules
            current_config.validation_rules.update(rules)

            # Update quality thresholds if provided
            if "quality_thresholds" in rules:
                current_config.quality_thresholds.update(rules["quality_thresholds"])

            # Update validator configs if provided
            if "validator_configs" in rules:
                for validator_id, validator_config in rules["validator_configs"].items():
                    if validator_id in current_config.validator_configs:
                        current_config.validator_configs[validator_id].update(validator_config)
                    else:
                        current_config.validator_configs[validator_id] = validator_config

            # Save updated configuration
            self.save_project_config(project_id, current_config)

            logger.info(f"Validation rules updated for project: {project_id}")
            return current_config

        except Exception as e:
            logger.error(f"Failed to update validation rules for project {project_id}: {e}")
            raise ConfigurationError(f"Rules update failed: {e}") from e

    def get_genre_configs(self) -> dict[str, dict[str, Any]]:
        """Get available genre-specific configurations"""
        return self.GENRE_SPECIFIC_CONFIGS.copy()

    def create_default_config_file(self, project_id: str | None = None) -> Path:
        """Create a default configuration file"""
        try:
            if project_id:
                config_path = self.config_dir / f"validation_config_{project_id}.yaml"
            else:
                config_path = self.config_dir / "validation_config.yaml"

            with open(config_path, "w") as f:
                yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, indent=2)

            logger.info(f"Default configuration file created: {config_path}")
            return config_path

        except Exception as e:
            logger.error(f"Failed to create default config file: {e}")
            raise ConfigurationError(f"Config file creation failed: {e}") from e

    # Private methods

    def _load_config_file(self, config_path: Path) -> dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path) as f:
                if config_path.suffix.lower() == ".json":
                    result = json.load(f)
                    return result if isinstance(result, dict) else {}
                else:
                    result = yaml.safe_load(f)
                    return result if isinstance(result, dict) else {}

        except Exception as e:
            logger.error(f"Failed to load config file {config_path}: {e}")
            raise ConfigurationError(f"Config file loading failed: {e}") from e

    def _merge_configs(self, base_config: dict[str, Any], override_config: dict[str, Any]) -> dict[str, Any]:
        """Merge two configuration dictionaries"""
        merged = base_config.copy()

        for key, value in override_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value

        return merged

    def _dict_to_validation_config(self, config_dict: dict[str, Any], project_id: str) -> ValidationConfig:
        """Convert dictionary to ValidationConfig object"""
        return ValidationConfig(
            project_id=project_id,
            validation_rules=config_dict.get("validation_rules", {}),
            quality_thresholds=config_dict.get("quality_thresholds", {}),
            human_review_threshold=config_dict.get("human_review_threshold", 70.0),
            enabled_validators=config_dict.get("enabled_validators", []),
            validator_configs=config_dict.get("validator_configs", {}),
            ai_mock_enabled=config_dict.get("ai_settings", {}).get("mock_enabled", False),
            ai_usage_tracking=config_dict.get("ai_settings", {}).get("usage_tracking", True),
            litellm_config=config_dict.get("ai_settings", {}).get("litellm_config", {}),
            parallel_processing=config_dict.get("processing", {}).get("parallel_processing", True),
            max_parallel_requests=config_dict.get("processing", {}).get("max_parallel_requests", 100),
            request_timeout=config_dict.get("processing", {}).get("request_timeout", 1200),
            chunk_size_tokens=config_dict.get("processing", {}).get("chunk_size_tokens", 50000),
            output_formats=config_dict.get("output", {}).get("formats", ["json", "html"]),
            report_template=config_dict.get("output", {}).get("report_template"),
            auto_validate_chapters=config_dict.get("workflow", {}).get("auto_validate_chapters", True),
            auto_validate_manuscript=config_dict.get("workflow", {}).get("auto_validate_manuscript", True),
            fail_fast=config_dict.get("workflow", {}).get("fail_fast", True),
            temp_directory=config_dict.get("resources", {}).get("temp_directory"),
            cleanup_on_completion=config_dict.get("resources", {}).get("cleanup_on_completion", True),
            health_check_enabled=config_dict.get("monitoring", {}).get("health_check_enabled", True),
            metrics_collection=config_dict.get("monitoring", {}).get("metrics_collection", True),
        )

    def _validate_config(self, config: ValidationConfig) -> None:
        """Validate configuration values"""
        if not config.project_id:
            raise ConfigurationError("Project ID is required")

        if config.human_review_threshold < 0 or config.human_review_threshold > 100:
            raise ConfigurationError("human_review_threshold must be between 0 and 100")

        if config.max_parallel_requests <= 0:
            raise ConfigurationError("max_parallel_requests must be positive")

        if config.request_timeout <= 0:
            raise ConfigurationError("request_timeout must be positive")

        if config.chunk_size_tokens <= 0:
            raise ConfigurationError("chunk_size_tokens must be positive")

        # Validate quality thresholds
        for threshold_name, threshold_value in config.quality_thresholds.items():
            if not isinstance(threshold_value, int | float):
                raise ConfigurationError(f"Quality threshold '{threshold_name}' must be numeric")
            if threshold_value < 0 or threshold_value > 100:
                raise ConfigurationError(f"Quality threshold '{threshold_name}' must be between 0 and 100")

        # Validate output formats
        supported_formats = ["json", "html", "pdf", "markdown", "csv"]
        for format_name in config.output_formats:
            if format_name not in supported_formats:
                raise ConfigurationError(f"Unsupported output format: {format_name}")

        logger.debug("Configuration validation passed")
