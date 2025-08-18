"""
Language normalization utilities for Libriscribe.
Uses langcodes to convert user input to BCP 47 language tags.
"""

import logging
import re
from typing import Any

logger: logging.Logger = logging.getLogger(__name__)

# Language mappings for common cases
LANGUAGE_MAPPINGS = {
    # Language codes (already normalized)
    "en": "en",
    "fr": "fr",
    "es": "es",
    "de": "de",
    "it": "it",
    "pt": "pt",
    "ru": "ru",
    "zh": "zh",
    "ja": "ja",
    "ko": "ko",
    # Language names
    "english": "en",
    "french": "fr",
    "spanish": "es",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "russian": "ru",
    "chinese": "zh",
    "japanese": "ja",
    "korean": "ko",
    # Regional variants
    "english (british)": "en-GB",
    "english (us)": "en-US",
    "english (american)": "en-US",
    "british english": "en-GB",
    "american english": "en-US",
    "uk english": "en-GB",
    "us english": "en-US",
    "spanish (spain)": "es-ES",
    "spanish (mexico)": "es-MX",
    "castilian spanish": "es-ES",
    "mexican spanish": "es-MX",
    "french (france)": "fr-FR",
    "french (canada)": "fr-CA",
    "portuguese (portugal)": "pt-PT",
    "portuguese (brazil)": "pt-BR",
    "european portuguese": "pt-PT",
    "brazilian portuguese": "pt-BR",
}


def normalize_language(user_input: Any) -> str:
    """
    Normalize a user-supplied language string to a BCP 47 language tag.

    This function converts various language inputs (names, codes, variants) into
    standardized BCP 47 language tags that are suitable for LLM prompts and
    consistent storage.

    Args:
        user_input: The language string to normalize. Can be:
            - Language names: "English", "French", "Spanish"
            - Language codes: "en", "fr", "es"
            - Regional variants: "English (British)", "en-GB", "en-US"
            - Common variations: "british english", "american english"

    Returns:
        A normalized BCP 47 language tag (e.g., "en", "en-GB", "fr", "es-ES")

    Examples:
        >>> normalize_language("English")
        'en'
        >>> normalize_language("English (British)")
        'en-GB'
        >>> normalize_language("british english")
        'en-GB'
        >>> normalize_language("French")
        'fr'
        >>> normalize_language("Spanish (Spain)")
        'es-ES'
        >>> normalize_language("invalid language")
        'en'  # Falls back to English
    """
    input_str = str(user_input) if user_input is not None else ""
    if not input_str.strip():
        logger.debug(f"normalize_language: input='{user_input}' -> output='en' (empty input)")
        return "en"

    # Clean and normalize the input - remove special chars but keep letters, spaces, parentheses, hyphens
    cleaned = re.sub(r"[^a-zA-Z\s\(\)\-]", "", input_str.strip().lower())
    # Remove trailing hyphens and underscores that might interfere with matching
    cleaned = re.sub(r"[-_]+$", "", cleaned)

    # Check direct mappings first
    if cleaned in LANGUAGE_MAPPINGS:
        result = LANGUAGE_MAPPINGS[cleaned]
        logger.debug(f"normalize_language: input='{user_input}' -> output='{result}' (direct mapping)")
        return result

    # If already a valid BCP 47 tag, return as-is
    if re.match(r"^[a-z]{2}(-[A-Z]{2})?$", input_str.strip()):
        result = input_str.strip().lower()
        logger.debug(f"normalize_language: input='{user_input}' -> output='{result}' (valid BCP 47)")
        return result

    # Fallback to English
    logger.debug(f"normalize_language: input='{user_input}' -> output='en' (fallback)")
    return "en"
