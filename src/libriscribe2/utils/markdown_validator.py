# src/libriscribe2/utils/markdown_validator.py

import logging
import os
import warnings

import mistletoe

logger = logging.getLogger(__name__)


class MarkdownValidationError(Exception):
    """Raised when Markdown content is invalid."""

    pass


def validate_markdown(content: str, *, strict: bool = False) -> bool:
    """Validate Markdown content using mistletoe parser.

    Args:
        content: The Markdown content to validate
        strict: If True, raise exception on validation failure.
                If False, issue warning and return False.
                In test environment (PYTEST_CURRENT_TEST set), warnings become errors.

    Returns:
        True if valid Markdown, False otherwise

    Raises:
        MarkdownValidationError: If strict=True or in test mode and validation fails
    """
    try:
        mistletoe.markdown(content)
        return True
    except Exception as e:
        error_msg = f"Invalid Markdown content: {e}"

        # Check if we're in test mode
        in_test_mode = os.getenv("PYTEST_CURRENT_TEST") is not None

        if strict or in_test_mode:
            raise MarkdownValidationError(error_msg) from e
        else:
            warnings.warn(error_msg, UserWarning, stacklevel=2)
            logger.warning(error_msg)
            return False
