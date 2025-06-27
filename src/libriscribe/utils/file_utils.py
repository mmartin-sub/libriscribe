# src/libriscribe/utils/file_utils.py

import json
import os
from typing import Dict, Any, Optional, Type, TypeVar, Union, List
import logging
from pathlib import Path
from pydantic import BaseModel, ValidationError  # Import ValidationError
#NEW IMPORTS
from libriscribe.knowledge_base import ProjectKnowledgeBase

logger = logging.getLogger(__name__)

# Generic type for Pydantic models
T = TypeVar('T', bound=BaseModel)

def read_json_file(file_path: str, model: Optional[Type[T]] = None) -> Union[Dict[str, Any], T, None]:
    """Reads a JSON file, optionally validating it against a Pydantic model."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if model:
                try:
                    return model.model_validate(data)  # Use model_validate
                except ValidationError as e:
                    logger.error(f"JSON validation error in {file_path}: {e}")
                    print(f"ERROR: Invalid JSON data in {file_path}. See log for details.")
                    return None  # Or raise, or return a default instance of the model
            return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        print(f"ERROR: File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.exception(f"Invalid JSON in {file_path}")
        print(f"ERROR: Invalid JSON in {file_path}")
        return None
    except Exception as e:
        logger.exception(f"Error reading JSON file {file_path}: {e}")
        print(f"ERROR: Could not read {file_path}")
        return None


def write_json_file(file_path: str, data: Union[Dict[str, Any], BaseModel, ProjectKnowledgeBase]) -> None:
    """Writes data (dict or Pydantic model) to a JSON file."""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            if isinstance(data, BaseModel):
                json.dump(data.model_dump(), f, indent=4)  # Use model_dump for Pydantic models
            elif isinstance(data, ProjectKnowledgeBase):
                json.dump(data.model_dump(), f, indent=4)
            else:
                json.dump(data, f, indent=4)
        logger.info(f"Data written to {file_path}")
    except Exception as e:
        logger.exception(f"Error writing to JSON file {file_path}: {e}")
        print(f"ERROR: Failed to write to {file_path}. See log.")

def write_markdown_file(path: str, content: str):
    """Writes content to a markdown file using UTF-8 encoding."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def read_markdown_file(path: str) -> str:
    """Reads content from a markdown file using UTF-8 encoding."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_chapter_files(project_dir: str) -> list[str]:
    """Gets a sorted list of chapter files in the project directory."""
    chapter_files = []
    for filename in os.listdir(project_dir):
        if filename.startswith("chapter_") and filename.endswith(".md"):
            chapter_files.append(os.path.join(project_dir, filename))
    # Sort by chapter number
    chapter_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    return chapter_files

def extract_json_from_markdown(markdown_text: str) -> Optional[Dict[str, Any]]:
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
        return json.loads(json_str)

    except json.JSONDecodeError:
        return None
    except Exception as e:
        logger.exception(f"Error extracting JSON from Markdown: {e}")
        print("Error extracting JSON.")
        return None