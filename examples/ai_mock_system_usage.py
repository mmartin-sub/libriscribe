#!/usr/bin/env python3
"""
AI Mock System Usage Examples

This file demonstrates how to use the AI Mock System for testing
LibriScribe validation components without consuming AI resources.
"""

import asyncio
import json
from typing import Dict, Any

from libriscribe.validation.ai_mock import (
    AIMockManager,
    MockScenario,
    create_mock_manager,
    get_mock_config_for_testing
)


async def basic_mock_usage():
    """Demonstrate basic mock usage"""
    print("=== Basic Mock Usage ===")
    
    # Initialize mock manager
    mock_manager = AIMockManager()
    
    # Get mock response for content validation
    response = await mock_manager.get_ai_response(
        prompt="Validate this chapter content for tone consistency and quality",
        validator_id="content_validator",
        content_type="chapter",
        scenario=MockScenario.SUCCESS,
        use_mock=True
    )
    
    print(f"Response content: {response.content}")
    print(f"Tokens used: {response.tokens_used}")
    print(f"Cost: ${response.cost}")
    print(f"Confidence: {response.confidence}")
    print()


async def test_different_scenarios():
    """Test different mock scenarios"""
    print("=== Testing Different Scenarios ===")
    
    mock_manager = AIMockManager()
    
    scenarios = [
        MockScenario.SUCCESS,
        MockScenario.HIGH_QUALITY,
        MockScenario.LOW_QUALITY,
        MockScenario.PARTIAL_FAILURE
    ]
    
    for scenario in scenarios:
        print(f"\nTesting scenario: {scenario.value}")
        
        try:
            response = await mock_manager.get_ai_response(
                prompt="Test validation prompt",
                validator_id="quality_validator",
                content_type="manuscript",
                scenario=scenario,
                use_mock=True
            )
            
            # Parse response content
            content_data = json.loads(response.content)
            print(f"  Status: {content_data.get('status', 'unknown')}")
            print(f"  Quality Score: {content_data.get('quality_score', 'N/A')}")
            print(f"  Findings: {len(content_data.get('findings', []))}")
            
        except Exception as e:
            print(f"  Exception: {e}")


async def test_error_scenarios():
    """Test error scenarios"""
    print("=== Testing Error Scenarios ===")
    
    mock_manager = AIMockManager()
    
    # Test timeout scenario
    print("\nTesting TIMEOUT scenario:")
    try:
        response = await mock_manager.get_ai_response(
            prompt="Test timeout",
            validator_id="test_validator",
            content_type="test",
            scenario=MockScenario.TIMEOUT,
            use_mock=True
        )
    except TimeoutError as e:
        print(f"  Timeout caught as expected: {e}")
    
    # Test rate limit scenario
    print("\nTesting RATE_LIMIT scenario:")
    try:
        response = await mock_manager.get_ai_response(
            prompt="Test rate limit",
            validator_id="test_validator",
            content_type="test",
            scenario=MockScenario.RATE_LIMIT,
            use_mock=True
        )
    except Exception as e:
        print(f"  Rate limit exception caught: {e}")
    
    # Test invalid response scenario
    print("\nTesting INVALID_RESPONSE scenario:")
    response = await mock_manager.get_ai_response(
        prompt="Test invalid response",
        validator_id="test_validator",
        content_type="test",
        scenario=MockScenario.INVALID_RESPONSE,
        use_mock=True
    )
    print(f"  Invalid response content: {response.content}")


async def comprehensive_test_suite():
    """Run comprehensive test suite"""
    print("=== Comprehensive Test Suite ===")
    
    mock_manager = AIMockManager()
    
    # Create test suite for multiple validators
    validators = [
        "content_validator",
        "publishing_standards_validator",
        "quality_originality_validator",
        "ai_output_validator"
    ]
    
    print(f"Creating test suite for {len(validators)} validators...")
    test_suite = await mock_manager.create_test_suite(validators)
    
    print("Test suite created:")
    for validator_id, scenarios in test_suite.items():
        print(f"  {validator_id}: {len(scenarios)} scenarios")
    
    # Run the test suite
    print("\nRunning test suite...")
    results = await mock_manager.run_test_suite(test_suite)
    
    print(f"\nTest Results:")
    print(f"  Total tests: {results['total_tests']}")
    print(f"  Passed: {results['passed_tests']}")
    print(f"  Failed: {results['failed_tests']}")
    print(f"  Success rate: {(results['passed_tests']/results['total_tests']*100):.1f}%")
    
    # Show coverage report
    coverage = results['coverage_report']
    print(f"\nCoverage Report:")
    print(f"  Validators tested: {coverage['validators_tested']}")
    print(f"  Scenarios covered: {coverage['scenarios_covered']}/{coverage['total_scenarios']}")
    print(f"  Coverage percentage: {coverage['coverage_percentage']:.1f}%")
    
    # Show results by validator
    print(f"\nResults by Validator:")
    for validator_id, validator_results in results['validator_results'].items():
        print(f"  {validator_id}:")
        print(f"    Passed: {validator_results['passed']}")
        print(f"    Failed: {validator_results['failed']}")
        
        # Show failed scenarios
        failed_scenarios = [
            scenario for scenario, result in validator_results['scenarios'].items()
            if result.startswith('failed')
        ]
        if failed_scenarios:
            print(f"    Failed scenarios: {', '.join(failed_scenarios)}")


async def record_and_playback_demo():
    """Demonstrate record and playback functionality"""
    print("=== Record and Playback Demo ===")
    
    mock_manager = AIMockManager()
    
    # Simulate recording a real AI interaction
    print("Simulating real AI interaction recording...")
    real_response = await mock_manager.get_ai_response(
        prompt="Validate this content for publishing standards",
        validator_id="publishing_standards_validator",
        content_type="manuscript",
        use_mock=False  # This would call real AI in production
    )
    
    print(f"Real AI response recorded (simulated)")
    print(f"  Model: {real_response.model}")
    print(f"  Tokens: {real_response.tokens_used}")
    print(f"  Cost: ${real_response.cost}")
    
    # Now use the recorded response
    print("\nUsing recorded response...")
    cached_response = await mock_manager.get_ai_response(
        prompt="Validate this content for publishing standards",  # Same prompt
        validator_id="publishing_standards_validator",           # Same validator
        content_type="manuscript",                              # Same content type
        use_mock=True  # Will use recorded response
    )
    
    print(f"Cached response retrieved")
    print(f"  Content matches: {real_response.content == cached_response.content}")
    print(f"  Tokens match: {real_response.tokens_used == cached_response.tokens_used}")


async def usage_statistics_demo():
    """Demonstrate usage statistics tracking"""
    print("=== Usage Statistics Demo ===")
    
    mock_manager = AIMockManager()
    
    # Make several mock calls
    validators = ["content_validator", "quality_validator", "publishing_validator"]
    scenarios = [MockScenario.SUCCESS, MockScenario.HIGH_QUALITY, MockScenario.LOW_QUALITY]
    
    print("Making mock calls to generate statistics...")
    for validator in validators:
        for scenario in scenarios:
            await mock_manager.get_ai_response(
                prompt=f"Test prompt for {validator}",
                validator_id=validator,
                content_type="test",
                scenario=scenario,
                use_mock=True
            )
    
    # Get usage statistics
    stats = mock_manager.get_usage_stats()
    
    print(f"\nUsage Statistics:")
    print(f"  Mock calls: {stats['mock_calls']}")
    print(f"  Real calls: {stats['real_calls']}")
    print(f"  Validators tested: {len(stats['validators_tested'])}")
    print(f"  Recorded interactions: {stats['recorded_interactions']}")
    
    print(f"\nScenarios used:")
    for scenario, count in stats['scenarios_used'].items():
        print(f"  {scenario}: {count}")
    
    print(f"\nValidators tested:")
    for validator in stats['validators_tested']:
        print(f"  {validator}")
    
    coverage = stats['mock_coverage']
    print(f"\nMock Coverage:")
    print(f"  Coverage percentage: {coverage['coverage_percentage']:.1f}%")
    print(f"  Scenarios covered: {coverage['scenarios_covered']}/{coverage['total_scenarios']}")


async def configuration_driven_demo():
    """Demonstrate configuration-driven mock usage"""
    print("=== Configuration-Driven Demo ===")
    
    # Get recommended configuration
    config = get_mock_config_for_testing()
    print("Recommended mock configuration:")
    print(json.dumps(config, indent=2))
    
    # Create mock manager with configuration
    mock_manager = await create_mock_manager(config)
    
    print(f"\nMock manager created with configuration")
    print(f"Mock data directory: {mock_manager.mock_data_dir}")
    
    # Test with configuration
    response = await mock_manager.get_ai_response(
        prompt="Test with configuration",
        validator_id="content_validator",
        content_type="chapter",
        use_mock=True
    )
    
    print(f"Response received with configured mock manager")
    print(f"Scenario used: {response.scenario.value}")


async def validator_specific_responses():
    """Show validator-specific mock responses"""
    print("=== Validator-Specific Responses ===")
    
    mock_manager = AIMockManager()
    
    validators = [
        "content_validator",
        "publishing_standards_validator", 
        "quality_originality_validator"
    ]
    
    for validator_id in validators:
        print(f"\n{validator_id} response:")
        response = await mock_manager.get_ai_response(
            prompt="Test validation",
            validator_id=validator_id,
            content_type="manuscript",
            scenario=MockScenario.SUCCESS,
            use_mock=True
        )
        
        # Parse and display key metrics
        content_data = json.loads(response.content)
        
        if validator_id == "content_validator":
            print(f"  Tone consistency: {content_data.get('tone_consistency_score', 'N/A')}")
            print(f"  Outline adherence: {content_data.get('outline_adherence_score', 'N/A')}")
            print(f"  Quality score: {content_data.get('quality_score', 'N/A')}")
        elif validator_id == "publishing_standards_validator":
            print(f"  Formatting score: {content_data.get('formatting_score', 'N/A')}")
            print(f"  Metadata completeness: {content_data.get('metadata_completeness', 'N/A')}")
            print(f"  Publishing ready: {content_data.get('publishing_ready', 'N/A')}")
        elif validator_id == "quality_originality_validator":
            print(f"  Originality score: {content_data.get('originality_score', 'N/A')}")
            print(f"  Grammar score: {content_data.get('grammar_score', 'N/A')}")
            print(f"  Plagiarism detected: {content_data.get('plagiarism_detected', 'N/A')}")
        
        print(f"  Findings: {len(content_data.get('findings', []))}")


async def main():
    """Run all demo functions"""
    print("AI Mock System Usage Examples")
    print("=" * 50)
    
    demos = [
        basic_mock_usage,
        test_different_scenarios,
        test_error_scenarios,
        comprehensive_test_suite,
        record_and_playback_demo,
        usage_statistics_demo,
        configuration_driven_demo,
        validator_specific_responses
    ]
    
    for demo in demos:
        try:
            await demo()
            print("\n" + "-" * 50 + "\n")
        except Exception as e:
            print(f"Error in {demo.__name__}: {e}")
            print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())