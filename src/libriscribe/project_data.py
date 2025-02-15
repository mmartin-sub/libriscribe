# src/libriscribe/project_data.py

from typing import Any, Dict, Optional, Tuple, Union
from pydantic import BaseModel, validator

class ProjectData(BaseModel):
    project_name: str
    title: str = "Untitled"
    genre: str = "Unknown Genre"
    description: str = "No description provided."
    category: str = "Unknown Category"
    num_characters: Union[int, Tuple[int, int]] = 0  # Can be a single number or a range
    num_characters_str: str = ""
    worldbuilding_needed: bool = False
    review_preference: str = "AI"  # Default to AI review
    book_length: str = ""
    logline: str = "No logline available"
    tone: Optional[str] = None  # Optional fields can be None
    target_audience: Optional[str] = None
    inspired_by: Optional[str] = None
    author_experience: Optional[str] = None
    key_takeaways: Optional[str] = None
    case_studies: Optional[bool] = None
    actionable_advice: Optional[bool] = None
    marketing_focus: Optional[str] = None
    sales_focus: Optional[str] = None
    research_question: Optional[str] = None
    hypothesis: Optional[str] = None
    methodology: Optional[str] = None
    num_chapters: Union[int, Tuple[int, int]] = 1
    num_chapters_str: str = ""

    # Store dynamic questions and their answers.
    dynamic_questions: Dict[str, str] = {}

    @validator("num_characters", "num_chapters", pre=True)
    def parse_range_or_plus(cls, value):
        if isinstance(value, str):
            if "-" in value:
                try:
                    min_val, max_val = map(int, value.split("-"))
                    return (min_val, max_val)
                except ValueError:
                    return 0  # Default value
            elif "+" in value:
                try:
                    return int(value.replace("+", ""))
                except ValueError:
                    return 0  # Default
            else:
                try:
                    return int(value)
                except ValueError:
                    return 0
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """Safely get a value from the project data, using Pydantic's built-in functionality."""
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def set(self, key: str, value: Any) -> None:
        """Safely set a value."""
        if hasattr(self, key):
            setattr(self, key, value)
        # else you might want to log a warning, or raise an exception.