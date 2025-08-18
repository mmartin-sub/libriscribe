#!/usr/bin/env python3
"""
Script to ensure the correct Python version is used for linting tools.
This script detects available Python versions and ensures Python 3.12+ is used.
"""

import subprocess
import sys


def find_python_version(min_version=(3, 12)):
    """Find the best available Python version."""
    # Try common Python executable names
    python_names = ["python3.12", "python3.13", "python3.11", "python3.10", "python3", "python"]

    for name in python_names:
        try:
            result = subprocess.run([name, "--version"], capture_output=True, text=True, check=True)
            version_str = result.stdout.strip()

            # Extract version numbers
            if "Python" in version_str:
                version_part = version_str.split()[1]
                version_tuple = tuple(map(int, version_part.split(".")[:2]))

                if version_tuple >= min_version:
                    return name, version_tuple
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            continue

    return None, None


def main():
    """Main function to check and report Python version."""
    python_exe, version = find_python_version()

    if python_exe is None:
        print("❌ No suitable Python version found (need 3.12+)")
        print("Available Python versions:")
        for name in ["python3.12", "python3.11", "python3.10", "python3", "python"]:
            try:
                result = subprocess.run([name, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✓ {name}: {result.stdout.strip()}")
                else:
                    print(f"  ✗ {name}: Not available")
            except FileNotFoundError:
                print(f"  ✗ {name}: Not found")
        sys.exit(1)

    print(f"✅ Using {python_exe} (Python {version[0]}.{version[1]})")

    # Check if we're in a virtual environment
    if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        print(f"✅ Running in virtual environment: {sys.prefix}")
    else:
        print("⚠️  Not running in a virtual environment")

    return python_exe


if __name__ == "__main__":
    main()
