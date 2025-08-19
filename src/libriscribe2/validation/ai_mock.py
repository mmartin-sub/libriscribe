"""
AI Mock System for LibriScribe Validation

This module provides comprehensive mocking capabilities for AI interactions
to enable testing without consuming expensive AI resources.

Key Features:
- Uses OpenAI SDK with LiteLLM configured via .env (transparent to service)
- API key-based switching (empty OPENAI_API_KEY = mock mode)
- Live response recording for input/output mapping population
- Scenario-based testing (success, failure, edge cases)
- Deterministic testing with recorded real responses
"""

import asyncio
import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..settings import Settings

# OpenAI SDK import
logger = logging.getLogger(__name__)

# OpenAI SDK import
try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"OpenAI SDK not available: {e}. Mock mode will be used.")
    OPENAI_AVAILABLE = False


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
    metadata: dict[str, Any] = field(default_factory=dict)
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
    Manages AI interactions with automatic mock/real switching based on API key

    Key Features:
    1. OpenAI SDK with LiteLLM via .env configuration (transparent)
    2. API key-based switching (empty OPENAI_API_KEY = mock mode)
    3. Live response recording for input/output mapping population
    4. Scenario-based testing with recorded real responses
    5. Deterministic testing and coverage tracking
    """

    def __init__(self, mock_data_dir: str | None = None):
        # Type annotations for instance variables
        self.openai_client: AsyncOpenAI | None
        self.recorded_interactions: dict[str, RecordedInteraction]
        self.mock_responses: dict[str, dict[str, MockResponse]]
        self.usage_stats: dict[str, Any]

        self.mock_data_dir = Path(mock_data_dir) if mock_data_dir else Path(".libriscribe2/mock_data")
        self.mock_data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize OpenAI client (LiteLLM configured via .env)
        self.settings = Settings()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", self.settings.openai_base_url_default)

        # Determine if we should use mock based on API key
        self.use_mock_mode = not bool(self.openai_api_key.strip())

        # Initialize OpenAI client with proper type annotation
        if not self.use_mock_mode and OPENAI_AVAILABLE:
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key, base_url=self.openai_base_url)
            logger.info(f"OpenAI client initialized with base URL: {self.openai_base_url}")
        else:
            self.openai_client = None
            if not self.use_mock_mode:
                logger.warning("OpenAI API key provided but OpenAI SDK not available. Using mock mode.")
                self.use_mock_mode = True
            else:
                logger.info("No OpenAI API key found. Using mock mode.")

        self.recorded_interactions = {}
        self.mock_responses = {}
        self.usage_stats = {
            "mock_calls": 0,
            "real_calls": 0,
            "scenarios_used": {},
            "validators_tested": set(),
            "coverage_metrics": {},
            "live_recordings": 0,
        }

        # Load existing mock data
        self._load_mock_data()

    async def get_ai_response(
        self,
        prompt: str,
        validator_id: str,
        content_type: str,
        model: str = "gpt-4",
        scenario: MockScenario | None = None,
    ) -> MockResponse:
        """
        Get AI response - automatically switches between mock and real based on API key

        Args:
            prompt: The AI prompt
            validator_id: ID of the validator making the request
            content_type: Type of content being validated
            model: OpenAI model to use (e.g., "gpt-4", "gpt-3.5-turbo")
            scenario: Specific mock scenario to use (only for mock mode)

        Returns:
            MockResponse: Standardized response structure
        """

        if self.use_mock_mode:
            return await self._get_mock_response(prompt, validator_id, content_type, scenario)
        else:
            # Call real AI through OpenAI SDK (LiteLLM configured via .env)
            response = await self._call_real_ai(prompt, validator_id, content_type, model)

            # Automatically record the interaction for future mock use
            await self._record_interaction(prompt, response, validator_id, content_type)

            return response

    async def _get_mock_response(
        self,
        prompt: str,
        validator_id: str,
        content_type: str,
        scenario: MockScenario | None = None,
    ) -> MockResponse:
        """Get mock AI response based on scenario or recorded data"""

        mock_calls = self.usage_stats.get("mock_calls", 0)
        self.usage_stats["mock_calls"] = mock_calls + 1

        validators_tested = self.usage_stats.get("validators_tested", set())
        if isinstance(validators_tested, set):
            validators_tested.add(validator_id)
            self.usage_stats["validators_tested"] = validators_tested

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

        scenarios_used = self.usage_stats.get("scenarios_used", {})
        if isinstance(scenarios_used, dict):
            current_count = scenarios_used.get(scenario.value, 0)
            scenarios_used[scenario.value] = current_count + 1
            self.usage_stats["scenarios_used"] = scenarios_used

        return await self._generate_scenario_response(prompt, validator_id, content_type, scenario)

    async def _generate_scenario_response(
        self, prompt: str, validator_id: str, content_type: str, scenario: MockScenario
    ) -> MockResponse:
        """Generate mock response based on scenario"""

        # Simulate AI processing delay
        await asyncio.sleep(0.1)

        # Handle all scenarios with explicit returns
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

        # This should never be reached, but mypy needs it
        raise AssertionError(f"Unhandled scenario: {scenario}")

    def _create_success_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create a successful mock response"""

        # Generate validator-specific response
        if validator_id == "content_validator":
            content = json.dumps(
                {
                    "tone_consistency_score": 85.0,
                    "outline_adherence_score": 90.0,
                    "quality_score": 87.5,
                    "findings": [
                        {
                            "type": "tone_consistency",
                            "severity": "low",
                            "message": "Minor tone variation in chapter 3",
                            "confidence": 0.8,
                        }
                    ],
                    "recommendations": ["Consider reviewing tone consistency in chapter 3"],
                },
                ensure_ascii=False,
            )
        elif validator_id == "publishing_standards_validator":
            content = json.dumps(
                {
                    "formatting_score": 95.0,
                    "metadata_completeness": 100.0,
                    "structure_score": 92.0,
                    "findings": [],
                    "publishing_ready": True,
                },
                ensure_ascii=False,
            )
        elif validator_id == "quality_originality_validator":
            content = json.dumps(
                {
                    "originality_score": 98.0,
                    "grammar_score": 94.0,
                    "readability_score": 88.0,
                    "plagiarism_detected": False,
                    "findings": [
                        {
                            "type": "grammar",
                            "severity": "low",
                            "message": "Minor grammar issue on page 45",
                            "confidence": 0.9,
                        }
                    ],
                },
                ensure_ascii=False,
            )
        else:
            content = json.dumps(
                {
                    "validation_score": 85.0,
                    "status": "passed",
                    "findings": [],
                    "recommendations": [],
                },
                ensure_ascii=False,
            )

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
                "mock_generated": True,
            },
        )

    def _create_high_quality_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create a high-quality mock response (scores > 90)"""
        content = json.dumps(
            {
                "validation_score": 95.0,
                "quality_score": 96.0,
                "status": "excellent",
                "findings": [],
                "recommendations": ["Content meets high quality standards"],
            },
            ensure_ascii=False,
        )

        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=120,
            cost=0.0024,
            confidence=0.95,
            scenario=MockScenario.HIGH_QUALITY,
        )

    def _create_low_quality_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create a low-quality mock response (scores < 70)"""
        content = json.dumps(
            {
                "validation_score": 65.0,
                "quality_score": 62.0,
                "status": "needs_review",
                "findings": [
                    {
                        "type": "content_quality",
                        "severity": "high",
                        "message": "Content quality below threshold",
                        "confidence": 0.9,
                    },
                    {
                        "type": "tone_consistency",
                        "severity": "medium",
                        "message": "Inconsistent tone throughout",
                        "confidence": 0.8,
                    },
                ],
                "recommendations": [
                    "Human review required",
                    "Consider regenerating content",
                    "Review tone consistency",
                ],
            },
            ensure_ascii=False,
        )

        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=200,
            cost=0.004,
            confidence=0.85,
            scenario=MockScenario.LOW_QUALITY,
        )

    def _create_failure_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create a failure mock response"""
        content = json.dumps(
            {
                "error": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "message": "Unable to complete validation due to content issues",
                "status": "failed",
            },
            ensure_ascii=False,
        )

        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=50,
            cost=0.001,
            confidence=0.0,
            scenario=MockScenario.FAILURE,
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
            scenario=MockScenario.INVALID_RESPONSE,
        )

    def _create_partial_failure_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create a partial failure mock response"""
        content = json.dumps(
            {
                "validation_score": 75.0,
                "status": "partial_success",
                "completed_checks": ["grammar", "structure"],
                "failed_checks": ["tone_consistency", "originality"],
                "findings": [
                    {
                        "type": "system_error",
                        "severity": "medium",
                        "message": "Unable to complete tone analysis",
                        "confidence": 0.0,
                    }
                ],
                "recommendations": ["Retry validation", "Check system resources"],
            },
            ensure_ascii=False,
        )

        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=180,
            cost=0.0036,
            confidence=0.9,
            scenario=MockScenario.PARTIAL_FAILURE,
        )

    def _create_edge_case_response(self, prompt: str, validator_id: str, content_type: str) -> MockResponse:
        """Create an edge case mock response"""
        content = json.dumps(
            {
                "validation_score": 0.0,  # Edge case: zero score
                "status": "edge_case",
                "findings": [
                    {
                        "type": "edge_case",
                        "severity": "info",
                        "message": "Empty content detected",
                        "confidence": 1.0,
                    }
                ],
                "metadata": {"content_length": 0, "processing_time": 0.001},
            },
            ensure_ascii=False,
        )

        return MockResponse(
            content=content,
            model="gpt-4-mock",
            tokens_used=1,
            cost=0.00002,
            confidence=1.0,
            scenario=MockScenario.EDGE_CASE,
        )

    async def _call_real_ai(self, prompt: str, validator_id: str, content_type: str, model: str) -> MockResponse:
        """Call real AI through OpenAI SDK (LiteLLM configured via .env)"""

        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        real_calls = self.usage_stats.get("real_calls", 0)
        self.usage_stats["real_calls"] = real_calls + 1

        try:
            logger.info(f"Calling real AI for {validator_id} using model {model}")

            start_time = datetime.now()

            # Call OpenAI API (LiteLLM proxy configured via OPENAI_BASE_URL)
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a {validator_id} for libriscribe2. Respond with valid JSON containing validation results.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # Low temperature for consistent validation results
                max_tokens=2000,
            )

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            # Extract response data
            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0

            # Calculate cost (approximate, based on model)
            cost = self._calculate_cost(model, tokens_used)

            logger.info(f"Real AI response received: {tokens_used} tokens, ${cost:.4f}, {execution_time:.2f}s")

            return MockResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                confidence=1.0,  # Real AI responses have full confidence
                metadata={
                    "real_ai": True,
                    "execution_time": execution_time,
                    "response_id": response.id,
                    "created": response.created,
                },
                scenario=MockScenario.SUCCESS,  # Real responses are considered "success"
            )

        except Exception as e:
            logger.error(f"Real AI call failed for {validator_id}: {e}")

            # Return error response in same format
            return MockResponse(
                content=json.dumps(
                    {"error": str(e), "status": "failed", "validator_id": validator_id}, ensure_ascii=False
                ),
                model=model,
                tokens_used=0,
                cost=0.0,
                confidence=0.0,
                metadata={"real_ai": True, "error": True},
                scenario=MockScenario.FAILURE,
            )

    async def _record_interaction(
        self, prompt: str, response: MockResponse, validator_id: str, content_type: str
    ) -> None:
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
            real_ai_used=True,
        )

        self.recorded_interactions[request_hash] = interaction

        # Save to disk
        await self._save_recorded_interaction(interaction)

    def _generate_request_hash(self, prompt: str, validator_id: str, content_type: str) -> str:
        """Generate consistent hash for request caching"""
        content = f"{prompt}|{validator_id}|{content_type}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _load_mock_data(self) -> None:
        """Load existing mock data from disk"""

        # Load recorded interactions
        interactions_file = self.mock_data_dir / "recorded_interactions.json"
        if interactions_file.exists():
            try:
                with open(interactions_file) as f:
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
                        real_ai_used=item.get("real_ai_used", True),
                    )
                    self.recorded_interactions[interaction.request_hash] = interaction

                logger.info(f"Loaded {len(self.recorded_interactions)} recorded interactions")

            except Exception as e:
                logger.error(f"Failed to load recorded interactions: {e}")

        # Load custom mock responses
        mock_responses_file = self.mock_data_dir / "mock_responses.json"
        if mock_responses_file.exists():
            try:
                with open(mock_responses_file) as f:
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
                with open(interactions_file) as f:
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
                "scenario": interaction.response.scenario.value,
            },
            "validator_id": interaction.validator_id,
            "content_type": interaction.content_type,
            "timestamp": interaction.timestamp.isoformat(),
            "real_ai_used": interaction.real_ai_used,
        }

        existing_data.append(interaction_data)

        # Save to disk
        try:
            with open(interactions_file, "w") as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save recorded interaction: {e}")

    def get_usage_stats(self) -> dict[str, Any]:
        """Get mock system usage statistics"""
        validators_tested = self.usage_stats.get("validators_tested", set())
        if isinstance(validators_tested, set):
            validators_list = list(validators_tested)
        else:
            validators_list = []

        return {
            **self.usage_stats,
            "validators_tested": validators_list,
            "recorded_interactions": len(self.recorded_interactions),
            "mock_coverage": self._calculate_mock_coverage(),
        }

    def _calculate_mock_coverage(self) -> dict[str, Any]:
        """Calculate test coverage metrics"""

        validators_tested = self.usage_stats.get("validators_tested", set())
        scenarios_used = self.usage_stats.get("scenarios_used", {})

        total_validators = len(validators_tested) if isinstance(validators_tested, set) else 0
        scenarios_covered = len(scenarios_used) if isinstance(scenarios_used, dict) else 0

        return {
            "validators_tested": total_validators,
            "scenarios_covered": scenarios_covered,
            "total_scenarios": len(MockScenario),
            "coverage_percentage": (scenarios_covered / len(MockScenario)) * 100,
            "recorded_interactions": len(self.recorded_interactions),
        }

    async def create_test_suite(self, validators: list[str]) -> dict[str, list[MockScenario]]:
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
                MockScenario.EDGE_CASE,
            ]

        return test_suite

    async def run_test_suite(self, test_suite: dict[str, list[MockScenario]]) -> dict[str, Any]:
        """Run comprehensive test suite and return results"""

        results: dict[str, Any] = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "validator_results": {},
            "scenario_results": {},
            "coverage_report": {},
        }

        for validator_id, scenarios in test_suite.items():
            validator_results: dict[str, Any] = {
                "passed": 0,
                "failed": 0,
                "scenarios": {},
            }

            for scenario in scenarios:
                try:
                    response = await self.get_ai_response(
                        prompt=f"Test prompt for {validator_id}",
                        validator_id=validator_id,
                        content_type="test",
                        scenario=scenario,
                    )
                    logger.debug(
                        f"Received response for {validator_id} ({scenario.value}): {response.content[:100]}..."
                    )

                    validator_results["passed"] += 1
                    validator_results["scenarios"][scenario.value] = "passed"
                    results["passed_tests"] += 1

                except Exception as e:
                    validator_results["failed"] += 1
                    validator_results["scenarios"][scenario.value] = f"failed: {e!s}"
                    results["failed_tests"] += 1

                results["total_tests"] += 1

            results["validator_results"][validator_id] = validator_results

        # Generate coverage report
        results["coverage_report"] = self._calculate_mock_coverage()

        return results

    def _calculate_cost(self, model: str, tokens_used: int) -> float:
        """Calculate approximate cost based on model and token usage"""

        # Pricing per 1K tokens (approximate, as of 2024)
        pricing = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.002,
            "gpt-3.5-turbo-16k": 0.004,
        }

        # Default pricing if model not found
        price_per_1k = pricing.get(model, 0.01)

        return (tokens_used / 1000) * price_per_1k

    async def populate_mock_mappings_from_live(
        self, prompts: list[dict[str, Any]], model: str = "gpt-4"
    ) -> dict[str, Any]:
        """
        Populate mock input/output mappings from live AI responses

        Args:
            prompts: List of prompt configurations with keys:
                    - prompt: The actual prompt text
                    - validator_id: Validator making the request
                    - content_type: Type of content being validated
                    - expected_scenario: Expected mock scenario for this prompt
            model: OpenAI model to use for live calls

        Returns:
            Dict with results of the mapping population process
        """

        if self.use_mock_mode:
            logger.warning("Cannot populate from live responses in mock mode. Set OPENAI_API_KEY.")
            return {"error": "Mock mode active - no API key available"}

        results: dict[str, Any] = {
            "total_prompts": len(prompts),
            "successful_recordings": 0,
            "failed_recordings": 0,
            "recordings": [],
            "errors": [],
        }

        logger.info(f"Populating mock mappings from {len(prompts)} live AI responses...")

        for i, prompt_config in enumerate(prompts):
            try:
                prompt_text = prompt_config["prompt"]
                validator_id = prompt_config["validator_id"]
                content_type = prompt_config["content_type"]
                expected_scenario = prompt_config.get("expected_scenario", "success")

                logger.info(f"Recording {i + 1}/{len(prompts)}: {validator_id} - {content_type}")

                # Call real AI
                response = await self._call_real_ai(prompt_text, validator_id, content_type, model)

                # Record the interaction
                await self._record_interaction(prompt_text, response, validator_id, content_type)

                results["successful_recordings"] += 1
                results["recordings"].append(
                    {
                        "prompt": prompt_text[:100] + "..." if len(prompt_text) > 100 else prompt_text,
                        "validator_id": validator_id,
                        "content_type": content_type,
                        "tokens_used": response.tokens_used,
                        "cost": response.cost,
                        "expected_scenario": expected_scenario,
                        "recorded_at": datetime.now().isoformat(),
                    }
                )

                live_recordings = self.usage_stats.get("live_recordings", 0)
                self.usage_stats["live_recordings"] = live_recordings + 1

                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Failed to record prompt {i + 1}: {e}")
                results["failed_recordings"] += 1
                results["errors"].append(
                    {
                        "prompt_index": i,
                        "error": str(e),
                        "validator_id": prompt_config.get("validator_id", "unknown"),
                    }
                )

        # Save updated recordings
        await self._save_all_recordings()

        logger.info(
            f"Mock mapping population complete: {results['successful_recordings']} successful, {results['failed_recordings']} failed"
        )

        return results

    async def _save_all_recordings(self) -> None:
        """Save all recorded interactions to disk"""

        interactions_file = self.mock_data_dir / "recorded_interactions.json"

        # Convert all interactions to serializable format
        interactions_data = []
        for interaction in self.recorded_interactions.values():
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
                    "scenario": interaction.response.scenario.value,
                },
                "validator_id": interaction.validator_id,
                "content_type": interaction.content_type,
                "timestamp": interaction.timestamp.isoformat(),
                "real_ai_used": interaction.real_ai_used,
            }
            interactions_data.append(interaction_data)

        try:
            with open(interactions_file, "w") as f:
                json.dump(interactions_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(interactions_data)} recorded interactions")
        except Exception as e:
            logger.error(f"Failed to save recorded interactions: {e}")


# Utility functions for easy integration


async def create_mock_manager(config: dict[str, Any]) -> AIMockManager:
    """Create and configure AI mock manager"""

    mock_data_dir = config.get("mock_data_dir", ".libriscribe2/mock_data")
    manager = AIMockManager(mock_data_dir)

    return manager


def get_mock_config_for_testing() -> dict[str, Any]:
    """Get recommended mock configuration for testing"""

    return {
        "mock_data_dir": ".libriscribe2/mock_data",
        "default_scenario": "success",
        "openai_model": "gpt-4",
        "test_coverage_required": 80.0,
        "scenarios_to_test": [
            "success",
            "high_quality",
            "low_quality",
            "failure",
            "partial_failure",
            "edge_case",
        ],
        "live_recording_prompts": [
            {
                "prompt": "Analyze this chapter for tone consistency and quality",
                "validator_id": "content_validator",
                "content_type": "chapter",
                "expected_scenario": "success",
            },
            {
                "prompt": "Check if this manuscript meets publishing standards",
                "validator_id": "publishing_standards_validator",
                "content_type": "manuscript",
                "expected_scenario": "success",
            },
        ],
    }


async def populate_mock_data_from_live_responses(mock_manager: AIMockManager, config: dict[str, Any]) -> dict[str, Any]:
    """
    Utility function to populate mock data from live AI responses

    Usage:
        # Set OPENAI_API_KEY in environment
        mock_manager = AIMockManager()
        config = get_mock_config_for_testing()
        results = await populate_mock_data_from_live_responses(mock_manager, config)
    """

    prompts = config.get("live_recording_prompts", [])
    model = config.get("openai_model", "gpt-4")

    return await mock_manager.populate_mock_mappings_from_live(prompts, model)
