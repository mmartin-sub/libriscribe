#!/usr/bin/env python3
"""
AI Mock System Usage Example

This example demonstrates the improved AI mock system with:
1. OpenAI SDK with LiteLLM configured via .env (transparent to service)
2. API key-based switching (empty OPENAI_API_KEY = mock mode)
3. Live response recording for input/output mapping population

Usage:
    # Mock mode (no API key)
    unset OPENAI_API_KEY
    python examples/ai_mock_system_usage.py

    # Real AI mode (with API key)
    export OPENAI_API_KEY="your-key-here"
    export OPENAI_BASE_URL="https://your-litellm-proxy.com/v1"  # Optional
    python examples/ai_mock_system_usage.py
"""

import asyncio
import json
import logging
import os
from pathlib import Path

# Import the updated AI mock system
from src.libriscribe2.validation.ai_mock import (
    AIMockManager,
    MockScenario,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def demonstrate_api_key_based_switching():
    """
    Demonstrate automatic switching between mock and real AI based on API key
    """

    print("🔑 API Key-Based Switching Demonstration")
    print("=" * 50)

    # Check current environment
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    print("Environment Status:")
    print(f"  - OPENAI_API_KEY: {'SET' if api_key else 'NOT SET'}")
    print(f"  - OPENAI_BASE_URL: {base_url}")

    # Create mock manager (automatically detects mode)
    mock_manager = AIMockManager(mock_data_dir=".demo/mock_data")

    print("\nAI Mock Manager Status:")
    print(f"  - Mode: {'MOCK' if mock_manager.use_mock_mode else 'REAL AI'}")
    print(f"  - OpenAI Client: {'Initialized' if mock_manager.openai_client else 'Not Available'}")

    # Test AI response
    print("\n🤖 Testing AI Response...")

    try:
        response = await mock_manager.get_ai_response(
            prompt="Analyze this chapter for content quality and tone consistency: 'Once upon a time, there was a brave knight who embarked on a quest to save the kingdom.'",
            validator_id="content_validator",
            content_type="chapter",
            model="gpt-4",
            scenario=MockScenario.SUCCESS,  # Only used in mock mode
        )

        print("✅ Response received:")
        print(f"   - Mode used: {'MOCK' if mock_manager.use_mock_mode else 'REAL AI'}")
        print(f"   - Model: {response.model}")
        print(f"   - Tokens: {response.tokens_used}")
        print(f"   - Cost: ${response.cost:.4f}")
        print(f"   - Content length: {len(response.content)} chars")

        # Try to parse response as JSON
        try:
            response_data = json.loads(response.content)
            print("   - Response type: Valid JSON")
            if "validation_score" in response_data:
                print(f"   - Validation score: {response_data['validation_score']}")
        except json.JSONDecodeError:
            print("   - Response type: Text (not JSON)")

    except Exception as e:
        print(f"❌ Error: {e}")

    return mock_manager


async def demonstrate_live_response_recording():
    """
    Demonstrate recording live AI responses for mock data population
    """

    print("\n📹 Live Response Recording Demonstration")
    print("=" * 50)

    mock_manager = AIMockManager(mock_data_dir=".demo/mock_data")

    if mock_manager.use_mock_mode:
        print("⚠️  Mock mode active - cannot record live responses")
        print("   Set OPENAI_API_KEY to enable live recording")
        return

    print("🎬 Recording live AI responses...")

    # Define prompts to record
    prompts_to_record = [
        {
            "prompt": "Validate this chapter content for tone consistency: 'The hero walked bravely into the dark forest, his heart filled with determination.'",
            "validator_id": "content_validator",
            "content_type": "chapter",
            "expected_scenario": "success",
        },
        {
            "prompt": "Check this manuscript for publishing standards: Title: 'My Great Novel', Length: 50000 words, Genre: Fantasy",
            "validator_id": "publishing_standards_validator",
            "content_type": "manuscript",
            "expected_scenario": "success",
        },
        {
            "prompt": "Analyze this low-quality content: 'this is bad writing with no caps or punctuation and poor grammar'",
            "validator_id": "content_validator",
            "content_type": "chapter",
            "expected_scenario": "low_quality",
        },
    ]

    try:
        # Record live responses
        results = await mock_manager.populate_mock_mappings_from_live(prompts=prompts_to_record, model="gpt-4")

        print("✅ Recording Results:")
        print(f"   - Total prompts: {results['total_prompts']}")
        print(f"   - Successful: {results['successful_recordings']}")
        print(f"   - Failed: {results['failed_recordings']}")

        total_cost = sum(r.get("cost", 0) for r in results["recordings"])
        total_tokens = sum(r.get("tokens_used", 0) for r in results["recordings"])

        print(f"   - Total tokens: {total_tokens}")
        print(f"   - Total cost: ${total_cost:.4f}")

        if results["recordings"]:
            print("\n📝 Recorded Interactions:")
            for i, recording in enumerate(results["recordings"][:3]):  # Show first 3
                print(f"   {i + 1}. {recording['validator_id']} - {recording['content_type']}")
                print(f"      Prompt: {recording['prompt']}")
                print(f"      Tokens: {recording['tokens_used']}, Cost: ${recording['cost']:.4f}")

        if results["errors"]:
            print("\n❌ Errors:")
            for error in results["errors"]:
                print(f"   - {error['validator_id']}: {error['error']}")

    except Exception as e:
        print(f"❌ Recording failed: {e}")


async def demonstrate_mock_playback():
    """
    Demonstrate playing back recorded responses in mock mode
    """

    print("\n▶️  Mock Playback Demonstration")
    print("=" * 50)

    # Temporarily disable API key to force mock mode
    original_api_key = os.environ.get("OPENAI_API_KEY")
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    try:
        mock_manager = AIMockManager(mock_data_dir=".demo/mock_data")

        print(f"🎭 Mock mode active: {mock_manager.use_mock_mode}")

        # Try to get response for previously recorded prompt
        response = await mock_manager.get_ai_response(
            prompt="Validate this chapter content for tone consistency: 'The hero walked bravely into the dark forest, his heart filled with determination.'",
            validator_id="content_validator",
            content_type="chapter",
            model="gpt-4",
        )

        print("✅ Playback response:")
        print(f"   - Source: {'Recorded interaction' if response.metadata.get('real_ai') else 'Generated mock'}")
        print(f"   - Model: {response.model}")
        print(f"   - Tokens: {response.tokens_used}")
        print(f"   - Cost: ${response.cost:.4f}")
        print(f"   - Scenario: {response.scenario.value}")

        # Show content preview
        content_preview = response.content[:200] + "..." if len(response.content) > 200 else response.content
        print(f"   - Content preview: {content_preview}")

    finally:
        # Restore original API key
        if original_api_key:
            os.environ["OPENAI_API_KEY"] = original_api_key


async def demonstrate_scenario_testing():
    """
    Demonstrate testing different scenarios in mock mode
    """

    print("\n🎭 Scenario Testing Demonstration")
    print("=" * 50)

    # Force mock mode for scenario testing
    original_api_key = os.environ.get("OPENAI_API_KEY")
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    try:
        mock_manager = AIMockManager(mock_data_dir=".demo/mock_data")

        scenarios_to_test = [
            MockScenario.SUCCESS,
            MockScenario.HIGH_QUALITY,
            MockScenario.LOW_QUALITY,
            MockScenario.FAILURE,
            MockScenario.EDGE_CASE,
        ]

        print(f"Testing {len(scenarios_to_test)} scenarios...")

        for scenario in scenarios_to_test:
            try:
                response = await mock_manager.get_ai_response(
                    prompt=f"Test scenario: {scenario.value}",
                    validator_id="content_validator",
                    content_type="chapter",
                    model="gpt-4",
                    scenario=scenario,
                )

                # Try to extract quality score
                try:
                    response_data = json.loads(response.content)
                    quality_score = response_data.get("validation_score", "N/A")
                except Exception:
                    quality_score = "N/A"

                print(f"✅ {scenario.value.upper()}: Quality={quality_score}, Tokens={response.tokens_used}")

            except Exception as e:
                print(f"❌ {scenario.value.upper()}: Error - {e!s}")

    finally:
        # Restore original API key
        if original_api_key:
            os.environ["OPENAI_API_KEY"] = original_api_key


async def demonstrate_usage_statistics():
    """
    Demonstrate usage statistics and monitoring
    """

    print("\n📊 Usage Statistics Demonstration")
    print("=" * 50)

    mock_manager = AIMockManager(mock_data_dir=".demo/mock_data")

    # Get usage statistics
    stats = mock_manager.get_usage_stats()

    print("📈 Current Usage Statistics:")
    print(f"   - Mock calls: {stats['mock_calls']}")
    print(f"   - Real AI calls: {stats['real_calls']}")
    print(f"   - Live recordings: {stats['live_recordings']}")
    print(f"   - Validators tested: {len(stats['validators_tested'])}")
    print(f"   - Recorded interactions: {stats['recorded_interactions']}")

    if stats["scenarios_used"]:
        print("   - Scenarios used:")
        for scenario, count in stats["scenarios_used"].items():
            print(f"     • {scenario}: {count} times")

    if stats["validators_tested"]:
        print(f"   - Validators tested: {', '.join(stats['validators_tested'])}")

    # Show mock coverage
    coverage = stats["mock_coverage"]
    print(f"   - Mock coverage: {coverage['coverage_percentage']:.1f}%")


async def demonstrate_configuration_examples():
    """
    Show configuration examples for different environments
    """

    print("\n⚙️  Configuration Examples")
    print("=" * 50)

    print("🔧 Environment Configurations:")

    print("\n1. Development (Mock Mode):")
    print("   # .env file")
    print("   # OPENAI_API_KEY=  # Empty or not set")
    print("   # OPENAI_BASE_URL=  # Not needed for mock mode")

    print("\n2. Testing with Live Recording:")
    print("   # .env file")
    print("   OPENAI_API_KEY=your-openai-key-here")
    print("   OPENAI_BASE_URL=https://api.openai.com/v1")

    print("\n3. Production with LiteLLM Proxy:")
    print("   # .env file")
    print("   OPENAI_API_KEY=your-proxy-key-here")
    print("   OPENAI_BASE_URL=https://your-litellm-proxy.com/v1")

    print("\n🐍 Python Usage:")
    print("""
    # Automatic mode detection
    mock_manager = AIMockManager()

    # Get AI response (automatically uses mock or real based on API key)
    response = await mock_manager.get_ai_response(
        prompt="Your validation prompt",
        validator_id="content_validator",
        content_type="chapter",
        model="gpt-4"
    )

    # Process response (same code for mock or real!)
    result_data = json.loads(response.content)
    """)


async def main():
    """
    Main demonstration function
    """

    print("🚀 AI Mock System Usage Demonstration")
    print("=" * 60)

    # Create demo directory
    Path(".demo").mkdir(exist_ok=True)

    try:
        # 1. Demonstrate API key-based switching
        mock_manager = await demonstrate_api_key_based_switching()

        # 2. If real AI is available, demonstrate live recording
        if not mock_manager.use_mock_mode:
            await demonstrate_live_response_recording()

        # 3. Demonstrate mock playback
        await demonstrate_mock_playback()

        # 4. Demonstrate scenario testing
        await demonstrate_scenario_testing()

        # 5. Show usage statistics
        await demonstrate_usage_statistics()

        # 6. Show configuration examples
        await demonstrate_configuration_examples()

        print("\n🎉 Demonstration Complete!")
        print("📁 Demo files saved to: .demo/")
        print("📊 Mock data saved to: .demo/mock_data/")

        print("\n💡 Key Takeaways:")
        print("   1. Set OPENAI_API_KEY to use real AI, leave empty for mock mode")
        print("   2. Use OPENAI_BASE_URL to configure LiteLLM proxy (transparent)")
        print("   3. Live responses are automatically recorded for future mock use")
        print("   4. Same code works in both mock and real AI modes")
        print("   5. Mock mode provides fast, free, deterministic testing")

    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
