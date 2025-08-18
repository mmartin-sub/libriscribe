#!/usr/bin/env python3
"""
Test Project Cleanup Script

This script moves test projects from the main projects directory to tests/output
to prevent confusion with user-created books.
"""

import shutil
import sys
from pathlib import Path


def identify_test_projects(projects_dir: Path) -> list[Path]:
    """Identify test projects in the projects directory."""
    test_projects: list[Path] = []

    if not projects_dir.exists():
        print(f"Projects directory {projects_dir} does not exist")
        return test_projects

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        project_name = project_dir.name

        # Check if this looks like a test project
        if is_test_project(project_name):
            test_projects.append(project_dir)

    return test_projects


def is_test_project(project_name: str) -> bool:
    """Determine if a project name indicates it's a test project."""
    test_indicators = [
        "test-",
        "quick-test",
        "test_",
        "demo-",
        "sample-",
        "example-",
        "temp-",
        "tmp-",
        "debug-",
        "dev-",
        "experiment-",
        "trial-",
        "check-",
        "verify-",
        "validate-",
        "test_config",
        "test_character",
        "test_concept",
        "test_logging",
        "test_security",
        "test_",
    ]

    project_lower = project_name.lower()

    # Check for test indicators
    for indicator in test_indicators:
        if project_lower.startswith(indicator):
            return True

    # Check for timestamp patterns that suggest test projects
    if "-2025" in project_name and any(indicator in project_lower for indicator in ["test", "demo", "sample"]):
        return True

    return False


def move_test_projects(test_projects: list[Path], output_dir: Path) -> None:
    """Move test projects to the tests/output directory."""
    if not test_projects:
        print("No test projects found to move")
        return

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    moved_count = 0
    failed_count = 0

    for project_dir in test_projects:
        try:
            # Create destination path
            dest_path = output_dir / project_dir.name

            # If destination already exists, add a suffix
            counter = 1
            while dest_path.exists():
                dest_path = output_dir / f"{project_dir.name}_{counter}"
                counter += 1

            # Move the project
            shutil.move(str(project_dir), str(dest_path))
            print(f"✅ Moved: {project_dir.name} -> tests/output/{dest_path.name}")
            moved_count += 1

        except Exception as e:
            print(f"❌ Failed to move {project_dir.name}: {e}")
            failed_count += 1

    print("\n📊 Summary:")
    print(f"   Moved: {moved_count} projects")
    print(f"   Failed: {failed_count} projects")
    print(f"   Total: {len(test_projects)} projects")


def list_test_projects(projects_dir: Path) -> None:
    """List all test projects without moving them."""
    test_projects = identify_test_projects(projects_dir)

    if not test_projects:
        print("No test projects found")
        return

    print(f"Found {len(test_projects)} test projects:")
    for project_dir in test_projects:
        print(f"  - {project_dir.name}")


def main():
    """Main function."""
    # Get project directories
    projects_dir = Path("projects")
    output_dir = Path("tests/output")

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "list":
            print("🔍 Listing test projects...")
            list_test_projects(projects_dir)
            return
        elif command == "move":
            print("🚚 Moving test projects...")
            test_projects = identify_test_projects(projects_dir)
            move_test_projects(test_projects, output_dir)
            return
        elif command == "help":
            print("""
Test Project Cleanup Script

Usage:
  python scripts/cleanup_test_projects.py [command]

Commands:
  list    - List all test projects without moving them
  move    - Move test projects to tests/output directory
  help    - Show this help message

Examples:
  python scripts/cleanup_test_projects.py list
  python scripts/cleanup_test_projects.py move
            """)
            return
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
            return

    # Default behavior: list then ask for confirmation
    print("🔍 Identifying test projects...")
    test_projects = identify_test_projects(projects_dir)

    if not test_projects:
        print("No test projects found")
        return

    print(f"\nFound {len(test_projects)} test projects:")
    for project_dir in test_projects:
        print(f"  - {project_dir.name}")

    print(f"\nThese projects will be moved to: {output_dir}")
    response = input("\nDo you want to move these projects? (y/N): ")

    if response.lower() in ["y", "yes"]:
        move_test_projects(test_projects, output_dir)
    else:
        print("Operation cancelled")


if __name__ == "__main__":
    main()
