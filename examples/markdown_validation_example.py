#!/usr/bin/env python3
"""
Example demonstrating Markdown validation functionality in LibriScribe2.

This example shows how to use the markdown validation features:
1. Basic validation with warnings
2. Strict validation with exceptions
3. Integration with file writing
"""

import sys
import warnings
from pathlib import Path

# Add the src directory to the path so we can import libriscribe2
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from libriscribe2.utils.file_utils import write_markdown_file
from libriscribe2.utils.markdown_validator import MarkdownValidationError, validate_markdown


def example_basic_validation():
    """Demonstrate basic markdown validation."""
    print("=== Basic Markdown Validation ===")

    # Valid markdown
    valid_md = """# My Book Title

This is a **bold** paragraph with *italic* text.

## Chapter 1

- List item 1
- List item 2

```python
print("Hello, World!")
```
"""

    result = validate_markdown(valid_md)
    print(f"Valid markdown validation result: {result}")

    # Empty content (also valid)
    result = validate_markdown("")
    print(f"Empty content validation result: {result}")


def example_strict_validation():
    """Demonstrate strict validation mode."""
    print("\n=== Strict Validation Mode ===")

    valid_md = "# Valid Title\n\nValid content."

    try:
        result = validate_markdown(valid_md, strict=True)
        print(f"Strict validation passed: {result}")
    except MarkdownValidationError as e:
        print(f"Strict validation failed: {e}")


def example_file_writing_with_validation():
    """Demonstrate file writing with validation."""
    print("\n=== File Writing with Validation ===")

    # Create a temporary directory for examples
    temp_dir = Path("temp_examples")
    temp_dir.mkdir(exist_ok=True)

    # Valid markdown content
    valid_content = """# Example Book

This is an example of **valid** markdown content.

## Features

- Proper headers
- **Bold** and *italic* text
- Lists and formatting

```python
# Code blocks work too
def hello():
    print("Hello from LibriScribe2!")
```
"""

    # Write with validation enabled (default)
    try:
        write_markdown_file(str(temp_dir / "valid_example.md"), valid_content)
        print("✅ Valid markdown file written successfully")
    except Exception as e:
        print(f"❌ Failed to write valid markdown: {e}")

    # Write with validation disabled
    try:
        write_markdown_file(str(temp_dir / "no_validation.md"), valid_content, validate=False)
        print("✅ File written without validation")
    except Exception as e:
        print(f"❌ Failed to write without validation: {e}")

    # Clean up
    for file in temp_dir.glob("*.md"):
        file.unlink()
    temp_dir.rmdir()


def example_warning_handling():
    """Demonstrate how warnings are handled outside of test mode."""
    print("\n=== Warning Handling (Outside Tests) ===")

    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # This would normally issue a warning in non-test mode
        # but since we're likely running in test mode, it might raise an exception
        try:
            # For demonstration, we'll show what happens with valid content
            result = validate_markdown("# Valid content")
            print(f"Validation result: {result}")

            if w:
                print(f"Warnings captured: {len(w)}")
                for warning in w:
                    print(f"  - {warning.message}")
            else:
                print("No warnings issued (content was valid)")

        except MarkdownValidationError as e:
            print(f"Validation error (test mode): {e}")


if __name__ == "__main__":
    print("LibriScribe2 Markdown Validation Examples")
    print("=" * 50)

    example_basic_validation()
    example_strict_validation()
    example_file_writing_with_validation()
    example_warning_handling()

    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nKey takeaways:")
    print("- Validation is enabled by default when writing markdown files")
    print("- Use validate=False to disable validation")
    print("- In test mode (pytest), warnings become errors")
    print("- Use strict=True for explicit error handling")
