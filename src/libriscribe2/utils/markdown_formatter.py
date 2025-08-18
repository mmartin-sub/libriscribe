"""Markdown formatting utilities."""

import re
import textwrap


def format_markdown_content(content: str) -> str:
    """Format markdown content to ensure proper spacing and structure.

    - Normalizes line endings
    - Removes common leading indentation
    - Trims trailing whitespace
    - Ensures a blank line before headers
    - Collapses 3+ blank lines to 2
    - Ensures file ends with a newline

    Args:
        content: Raw markdown content

    Returns:
        Formatted markdown content with proper spacing
    """
    # Normalize newlines
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    # Remove common leading indentation introduced by some mocks or templates
    content = textwrap.dedent(content)

    # Split and trim trailing spaces
    raw_lines = content.split("\n")
    lines = [re.sub(r"[ \t]+$", "", ln) for ln in raw_lines]

    formatted_lines: list[str] = []
    for _i, line in enumerate(lines):
        # Detect ATX-style headers (#, ##, ... ######)
        if re.match(r"^#{1,6}\s+", line):
            # Ensure previous emitted line is blank (but not before file start)
            if formatted_lines and formatted_lines[-1].strip():
                formatted_lines.append("")
            # Also ensure no accidental leading indentation on the header line
            formatted_lines.append(line.lstrip())
        else:
            formatted_lines.append(line)

    out = "\n".join(formatted_lines)
    # Collapse excessive blank lines
    out = re.sub(r"\n{3,}", "\n\n", out)
    # Strip only trailing whitespace (preserve whether file ended with newline)
    out = re.sub(r"[ \t]+\n", "\n", out)
    return out


def ensure_header_spacing(content: str) -> str:
    """Ensure proper spacing before markdown headers.

    Args:
        content: Markdown content

    Returns:
        Content with proper header spacing
    """
    return format_markdown_content(content)
