# tests/unit/utils/test_markdown_formatter.py
"""Tests for markdown formatting utilities."""

from libriscribe2.utils.markdown_formatter import format_markdown_content


class TestMarkdownFormatter:
    """Test markdown formatting utilities."""

    def test_format_markdown_content_applies_all_fixes(self):
        """Test that format_markdown_content applies all formatting fixes."""
        input_text = """Some content
---
More content"""

        expected = """Some content
---
More content"""

        result = format_markdown_content(input_text)
        assert result == expected
