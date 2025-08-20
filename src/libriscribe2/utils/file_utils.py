# src/libriscribe2/utils/file_utils.py

import hashlib
import logging
import os
from pathlib import Path
from typing import Any, TypeVar

import pyjson5 as json
from pydantic import BaseModel, ValidationError  # Import ValidationError

from .markdown_formatter import ensure_header_spacing
from .markdown_validator import (  # Import MarkdownValidationError
    MarkdownValidationError,
    validate_markdown,
)
from .timestamp_utils import get_unix_timestamp_int

logger = logging.getLogger(__name__)


def _get_relative_path(file_path: str) -> str:
    """Convert absolute path to relative path for logging.

    Returns path relative to current working directory, or just the project folder
    and filename if it's in the projects directory.
    """
    try:
        path = Path(file_path)
        cwd = Path.cwd()

        # Try to get relative path from current working directory
        try:
            rel_path = path.relative_to(cwd)
            return str(rel_path)
        except ValueError:
            # If not relative to cwd, check if it's in projects directory
            if "projects" in path.parts:
                # Find the projects directory index
                parts = path.parts
                try:
                    projects_idx = parts.index("projects")
                    # Return projects/project_name/filename
                    return str(Path(*parts[projects_idx:]))
                except ValueError:
                    pass

            # Fallback: return just the filename
            return path.name
    except Exception:
        # If anything fails, return the original path
        return file_path


# Generic type for Pydantic models
T = TypeVar("T", bound=BaseModel)


def read_json_file(file_path: str, model: type[BaseModel] | None = None) -> dict[str, Any] | BaseModel | None:
    """Reads a JSON file, optionally validating it against a Pydantic model."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        data = json.loads(content)
        if model:
            try:
                # Call model_validate as a class method
                validated_data = model.model_validate(data)
                return validated_data
            except ValidationError as e:
                logger.error(f"JSON validation error in {file_path}: {e}")
                print(f"ERROR: Invalid JSON data in {file_path}. See log for details.")
                return None  # Or raise, or return a default instance of the model
        # Cast to dict[str, Any] since json.load() returns Any but we expect dict
        if isinstance(data, dict):
            result: dict[str, Any] = data
            return result
        else:
            # Handle non-dict return from json.load
            return None
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        print(f"ERROR: File not found: {file_path}")
        return None
    except Exception as e:
        logger.exception(f"Error reading JSON file {file_path}: {e}")
        print(f"ERROR: Could not read {file_path}")
        return None


def write_json_file(file_path: str, data: dict[str, Any] | BaseModel) -> None:
    """Writes data (dict or Pydantic model) to a JSON file."""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            if isinstance(data, BaseModel):
                json.dump(data.model_dump(), f, indent=4, ensure_ascii=False)  # Use model_dump for Pydantic models
            else:
                json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Data written to {_get_relative_path(file_path)}")
    except Exception as e:
        logger.exception(f"Error writing to JSON file {file_path}: {e}")
        print(f"ERROR: Failed to write to {file_path}. See log.")


def write_markdown_file(file_path: str, content: str, *, validate: bool = True, format_headers: bool = True) -> None:
    """Write content to a markdown file with optional validation.

    Args:
        file_path: Path to the markdown file
        content: Markdown content to write
        validate: Whether to validate the markdown content
        format_headers: Whether to ensure proper spacing before headers

    Returns:
        None

    Raises:
        MarkdownValidationError: If validation is enabled and content is invalid
    """
    try:
        # First, normalize/format content so validation sees the corrected version
        if format_headers:
            content = ensure_header_spacing(content)

        # Then validate the normalized content
        if validate:
            validate_markdown(content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except MarkdownValidationError as e:
        logger.warning(f"Markdown validation failed: {e}")
        return  # Don't write the file if validation fails
    except Exception as e:
        logger.error(f"Failed to write markdown file: {e}")
        raise


def read_markdown_file(path: str) -> str:
    """Reads content from a markdown file using UTF-8 encoding."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def get_chapter_files(project_dir: str) -> list[str]:
    """Gets a sorted list of main chapter files in the project directory.

    Only returns files matching the pattern 'chapter_N.md' where N is a number,
    excluding scene files like 'chapter_NN_scene_NN.md'.
    """
    chapter_files = []
    for filename in os.listdir(project_dir):
        # Only match files like 'chapter_1.md', 'chapter_2.md', etc.
        # Exclude scene files like 'chapter_01_scene_01.md'
        if filename.startswith("chapter_") and filename.endswith(".md") and "_scene_" not in filename:
            chapter_files.append(os.path.join(project_dir, filename))
    # Sort by chapter number, with error handling
    try:
        chapter_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    except (ValueError, IndexError) as e:
        logger.warning(f"Error sorting chapter files: {e}. Returning unsorted list.")
        # Return unsorted list if sorting fails
        pass
    return chapter_files


def dump_content_for_logging(
    content: str, threshold: int = 400, project_dir: str | None = None, process_name: str = "unknown"
) -> str:
    """
    Dump content for logging purposes.

    If content is shorter than threshold, return it directly.
    If content is longer, save to file and return file path.

    Security: Uses SHA-256 for content hashing to ensure cryptographic security.

    Args:
        content: The content to dump
        threshold: Maximum length to include in log
        project_dir: Directory to save file (if None, uses logs directory)
        process_name: Name of the process for file naming

    Returns:
        Either the content (if short) or a file path (if long)
    """
    if len(content) <= threshold:
        return content

    # Generate unique filename

    timestamp = get_unix_timestamp_int()
    process_id = os.getpid()
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]

    filename = f"llm_output_{timestamp}_{process_id}_{process_name}_{content_hash}.log"

    if project_dir:
        # Use project directory if provided
        file_path = Path(project_dir) / filename
    else:
        # Use logs directory instead of current directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        file_path = logs_dir / filename

    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Long content dumped to file: {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Failed to dump content to file: {e}")
        # Fallback: return truncated content
        return f"{content[:threshold]}... (truncated, failed to save to file)"


def extract_json_from_markdown(
    markdown_text: str,
) -> dict[str, Any] | list[Any] | None:
    """Extracts JSON from within Markdown code blocks, handling potential errors."""
    try:
        # Find the start and end of the JSON code block
        start = markdown_text.find("```json")
        if start == -1:
            return None  # No JSON code block found

        start += len("```json")
        end = markdown_text.find("```", start)
        if end == -1:
            return None  # No closing code block found

        json_str = markdown_text[start:end].strip()
        result = json.loads(json_str)
        return result if isinstance(result, dict | list) else None

    except Exception as e:
        logger.exception(f"Error extracting JSON from Markdown: {e}")
        print("Error extracting JSON.")
        return None
