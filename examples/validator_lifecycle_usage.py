#!/usr/bin/env python3
"""
Validator Lifecycle Usage Example

This example demonstrates the enhanced ValidatorBase class with comprehensive
lifecycle management, including hooks, configuration management, and error handling.

Features Demonstrated:
1. Lifecycle hooks (pre/post validation, error handling)
2. Dynamic configuration management
3. Quality threshold management
4. Finding creation helpers
5. Human review flagging
6. Error recovery mechanisms
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import validation system components
from src.libriscribe.validation import (
    ValidatorBase,
    ValidatorResult,
    ValidationStatus,
    Finding,
    FindingType,
    Severity,
    ContentLocation,
    ValidationError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdvancedContentValidator(ValidatorBase):
    """
    Advanced content validator demonstrating lifecycle management features
    """
    
    def __init__(self):
        super().__init__(
            validator_id="advanced_content_validator",
            name="Advanced Content Validator",
            version="2.0.0"
        )
        self.processing_stats = {
            "validations_run": 0,
            "errors_recovered": 0,
            "human_reviews_flagged": 0
        }
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize validator with comprehensive configuration"""
        self.config = config
        self.is_initialized = True
        
        # Configure validation rules
        self.configure_validation_rules({
            "min_word_count": config.get("min_word_count", 1000),
            "max_word_count": config.get("max_word_count", 10000),
            "check_grammar": config.get("check_grammar", True),
            "check_spelling": config.get("check_spelling", True),
            "check_readability": config.get("check_readability", True),
            "require_citations": config.get("require_citations", False),
            "check_tone_consistency": config.get("check_tone_consistency", True)
        })
        
        # Configure quality thresholds
        self.configure_quality_thresholds({
            "human_review": config.get("human_review_threshold", 70.0),
            "grammar_score": config.get("grammar_threshold", 85.0),
            "readability_score": config.get("readability_threshold", 75.0),
            "spelling_score": config.get("spelling_threshold", 90.0),
            "tone_consistency": config.get("tone_threshold", 80.0)
        })
        
        logger.info(f"Initialized {self.name} with {len(self.validation_rules)} rules and {len(self.quality_thresholds)} thresholds")
    
    async def validate(self, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        """Perform comprehensive content validation"""
        findings = []
        metrics = {}
        
        # Convert content to string for analysis
        text_content = str(content) if content else ""
        
        # Word count validation
        word_count = len(text_content.split())
        metrics["word_count"] = word_count
        
        min_words = self.get_validation_rule("min_word_count", 1000)
        max_words = self.get_validation_rule("max_word_count", 10000)
        
        if word_count < min_words:
            findings.append(self.create_finding(
                finding_type=FindingType.CONTENT_QUALITY,
                severity=Severity.HIGH,
                title="Insufficient Word Count",
                message=f"Content has {word_count} words, minimum required is {min_words}",
                location=ContentLocation(
                    content_type=context.get("content_type", "unknown"),
                    content_id=context.get("content_id", "unknown")
                ),
                remediation="Add more content to meet minimum word count requirement",
                confidence=1.0,
                metadata={"actual_count": word_count, "required_count": min_words}
            ))
        
        if word_count > max_words:
            findings.append(self.create_finding(
                finding_type=FindingType.CONTENT_QUALITY,
                severity=Severity.MEDIUM,
                title="Excessive Word Count",
                message=f"Content has {word_count} words, maximum allowed is {max_words}",
                location=ContentLocation(
                    content_type=context.get("content_type", "unknown"),
                    content_id=context.get("content_id", "unknown")
                ),
                remediation="Consider condensing content or splitting into multiple sections",
                confidence=0.9,
                metadata={"actual_count": word_count, "max_count": max_words}
            ))
        
        # Grammar validation (simulated)
        if self.get_validation_rule("check_grammar", True):
            grammar_score = self._simulate_grammar_check(text_content)
            metrics["grammar_score"] = grammar_score
            
            grammar_threshold = self.get_quality_threshold("grammar_score", 85.0)
            if grammar_score < grammar_threshold:
                findings.append(self.create_finding(
                    finding_type=FindingType.CONTENT_QUALITY,
                    severity=Severity.MEDIUM,
                    title="Grammar Issues Detected",
                    message=f"Grammar score {grammar_score:.1f} below threshold {grammar_threshold}",
                    remediation="Review and correct grammar errors",
                    confidence=0.8,
                    metadata={"grammar_score": grammar_score, "threshold": grammar_threshold}
                ))
        
        # Readability validation (simulated)
        if self.get_validation_rule("check_readability", True):
            readability_score = self._simulate_readability_check(text_content)
            metrics["readability_score"] = readability_score
            
            readability_threshold = self.get_quality_threshold("readability_score", 75.0)
            if readability_score < readability_threshold:
                findings.append(self.create_finding(
                    finding_type=FindingType.CONTENT_QUALITY,
                    severity=Severity.LOW,
                    title="Readability Could Be Improved",
                    message=f"Readability score {readability_score:.1f} below optimal threshold {readability_threshold}",
                    remediation="Consider simplifying sentence structure and vocabulary",
                    confidence=0.7,
                    metadata={"readability_score": readability_score, "threshold": readability_threshold}
                ))
        
        # Tone consistency validation (simulated)
        if self.get_validation_rule("check_tone_consistency", True):
            tone_score = self._simulate_tone_check(text_content, context)
            metrics["tone_consistency_score"] = tone_score
            
            tone_threshold = self.get_quality_threshold("tone_consistency", 80.0)
            if tone_score < tone_threshold:
                findings.append(self.create_finding(
                    finding_type=FindingType.TONE_CONSISTENCY,
                    severity=Severity.HIGH,
                    title="Tone Inconsistency Detected",
                    message=f"Tone consistency score {tone_score:.1f} below threshold {tone_threshold}",
                    remediation="Review content for consistent tone throughout",
                    confidence=0.85,
                    metadata={"tone_score": tone_score, "threshold": tone_threshold}
                ))
        
        # Calculate overall quality score
        overall_quality = self._calculate_overall_quality(metrics, findings)
        metrics["overall_quality_score"] = overall_quality
        
        # Update processing stats
        self.processing_stats["validations_run"] += 1
        
        # Check if human review is needed
        if self.should_flag_for_human_review(overall_quality):
            self.processing_stats["human_reviews_flagged"] += 1
            findings.append(self.create_finding(
                finding_type=FindingType.CONTENT_QUALITY,
                severity=Severity.HIGH,
                title="Human Review Required",
                message=f"Overall quality score {overall_quality:.1f} requires human review",
                remediation="Content should be reviewed by a human before proceeding",
                confidence=1.0,
                metadata={"quality_score": overall_quality, "review_threshold": self.get_quality_threshold("human_review")}
            ))
        
        return ValidatorResult(
            validator_id=self.validator_id,
            status=ValidationStatus.COMPLETED,
            findings=findings,
            metrics=metrics
        )
    
    def get_supported_content_types(self) -> List[str]:
        """Return supported content types"""
        return ["chapter", "manuscript", "scene", "outline", "character_description"]
    
    async def pre_validation_hook(self, content: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-validation processing with comprehensive context setup"""
        logger.info(f"Starting validation for {context.get('content_type', 'unknown')} content")
        
        # Add preprocessing metadata
        context["validation_start_time"] = datetime.now()
        context["content_length"] = len(str(content)) if content else 0
        context["validator_version"] = self.version
        context["preprocessing_applied"] = []
        
        # Simulate content preprocessing
        if context.get("content_type") == "chapter":
            context["preprocessing_applied"].append("chapter_structure_analysis")
        
        if self.get_validation_rule("check_grammar", True):
            context["preprocessing_applied"].append("grammar_preparation")
        
        logger.debug(f"Pre-validation context: {context}")
        return context
    
    async def post_validation_hook(self, result: ValidatorResult, content: Any, context: Dict[str, Any]) -> ValidatorResult:
        """Post-validation processing with result enhancement"""
        # Calculate execution time
        start_time = context.get("validation_start_time")
        if start_time:
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            result.metadata["execution_time_seconds"] = execution_time
        
        # Add processing statistics
        result.metadata["processing_stats"] = self.processing_stats.copy()
        result.metadata["validation_rules_applied"] = list(self.validation_rules.keys())
        result.metadata["quality_thresholds_checked"] = list(self.quality_thresholds.keys())
        
        # Add recommendations based on findings
        recommendations = self._generate_recommendations(result.findings)
        if recommendations:
            result.metadata["recommendations"] = recommendations
        
        # Log validation completion
        logger.info(f"Validation completed: {len(result.findings)} findings, quality score: {result.metrics.get('overall_quality_score', 'N/A')}")
        
        return result
    
    async def on_validation_error(self, error: Exception, content: Any, context: Dict[str, Any]) -> Optional[ValidatorResult]:
        """Error handling with recovery mechanisms"""
        logger.warning(f"Validation error occurred: {error}")
        
        # Attempt recovery for specific error types
        if isinstance(error, ConnectionError):
            logger.info("Attempting recovery from connection error using fallback validation")
            self.processing_stats["errors_recovered"] += 1
            
            # Provide basic fallback validation
            return ValidatorResult(
                validator_id=self.validator_id,
                status=ValidationStatus.COMPLETED,
                findings=[self.create_finding(
                    finding_type=FindingType.SYSTEM_ERROR,
                    severity=Severity.LOW,
                    title="Fallback Validation Applied",
                    message="Primary validation failed due to connection error, fallback validation used",
                    remediation="Consider re-running validation when connection is stable",
                    confidence=0.6,
                    metadata={"original_error": str(error), "fallback_used": True}
                )],
                metrics={"fallback_validation": True, "original_error": str(error)}
            )
        
        elif isinstance(error, ValueError):
            logger.info("Attempting recovery from value error")
            self.processing_stats["errors_recovered"] += 1
            
            return ValidatorResult(
                validator_id=self.validator_id,
                status=ValidationStatus.COMPLETED,
                findings=[self.create_finding(
                    finding_type=FindingType.SYSTEM_ERROR,
                    severity=Severity.MEDIUM,
                    title="Data Processing Error Recovered",
                    message=f"Data processing error occurred but was handled: {str(error)}",
                    remediation="Check input data format and try again",
                    confidence=0.7,
                    metadata={"original_error": str(error), "error_type": "ValueError"}
                )],
                metrics={"error_recovery": True, "original_error": str(error)}
            )
        
        # For other errors, let them propagate
        logger.error(f"Unrecoverable error: {error}")
        return None
    
    async def on_configuration_change(self, old_config: Dict[str, Any], new_config: Dict[str, Any]) -> None:
        """Handle configuration changes"""
        logger.info("Configuration changed, updating validator settings")
        
        # Log configuration changes
        changed_rules = set(new_config.get("validation_rules", {}).keys()) - set(old_config.get("validation_rules", {}).keys())
        if changed_rules:
            logger.info(f"New validation rules added: {changed_rules}")
        
        # Reinitialize if needed
        if new_config.get("reinitialize_on_change", False):
            await self.initialize(new_config)
    
    # Helper methods for simulated validation
    
    def _simulate_grammar_check(self, text: str) -> float:
        """Simulate grammar checking (returns score 0-100)"""
        # Simple simulation based on text characteristics
        if not text:
            return 0.0
        
        # Simulate grammar score based on text length and complexity
        base_score = 85.0
        
        # Penalize very short text
        if len(text) < 100:
            base_score -= 20.0
        
        # Penalize excessive punctuation (simulated grammar issues)
        punct_ratio = sum(1 for c in text if c in "!?.,;:") / len(text)
        if punct_ratio > 0.1:
            base_score -= 15.0
        
        return max(0.0, min(100.0, base_score))
    
    def _simulate_readability_check(self, text: str) -> float:
        """Simulate readability checking (returns score 0-100)"""
        if not text:
            return 0.0
        
        # Simple readability simulation
        words = text.split()
        if not words:
            return 0.0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentences = text.count('.') + text.count('!') + text.count('?')
        
        if sentences == 0:
            sentences = 1
        
        avg_sentence_length = len(words) / sentences
        
        # Simple readability formula (higher is better)
        readability = 100 - (avg_word_length * 5) - (avg_sentence_length * 2)
        
        return max(0.0, min(100.0, readability))
    
    def _simulate_tone_check(self, text: str, context: Dict[str, Any]) -> float:
        """Simulate tone consistency checking"""
        if not text:
            return 0.0
        
        # Simulate tone analysis
        expected_tone = context.get("expected_tone", "neutral")
        
        # Simple tone simulation based on word patterns
        positive_words = ["good", "great", "excellent", "wonderful", "amazing"]
        negative_words = ["bad", "terrible", "awful", "horrible", "dreadful"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate tone consistency score
        if expected_tone == "positive":
            return min(100.0, 70.0 + positive_count * 10 - negative_count * 5)
        elif expected_tone == "negative":
            return min(100.0, 70.0 + negative_count * 10 - positive_count * 5)
        else:  # neutral
            return min(100.0, 80.0 - abs(positive_count - negative_count) * 3)
    
    def _calculate_overall_quality(self, metrics: Dict[str, Any], findings: List[Finding]) -> float:
        """Calculate overall quality score"""
        base_score = 100.0
        
        # Deduct points for findings based on severity
        severity_penalties = {
            Severity.CRITICAL: 25.0,
            Severity.HIGH: 15.0,
            Severity.MEDIUM: 10.0,
            Severity.LOW: 5.0,
            Severity.INFO: 1.0
        }
        
        for finding in findings:
            base_score -= severity_penalties.get(finding.severity, 5.0)
        
        # Factor in individual metric scores
        metric_weights = {
            "grammar_score": 0.3,
            "readability_score": 0.2,
            "tone_consistency_score": 0.3
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for metric, weight in metric_weights.items():
            if metric in metrics:
                weighted_score += metrics[metric] * weight
                total_weight += weight
        
        if total_weight > 0:
            # Combine base score with weighted metrics
            final_score = (base_score * 0.4) + (weighted_score / total_weight * 0.6)
        else:
            final_score = base_score
        
        return max(0.0, min(100.0, final_score))
    
    def _generate_recommendations(self, findings: List[Finding]) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []
        
        # Group findings by type
        finding_types = {}
        for finding in findings:
            if finding.type not in finding_types:
                finding_types[finding.type] = []
            finding_types[finding.type].append(finding)
        
        # Generate type-specific recommendations
        if FindingType.CONTENT_QUALITY in finding_types:
            quality_findings = finding_types[FindingType.CONTENT_QUALITY]
            high_severity = [f for f in quality_findings if f.severity in [Severity.HIGH, Severity.CRITICAL]]
            
            if high_severity:
                recommendations.append("Priority: Address high-severity content quality issues first")
            
            if len(quality_findings) > 3:
                recommendations.append("Consider comprehensive content review due to multiple quality issues")
        
        if FindingType.TONE_CONSISTENCY in finding_types:
            recommendations.append("Review content for consistent tone and voice throughout")
        
        if any(f.severity == Severity.CRITICAL for f in findings):
            recommendations.append("Critical issues detected - content should not proceed without resolution")
        
        return recommendations
    
    async def cleanup(self) -> None:
        """Cleanup validator resources"""
        logger.info(f"Cleaning up {self.name}")
        logger.info(f"Final processing stats: {self.processing_stats}")
        
        # Reset processing stats
        self.processing_stats = {
            "validations_run": 0,
            "errors_recovered": 0,
            "human_reviews_flagged": 0
        }


async def demonstrate_validator_lifecycle():
    """
    Demonstrate comprehensive validator lifecycle management
    """
    
    print("🚀 Validator Lifecycle Management Demonstration")
    print("=" * 50)
    
    # 1. VALIDATOR INITIALIZATION
    print("\n1. 📋 Validator Initialization")
    print("-" * 30)
    
    validator = AdvancedContentValidator()
    
    # Initialize with comprehensive configuration
    config = {
        "min_word_count": 500,
        "max_word_count": 5000,
        "check_grammar": True,
        "check_spelling": True,
        "check_readability": True,
        "check_tone_consistency": True,
        "human_review_threshold": 75.0,
        "grammar_threshold": 80.0,
        "readability_threshold": 70.0,
        "tone_threshold": 85.0
    }
    
    await validator.initialize(config)
    
    print(f"✅ Initialized {validator.name}")
    print(f"   - Validation rules: {len(validator.validation_rules)}")
    print(f"   - Quality thresholds: {len(validator.quality_thresholds)}")
    
    # 2. CONFIGURATION MANAGEMENT
    print("\n2. ⚙️ Configuration Management")
    print("-" * 30)
    
    # Update validation rules
    validator.configure_validation_rules({
        "require_citations": True,
        "check_plagiarism": False
    })
    
    # Update quality thresholds
    validator.configure_quality_thresholds({
        "citation_coverage": 90.0,
        "originality_score": 95.0
    })
    
    print(f"✅ Updated configuration")
    print(f"   - Min word count: {validator.get_validation_rule('min_word_count')}")
    print(f"   - Grammar threshold: {validator.get_quality_threshold('grammar_score')}")
    print(f"   - Human review threshold: {validator.get_quality_threshold('human_review')}")
    
    # 3. CONTENT VALIDATION WITH LIFECYCLE
    print("\n3. 🔍 Content Validation with Lifecycle")
    print("-" * 30)
    
    # Test content samples
    test_contents = [
        {
            "content": "This is a very short text that will likely fail word count validation.",
            "context": {
                "content_type": "chapter",
                "content_id": "chapter_1",
                "expected_tone": "neutral"
            },
            "description": "Short content (should trigger word count issue)"
        },
        {
            "content": """
            This is a much longer piece of content that should meet the minimum word count requirements.
            It contains multiple sentences with varying complexity to test the readability algorithms.
            The grammar should be generally acceptable, though there might be some areas for improvement.
            This content is designed to demonstrate the comprehensive validation capabilities of the system.
            It includes various sentence structures and vocabulary to provide a realistic test case.
            The tone should be consistent throughout this sample text.
            """,
            "context": {
                "content_type": "chapter",
                "content_id": "chapter_2",
                "expected_tone": "neutral"
            },
            "description": "Good quality content (should pass most validations)"
        },
        {
            "content": "Bad bad bad terrible awful horrible content with many issues!!!",
            "context": {
                "content_type": "scene",
                "content_id": "scene_1",
                "expected_tone": "positive"
            },
            "description": "Poor quality content (should trigger multiple issues)"
        }
    ]
    
    for i, test_case in enumerate(test_contents, 1):
        print(f"\n   Test Case {i}: {test_case['description']}")
        
        try:
            # Use lifecycle validation method
            result = await validator.validate_with_lifecycle(
                test_case["content"],
                test_case["context"]
            )
            
            print(f"   ✅ Status: {result.status.value}")
            print(f"   📊 Quality Score: {result.metrics.get('overall_quality_score', 'N/A'):.1f}")
            print(f"   🔍 Findings: {len(result.findings)}")
            print(f"   ⏱️ Execution Time: {result.execution_time:.3f}s")
            
            # Show findings summary
            if result.findings:
                severity_counts = {}
                for finding in result.findings:
                    severity_counts[finding.severity.value] = severity_counts.get(finding.severity.value, 0) + 1
                
                print(f"   📋 Findings by severity: {severity_counts}")
                
                # Show critical/high findings
                critical_findings = [f for f in result.findings if f.severity in [Severity.CRITICAL, Severity.HIGH]]
                if critical_findings:
                    print(f"   ⚠️  Critical/High findings:")
                    for finding in critical_findings[:2]:  # Show first 2
                        print(f"      - {finding.title}")
            
            # Check human review requirement
            quality_score = result.metrics.get('overall_quality_score', 100)
            if validator.should_flag_for_human_review(quality_score):
                print(f"   👤 Human review required (score: {quality_score:.1f})")
            
        except Exception as e:
            print(f"   ❌ Validation failed: {e}")
    
    # 4. ERROR RECOVERY DEMONSTRATION
    print("\n4. 🛠️ Error Recovery Demonstration")
    print("-" * 30)
    
    # Simulate connection error
    class MockConnectionError(ConnectionError):
        pass
    
    # Temporarily override validate method to simulate error
    original_validate = validator.validate
    
    async def error_validate(content, context):
        if "error_test" in str(content):
            raise MockConnectionError("Simulated connection error")
        return await original_validate(content, context)
    
    validator.validate = error_validate
    
    try:
        result = await validator.validate_with_lifecycle(
            "error_test content",
            {"content_type": "test", "content_id": "error_test"}
        )
        
        print(f"   ✅ Error recovery successful")
        print(f"   📊 Status: {result.status.value}")
        print(f"   🔍 Findings: {len(result.findings)}")
        
        if result.findings:
            recovery_finding = result.findings[0]
            print(f"   🛠️ Recovery finding: {recovery_finding.title}")
            
    except Exception as e:
        print(f"   ❌ Error recovery failed: {e}")
    finally:
        # Restore original method
        validator.validate = original_validate
    
    # 5. VALIDATOR INFORMATION
    print("\n5. 📋 Validator Information")
    print("-" * 30)
    
    validator_info = validator.get_validator_info()
    print(f"   ID: {validator_info['id']}")
    print(f"   Name: {validator_info['name']}")
    print(f"   Version: {validator_info['version']}")
    print(f"   Supported Types: {validator_info['supported_types']}")
    print(f"   Initialized: {validator_info['is_initialized']}")
    print(f"   Validation Rules: {len(validator_info['validation_rules'])}")
    print(f"   Quality Thresholds: {len(validator_info['quality_thresholds'])}")
    
    # 6. PROCESSING STATISTICS
    print("\n6. 📈 Processing Statistics")
    print("-" * 30)
    
    stats = validator.processing_stats
    print(f"   Validations Run: {stats['validations_run']}")
    print(f"   Errors Recovered: {stats['errors_recovered']}")
    print(f"   Human Reviews Flagged: {stats['human_reviews_flagged']}")
    
    # 7. CLEANUP
    print("\n7. 🧹 Cleanup")
    print("-" * 30)
    
    await validator.cleanup()
    print(f"   ✅ Validator cleanup completed")
    
    print(f"\n🎉 Validator Lifecycle Demonstration Complete!")


async def demonstrate_configuration_scenarios():
    """
    Demonstrate different configuration scenarios
    """
    
    print("\n🔧 Configuration Scenarios Demonstration")
    print("=" * 50)
    
    # Scenario 1: Strict validation for professional publishing
    print("\n1. 📚 Professional Publishing Configuration")
    print("-" * 40)
    
    professional_validator = AdvancedContentValidator()
    await professional_validator.initialize({
        "min_word_count": 2000,
        "max_word_count": 8000,
        "check_grammar": True,
        "check_spelling": True,
        "check_readability": True,
        "check_tone_consistency": True,
        "require_citations": True,
        "human_review_threshold": 85.0,
        "grammar_threshold": 95.0,
        "readability_threshold": 80.0,
        "tone_threshold": 90.0
    })
    
    print(f"   ✅ Professional validator configured")
    print(f"   📊 Human review threshold: {professional_validator.get_quality_threshold('human_review')}")
    print(f"   📝 Grammar threshold: {professional_validator.get_quality_threshold('grammar_score')}")
    
    # Scenario 2: Lenient validation for draft content
    print("\n2. ✏️ Draft Content Configuration")
    print("-" * 40)
    
    draft_validator = AdvancedContentValidator()
    await draft_validator.initialize({
        "min_word_count": 200,
        "max_word_count": 15000,
        "check_grammar": False,
        "check_spelling": True,
        "check_readability": False,
        "check_tone_consistency": False,
        "require_citations": False,
        "human_review_threshold": 50.0,
        "grammar_threshold": 60.0,
        "spelling_threshold": 70.0
    })
    
    print(f"   ✅ Draft validator configured")
    print(f"   📊 Human review threshold: {draft_validator.get_quality_threshold('human_review')}")
    print(f"   📝 Spelling threshold: {draft_validator.get_quality_threshold('spelling_score')}")
    
    # Test same content with both configurations
    test_content = "This is a test content with some basic text for validation testing purposes."
    test_context = {"content_type": "chapter", "content_id": "test_chapter"}
    
    print(f"\n   Testing same content with both configurations:")
    
    # Professional validation
    prof_result = await professional_validator.validate_with_lifecycle(test_content, test_context)
    print(f"   📚 Professional: {len(prof_result.findings)} findings, quality: {prof_result.metrics.get('overall_quality_score', 0):.1f}")
    
    # Draft validation
    draft_result = await draft_validator.validate_with_lifecycle(test_content, test_context)
    print(f"   ✏️ Draft: {len(draft_result.findings)} findings, quality: {draft_result.metrics.get('overall_quality_score', 0):.1f}")
    
    await professional_validator.cleanup()
    await draft_validator.cleanup()


if __name__ == "__main__":
    # Run demonstrations
    asyncio.run(demonstrate_validator_lifecycle())
    asyncio.run(demonstrate_configuration_scenarios())
    
    print(f"\n🎯 Key Takeaways:")
    print(f"   1. ValidatorBase provides comprehensive lifecycle management")
    print(f"   2. Lifecycle hooks enable custom preprocessing and postprocessing")
    print(f"   3. Error recovery mechanisms provide robust validation")
    print(f"   4. Dynamic configuration allows flexible validation rules")
    print(f"   5. Quality thresholds enable automated human review flagging")
    print(f"   6. Helper methods simplify finding creation and management")
    print(f"\n📚 This demonstrates the enhanced ValidatorBase interface capabilities")