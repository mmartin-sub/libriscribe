#!/usr/bin/env python3
"""
Pre-commit hook to check for Pydantic v1 syntax.
Prevents committing code that uses deprecated Pydantic v1 patterns.
"""

import re
import sys
from pathlib import Path

# Patterns that indicate Pydantic v1 usage
V1_PATTERNS = [
    # Old validator imports (but not field_validator or model_validator)
    (
        r"from pydantic import.*validator(?!.*field_validator)(?!.*model_validator)(?!.*field_validator)(?!.*model_validator)",
        "Use @field_validator or @model_validator instead of @validator",
    ),
    (
        r"from pydantic import.*root_validator",
        "Use @model_validator instead of @root_validator",
    ),
    # Old validator decorators
    (r"@validator\(", "Use @field_validator instead of @validator"),
    (r"@root_validator\(", "Use @model_validator instead of @root_validator"),
    # Old validation methods
    (r"\.parse_obj\(", "Use .model_validate() instead of .parse_obj()"),
    (r"\.parse_raw\(", "Use .model_validate_json() instead of .parse_raw()"),
    (r"\.dict\(", "Use .model_dump() instead of .dict()"),
    # More specific pattern for Pydantic model .json() calls - only catch model instances
    (r"(self|model|kb|data|obj)\.json\(", "Use .model_dump_json() instead of .json() for Pydantic models"),
    # Old Config class
    (r"class Config:", "Use model_config = ConfigDict() instead of inner Config class"),
    # Old BaseSettings (should use pydantic-settings)
    (
        r"from pydantic import BaseSettings",
        "Use pydantic-settings instead of BaseSettings",
    ),
    (
        r"class.*BaseSettings(?!.*pydantic_settings)",
        "Use pydantic-settings instead of BaseSettings",
    ),
]


def check_file(file_path: Path) -> list:
    """Check a single file for Pydantic v1 patterns."""
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        # Check if file imports from pydantic_settings (which is v2)
        has_pydantic_settings_import = any("from pydantic_settings import" in line for line in lines)

        for line_num, line in enumerate(lines, 1):
            for pattern, message in V1_PATTERNS:
                if re.search(pattern, line):
                    # Skip if the line contains field_validator, model_validator, or pydantic_settings
                    if "field_validator" in line or "model_validator" in line or "pydantic_settings" in line:
                        continue
                    # Skip if file imports from pydantic_settings (v2)
                    if has_pydantic_settings_import and "BaseSettings" in line:
                        continue
                    violations.append((line_num, line.strip(), message))

    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)

    return violations


def main():
    """Main function to check all provided files."""
    if len(sys.argv) < 2:
        print("Usage: python check_pydantic_v1.py <file1> <file2> ...")
        sys.exit(1)

    all_violations = []

    for file_path in sys.argv[1:]:
        path = Path(file_path)
        if path.exists() and path.suffix == ".py" and "check_pydantic_v1.py" not in str(path):
            violations = check_file(path)
            if violations:
                all_violations.append((path, violations))

    if all_violations:
        print("❌ Pydantic v1 syntax detected!")
        print("\nPlease update to Pydantic v2 syntax:\n")

        for file_path, violations in all_violations:
            print(f"📁 {file_path}:")
            for line_num, line, message in violations:
                print(f"  Line {line_num}: {line}")
                print(f"  💡 {message}")
                print()

        print("🔗 For migration guide, see: https://docs.pydantic.dev/latest/migration/")
        sys.exit(1)
    else:
        print("✅ No Pydantic v1 syntax detected")


if __name__ == "__main__":
    main()
