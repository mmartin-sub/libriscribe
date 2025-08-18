"""
Comprehensive testing framework for validation system.

This module provides a complete testing framework that follows best practices
for AI system testing with mocking, coverage, and accuracy measurement.
"""

import asyncio
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from libriscribe2.validation.ai_mock import AIMockManager, MockScenario
from libriscribe2.validation.engine import ValidationEngineImpl
from libriscribe2.validation.interfaces import (
    Finding,
    FindingType,
    Severity,
    ValidationConfig,
    ValidationEngine,
    ValidationResult,
    ValidationStatus,
    ValidatorBase,
    ValidatorResult,
)
from tests.lib.coverage import CoverageReporter

from .test_data import TestDataGenerator

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """Individual test case definition"""

    test_id: str
    name: str
    description: str
    validator_id: str
    content_type: str
    test_data: Any
    expected_status: ValidationStatus
    expected_findings_count: int
    expected_quality_score_range: tuple[float, float]
    mock_scenario: MockScenario | None = None
    timeout: float = 30.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """Test execution result"""

    test_case: TestCase
    passed: bool
    execution_time: float
    actual_status: ValidationStatus
    actual_findings_count: int
    actual_quality_score: float
    error_message: str | None = None
    validation_result: ValidationResult | None = None
    timestamp: datetime = field(default_factory=datetime.now)


class ValidationTestFramework:
    """
    Comprehensive testing framework for validation system

    Best Practices Implemented:
    1. Scenario-based testing with mock AI responses
    2. Deterministic testing with recorded interactions
    3. Coverage measurement across validators and scenarios
    4. Accuracy testing against known-good/bad content
    5. Performance testing with timeout handling
    6. Regression testing with baseline comparisons
    """

    def __init__(self, mock_manager: AIMockManager, test_data_dir: str | None = None) -> None:
        self.mock_manager = mock_manager
        self.test_data_dir = Path(test_data_dir) if test_data_dir else Path(".libriscribe2/test_data")
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

        self.test_data_generator = TestDataGenerator()
        self.coverage_reporter = CoverageReporter()

        self.test_cases: list[TestCase] = []
        self.test_results: list[TestResult] = []
        self.baseline_results: dict[str, dict[str, Any]] = {}

        # Load existing test cases and baselines
        self._load_test_data()

    async def create_comprehensive_test_suite(self, validators: list[str], content_types: list[str]) -> list[TestCase]:
        """Create comprehensive test suite for all validators and scenarios"""

        test_cases = []

        for validator_id in validators:
            for content_type in content_types:
                # Create test cases for each scenario
                for scenario in MockScenario:
                    test_case = await self._create_test_case_for_scenario(validator_id, content_type, scenario)
                    test_cases.append(test_case)

                # Create accuracy test cases with known-good/bad content
                accuracy_cases = await self._create_accuracy_test_cases(validator_id, content_type)
                test_cases.extend(accuracy_cases)

        self.test_cases = test_cases
        return test_cases

    async def _create_test_case_for_scenario(
        self, validator_id: str, content_type: str, scenario: MockScenario
    ) -> TestCase:
        """Create test case for specific scenario"""

        # Generate appropriate test data
        test_data = await self.test_data_generator.generate_content(content_type, scenario)

        # Set expected results based on scenario
        expected_status, expected_findings, quality_range = self._get_expected_results_for_scenario(scenario)

        return TestCase(
            test_id=f"{validator_id}_{content_type}_{scenario.value}",
            name=f"{validator_id.title()} - {scenario.value.title()} Scenario",
            description=f"Test {validator_id} with {scenario.value} scenario on {content_type}",
            validator_id=validator_id,
            content_type=content_type,
            test_data=test_data,
            expected_status=expected_status,
            expected_findings_count=expected_findings,
            expected_quality_score_range=quality_range,
            mock_scenario=scenario,
            metadata={
                "scenario": scenario.value,
                "generated_at": datetime.now().isoformat(),
            },
        )

    async def _create_accuracy_test_cases(self, validator_id: str, content_type: str) -> list[TestCase]:
        """Create test cases for accuracy measurement"""

        accuracy_cases = []

        # Known-good content (should pass validation)
        good_content = await self.test_data_generator.generate_known_good_content(content_type, validator_id)

        good_case = TestCase(
            test_id=f"{validator_id}_{content_type}_known_good",
            name=f"{validator_id.title()} - Known Good Content",
            description=f"Test {validator_id} with known good {content_type}",
            validator_id=validator_id,
            content_type=content_type,
            test_data=good_content,
            expected_status=ValidationStatus.COMPLETED,
            expected_findings_count=0,
            expected_quality_score_range=(80.0, 100.0),
            metadata={"accuracy_test": True, "content_quality": "good"},
        )
        accuracy_cases.append(good_case)

        # Known-bad content (should fail validation)
        bad_content = await self.test_data_generator.generate_known_bad_content(content_type, validator_id)

        bad_case = TestCase(
            test_id=f"{validator_id}_{content_type}_known_bad",
            name=f"{validator_id.title()} - Known Bad Content",
            description=f"Test {validator_id} with known bad {content_type}",
            validator_id=validator_id,
            content_type=content_type,
            test_data=bad_content,
            expected_status=ValidationStatus.NEEDS_HUMAN_REVIEW,
            expected_findings_count=1,
            expected_quality_score_range=(0.0, 70.0),
            metadata={"accuracy_test": True, "content_quality": "bad"},
        )
        accuracy_cases.append(bad_case)

        return accuracy_cases

    def _get_expected_results_for_scenario(
        self, scenario: MockScenario
    ) -> tuple[ValidationStatus, int, tuple[float, float]]:
        """Get expected results for a mock scenario"""

        if scenario == MockScenario.SUCCESS:
            return ValidationStatus.COMPLETED, 1, (80.0, 90.0)
        elif scenario == MockScenario.HIGH_QUALITY:
            return ValidationStatus.COMPLETED, 0, (90.0, 100.0)
        elif scenario == MockScenario.LOW_QUALITY:
            return ValidationStatus.NEEDS_HUMAN_REVIEW, 2, (60.0, 70.0)
        elif scenario == MockScenario.FAILURE:
            return ValidationStatus.ERROR, 0, (0.0, 0.0)
        elif scenario == MockScenario.PARTIAL_FAILURE:
            return ValidationStatus.COMPLETED, 1, (70.0, 80.0)
        elif scenario == MockScenario.EDGE_CASE:
            return ValidationStatus.COMPLETED, 1, (0.0, 10.0)
        else:
            return ValidationStatus.COMPLETED, 0, (70.0, 90.0)

    async def run_test_suite(
        self,
        test_cases: list[TestCase] | None = None,
        parallel: bool = True,
        max_workers: int = 10,
    ) -> dict[str, Any]:
        """Run comprehensive test suite"""

        if test_cases is None:
            test_cases = self.test_cases

        logger.info(f"Running test suite with {len(test_cases)} test cases")

        # Clear previous results
        self.test_results = []

        if parallel:
            results = await self._run_tests_parallel(test_cases, max_workers)
        else:
            results = await self._run_tests_sequential(test_cases)

        # Generate comprehensive report
        report = await self._generate_test_report(results)

        # Save results
        await self._save_test_results(results, report)

        return report

    async def _run_tests_parallel(self, test_cases: list[TestCase], max_workers: int) -> list[TestResult]:
        """Run tests in parallel"""

        semaphore = asyncio.Semaphore(max_workers)

        async def run_single_test(test_case: TestCase) -> TestResult:
            async with semaphore:
                return await self._execute_test_case(test_case)

        tasks = [run_single_test(test_case) for test_case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        valid_results: list[TestResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Test case {test_cases[i].test_id} failed with exception: {result}")
                # Create failed test result
                failed_result = TestResult(
                    test_case=test_cases[i],
                    passed=False,
                    execution_time=0.0,
                    actual_status=ValidationStatus.ERROR,
                    actual_findings_count=0,
                    actual_quality_score=0.0,
                    error_message=str(result),
                )
                valid_results.append(failed_result)
            elif isinstance(result, TestResult):
                valid_results.append(result)
            else:
                # Handle unexpected result type
                logger.error(f"Unexpected result type: {type(result)}")
                failed_result = TestResult(
                    test_case=test_cases[i],
                    passed=False,
                    execution_time=0.0,
                    actual_status=ValidationStatus.ERROR,
                    actual_findings_count=0,
                    actual_quality_score=0.0,
                    error_message=f"Unexpected result type: {type(result)}",
                )
                valid_results.append(failed_result)

        return valid_results

    async def _run_tests_sequential(self, test_cases: list[TestCase]) -> list[TestResult]:
        """Run tests sequentially"""

        results = []
        for i, test_case in enumerate(test_cases):
            logger.info(f"Running test {i + 1}/{len(test_cases)}: {test_case.name}")
            result = await self._execute_test_case(test_case)
            results.append(result)

        return results

    async def _execute_test_case(self, test_case: TestCase) -> TestResult:
        """Execute individual test case"""

        start_time = datetime.now()

        try:
            # Create validation engine with mock configuration
            config = ValidationConfig(
                project_id=f"test_{test_case.test_id}",
                ai_mock_enabled=True,
                enabled_validators=[test_case.validator_id],
                validator_configs={
                    test_case.validator_id: {
                        "mock_scenario": test_case.mock_scenario.value if test_case.mock_scenario else "success"
                    }
                },
            )

            engine = ValidationEngineImpl()
            await engine.initialize(config)

            # Create mock validator for testing
            mock_validator = await self._create_mock_validator(test_case)
            await engine.register_validator(mock_validator)

            # Run validation with timeout
            validation_result = await asyncio.wait_for(
                engine.validate_project(test_case.test_data, test_case.test_id),
                timeout=test_case.timeout,
            )

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Evaluate test result
            passed = self._evaluate_test_result(test_case, validation_result)

            # Extract actual values
            actual_status = validation_result.status
            actual_findings_count = sum(len(result.findings) for result in validation_result.validator_results.values())
            actual_quality_score = validation_result.overall_quality_score

            result = TestResult(
                test_case=test_case,
                passed=passed,
                execution_time=execution_time,
                actual_status=actual_status,
                actual_findings_count=actual_findings_count,
                actual_quality_score=actual_quality_score,
                validation_result=validation_result,
            )

            self.test_results.append(result)
            return result

        except TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestResult(
                test_case=test_case,
                passed=False,
                execution_time=execution_time,
                actual_status=ValidationStatus.ERROR,
                actual_findings_count=0,
                actual_quality_score=0.0,
                error_message=f"Test timed out after {test_case.timeout} seconds",
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestResult(
                test_case=test_case,
                passed=False,
                execution_time=execution_time,
                actual_status=ValidationStatus.ERROR,
                actual_findings_count=0,
                actual_quality_score=0.0,
                error_message=str(e),
            )

    async def _create_mock_validator(self, test_case: TestCase) -> ValidatorBase:
        """Create mock validator for testing"""

        class MockValidator(ValidatorBase):
            def __init__(self, test_case: TestCase, mock_manager: AIMockManager) -> None:
                super().__init__(
                    test_case.validator_id,
                    f"Mock {test_case.validator_id}",
                    "1.0.0-test",
                )
                self.test_case = test_case
                self.mock_manager = mock_manager

            async def initialize(self, config: dict[str, Any]) -> None:
                self.config = config

            async def validate(self, content: Any, context: dict[str, Any]) -> ValidatorResult:
                # Use mock AI response
                mock_response = await self.mock_manager.get_ai_response(
                    prompt=f"Validate {self.test_case.content_type}",
                    validator_id=self.validator_id,
                    content_type=self.test_case.content_type,
                    scenario=self.test_case.mock_scenario,
                )

                # Parse mock response and create validator result
                try:
                    response_data = json.loads(mock_response.content)

                    # Create findings from response
                    findings = []
                    if "findings" in response_data:
                        for finding_data in response_data["findings"]:
                            finding = Finding(
                                validator_id=self.validator_id,
                                type=FindingType(finding_data.get("type", "content_quality")),
                                severity=Severity(finding_data.get("severity", "medium")),
                                title=finding_data.get("title", "Test Finding"),
                                message=finding_data.get("message", "Test message"),
                                confidence=finding_data.get("confidence", 0.8),
                            )
                            findings.append(finding)

                    from libriscribe2.validation.interfaces import ValidatorResult

                    return ValidatorResult(
                        validator_id=self.validator_id,
                        status=ValidationStatus.COMPLETED,
                        findings=findings,
                        metrics={
                            "quality_score": response_data.get("validation_score", 85.0),
                            "mock_response": True,
                        },
                        ai_usage={
                            "tokens": mock_response.tokens_used,
                            "cost": mock_response.cost,
                            "model": mock_response.model,
                        },
                    )

                except json.JSONDecodeError:
                    # Handle invalid JSON response
                    return ValidatorResult(
                        validator_id=self.validator_id,
                        status=ValidationStatus.ERROR,
                        findings=[
                            Finding(
                                validator_id=self.validator_id,
                                type=FindingType.SYSTEM_ERROR,
                                severity=Severity.CRITICAL,
                                title="Invalid Response",
                                message="Failed to parse AI response",
                            )
                        ],
                    )

            def get_supported_content_types(self) -> list[str]:
                return [self.test_case.content_type]

            async def cleanup(self) -> None:
                """Cleanup method for MockValidator."""
                pass

            async def on_configuration_change(self, _old_config: dict[str, Any], new_config: dict[str, Any]) -> None:
                """Handle configuration changes for MockValidator."""
                pass

        return MockValidator(test_case, self.mock_manager)

    def _evaluate_test_result(self, test_case: TestCase, validation_result: ValidationResult) -> bool:
        """Evaluate if test result matches expectations"""

        # Check status
        if validation_result.status != test_case.expected_status:
            return False

        # Check findings count
        actual_findings_count = sum(len(result.findings) for result in validation_result.validator_results.values())
        if actual_findings_count != test_case.expected_findings_count:
            return False

        # Check quality score range
        min_score, max_score = test_case.expected_quality_score_range
        if not (min_score <= validation_result.overall_quality_score <= max_score):
            return False

        return True

    async def _generate_test_report(self, results: list[TestResult]) -> dict[str, Any]:
        """Generate comprehensive test report"""

        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests

        # Calculate metrics by validator
        validator_metrics: dict[str, dict[str, Any]] = {}
        for result in results:
            validator_id = result.test_case.validator_id
            if validator_id not in validator_metrics:
                validator_metrics[validator_id] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "avg_execution_time": 0.0,
                    "scenarios_tested": set[str](),
                }

            metrics = validator_metrics[validator_id]
            metrics["total"] += 1
            if result.passed:
                metrics["passed"] += 1
            else:
                metrics["failed"] += 1

            metrics["avg_execution_time"] += result.execution_time

            if result.test_case.mock_scenario:
                metrics["scenarios_tested"].add(result.test_case.mock_scenario.value)

        # Calculate average execution times
        for _validator_id, metrics in validator_metrics.items():
            if metrics["total"] > 0:
                metrics["avg_execution_time"] /= metrics["total"]
            metrics["scenarios_tested"] = list(metrics["scenarios_tested"])

        # Calculate scenario coverage
        scenario_coverage = {}
        for scenario in MockScenario:
            scenario_results = [r for r in results if r.test_case.mock_scenario == scenario]
            scenario_coverage[scenario.value] = {
                "total": len(scenario_results),
                "passed": sum(1 for r in scenario_results if r.passed),
                "failed": sum(1 for r in scenario_results if not r.passed),
            }

        # Generate coverage report
        coverage_report = await self.coverage_reporter.generate_coverage_report(results)

        # Get mock system stats
        mock_stats = self.mock_manager.get_usage_stats()

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_execution_time": sum(r.execution_time for r in results),
                "avg_execution_time": sum(r.execution_time for r in results) / total_tests if total_tests > 0 else 0,
            },
            "validator_metrics": validator_metrics,
            "scenario_coverage": scenario_coverage,
            "coverage_report": coverage_report,
            "mock_system_stats": mock_stats,
            "failed_tests": [
                {
                    "test_id": r.test_case.test_id,
                    "name": r.test_case.name,
                    "error_message": r.error_message,
                    "expected_status": r.test_case.expected_status.value,
                    "actual_status": r.actual_status.value,
                    "expected_quality_range": r.test_case.expected_quality_score_range,
                    "actual_quality_score": r.actual_quality_score,
                }
                for r in results
                if not r.passed
            ],
            "timestamp": datetime.now().isoformat(),
        }

        return report

    async def _save_test_results(self, results: list[TestResult], report: dict[str, Any]) -> None:
        """Save test results and report to disk"""

        # Save detailed results
        results_file = self.test_data_dir / "test_results.json"
        results_data = []

        for result in results:
            result_data = {
                "test_case": {
                    "test_id": result.test_case.test_id,
                    "name": result.test_case.name,
                    "validator_id": result.test_case.validator_id,
                    "content_type": result.test_case.content_type,
                    "expected_status": result.test_case.expected_status.value,
                    "expected_findings_count": result.test_case.expected_findings_count,
                    "expected_quality_score_range": result.test_case.expected_quality_score_range,
                    "mock_scenario": result.test_case.mock_scenario.value if result.test_case.mock_scenario else None,
                },
                "result": {
                    "passed": result.passed,
                    "execution_time": result.execution_time,
                    "actual_status": result.actual_status.value,
                    "actual_findings_count": result.actual_findings_count,
                    "actual_quality_score": result.actual_quality_score,
                    "error_message": result.error_message,
                    "timestamp": result.timestamp.isoformat(),
                },
            }
            results_data.append(result_data)

        try:
            with open(results_file, "w") as f:
                json.dump(results_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")

        # Save report
        report_file = self.test_data_dir / "test_report.json"
        try:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save test report: {e}")

    def _load_test_data(self) -> None:
        """Load existing test data"""

        # Load baseline results for regression testing
        baseline_file = self.test_data_dir / "baseline_results.json"
        if baseline_file.exists():
            try:
                with open(baseline_file) as f:
                    baseline_data = json.load(f)

                for item in baseline_data:
                    test_id = item["test_case"]["test_id"]
                    # Reconstruct baseline result (simplified)
                    self.baseline_results[test_id] = item["result"]

                logger.info(f"Loaded {len(self.baseline_results)} baseline results")

            except Exception as e:
                logger.error(f"Failed to load baseline results: {e}")

    async def run_regression_tests(self) -> dict[str, Any]:
        """Run regression tests against baseline results"""

        if not self.baseline_results:
            logger.warning("No baseline results available for regression testing")
            return {"error": "No baseline results available"}

        # Run current test suite
        current_report = await self.run_test_suite()

        # Compare with baseline
        regression_results: dict[str, list[Any]] = {
            "regressions": [],
            "improvements": [],
            "new_tests": [],
            "removed_tests": [],
        }

        current_results = {r.test_case.test_id: r for r in self.test_results}

        for test_id, baseline_result in self.baseline_results.items():
            if test_id in current_results:
                current_result = current_results[test_id]

                # Check for regressions
                if baseline_result["passed"] and not current_result.passed:
                    regression_results["regressions"].append(
                        {
                            "test_id": test_id,
                            "baseline_status": "passed",
                            "current_status": "failed",
                            "error": current_result.error_message,
                        }
                    )

                # Check for improvements
                elif not baseline_result["passed"] and current_result.passed:
                    regression_results["improvements"].append(
                        {
                            "test_id": test_id,
                            "baseline_status": "failed",
                            "current_status": "passed",
                        }
                    )
            else:
                regression_results["removed_tests"].append(test_id)

        # Check for new tests
        for test_id in current_results:
            if test_id not in self.baseline_results:
                regression_results["new_tests"].append(test_id)

        return {
            "regression_summary": {
                "regressions_count": len(regression_results["regressions"]),
                "improvements_count": len(regression_results["improvements"]),
                "new_tests_count": len(regression_results["new_tests"]),
                "removed_tests_count": len(regression_results["removed_tests"]),
            },
            "details": regression_results,
            "current_report": current_report,
        }

    async def save_as_baseline(self) -> None:
        """Save current test results as baseline for future regression testing"""

        if not self.test_results:
            logger.warning("No test results to save as baseline")
            return

        baseline_file = self.test_data_dir / "baseline_results.json"
        baseline_data = []

        for result in self.test_results:
            baseline_item = {
                "test_case": {
                    "test_id": result.test_case.test_id,
                    "name": result.test_case.name,
                    "validator_id": result.test_case.validator_id,
                },
                "result": {
                    "passed": result.passed,
                    "execution_time": result.execution_time,
                    "actual_quality_score": result.actual_quality_score,
                    "timestamp": result.timestamp.isoformat(),
                },
            }
            baseline_data.append(baseline_item)

        try:
            with open(baseline_file, "w") as f:
                json.dump(baseline_data, f, indent=2)
            logger.info(f"Saved {len(baseline_data)} results as baseline")
        except Exception as e:
            logger.error(f"Failed to save baseline results: {e}")
