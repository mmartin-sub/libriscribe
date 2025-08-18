"""Markdown processing utilities using mistletoe for AST-based transformations."""

import logging
from typing import Literal

from mistletoe import Document
from mistletoe.block_token import Heading
from mistletoe.markdown_renderer import MarkdownRenderer

logger = logging.getLogger(__name__)


def remove_h3_from_markdown(markdown_text: str | None, action: Literal["remove", "comment"] = "remove") -> str:
    """
    Centralized function to process level 3 headers in revised chapters.

    Args:
        markdown_text: The input Markdown string
        action: "remove" to delete headers, "comment" to convert to HTML comments

    Returns:
        Processed Markdown string with level 3 headers handled according to action

    Raises:
        ValueError: If markdown_text is None or empty
        RuntimeError: If mistletoe parsing fails (indicates malformed Markdown)
    """
    if markdown_text is None or not markdown_text.strip():
        raise ValueError("markdown_text cannot be empty")

    try:
        if action == "comment":
            # For comment conversion, we'll use a simpler string-based approach
            # as it's harder to replace a node with a raw text/HTML comment node in the AST
            # without creating a custom token and renderer modification.
            lines = markdown_text.split("\n")
            new_lines: list[str] = []
            for line in lines:
                if line.strip().startswith("### "):
                    # Convert level 3 header to comment
                    header_text = line.strip()[4:]  # Remove '### '
                    comment_line = f"<!-- {header_text} -->"
                    new_lines.append(comment_line)
                else:
                    new_lines.append(line)
            return "\n".join(new_lines)

        # Parse the Markdown into an AST for the "remove" action
        # The correct way to get the AST is to instantiate the Document class
        doc = Document(markdown_text)

        if action == "remove":
            # Filter out level 3 headings, keeping everything else
            if doc.children is not None:
                doc.children = [
                    child for child in doc.children if not (isinstance(child, Heading) and child.level == 3)
                ]

        # Render the modified AST back to Markdown
        # The use of the context manager is the recommended approach
        with MarkdownRenderer() as renderer:
            output_markdown: str = renderer.render(doc)

        return output_markdown

    except Exception as e:
        logger.error(f"Failed to process markdown with mistletoe: {e}")
        raise RuntimeError(f"Markdown processing failed - likely malformed input: {e}")


def format_chapter_filename(chapter_number: int) -> str:
    """
    Format chapter filename with zero-padding.

    Args:
        chapter_number: The chapter number

    Returns:
        Formatted filename like "chapter_01.md"
    """
    return f"chapter_{chapter_number:02d}.md"


def format_scene_filename(chapter_number: int, scene_number: int) -> str:
    """
    Format scene filename with zero-padding.

    Args:
        chapter_number: The chapter number
        scene_number: The scene number

    Returns:
        Formatted filename like "chapter_01_scene_04.md"
    """
    return f"chapter_{chapter_number:02d}_scene_{scene_number:02d}.md"


def format_revised_chapter_filename(chapter_number: int) -> str:
    """
    Format revised chapter filename with zero-padding.

    Args:
        chapter_number: The chapter number

    Returns:
        Formatted filename like "chapter_01_revised.md"
    """
    return f"chapter_{chapter_number:02d}_revised.md"
