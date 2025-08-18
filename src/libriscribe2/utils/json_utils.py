# src/libriscribe2/utils/json_utils.py
"""Common JSON processing utilities for libriscribe2."""

import json
import logging
import re
from typing import Any, cast

import jsonschema
import pyjson5

logger = logging.getLogger(__name__)


def load_json_with_schema(file_path: str, schema: dict[str, Any]) -> dict[str, Any] | None:
    """
    Loads a JSON5 file and validates it against a schema.

    Args:
        file_path: The path to the JSON5 file.
        schema: The JSON schema to validate against.

    Returns:
        The validated JSON data, or None if validation fails.
    """
    try:
        with open(file_path) as f:
            data = cast(dict[str, Any], pyjson5.load(f))
        jsonschema.validate(data, schema)
        return data
    except (OSError, jsonschema.ValidationError, pyjson5.Json5Exception) as e:
        logger.error(f"Failed to load or validate JSON file {file_path}: {e}")
        return None


class JSONProcessor:
    """Utility class for common JSON processing operations."""

    @staticmethod
    def flatten_nested_dict(data: dict[str, Any]) -> dict[str, str]:
        """Flatten nested dictionaries into string values."""
        flattened = {}
        for key, value in data.items():
            if isinstance(value, dict):
                # Flatten nested dictionary into a single string
                flattened_value = ""
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        flattened_value += f"{sub_key}: {sub_value} "
                    else:
                        flattened_value += f"{sub_key}: {json.dumps(sub_value)} "
                flattened[key] = flattened_value.strip()
            elif isinstance(value, str):
                flattened[key] = value
            else:
                flattened[key] = json.dumps(value)
        return flattened

    @staticmethod
    def normalize_dict_keys(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize dictionary keys to lowercase."""
        return {k.lower(): v for k, v in data.items()}

    @staticmethod
    def validate_json_structure(data: Any, expected_type: type = dict) -> bool:
        """Validate JSON data structure."""
        if not isinstance(data, expected_type):
            return False
        if expected_type is dict and not data:
            return False
        return True

    @staticmethod
    def safe_json_dumps(obj: Any, **kwargs: Any) -> str:
        """Safely convert object to JSON string."""
        try:
            return json.dumps(obj, **kwargs)
        except (TypeError, ValueError) as e:
            logger.error(f"Error serializing object to JSON: {e}")
            return "{}"

    @staticmethod
    def safe_json_loads(json_str: str) -> Any | None:
        """Safely parse JSON string using pyjson5."""
        try:
            return pyjson5.loads(json_str)
        except pyjson5.Json5Exception as e:
            logger.error(f"Error parsing JSON string: {e}")
            return None

    @staticmethod
    def extract_json_from_response(response: str) -> dict[str, Any] | None:
        """Extract JSON from LLM response, handling various formats."""
        if not response or not isinstance(response, str):
            return None

        # Try to find JSON in code blocks first
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end != -1:
                json_str = response[start:end].strip()
                return JSONProcessor.safe_json_loads(json_str)

        # Try to find JSON in generic code blocks
        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                json_str = response[start:end].strip()
                # Skip language identifier if present
                if json_str.startswith("json"):
                    json_str = json_str[4:].strip()
                return JSONProcessor.safe_json_loads(json_str)

        # Try to find JSON object in the response
        try:
            # Look for { ... } pattern
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end != -1 and end > start:
                json_str = response[start : end + 1]
                return JSONProcessor.safe_json_loads(json_str)
        except (ValueError, TypeError, IndexError) as e:
            # Log the specific error for debugging but continue gracefully
            logger.debug(f"Failed to extract JSON from response pattern: {e}")
            # Continue to return None if no JSON found

        # If no JSON found, return None
        return None

    @staticmethod
    def merge_json_objects(obj1: dict[str, Any], obj2: dict[str, Any]) -> dict[str, Any]:
        """Merge two JSON objects, with obj2 taking precedence."""
        result = obj1.copy()
        result.update(obj2)
        return result

    @staticmethod
    def extract_list_from_json(data: Any, key: str, default: list[Any] | None = None) -> list[Any]:
        """Extract a list from JSON data with fallback."""
        if not isinstance(data, dict):
            return default or []

        value = data.get(key)
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            # Try to parse comma-separated string
            return [item.strip() for item in value.split(",") if item.strip()]
        else:
            return default or []

    @staticmethod
    def extract_string_from_json(data: Any, key: str, default: str = "") -> str:
        """Extract a string from JSON data with fallback."""
        if not isinstance(data, dict):
            return default

        value = data.get(key)
        if isinstance(value, str):
            return value.strip()
        elif value is not None:
            return str(value)
        else:
            return default

    @staticmethod
    def extract_int_from_json(data: Any, key: str, default: int = 0) -> int:
        """Extract an integer from JSON data with fallback."""
        if not isinstance(data, dict):
            return default

        value = data.get(key)
        if isinstance(value, int):
            return value
        elif isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return default
        else:
            return default

    @staticmethod
    def validate_required_fields(data: dict[str, Any], required_fields: list[str]) -> list[str]:
        """Validate that required fields are present and non-empty."""
        missing_fields = []
        for field in required_fields:
            value = data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)
        return missing_fields

    @staticmethod
    def clean_json_data(data: dict[str, Any]) -> dict[str, Any]:
        """Clean JSON data by removing None values and empty strings."""
        cleaned = {}
        for key, value in data.items():
            if value is not None and value != "":
                if isinstance(value, str) and value.strip():
                    cleaned[key] = value.strip()
                elif not isinstance(value, str):
                    cleaned[key] = value
        return cleaned

    @staticmethod
    def detect_markdown_artifacts(response: str) -> list[str]:
        """Detect problematic formatting patterns in LLM responses."""
        if not response or not isinstance(response, str):
            return []

        artifacts = []

        # Check for markdown code blocks
        if "```json" in response:
            artifacts.append("markdown_json_blocks")
        if "```" in response and "```json" not in response:
            artifacts.append("generic_code_blocks")

        # Check for multiple JSON objects
        json_object_count = len(re.findall(r"\{[^{}]*\}", response))
        if json_object_count > 1:
            artifacts.append("multiple_json_objects")

        # Check for escaped characters that might cause issues
        if re.search(r'\\[nt"\\]', response):
            artifacts.append("escape_sequences")

        # Check for HTML-like tags
        if re.search(r"<[^>]+>", response):
            artifacts.append("html_tags")

        # Check for very long responses that might be truncated
        if len(response) > 10000:
            artifacts.append("very_long_response")

        return artifacts

    @staticmethod
    def clean_llm_response(response: str) -> str:
        """Remove markdown artifacts and clean LLM response."""
        if not response or not isinstance(response, str):
            return ""

        cleaned = response.strip()

        # Remove markdown code block markers
        cleaned = re.sub(r"```json\s*", "", cleaned)
        cleaned = re.sub(r"```\s*$", "", cleaned)
        cleaned = re.sub(r"^```\s*", "", cleaned)

        # Remove any leading/trailing whitespace after cleanup
        cleaned = cleaned.strip()

        # If the response starts and ends with curly braces, extract just that part
        if cleaned.startswith("{") and cleaned.endswith("}"):
            # Find the outermost JSON object
            brace_count = 0
            start_idx = 0
            end_idx = len(cleaned)

            for i, char in enumerate(cleaned):
                if char == "{":
                    if brace_count == 0:
                        start_idx = i
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

            cleaned = cleaned[start_idx:end_idx]

        return cleaned

    @staticmethod
    def extract_json_from_llm_response(response: str) -> dict[str, Any] | None:
        """Enhanced JSON extraction from LLM response with markdown detection."""
        if not response or not isinstance(response, str):
            logger.debug("Empty or invalid response provided")
            return None

        # Detect artifacts for logging
        artifacts = JSONProcessor.detect_markdown_artifacts(response)
        if artifacts:
            logger.warning(f"Detected formatting artifacts in LLM response: {artifacts}")

        # Clean the response first
        cleaned_response = JSONProcessor.clean_llm_response(response)

        # Try the existing extraction method first
        result = JSONProcessor.extract_json_from_response(cleaned_response)
        if result:
            return result

        # If that fails, try more aggressive extraction
        # Look for JSON patterns in the original response
        json_patterns = [
            r"```json\s*(\{.*?\})\s*```",  # JSON in code blocks
            r"```\s*(\{.*?\})\s*```",  # JSON in generic code blocks
            r"(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})",  # Nested JSON objects
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    result = pyjson5.loads(match)
                    if isinstance(result, dict):
                        logger.debug(f"Successfully extracted JSON using pattern: {pattern}")
                        return result
                except pyjson5.Json5Exception:
                    continue

        logger.debug("Failed to extract valid JSON from response")
        return None
