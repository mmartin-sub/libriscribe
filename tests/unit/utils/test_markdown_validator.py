"""
Unit tests for markdown_validator module.
"""

import pytest

from libriscribe2.utils.markdown_validator import MarkdownValidationError, validate_markdown


class TestMarkdownValidator:
    """Test cases for markdown_validator module."""

    def test_validate_markdown_valid_content(self):
        """Test validation with valid Markdown content."""
        # Arrange
        valid_markdown = """# Test Title

This is a paragraph with **bold** and *italic* text.

## Subsection

- List item 1
- List item 2

```python
print("Hello, World!")
```
"""

        # Act & Assert
        assert validate_markdown(valid_markdown) is True

    def test_validate_markdown_empty_content(self):
        """Test validation with empty content."""
        # Act & Assert
        assert validate_markdown("") is True

    def test_validate_markdown_simple_content(self):
        """Test validation with simple content."""
        # Act & Assert
        assert validate_markdown("# Simple Title") is True
        assert validate_markdown("Just plain text") is True

    def test_validate_markdown_strict_mode_valid(self):
        """Test strict mode with valid content."""
        # Arrange
        valid_markdown = "# Valid Title\n\nValid content."

        # Act & Assert
        assert validate_markdown(valid_markdown, strict=True) is True

    def test_validate_markdown_warning_mode_on_error(self):
        """Test that warnings are converted to errors in test mode."""
        # In test mode (PYTEST_CURRENT_TEST is set), warnings become errors
        import mistletoe

        original_markdown = mistletoe.markdown

        def mock_markdown(content):
            raise ValueError("Simulated parsing error")

        mistletoe.markdown = mock_markdown
        try:
            # In test mode, this should raise MarkdownValidationError
            with pytest.raises(MarkdownValidationError, match="Invalid Markdown content"):
                validate_markdown("test content")
        finally:
            mistletoe.markdown = original_markdown

    def test_validate_markdown_warning_mode_outside_tests(self):
        """Test that warnings are issued when not in test mode."""
        import os

        import mistletoe

        # Temporarily unset the test environment variable
        original_test_env = os.environ.pop("PYTEST_CURRENT_TEST", None)

        original_markdown = mistletoe.markdown

        def mock_markdown(content):
            raise ValueError("Simulated parsing error")

        mistletoe.markdown = mock_markdown
        try:
            with pytest.warns(UserWarning, match="Invalid Markdown content"):
                result = validate_markdown("test content")
                assert result is False
        finally:
            mistletoe.markdown = original_markdown
            # Restore the test environment variable if it was set
            if original_test_env is not None:
                os.environ["PYTEST_CURRENT_TEST"] = original_test_env

    def test_validate_markdown_strict_mode_raises_exception(self):
        """Test that strict mode raises exception on validation failure."""
        # Mock mistletoe to raise an exception
        import mistletoe

        original_markdown = mistletoe.markdown

        def mock_markdown(content):
            raise ValueError("Simulated parsing error")

        mistletoe.markdown = mock_markdown
        try:
            with pytest.raises(MarkdownValidationError, match="Invalid Markdown content"):
                validate_markdown("test content", strict=True)
        finally:
            mistletoe.markdown = original_markdown
