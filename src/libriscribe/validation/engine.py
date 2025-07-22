"""
Core validation engine implementation.

This module provides the main ValidationEngine implementation that orchestrates
validation processes and manages validator lifecycle.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .interfaces import (
    ValidationEngine,
    ValidatorBase,
    ValidationResult,
    ValidationConfig,
    ValidationStatus,
    ValidatorResult,
    Finding,
    FindingType,
    Severity,
    ValidationError,
    ValidatorNotFoundError
)


logger = logging.getLogger(__name__)


class ValidationEngineImpl(ValidationEngine):
    """Implementation of the core validation engine"""
    
    def __init__(self):
        self.config: Optional[ValidationConfig] = None
        self.validators: Dict[str, ValidatorBase] = {}
        self.active_validations: Dict[str, ValidationResult] = {}
        self._initialized = False
        
    async def initialize(self, config: ValidationConfig) -> None:
        """Initialize the validation engine with configuration"""
        try:
            self.config = config
            logger.info(f"Initializing validation engine for project: {config.project_id}")
            
            # Validate configuration
            await self._validate_config(config)
            
            # Initialize internal components
            await self._initialize_components()
            
            self._initialized = True
            logger.info("Validation engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize validation engine: {e}")
            raise ValidationError(f"Engine initialization failed: {e}") from e
            
    async def register_validator(self, validator: ValidatorBase) -> None:
        """Register a validator with the engine"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")
            
        try:
            # Initialize validator with its specific config
            validator_config = self.config.validator_configs.get(validator.validator_id, {})
            await validator.initialize(validator_config)
            
            # Register validator
            self.validators[validator.validator_id] = validator
            logger.info(f"Registered validator: {validator.validator_id}")
            
        except Exception as e:
            logger.error(f"Failed to register validator {validator.validator_id}: {e}")
            raise ValidationError(f"Validator registration failed: {e}") from e
            
    async def validate_project(self, project_data: Any, project_id: str) -> ValidationResult:
        """Validate a complete project"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")
            
        validation_result = ValidationResult(
            project_id=project_id,
            status=ValidationStatus.IN_PROGRESS
        )
        
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
            
    async def validate_chapter(self, chapter_data: Any, project_context: Dict[str, Any]) -> ValidationResult:
        """Validate individual chapter"""
        if not self._initialized:
            raise ValidationError("Engine not initialized")
            
        validation_result = ValidationResult(
            project_id=project_context.get("project_id", ""),
            status=ValidationStatus.IN_PROGRESS
        )
        
        try:
            start_time = datetime.now()
            logger.info(f"Starting chapter validation for project: {project_context.get('project_id')}")
            
            # Get validators that support chapter validation
            chapter_validators = [
                v for v in self._get_enabled_validators()
                if "chapter" in v.get_supported_content_types()
            ]
            
            if not chapter_validators:
                logger.warning("No chapter validators available")
                validation_result.status = ValidationStatus.COMPLETED
                return validation_result
                
            # Run chapter-specific validation
            validator_results = await self._run_validators_sequential(
                chapter_validators, chapter_data, project_context
            )
            
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
            
    async def get_validation_status(self, validation_id: str) -> Optional[ValidationResult]:
        """Get status of ongoing validation"""
        return self.active_validations.get(validation_id)
        
    async def get_registered_validators(self) -> List[Dict[str, str]]:
        """Get list of registered validators"""
        return [validator.get_validator_info() for validator in self.validators.values()]
        
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
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize other components as needed
        pass
        
    def _get_enabled_validators(self) -> List[ValidatorBase]:
        """Get list of enabled validators"""
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
        
    async def _run_validators_parallel(self, validators: List[ValidatorBase], 
                                     content: Any, context: Dict[str, Any]) -> Dict[str, ValidatorResult]:
        """Run validators in parallel"""
        tasks = []
        for validator in validators:
            task = asyncio.create_task(
                self._run_single_validator(validator, content, context)
            )
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
                    findings=[Finding(
                        validator_id=validator_id,
                        type=FindingType.SYSTEM_ERROR,
                        severity=Severity.CRITICAL,
                        title="Validator Error",
                        message=str(e)
                    )]
                )
                
        return results
        
    async def _run_validators_sequential(self, validators: List[ValidatorBase],
                                       content: Any, context: Dict[str, Any]) -> Dict[str, ValidatorResult]:
        """Run validators sequentially"""
        results = {}
        
        for validator in validators:
            try:
                result = await self._run_single_validator(validator, content, context)
                results[validator.validator_id] = result
                
                # Check for fail-fast conditions
                if self.config.fail_fast and result.status == ValidationStatus.ERROR:
                    logger.info(f"Fail-fast triggered by validator: {validator.validator_id}")
                    break
                    
            except Exception as e:
                logger.error(f"Validator {validator.validator_id} failed: {e}")
                results[validator.validator_id] = ValidatorResult(
                    validator_id=validator.validator_id,
                    status=ValidationStatus.ERROR,
                    findings=[Finding(
                        validator_id=validator.validator_id,
                        type=FindingType.SYSTEM_ERROR,
                        severity=Severity.CRITICAL,
                        title="Validator Error",
                        message=str(e)
                    )]
                )
                
                if self.config.fail_fast:
                    break
                    
        return results
        
    async def _run_single_validator(self, validator: ValidatorBase, 
                                  content: Any, context: Dict[str, Any]) -> ValidatorResult:
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
                findings=[Finding(
                    validator_id=validator.validator_id,
                    type=FindingType.SYSTEM_ERROR,
                    severity=Severity.CRITICAL,
                    title="Validator Execution Error",
                    message=str(e)
                )]
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
        validation_result.human_review_required = (
            validation_result.overall_quality_score < self.config.human_review_threshold
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
            "ai_usage": total_ai_usage
        }
        
        return validation_result
        
    def _calculate_quality_score(self, findings: List[Finding]) -> float:
        """Calculate overall quality score based on findings"""
        if not findings:
            return 100.0
            
        # Simple scoring algorithm - can be made more sophisticated
        severity_weights = {
            Severity.INFO: 0,
            Severity.LOW: 1,
            Severity.MEDIUM: 3,
            Severity.HIGH: 7,
            Severity.CRITICAL: 15
        }
        
        total_penalty = sum(severity_weights.get(finding.severity, 0) for finding in findings)
        
        # Base score of 100, subtract penalties
        score = max(0.0, 100.0 - total_penalty)
        
        return score
        
    def _count_findings_by_severity(self, findings: List[Finding]) -> Dict[str, int]:
        """Count findings by severity"""
        counts = {severity.value: 0 for severity in Severity}
        for finding in findings:
            counts[finding.severity.value] += 1
        return counts
        
    def _count_findings_by_type(self, findings: List[Finding]) -> Dict[str, int]:
        """Count findings by type"""
        counts = {finding_type.value: 0 for finding_type in FindingType}
        for finding in findings:
            counts[finding.type.value] += 1
        return counts
        
    def _determine_final_status(self, validation_result: ValidationResult) -> ValidationStatus:
        """Determine the final validation status"""
        # Check for errors
        error_results = [
            r for r in validation_result.validator_results.values()
            if r.status == ValidationStatus.ERROR
        ]
        
        if error_results:
            return ValidationStatus.ERROR
            
        # Check for human review requirement
        if validation_result.human_review_required:
            return ValidationStatus.NEEDS_HUMAN_REVIEW
            
        # Check for critical findings
        critical_findings = [
            f for result in validation_result.validator_results.values()
            for f in result.findings
            if f.severity == Severity.CRITICAL
        ]
        
        if critical_findings:
            return ValidationStatus.NEEDS_HUMAN_REVIEW
            
        return ValidationStatus.COMPLETED