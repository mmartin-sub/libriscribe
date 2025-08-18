"""Unit tests for markdown processor utilities."""

import pytest

from libriscribe2.utils.markdown_processor import (
    format_chapter_filename,
    format_revised_chapter_filename,
    format_scene_filename,
    remove_h3_from_markdown,
)


class TestMarkdownProcessor:
    """Test cases for markdown processor functions."""

    def test_remove_h3_from_markdown_basic(self):
        """Test basic level 3 header removal."""
        input_md = """
# Chapter 1

Some content here.

### Section Header

Content under section.

## Scene Title

More content.
"""
        result = remove_h3_from_markdown(input_md)

        assert "### Section Header" not in result
        assert "Content under section." in result
        assert "# Chapter 1" in result
        assert "## Scene Title" in result

    def test_remove_h3_from_markdown_comment_action(self):
        """Test converting level 3 headers to comments."""
        input_md = """
# Chapter 1

### Section Header

Content under section.
"""
        result = remove_h3_from_markdown(input_md, action="comment")

        assert "### Section Header" not in result
        assert "<!-- Section Header -->" in result
        assert "Content under section." in result

    def test_remove_h3_from_markdown_no_h3(self):
        """Test processing markdown with no level 3 headers."""
        input_md = """
# Chapter 1

## Scene 1

Content here.

## Scene 2

More content.
"""
        result = remove_h3_from_markdown(input_md)

        # Should be unchanged (normalize whitespace for comparison)
        # mistletoe may normalize whitespace, so we compare the essential content
        assert "# Chapter 1" in result
        assert "## Scene 1" in result
        assert "## Scene 2" in result
        assert "Content here." in result
        assert "More content." in result

    def test_remove_h3_from_markdown_empty_input(self):
        """Test handling of empty input."""
        with pytest.raises(ValueError, match="markdown_text cannot be empty"):
            remove_h3_from_markdown("")

        with pytest.raises(ValueError, match="markdown_text cannot be empty"):
            remove_h3_from_markdown("   ")

    def test_remove_h3_from_markdown_none_input(self):
        """Test handling of None input."""
        with pytest.raises(ValueError, match="markdown_text cannot be empty"):
            remove_h3_from_markdown(None)

    def test_remove_h3_from_markdown_malformed(self):
        """Test handling of malformed markdown."""
        malformed_md = """
# Chapter 1

### Section Header
Content without proper spacing
### Another Section
"""
        # Should handle gracefully or raise RuntimeError
        try:
            result = remove_h3_from_markdown(malformed_md)
            # If it processes successfully, verify headers are removed
            assert "### Section Header" not in result
            assert "### Another Section" not in result
        except RuntimeError:
            # Expected for severely malformed markdown
            pass

    def test_remove_h3_from_markdown_complex_structure(self):
        """Test processing complex markdown structure."""
        input_md = """
# Chapter 1: The Beginning

## Scene 1: Opening

Some opening content.

### Subsection A

Content A.

### Subsection B

Content B.

## Scene 2: Development

More content.

### Another Subsection

Final content.
"""
        result = remove_h3_from_markdown(input_md)

        # Level 3 headers should be removed
        assert "### Subsection A" not in result
        assert "### Subsection B" not in result
        assert "### Another Subsection" not in result

        # Other content should be preserved
        assert "# Chapter 1: The Beginning" in result
        assert "## Scene 1: Opening" in result
        assert "## Scene 2: Development" in result
        assert "Content A." in result
        assert "Content B." in result
        assert "Final content." in result

    def test_remove_h3_from_markdown_comment_action_complex(self):
        """Test comment conversion with complex structure."""
        input_md = """
# Chapter 1

### Section 1

Content 1.

### Section 2

Content 2.
"""
        result = remove_h3_from_markdown(input_md, action="comment")

        # Headers should be converted to comments
        assert "<!-- Section 1 -->" in result
        assert "<!-- Section 2 -->" in result

        # Original headers should be removed
        assert "### Section 1" not in result
        assert "### Section 2" not in result

        # Content should be preserved
        assert "Content 1." in result
        assert "Content 2." in result


class TestFilenameFormatters:
    """Test cases for filename formatting functions."""

    def test_format_chapter_filename(self):
        """Test chapter filename formatting with zero-padding."""
        assert format_chapter_filename(1) == "chapter_01.md"
        assert format_chapter_filename(10) == "chapter_10.md"
        assert format_chapter_filename(99) == "chapter_99.md"

    def test_format_scene_filename(self):
        """Test scene filename formatting with zero-padding."""
        assert format_scene_filename(1, 1) == "chapter_01_scene_01.md"
        assert format_scene_filename(10, 5) == "chapter_10_scene_05.md"
        assert format_scene_filename(99, 99) == "chapter_99_scene_99.md"

    def test_format_revised_chapter_filename(self):
        """Test revised chapter filename formatting with zero-padding."""
        assert format_revised_chapter_filename(1) == "chapter_01_revised.md"
        assert format_revised_chapter_filename(10) == "chapter_10_revised.md"
        assert format_revised_chapter_filename(99) == "chapter_99_revised.md"
