"""
Tests for language normalization utilities.
"""

from libriscribe2.utils.language import normalize_language


class TestNormalizeLanguage:
    """Test cases for the normalize_language function."""

    def test_common_language_names(self):
        """Test normalization of common language names."""
        test_cases = [
            ("English", "en"),
            ("english", "en"),
            ("ENGLISH", "en"),
            ("French", "fr"),
            ("Spanish", "es"),
            ("German", "de"),
            ("Italian", "it"),
            ("Portuguese", "pt"),
            ("Russian", "ru"),
            ("Chinese", "zh"),
            ("Japanese", "ja"),
            ("Korean", "ko"),
        ]

        for input_lang, expected in test_cases:
            assert normalize_language(input_lang) == expected, f"Failed for input: {input_lang}"

    def test_language_codes(self):
        """Test normalization of language codes."""
        test_cases = [
            ("en", "en"),
            ("fr", "fr"),
            ("es", "es"),
            ("de", "de"),
            ("it", "it"),
            ("pt", "pt"),
            ("ru", "ru"),
            ("zh", "zh"),
            ("ja", "ja"),
            ("ko", "ko"),
        ]

        for input_lang, expected in test_cases:
            assert normalize_language(input_lang) == expected, f"Failed for input: {input_lang}"

    def test_regional_variants(self):
        """Test normalization of regional language variants."""
        test_cases = [
            ("English (British)", "en-GB"),
            ("English (US)", "en-US"),
            ("English (American)", "en-US"),
            ("British English", "en-GB"),
            ("American English", "en-US"),
            ("Spanish (Spain)", "es-ES"),
            ("Spanish (Mexico)", "es-MX"),
            ("French (France)", "fr-FR"),
            ("French (Canada)", "fr-CA"),
            ("Portuguese (Portugal)", "pt-PT"),
            ("Portuguese (Brazil)", "pt-BR"),
        ]

        for input_lang, expected in test_cases:
            assert normalize_language(input_lang) == expected, f"Failed for input: {input_lang}"

    def test_common_variations(self):
        """Test normalization of common language variations."""
        test_cases = [
            ("british english", "en-GB"),
            ("american english", "en-US"),
            ("uk english", "en-GB"),
            ("us english", "en-US"),
            ("castilian spanish", "es-ES"),
            ("mexican spanish", "es-MX"),
            ("european portuguese", "pt-PT"),
            ("brazilian portuguese", "pt-BR"),
        ]

        for input_lang, expected in test_cases:
            assert normalize_language(input_lang) == expected, f"Failed for input: {input_lang}"

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        test_cases = [
            ("", "en"),  # Empty string
            ("   ", "en"),  # Whitespace only
            ("  English  ", "en"),  # Extra whitespace
            ("english", "en"),  # Lowercase
            ("ENGLISH", "en"),  # Uppercase
            ("EnGlIsH", "en"),  # Mixed case
        ]

        for input_lang, expected in test_cases:
            assert normalize_language(input_lang) == expected, f"Failed for input: '{input_lang}'"

    def test_invalid_inputs(self):
        """Test behavior with invalid or unrecognized inputs."""
        test_cases = [
            ("invalid language", "en"),
            ("xyz123", "en"),
            ("fake language", "en"),
            ("unknown", "en"),
            ("not a language", "en"),
        ]

        for input_lang, expected in test_cases:
            assert normalize_language(input_lang) == expected, f"Failed for input: {input_lang}"

    def test_none_input(self):
        """Test behavior with None input."""
        assert normalize_language(None) == "en"

    def test_special_characters(self):
        """Test behavior with special characters in input."""
        test_cases = [
            ("English!", "en"),
            ("French?", "fr"),
            ("Spanish.", "es"),
            ("German-", "de"),
            ("Italian_", "it"),
        ]

        for input_lang, expected in test_cases:
            assert normalize_language(input_lang) == expected, f"Failed for input: {input_lang}"

    def test_numbers_and_symbols(self):
        """Test behavior with numbers and symbols in input."""
        test_cases = [
            ("English123", "en"),
            ("French@#$", "fr"),
            ("Spanish123@#$", "es"),
        ]

        for input_lang, expected in test_cases:
            assert normalize_language(input_lang) == expected, f"Failed for input: {input_lang}"

    def test_consistency(self):
        """Test that the same input always produces the same output."""
        test_inputs = ["English", "english", "ENGLISH", "  English  "]
        expected = "en"

        for input_lang in test_inputs:
            result = normalize_language(input_lang)
            assert result == expected, f"Failed for input: '{input_lang}', got: {result}"

    def test_bcp47_compliance(self):
        """Test that outputs are valid BCP 47 language tags."""
        test_inputs = [
            "English",
            "French",
            "Spanish",
            "German",
            "Italian",
            "English (British)",
            "Spanish (Spain)",
            "French (Canada)",
            "Portuguese (Brazil)",
            "Chinese",
            "Japanese",
        ]

        for input_lang in test_inputs:
            result = normalize_language(input_lang)
            # BCP 47 tags should be lowercase language codes with optional region
            assert result.islower() or "-" in result, f"Invalid BCP 47 tag: {result}"
            if "-" in result:
                lang, region = result.split("-", 1)
                assert len(lang) == 2, f"Invalid language code: {lang}"
                assert len(region) == 2, f"Invalid region code: {region}"
