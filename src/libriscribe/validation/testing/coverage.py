"""
Coverage reporting for validation system testing.

This module provides comprehensive coverage analysis including:
- Validator coverage across different scenarios
- Code path coverage within validators
- AI interaction coverage
- Edge case coverage
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from ..ai_mock import MockScenario


logger = logging.getLogger(__name__)


@dataclass
class CoverageMetrics:
    """Coverage metrics for a specific area"""
    total_items: int
    covered_items: int
    coverage_percentage: float
    uncovered_items: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoverageReport:
    """Comprehensive coverage report"""
    validator_coverage: Dict[str, CoverageMetrics]
    scenario_coverage: Dict[str, CoverageMetrics]
    content_type_coverage: Dict[str, CoverageMetrics]
    overall_coverage: CoverageMetrics
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class CoverageReporter:
    """
    Generates comprehensive coverage reports for validation testing
    
    Coverage Areas:
    1. Validator Coverage - Which validators have been tested
    2. Scenario Coverage - Which mock scenarios have been exercised
    3. Content Type Coverage - Which content types have been validated
    4. Code Path Coverage - Which code paths within validators have been executed
    5. Edge Case Coverage - Which edge cases have been tested
    6. AI Interaction Coverage - Which AI interaction patterns have been tested
    """
    
    def __init__(self, coverage_data_dir: Optional[str] = None):
        self.coverage_data_dir = Path(coverage_data_dir) if coverage_data_dir else Path(".libriscribe/coverage_data")
        self.coverage_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Define expected coverage targets
        self.expected_validators = [
            "content_validator",
            "publishing_standards_validator", 
            "quality_originality_validator",
            "system_code_validator",
            "ai_output_validator",
            "compliance_validator",
            "security_validator",
            "documentation_validator"
        ]
        
        self.expected_scenarios = [scenario.value for scenario in MockScenario]
        
        self.expected_content_types = [
            "chapter",
            "manuscript", 
            "scene",
            "character",
            "outline",
            "code_file",
            "documentation"
        ]
        
    async def generate_coverage_report(self, test_results: List[Any]) -> CoverageReport:
        """Generate comprehensive coverage report from test results"""
        
        # Analyze validator coverage
        validator_coverage = self._analyze_validator_coverage(test_results)
        
        # Analyze scenario coverage
        scenario_coverage = self._analyze_scenario_coverage(test_results)
        
        # Analyze content type coverage
        content_type_coverage = self._analyze_content_type_coverage(test_results)
        
        # Calculate overall coverage
        overall_coverage = self._calculate_overall_coverage(
            validator_coverage, scenario_coverage, content_type_coverage
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            validator_coverage, scenario_coverage, content_type_coverage
        )
        
        report = CoverageReport(
            validator_coverage=validator_coverage,
            scenario_coverage=scenario_coverage,
            content_type_coverage=content_type_coverage,
            overall_coverage=overall_coverage,
            recommendations=recommendations
        )
        
        # Save coverage report
        await self._save_coverage_report(report)
        
        return report
        
    def _analyze_validator_coverage(self, test_results: List[Any]) -> Dict[str, CoverageMetrics]:
        """Analyze coverage across validators"""
        
        tested_validators = set()
        validator_test_counts = {}
        validator_scenarios = {}
        
        for result in test_results:
            validator_id = result.test_case.validator_id
            tested_validators.add(validator_id)
            
            # Count tests per validator
            validator_test_counts[validator_id] = validator_test_counts.get(validator_id, 0) + 1
            
            # Track scenarios per validator
            if validator_id not in validator_scenarios:
                validator_scenarios[validator_id] = set()
            if result.test_case.mock_scenario:
                validator_scenarios[validator_id].add(result.test_case.mock_scenario.value)
                
        coverage_metrics = {}
        
        for validator_id in self.expected_validators:
            if validator_id in tested_validators:
                scenarios_tested = len(validator_scenarios.get(validator_id, set()))
                total_scenarios = len(self.expected_scenarios)
                scenario_coverage = (scenarios_tested / total_scenarios) * 100
                
                coverage_metrics[validator_id] = CoverageMetrics(
                    total_items=total_scenarios,
                    covered_items=scenarios_tested,
                    coverage_percentage=scenario_coverage,
                    uncovered_items=[
                        scenario for scenario in self.expected_scenarios
                        if scenario not in validator_scenarios.get(validator_id, set())
                    ],
                    details={
                        "test_count": validator_test_counts.get(validator_id, 0),
                        "scenarios_tested": list(validator_scenarios.get(validator_id, set())),
                        "status": "tested"
                    }
                )
            else:
                coverage_metrics[validator_id] = CoverageMetrics(
                    total_items=len(self.expected_scenarios),
                    covered_items=0,
                    coverage_percentage=0.0,
                    uncovered_items=self.expected_scenarios.copy(),
                    details={
                        "test_count": 0,
                        "scenarios_tested": [],
                        "status": "not_tested"
                    }
                )
                
        return coverage_metrics
        
    def _analyze_scenario_coverage(self, test_results: List[Any]) -> Dict[str, CoverageMetrics]:
        """Analyze coverage across mock scenarios"""
        
        scenario_validators = {}
        scenario_test_counts = {}
        
        for result in test_results:
            if result.test_case.mock_scenario:
                scenario = result.test_case.mock_scenario.value
                validator_id = result.test_case.validator_id
                
                # Track validators per scenario
                if scenario not in scenario_validators:
                    scenario_validators[scenario] = set()
                scenario_validators[scenario].add(validator_id)
                
                # Count tests per scenario
                scenario_test_counts[scenario] = scenario_test_counts.get(scenario, 0) + 1
                
        coverage_metrics = {}
        
        for scenario in self.expected_scenarios:
            validators_tested = len(scenario_validators.get(scenario, set()))
            total_validators = len(self.expected_validators)
            validator_coverage = (validators_tested / total_validators) * 100 if total_validators > 0 else 0
            
            coverage_metrics[scenario] = CoverageMetrics(
                total_items=total_validators,
                covered_items=validators_tested,
                coverage_percentage=validator_coverage,
                uncovered_items=[
                    validator for validator in self.expected_validators
                    if validator not in scenario_validators.get(scenario, set())
                ],
                details={
                    "test_count": scenario_test_counts.get(scenario, 0),
                    "validators_tested": list(scenario_validators.get(scenario, set())),
                    "status": "tested" if scenario in scenario_validators else "not_tested"
                }
            )
            
        return coverage_metrics
        
    def _analyze_content_type_coverage(self, test_results: List[Any]) -> Dict[str, CoverageMetrics]:
        """Analyze coverage across content types"""
        
        content_type_validators = {}
        content_type_scenarios = {}
        content_type_test_counts = {}
        
        for result in test_results:
            content_type = result.test_case.content_type
            validator_id = result.test_case.validator_id
            
            # Track validators per content type
            if content_type not in content_type_validators:
                content_type_validators[content_type] = set()
            content_type_validators[content_type].add(validator_id)
            
            # Track scenarios per content type
            if content_type not in content_type_scenarios:
                content_type_scenarios[content_type] = set()
            if result.test_case.mock_scenario:
                content_type_scenarios[content_type].add(result.test_case.mock_scenario.value)
                
            # Count tests per content type
            content_type_test_counts[content_type] = content_type_test_counts.get(content_type, 0) + 1
            
        coverage_metrics = {}
        
        for content_type in self.expected_content_types:
            validators_tested = len(content_type_validators.get(content_type, set()))
            scenarios_tested = len(content_type_scenarios.get(content_type, set()))
            
            # Calculate combined coverage (validators × scenarios)
            total_combinations = len(self.expected_validators) * len(self.expected_scenarios)
            covered_combinations = validators_tested * scenarios_tested
            combination_coverage = (covered_combinations / total_combinations) * 100 if total_combinations > 0 else 0
            
            coverage_metrics[content_type] = CoverageMetrics(
                total_items=total_combinations,
                covered_items=covered_combinations,
                coverage_percentage=combination_coverage,
                uncovered_items=[
                    f"{validator}+{scenario}" 
                    for validator in self.expected_validators
                    for scenario in self.expected_scenarios
                    if validator not in content_type_validators.get(content_type, set())
                    or scenario not in content_type_scenarios.get(content_type, set())
                ],
                details={
                    "test_count": content_type_test_counts.get(content_type, 0),
                    "validators_tested": list(content_type_validators.get(content_type, set())),
                    "scenarios_tested": list(content_type_scenarios.get(content_type, set())),
                    "validator_coverage": (validators_tested / len(self.expected_validators)) * 100,
                    "scenario_coverage": (scenarios_tested / len(self.expected_scenarios)) * 100,
                    "status": "tested" if content_type in content_type_validators else "not_tested"
                }
            )
            
        return coverage_metrics
        
    def _calculate_overall_coverage(self, 
                                  validator_coverage: Dict[str, CoverageMetrics],
                                  scenario_coverage: Dict[str, CoverageMetrics],
                                  content_type_coverage: Dict[str, CoverageMetrics]) -> CoverageMetrics:
        """Calculate overall coverage metrics"""
        
        # Calculate weighted average coverage
        validator_avg = sum(m.coverage_percentage for m in validator_coverage.values()) / len(validator_coverage)
        scenario_avg = sum(m.coverage_percentage for m in scenario_coverage.values()) / len(scenario_coverage)
        content_type_avg = sum(m.coverage_percentage for m in content_type_coverage.values()) / len(content_type_coverage)
        
        # Weight: validators 40%, scenarios 30%, content types 30%
        overall_percentage = (validator_avg * 0.4) + (scenario_avg * 0.3) + (content_type_avg * 0.3)
        
        # Calculate total items and covered items
        total_items = (
            len(self.expected_validators) * len(self.expected_scenarios) * len(self.expected_content_types)
        )
        covered_items = int((overall_percentage / 100) * total_items)
        
        # Identify major gaps
        uncovered_items = []
        
        # Add untested validators
        for validator_id, metrics in validator_coverage.items():
            if metrics.coverage_percentage == 0:
                uncovered_items.append(f"validator:{validator_id}")
                
        # Add untested scenarios
        for scenario, metrics in scenario_coverage.items():
            if metrics.coverage_percentage < 50:  # Less than 50% validator coverage
                uncovered_items.append(f"scenario:{scenario}")
                
        # Add untested content types
        for content_type, metrics in content_type_coverage.items():
            if metrics.coverage_percentage < 25:  # Less than 25% combination coverage
                uncovered_items.append(f"content_type:{content_type}")
                
        return CoverageMetrics(
            total_items=total_items,
            covered_items=covered_items,
            coverage_percentage=overall_percentage,
            uncovered_items=uncovered_items,
            details={
                "validator_coverage": validator_avg,
                "scenario_coverage": scenario_avg,
                "content_type_coverage": content_type_avg,
                "coverage_breakdown": {
                    "validators": {
                        "tested": sum(1 for m in validator_coverage.values() if m.coverage_percentage > 0),
                        "total": len(validator_coverage)
                    },
                    "scenarios": {
                        "tested": sum(1 for m in scenario_coverage.values() if m.coverage_percentage > 0),
                        "total": len(scenario_coverage)
                    },
                    "content_types": {
                        "tested": sum(1 for m in content_type_coverage.values() if m.coverage_percentage > 0),
                        "total": len(content_type_coverage)
                    }
                }
            }
        )
        
    def _generate_recommendations(self,
                                validator_coverage: Dict[str, CoverageMetrics],
                                scenario_coverage: Dict[str, CoverageMetrics],
                                content_type_coverage: Dict[str, CoverageMetrics]) -> List[str]:
        """Generate recommendations for improving coverage"""
        
        recommendations = []
        
        # Validator recommendations
        untested_validators = [
            validator_id for validator_id, metrics in validator_coverage.items()
            if metrics.coverage_percentage == 0
        ]
        if untested_validators:
            recommendations.append(
                f"Implement tests for untested validators: {', '.join(untested_validators)}"
            )
            
        low_coverage_validators = [
            validator_id for validator_id, metrics in validator_coverage.items()
            if 0 < metrics.coverage_percentage < 50
        ]
        if low_coverage_validators:
            recommendations.append(
                f"Increase scenario coverage for validators: {', '.join(low_coverage_validators)}"
            )
            
        # Scenario recommendations
        poorly_covered_scenarios = [
            scenario for scenario, metrics in scenario_coverage.items()
            if metrics.coverage_percentage < 50
        ]
        if poorly_covered_scenarios:
            recommendations.append(
                f"Add more validator tests for scenarios: {', '.join(poorly_covered_scenarios)}"
            )
            
        # Content type recommendations
        untested_content_types = [
            content_type for content_type, metrics in content_type_coverage.items()
            if metrics.coverage_percentage == 0
        ]
        if untested_content_types:
            recommendations.append(
                f"Create tests for untested content types: {', '.join(untested_content_types)}"
            )
            
        # Specific improvement recommendations
        if len(recommendations) == 0:
            recommendations.append("Coverage is comprehensive. Consider adding edge case tests.")
        else:
            recommendations.append("Focus on achieving 80%+ coverage in all areas before adding new features.")
            
        # Priority recommendations based on coverage gaps
        overall_coverage = sum(
            sum(m.coverage_percentage for m in coverage.values()) / len(coverage)
            for coverage in [validator_coverage, scenario_coverage, content_type_coverage]
        ) / 3
        
        if overall_coverage < 60:
            recommendations.insert(0, "PRIORITY: Overall coverage is below 60%. Focus on basic test coverage first.")
        elif overall_coverage < 80:
            recommendations.insert(0, "Coverage is moderate. Focus on filling major gaps identified above.")
            
        return recommendations
        
    async def _save_coverage_report(self, report: CoverageReport) -> None:
        """Save coverage report to disk"""
        
        report_file = self.coverage_data_dir / f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert report to serializable format
        report_data = {
            "validator_coverage": {
                validator_id: {
                    "total_items": metrics.total_items,
                    "covered_items": metrics.covered_items,
                    "coverage_percentage": metrics.coverage_percentage,
                    "uncovered_items": metrics.uncovered_items,
                    "details": metrics.details
                }
                for validator_id, metrics in report.validator_coverage.items()
            },
            "scenario_coverage": {
                scenario: {
                    "total_items": metrics.total_items,
                    "covered_items": metrics.covered_items,
                    "coverage_percentage": metrics.coverage_percentage,
                    "uncovered_items": metrics.uncovered_items,
                    "details": metrics.details
                }
                for scenario, metrics in report.scenario_coverage.items()
            },
            "content_type_coverage": {
                content_type: {
                    "total_items": metrics.total_items,
                    "covered_items": metrics.covered_items,
                    "coverage_percentage": metrics.coverage_percentage,
                    "uncovered_items": metrics.uncovered_items,
                    "details": metrics.details
                }
                for content_type, metrics in report.content_type_coverage.items()
            },
            "overall_coverage": {
                "total_items": report.overall_coverage.total_items,
                "covered_items": report.overall_coverage.covered_items,
                "coverage_percentage": report.overall_coverage.coverage_percentage,
                "uncovered_items": report.overall_coverage.uncovered_items,
                "details": report.overall_coverage.details
            },
            "recommendations": report.recommendations,
            "timestamp": report.timestamp.isoformat()
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            logger.info(f"Coverage report saved to {report_file}")
        except Exception as e:
            logger.error(f"Failed to save coverage report: {e}")
            
    async def generate_coverage_trend_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate coverage trend report over time"""
        
        # Find coverage reports from the last N days
        report_files = []
        for file_path in self.coverage_data_dir.glob("coverage_report_*.json"):
            try:
                # Extract timestamp from filename
                timestamp_str = file_path.stem.split("_", 2)[2]  # coverage_report_YYYYMMDD_HHMMSS
                file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                if (datetime.now() - file_date).days <= days:
                    report_files.append((file_date, file_path))
            except (ValueError, IndexError):
                continue
                
        # Sort by date
        report_files.sort(key=lambda x: x[0])
        
        if len(report_files) < 2:
            return {"error": "Insufficient historical data for trend analysis"}
            
        # Load and analyze reports
        trend_data = {
            "dates": [],
            "overall_coverage": [],
            "validator_coverage": [],
            "scenario_coverage": [],
            "content_type_coverage": [],
            "recommendations_count": []
        }
        
        for file_date, file_path in report_files:
            try:
                with open(file_path, 'r') as f:
                    report_data = json.load(f)
                    
                trend_data["dates"].append(file_date.isoformat())
                trend_data["overall_coverage"].append(
                    report_data["overall_coverage"]["coverage_percentage"]
                )
                
                # Calculate average coverage for each category
                validator_avg = sum(
                    metrics["coverage_percentage"] 
                    for metrics in report_data["validator_coverage"].values()
                ) / len(report_data["validator_coverage"])
                trend_data["validator_coverage"].append(validator_avg)
                
                scenario_avg = sum(
                    metrics["coverage_percentage"]
                    for metrics in report_data["scenario_coverage"].values()
                ) / len(report_data["scenario_coverage"])
                trend_data["scenario_coverage"].append(scenario_avg)
                
                content_type_avg = sum(
                    metrics["coverage_percentage"]
                    for metrics in report_data["content_type_coverage"].values()
                ) / len(report_data["content_type_coverage"])
                trend_data["content_type_coverage"].append(content_type_avg)
                
                trend_data["recommendations_count"].append(
                    len(report_data["recommendations"])
                )
                
            except Exception as e:
                logger.error(f"Failed to load report {file_path}: {e}")
                continue
                
        # Calculate trends
        if len(trend_data["overall_coverage"]) >= 2:
            latest_coverage = trend_data["overall_coverage"][-1]
            previous_coverage = trend_data["overall_coverage"][-2]
            coverage_trend = latest_coverage - previous_coverage
            
            trend_analysis = {
                "coverage_trend": coverage_trend,
                "trend_direction": "improving" if coverage_trend > 0 else "declining" if coverage_trend < 0 else "stable",
                "latest_coverage": latest_coverage,
                "coverage_change_percentage": (coverage_trend / previous_coverage) * 100 if previous_coverage > 0 else 0
            }
        else:
            trend_analysis = {"error": "Insufficient data for trend calculation"}
            
        return {
            "trend_data": trend_data,
            "trend_analysis": trend_analysis,
            "report_count": len(report_files),
            "date_range": {
                "start": report_files[0][0].isoformat() if report_files else None,
                "end": report_files[-1][0].isoformat() if report_files else None
            }
        }