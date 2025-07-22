"""
AI Mock System for LibriScribe Validation

This module provides comprehensive mocking capabilities for AI interactions
to enable testing without consuming expensive AI resources.

Best Practices Implemented:
- Interface consistency with real AI calls
- Scenario-based testing (success, failure, edge cases)
- Record and playback system for deterministic testing
- Configuration-driven switching between mock and real AI
- Test coverage and accuracy metrics
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime
import uuid
import hashlib


logger = logging.getLogger(__name__)


class MockScenario(Enum):
    """Available mock scenarios for testing"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    INVALID_RESPONSE = "invalid_response"
    PARTIAL_FAILURE = "partial_failure"
    HIGH_QUALITY = "high_quality"
    LOW_QUALITY = "low_quality"
    EDGE_CASE = "edge_case"


@dataclass
class MockResponse:
    """Mock AI response structure"""
    content: str
    model: str
    tokens_used: int
    cost: float
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    scenario: MockScenario = MockScenario.SUCCESS


@dataclass
class RecordedInteraction:
    """Recorded AI interaction for playback"""
    interaction_id: str
    request_hash: str
    prompt: str
    response: MockResponse
    validator_id: str
    content_type: str
    timestamp: datetime
    real_ai_used: bool = True


class AIMockManager:
    """
    Manages AI mocking with record/playback capabilities
    
    Best Practices:
    1. Interface Consistency - Same response format as real AI
    2. Scenario Testing - Multiple test scenarios supported
    3. Record/Playback - Deterministic testing with real data
    4. Configuration Driven - Easy switching via config
    5. Metrics Tracking - Coverage and accuracy measurement
    """
    
    def __init__(self, mock_data_dir: Optional[str] = None):
        self.mock_data_dir = Path(mock_data_dir) if mock_data_dir else Path(".libriscribe/mock_data")
        self.mock_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.recorded_interactions: Dict[str, RecordedInteraction] = {}
        self.mock_responses: Dict[str, Dict[str, MockResponse]] = {}
        self.usage_stats = {
            "mock_calls": 0,
            "real_calls": 0,
            "scenarios_used": {},
            "validators_tested": set(),
            "coverage_metrics": {}
        }
        
        # Load existing mock data
        self._load_mock_data()
        
    async def get_ai_response(self, 
                            prompt: str, 
                            validator_id: str,
                            content_type: str,
                            scenario: Optional[MockScenario] = None,
                            use_mock: bool = True) -> MockResponse:
        """
        Get AI response - either mock or real based on configuration
        
        Args:
            prompt: The AI prompt
            validator_id: ID of the validator making the request
            content_type: Type of content being validated
            scenario: Specific mock scenario to use
            use_mock: Whether to use mock (True) or real AI (False)
        """
        
        if use_mock:
            return await self._get_mock_response(prompt, validator_id, content_type, scenario)
        else:
            # This would call real AI through LiteLLM
            response = await self._call_real_ai(prompt, validator_id, content_type)
            
            # Record the interaction for future playback
            await self._record_interaction(prompt, response, validator_id, content_type)
            
            return response
            
    async def _get_mock_response(self, 
                               prompt: str, 
                               validator_id: str,
                               content_type: str,
                               scenario: Optional[MockScenario] = None) -> MockResponse:
        """Get mock AI response based on scenario or recorded data"""
        
        self.usage_stats["mock_calls"] += 1
        self.usage_stats["validators_tested"].add(validator_id)
        
        # Generate request hash for consistent responses
        request_hash = self._generate_request_hash(prompt, validator_id, content_type)
        
        # Try to find recorded interaction first
        if request_hash in self.recorded_interactions:
            recorded = self.recorded_interactions[request_hash]
            logger.debug(f"Using recorded response for {validator_id}")
            return recorded.response
            
        # Use scenario-based mock response
        if scenario is None:
            scenario = MockScenario.SUCCESS
            
        self.usage_stats["scenarios_used"][scenario.value] = \
            self.usage_stats["scenarios_used"].get(scenario.value, 0) + 1
            
        return await self._generate_scenario_response(prompt, validator_id, content_type, scenario)
        
    async def _generate_scenario_response(self, 
                                        prompt: str, 
                                        validator_id: str,
                                        content_type: str,
                                        scenario: MockScenario) -> MockResponse:
        """Generate mock response based on scenario"""
        
        # Simulate AI processing delay
        await asyncio.sleep(0.1)
        
        if scenario == MockScenario.SUCCESS:
            return self._create_success_response(prompt, validator_id, content_type)
        elif scenario == MockScenario.HIGH_QUALITY:
            return self._create_high_quality_response(prompt, validator_id, content_type)
        elif scenario == MockScenario.LOW_QUALITY:
            return self._create_low_quality_response(prompt, validator_id, content_type)
        elif scenario == MockScenario.FAILURE:
            return self._create_failure_response(prompt, validator_id, content_type)
        elif scenario == MockScenario.TIMEOUT:
            await asyncio.sleep(5)  # Simulate timeout
            raise TimeoutError("Mock AI timeout")
        elif scenario == MockScenario.RATE_LIMIT:
            raise Exception("Rate limit exceeded (mock)")
        elif scenario == MockScenario.INVALID_RESPONSE:
            return self._create_invalid_response(prompt, validator_id, content_type)
        elif scenario == MockScenario.PARTIAL_FAILURE:
            return self._create_partial_failure_response(prompt, validator_id, content_type)
        elif scenario == MockScenario.EDGE_CASE:
            return self._create_edge_case_response(prompt, validator_id, content_type)
        else:
            return self._create_success_response(prompt, validator_id, content_type)
            
    def _create_success_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create a successful mock response"""
        
        # Generate validator-specific response
        if validator_id == "content_validator":
            content = json.dumps({
                "tone_consistency_score": 85.0,
                "outline_adherence_score": 90.0,
                "quality_score": 87.5,
                "findings": [
                    {
                        "type": "tone_consistency",
                        "severity": "low",
                        "message": "Minor tone variation in chapter 3",
                        "confidence": 0.8
                    }
                ],
                "recommendations": [
                    "Consider reviewing tone consistency in chapter 3"
                ]
            })
        elif validator_id == "publishing_standards_validator":
            content = json.dumps({
                "formatting_score": 95.0,
                "metadata_completeness": 100.0,
                "structure_score": 92.0,
                "findings": [],
                "publishing_ready": True
            })
        elif validator_id == "quality_originality_validator":
            content = json.dumps({
                "originality_score": 98.0,
                "grammar_score": 94.0,
                "readability_score": 88.0,
                "plagiarism_detected": False,
                "findings": [
                    {
                        "type": "grammar",
                        "severity": "low",
                        "message": "Minor grammar issue on page 45",
                        "confidence": 0.9
                    }
                ]
            })
        else:
            content = json.dumps({
                "validation_score": 85.0,
                "status": "passed",
                "findings": [],
                "recommendations": []
            })
            
        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=150,
            cost=0.003,
            confidence=0.9,
            scenario=MockScenario.SUCCESS,
            metadata={
                "validator_id": validator_id,
                "content_type": content_type,
                "mock_generated": True
            }
        )
        
    def _create_high_quality_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create a high-quality mock response (scores > 90)"""
        content = json.dumps({
            "validation_score": 95.0,
            "quality_score": 96.0,
            "status": "excellent",
            "findings": [],
            "recommendations": ["Content meets high quality standards"]
        })
        
        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=120,
            cost=0.0024,
            confidence=0.95,
            scenario=MockScenario.HIGH_QUALITY
        )
        
    def _create_low_quality_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create a low-quality mock response (scores < 70)"""
        content = json.dumps({
            "validation_score": 65.0,
            "quality_score": 62.0,
            "status": "needs_review",
            "findings": [
                {
                    "type": "content_quality",
                    "severity": "high",
                    "message": "Content quality below threshold",
                    "confidence": 0.9
                },
                {
                    "type": "tone_consistency",
                    "severity": "medium",
                    "message": "Inconsistent tone throughout",
                    "confidence": 0.8
                }
            ],
            "recommendations": [
                "Human review required",
                "Consider regenerating content",
                "Review tone consistency"
            ]
        })
        
        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=200,
            cost=0.004,
            confidence=0.85,
            scenario=MockScenario.LOW_QUALITY
        )
        
    def _create_failure_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create a failure mock response"""
        content = json.dumps({
            "error": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "message": "Unable to complete validation due to content issues",
            "status": "failed"
        })
        
        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=50,
            cost=0.001,
            confidence=0.0,
            scenario=MockScenario.FAILURE
        )
        
    def _create_invalid_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create an invalid/malformed mock response"""
        content = "{ invalid json response for testing"  # Malformed JSON
        
        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=30,
            cost=0.0006,
            confidence=0.0,
            scenario=MockScenario.INVALID_RESPONSE
        )
        
    def _create_partial_failure_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create a partial failure mock response"""
        content = json.dumps({
            "validation_score": 75.0,
            "status": "partial_success",
            "completed_checks": ["grammar", "structure"],
            "failed_checks": ["tone_consistency", "originality"],
            "findings": [
                {
                    "type": "system_error",
                    "severity": "medium",
                    "message": "Unable to complete tone analysis",
                    "confidence": 0.0
                }
            ],
            "recommendations": ["Retry validation", "Check system resources"]
        })
        
        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=180,
            cost=0.0036,
            confidence=0.7,
            scenario=MockScenario.PARTIAL_FAILURE
        )
        
    def _create_edge_case_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create an edge case mock response"""
        content = json.dumps({
            "validation_score": 0.0,  # Edge case: zero score
            "status": "edge_case",
            "findings": [
                {
                    "type": "edge_case",
                    "severity": "info",
                    "message": "Empty content detected",
                    "confidence": 1.0
                }
            ],
            "metadata": {
                "content_length": 0,
                "processing_time": 0.001
            }
        })
        
        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=1,
            cost=0.00002,
            confidence=1.0,
            scenario=MockScenario.EDGE_CASE
        )
        
    async def _call_real_ai(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Call real AI through LiteLLM (placeholder implementation)"""
        
        self.usage_stats["real_calls"] += 1
        
        # This would integrate with the actual LiteLLM proxy
        # For now, return a mock response that simulates real AI
        logger.info(f"Calling real AI for {validator_id} (mock implementation)")
        
        # Simulate real AI call delay
        await asyncio.sleep(2.0)
        
        # Return realistic response
        return MockResponse(
            content=json.dumps({
                "validation_score": 82.0,
                "status": "completed",
                "findings": [],
                "real_ai_response": True
            }),
            model="gpt-4",
            tokens_used=175,
            cost=0.0035,
            confidence=0.92,
            metadata={"real_ai": True}
        )
        
    async def _record_interaction(self, 
                                prompt: str, 
                                response: MockResponse, 
                                validator_id: str,
                                content_type: str) -> None:
        """Record AI interaction for future playback"""
        
        request_hash = self._generate_request_hash(prompt, validator_id, content_type)
        
        interaction = RecordedInteraction(
            interaction_id=str(uuid.uuid4()),
            request_hash=request_hash,
            prompt=prompt,
            response=response,
            validator_id=validator_id,
            content_type=content_type,
            timestamp=datetime.now(),
            real_ai_used=True
        )
        
        self.recorded_interactions[request_hash] = interaction
        
        # Save to disk
        await self._save_recorded_interaction(interaction)
        
    def _generate_request_hash(self, prompt: str, validator_id: str, content_type: str) -> str:
        """Generate consistent hash for request caching"""
        content = f"{prompt}|{validator_id}|{content_type}"
        return hashlib.md5(content.encode()).hexdigest()
        
    def _load_mock_data(self) -> None:
        """Load existing mock data from disk"""
        
        # Load recorded interactions
        interactions_file = self.mock_data_dir / "recorded_interactions.json"
        if interactions_file.exists():
            try:
                with open(interactions_file, 'r') as f:
                    data = json.load(f)
                    
                for item in data:
                    interaction = RecordedInteraction(
                        interaction_id=item["interaction_id"],
                        request_hash=item["request_hash"],
                        prompt=item["prompt"],
                        response=MockResponse(**item["response"]),
                        validator_id=item["validator_id"],
                        content_type=item["content_type"],
                        timestamp=datetime.fromisoformat(item["timestamp"]),
                        real_ai_used=item.get("real_ai_used", True)
                    )
                    self.recorded_interactions[interaction.request_hash] = interaction
                    
                logger.info(f"Loaded {len(self.recorded_interactions)} recorded interactions")
                
            except Exception as e:
                logger.error(f"Failed to load recorded interactions: {e}")
                
        # Load custom mock responses
        mock_responses_file = self.mock_data_dir / "mock_responses.json"
        if mock_responses_file.exists():
            try:
                with open(mock_responses_file, 'r') as f:
                    self.mock_responses = json.load(f)
                logger.info(f"Loaded custom mock responses for {len(self.mock_responses)} validators")
            except Exception as e:
                logger.error(f"Failed to load mock responses: {e}")
                
    async def _save_recorded_interaction(self, interaction: RecordedInteraction) -> None:
        """Save recorded interaction to disk"""
        
        interactions_file = self.mock_data_dir / "recorded_interactions.json"
        
        # Load existing data
        existing_data = []
        if interactions_file.exists():
            try:
                with open(interactions_file, 'r') as f:
                    existing_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load existing interactions: {e}")
                
        # Add new interaction
        interaction_data = {
            "interaction_id": interaction.interaction_id,
            "request_hash": interaction.request_hash,
            "prompt": interaction.prompt,
            "response": {
                "content": interaction.response.content,
                "model": interaction.response.model,
                "tokens_used": interaction.response.tokens_used,
                "cost": interaction.response.cost,
                "confidence": interaction.response.confidence,
                "metadata": interaction.response.metadata,
                "timestamp": interaction.response.timestamp.isoformat(),
                "scenario": interaction.response.scenario.value
            },
            "validator_id": interaction.validator_id,
            "content_type": interaction.content_type,
            "timestamp": interaction.timestamp.isoformat(),
            "real_ai_used": interaction.real_ai_used
        }
        
        existing_data.append(interaction_data)
        
        # Save to disk
        try:
            with open(interactions_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save recorded interaction: {e}")
            
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get mock system usage statistics"""
        return {
            **self.usage_stats,
            "validators_tested": list(self.usage_stats["validators_tested"]),
            "recorded_interactions": len(self.recorded_interactions),
            "mock_coverage": self._calculate_mock_coverage()
        }
        
    def _calculate_mock_coverage(self) -> Dict[str, Any]:
        """Calculate test coverage metrics"""
        
        total_validators = len(self.usage_stats["validators_tested"])
        scenarios_covered = len(self.usage_stats["scenarios_used"])
        
        return {
            "validators_tested": total_validators,
            "scenarios_covered": scenarios_covered,
            "total_scenarios": len(MockScenario),
            "coverage_percentage": (scenarios_covered / len(MockScenario)) * 100,
            "recorded_interactions": len(self.recorded_interactions)
        }
        
    async def create_test_suite(self, validators: List[str]) -> Dict[str, List[MockScenario]]:
        """Create comprehensive test suite for validators"""
        
        test_suite = {}
        
        for validator_id in validators:
            # Create test scenarios for each validator
            test_suite[validator_id] = [
                MockScenario.SUCCESS,
                MockScenario.HIGH_QUALITY,
                MockScenario.LOW_QUALITY,
                MockScenario.FAILURE,
                MockScenario.PARTIAL_FAILURE,
                MockScenario.EDGE_CASE
            ]
            
        return test_suite
        
    async def run_test_suite(self, test_suite: Dict[str, List[MockScenario]]) -> Dict[str, Any]:
        """Run comprehensive test suite and return results"""
        
        results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "validator_results": {},
            "scenario_results": {},
            "coverage_report": {}
        }
        
        for validator_id, scenarios in test_suite.items():
            validator_results = {
                "passed": 0,
                "failed": 0,
                "scenarios": {}
            }
            
            for scenario in scenarios:
                try:
                    response = await self.get_ai_response(
                        prompt=f"Test prompt for {validator_id}",
                        validator_id=validator_id,
                        content_type="test",
                        scenario=scenario,
                        use_mock=True
                    )
                    
                    validator_results["passed"] += 1
                    validator_results["scenarios"][scenario.value] = "passed"
                    results["passed_tests"] += 1
                    
                except Exception as e:
                    validator_results["failed"] += 1
                    validator_results["scenarios"][scenario.value] = f"failed: {str(e)}"
                    results["failed_tests"] += 1
                    
                results["total_tests"] += 1
                
            results["validator_results"][validator_id] = validator_results
            
        # Generate coverage report
        results["coverage_report"] = self._calculate_mock_coverage()
        
        return results


# Utility functions for easy integration

async def create_mock_manager(config: Dict[str, Any]) -> AIMockManager:
    """Create and configure AI mock manager"""
    
    mock_data_dir = config.get("mock_data_dir", ".libriscribe/mock_data")
    manager = AIMockManager(mock_data_dir)
    
    return manager


def get_mock_config_for_testing() -> Dict[str, Any]:
    """Get recommended mock configuration for testing"""
    
    return {
        "ai_mock_enabled": True,
        "mock_data_dir": ".libriscribe/mock_data",
        "default_scenario": "success",
        "record_real_interactions": True,
        "test_coverage_required": 80.0,
        "scenarios_to_test": [
            "success",
            "high_quality", 
            "low_quality",
            "failure",
            "partial_failure",
            "edge_case"
        ]
    }