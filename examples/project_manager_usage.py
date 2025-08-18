#!/usr/bin/env python3
"""
ProjectManagerAgent Usage Example

This example demonstrates how to use the ProjectManagerAgent for comprehensive
book creation and project management in LibriScribe2.

Key features demonstrated:
1. Project creation and initialization
2. Loading existing projects
3. Content generation workflow
4. Chapter writing and review
5. Quality assurance processes
6. AutoGen integration
7. Error handling and recovery
"""

import asyncio
import logging
from pathlib import Path

from libriscribe2.agents.project_manager import ProjectManagerAgent
from libriscribe2.knowledge_base import ProjectKnowledgeBase
from libriscribe2.settings import Settings

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def demonstrate_project_creation():
    """Demonstrate creating a new project from scratch"""

    print("🚀 Project Creation Demonstration")
    print("=" * 50)

    # Initialize settings and project manager
    settings = Settings()
    project_manager = ProjectManagerAgent(settings)
    project_manager.initialize_llm_client("openai")

    # Create a new project knowledge base
    project_kb = ProjectKnowledgeBase(
        project_name="demo-fantasy-novel",
        title="The Crystal Prophecy",
        genre="fantasy",
        description="An epic fantasy adventure about a young mage discovering ancient prophecies",
        category="Fiction",
        language="English",
        target_chapters=10,
        target_characters=5,
        worldbuilding_enabled=True,
        auto_title=False,
    )

    print(f"✅ Created project: {project_kb.title}")

    # Initialize the project
    project_manager.initialize_project_with_data(project_kb)

    print(f"✅ Project initialized at: {project_manager.project_dir}")

    # Generate core content
    print("\n📝 Generating core content...")

    try:
        await project_manager.generate_concept()
        print("✅ Concept generated")

        await project_manager.generate_outline()
        print("✅ Outline generated")

        await project_manager.generate_characters()
        print("✅ Characters generated")

        await project_manager.generate_worldbuilding()
        print("✅ Worldbuilding generated")

    except Exception as e:
        logger.error(f"Error during content generation: {e}")
        return False

    print("🎉 Project creation completed successfully!")
    return True


async def demonstrate_project_loading():
    """Demonstrate loading an existing project"""

    print("\n📂 Project Loading Demonstration")
    print("=" * 50)

    settings = Settings()
    project_manager = ProjectManagerAgent(settings)
    project_manager.initialize_llm_client("openai")

    try:
        # Try to load the project we just created
        project_manager.load_project_data("demo-fantasy-novel")

        print("✅ Project loaded successfully!")
        print(f"   - Title: {project_manager.project_knowledge_base.title}")
        print(f"   - Genre: {project_manager.project_knowledge_base.genre}")
        print(f"   - Chapters: {len(project_manager.project_knowledge_base.chapters)}")
        print(f"   - Characters: {len(project_manager.project_knowledge_base.characters)}")

        return True

    except FileNotFoundError as e:
        print(f"❌ Project not found: {e}")
        return False
    except ValueError as e:
        print(f"❌ Invalid project data: {e}")
        return False


async def demonstrate_chapter_writing():
    """Demonstrate chapter writing and review process"""

    print("\n📖 Chapter Writing Demonstration")
    print("=" * 50)

    settings = Settings()
    project_manager = ProjectManagerAgent(settings)
    project_manager.initialize_llm_client("openai")

    try:
        # Load existing project
        project_manager.load_project_data("demo-fantasy-novel")

        # Write and review first few chapters
        for chapter_num in range(1, 4):  # Write chapters 1-3
            print(f"\n📝 Writing Chapter {chapter_num}...")

            try:
                # Write and automatically review the chapter
                await project_manager.write_and_review_chapter(chapter_num)
                print(f"✅ Chapter {chapter_num} completed")

                # Create checkpoint after each chapter
                project_manager.checkpoint()
                print(f"💾 Checkpoint saved after Chapter {chapter_num}")

            except Exception as e:
                logger.error(f"Error writing chapter {chapter_num}: {e}")
                continue

        print("🎉 Chapter writing demonstration completed!")
        return True

    except FileNotFoundError:
        print("❌ Project not found. Please run project creation first.")
        return False


async def demonstrate_quality_assurance():
    """Demonstrate quality assurance processes"""

    print("\n🔍 Quality Assurance Demonstration")
    print("=" * 50)

    settings = Settings()
    project_manager = ProjectManagerAgent(settings)
    project_manager.initialize_llm_client("openai")

    try:
        project_manager.load_project_data("demo-fantasy-novel")

        # Perform quality checks on existing chapters
        chapters = list(project_manager.project_knowledge_base.chapters.keys())

        if not chapters:
            print("⚠️  No chapters found. Please write some chapters first.")
            return False

        # Check first chapter for demonstration
        chapter_num = 1

        print(f"🔍 Performing quality checks on Chapter {chapter_num}...")

        try:
            # Plagiarism check
            await project_manager.check_plagiarism(chapter_num)
            print("✅ Plagiarism check completed")

            # Fact check
            await project_manager.fact_check(chapter_num)
            print("✅ Fact check completed")

            # Content review
            await project_manager.review_content(chapter_num)
            print("✅ Content review completed")

            # Edit chapter for quality
            await project_manager.edit_chapter(chapter_num)
            print("✅ Chapter editing completed")

        except Exception as e:
            logger.error(f"Error during quality assurance: {e}")
            return False

        print("🎉 Quality assurance demonstration completed!")
        return True

    except FileNotFoundError:
        print("❌ Project not found. Please run project creation first.")
        return False


async def demonstrate_research_and_formatting():
    """Demonstrate research capabilities and final formatting"""

    print("\n📚 Research and Formatting Demonstration")
    print("=" * 50)

    settings = Settings()
    project_manager = ProjectManagerAgent(settings)
    project_manager.initialize_llm_client("openai")

    try:
        project_manager.load_project_data("demo-fantasy-novel")

        # Research a topic related to the book
        print("🔬 Researching fantasy magic systems...")
        await project_manager.research_topic("fantasy magic systems")
        print("✅ Research completed")

        # Format the final book
        print("📄 Formatting final book...")
        await project_manager.format_book()
        print("✅ Book formatting completed")

        # Check if title generation is needed
        if project_manager.needs_title_generation():
            print("📝 Generating project title...")
            success = await project_manager.generate_project_title()
            if success:
                print(f"✅ New title generated: {project_manager.project_knowledge_base.title}")
            else:
                print("⚠️  Title generation failed")

        print("🎉 Research and formatting demonstration completed!")
        return True

    except FileNotFoundError:
        print("❌ Project not found. Please run project creation first.")
        return False


async def demonstrate_autogen_integration():
    """Demonstrate AutoGen multi-agent framework integration"""

    print("\n🤖 AutoGen Integration Demonstration")
    print("=" * 50)

    # Create project manager with AutoGen enabled
    settings = Settings()
    project_manager = ProjectManagerAgent(settings, use_autogen=True)
    project_manager.initialize_llm_client("openai")

    # Create a new project for AutoGen demonstration
    project_kb = ProjectKnowledgeBase(
        project_name="autogen-demo-book",
        title="AI Coordinated Novel",
        genre="science fiction",
        description="A book created using AI agent coordination",
        target_chapters=5,
    )

    project_manager.initialize_project_with_data(project_kb)
    print("✅ AutoGen-enabled project created")

    try:
        # Run AutoGen workflow
        print("🚀 Running AutoGen workflow...")
        success = await project_manager.run_autogen_workflow()

        if success:
            print("✅ AutoGen workflow completed successfully")

            # Get analytics
            analytics = project_manager.get_autogen_analytics()
            print(f"📊 Analytics: {analytics}")

            # Export logs
            log_path = str(project_manager.project_dir / "autogen_logs.json")
            project_manager.export_autogen_logs(log_path)
            print(f"📄 Logs exported to: {log_path}")

        else:
            print("❌ AutoGen workflow failed")

        # Try hybrid workflow as alternative
        print("\n🔄 Running hybrid workflow...")
        hybrid_success = await project_manager.run_hybrid_workflow()

        if hybrid_success:
            print("✅ Hybrid workflow completed successfully")
        else:
            print("❌ Hybrid workflow failed")

    except Exception as e:
        logger.error(f"Error in AutoGen demonstration: {e}")
        return False

    print("🎉 AutoGen integration demonstration completed!")
    return True


async def demonstrate_error_handling():
    """Demonstrate error handling and recovery"""

    print("\n⚠️  Error Handling Demonstration")
    print("=" * 50)

    settings = Settings()
    project_manager = ProjectManagerAgent(settings)
    project_manager.initialize_llm_client("openai")

    # Test 1: Loading non-existent project
    print("🧪 Test 1: Loading non-existent project")
    try:
        project_manager.load_project_data("non-existent-project")
        print("❌ This should have failed!")
    except FileNotFoundError as e:
        print(f"✅ Correctly caught FileNotFoundError: {e}")

    # Test 2: Running agent without project
    print("\n🧪 Test 2: Running agent without project initialization")
    try:
        await project_manager.run_agent("concept_generator")
        print("❌ This should have failed!")
    except ValueError as e:
        print(f"✅ Correctly caught ValueError: {e}")

    # Test 3: Running non-existent agent
    print("\n🧪 Test 3: Running non-existent agent")
    try:
        # First initialize a project
        project_kb = ProjectKnowledgeBase(project_name="error-test")
        project_manager.initialize_project_with_data(project_kb)

        await project_manager.run_agent("non_existent_agent")
        print("❌ This should have failed!")
    except ValueError as e:
        print(f"✅ Correctly caught ValueError: {e}")

    print("🎉 Error handling demonstration completed!")


async def demonstrate_complete_workflow():
    """Demonstrate a complete book creation workflow with error recovery"""

    print("\n🎯 Complete Workflow Demonstration")
    print("=" * 50)

    settings = Settings()
    project_manager = ProjectManagerAgent(settings)
    project_manager.initialize_llm_client("openai")

    # Create project
    project_kb = ProjectKnowledgeBase(
        project_name="complete-workflow-demo",
        title="The Complete Guide",
        genre="non-fiction",
        description="A comprehensive guide created with LibriScribe2",
        target_chapters=3,
        target_characters=0,  # Non-fiction doesn't need characters
        worldbuilding_enabled=False,
    )

    project_manager.initialize_project_with_data(project_kb)
    print("✅ Project created")

    try:
        # Phase 1: Core content generation
        print("\n📋 Phase 1: Core Content Generation")
        await project_manager.generate_concept()
        project_manager.checkpoint()
        print("✅ Concept generated and saved")

        await project_manager.generate_outline()
        project_manager.checkpoint()
        print("✅ Outline generated and saved")

        # Phase 2: Chapter writing with error recovery
        print("\n📖 Phase 2: Chapter Writing")
        for chapter_num in range(1, 4):
            try:
                await project_manager.write_and_review_chapter(chapter_num)
                project_manager.checkpoint()
                print(f"✅ Chapter {chapter_num} completed and saved")
            except Exception as e:
                logger.error(f"Failed to write chapter {chapter_num}: {e}")
                print(f"⚠️  Skipping chapter {chapter_num} due to error")
                continue

        # Phase 3: Quality assurance
        print("\n🔍 Phase 3: Quality Assurance")
        for chapter_num in range(1, 4):
            try:
                await project_manager.check_plagiarism(chapter_num)
                await project_manager.fact_check(chapter_num)
                print(f"✅ Quality checks completed for Chapter {chapter_num}")
            except Exception as e:
                logger.error(f"Quality check failed for chapter {chapter_num}: {e}")
                continue

        # Phase 4: Final formatting
        print("\n📄 Phase 4: Final Formatting")
        await project_manager.format_book()
        print("✅ Book formatted successfully")

        # Final checkpoint
        project_manager.checkpoint()
        print("💾 Final checkpoint saved")

        print("\n🎉 Complete workflow demonstration finished successfully!")

        # Show final project status
        kb = project_manager.project_knowledge_base
        print("\n📊 Final Project Status:")
        print(f"   - Title: {kb.title}")
        print(f"   - Chapters: {len(kb.chapters)}")
        print(f"   - Project Directory: {project_manager.project_dir}")

        return True

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        return False


async def main():
    """Run all demonstrations"""

    print("🚀 LibriScribe2 ProjectManagerAgent Usage Demonstration")
    print("=" * 60)

    # Create demo directory
    demo_dir = Path("demo_projects")
    demo_dir.mkdir(exist_ok=True)

    try:
        # Run demonstrations in sequence
        demos = [
            ("Project Creation", demonstrate_project_creation),
            ("Project Loading", demonstrate_project_loading),
            ("Chapter Writing", demonstrate_chapter_writing),
            ("Quality Assurance", demonstrate_quality_assurance),
            ("Research and Formatting", demonstrate_research_and_formatting),
            ("AutoGen Integration", demonstrate_autogen_integration),
            ("Error Handling", demonstrate_error_handling),
            ("Complete Workflow", demonstrate_complete_workflow),
        ]

        results = {}

        for demo_name, demo_func in demos:
            print(f"\n{'=' * 60}")
            print(f"Running: {demo_name}")
            print(f"{'=' * 60}")

            try:
                result = await demo_func()
                results[demo_name] = result
                print(f"✅ {demo_name} completed")
            except Exception as e:
                logger.error(f"Demo '{demo_name}' failed: {e}")
                results[demo_name] = False
                print(f"❌ {demo_name} failed")

        # Summary
        print(f"\n{'=' * 60}")
        print("DEMONSTRATION SUMMARY")
        print(f"{'=' * 60}")

        for demo_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{demo_name}: {status}")

        total_passed = sum(1 for success in results.values() if success)
        total_demos = len(results)

        print(f"\nOverall: {total_passed}/{total_demos} demonstrations passed")

        if total_passed == total_demos:
            print("🎉 All demonstrations completed successfully!")
        else:
            print("⚠️  Some demonstrations failed. Check logs for details.")

    except KeyboardInterrupt:
        print("\n⚠️  Demonstration interrupted by user")
    except Exception as e:
        logger.error(f"Demonstration suite failed: {e}")
        print("❌ Demonstration suite failed")


if __name__ == "__main__":
    asyncio.run(main())
