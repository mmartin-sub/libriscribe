---
sidebar_position: 1
---

# Project Manager Agent

The Project Manager Agent is the central coordinator of LibriScribe's book writing process. It manages the workflow and orchestrates the interactions between all other agents.

## Overview

The Project Manager Agent serves as the main interface between the user and LibriScribe's various specialized agents. It handles project initialization, coordinates the execution of different writing stages, and manages the overall book creation process.

## Key Responsibilities

- **Project Initialization**: Creates and configures new book projects
- **Workflow Management**: Coordinates the sequence of agent operations
- **Resource Management**: Handles file organization and agent communication
- **Process Oversight**: Monitors and reports on the progress of book creation

## Command Interface

The Project Manager provides several key commands:

```bash
# Create a new project
libriscribe create PROJECT_NAME --title TITLE --genre GENRE

# Generate initial book concept
libriscribe generate-concept

# Create book outline
libriscribe generate-outline

# Generate character profiles
libriscribe generate-characters

# Create worldbuilding details
libriscribe generate-worldbuilding

# Write specific chapters
libriscribe write-chapter CHAPTER_NUMBER

# Edit chapters
libriscribe edit-chapter CHAPTER_NUMBER

# Format final book
libriscribe format-book

# Conduct research
libriscribe research QUERY
```

## File Structure

The Project Manager creates and maintains the following project structure:

```
project_name/
├── project_data.json     # Project configuration and metadata
├── outline.md           # Book outline
├── characters.json      # Character profiles
├── world.json          # Worldbuilding details
├── chapter_1.md        # Individual chapter files
├── chapter_2.md
└── ...
```

## Error Handling

The Project Manager implements comprehensive error handling:
- Validates project initialization parameters
- Ensures required files exist before agent execution
- Logs errors and provides user-friendly error messages
- Maintains project consistency during failures

## Integration with Other Agents

The Project Manager seamlessly integrates with all other LibriScribe agents:
- Passes necessary context between agents
- Ensures proper sequencing of operations
- Manages file dependencies
- Coordinates multi-agent operations

# Project Data Reference

The `project_data.json` file stores all project metadata and configuration. Below are the main fields and their possible values:

| Field              | Type      | Description                                      | Example / Options                                  |
|--------------------|-----------|--------------------------------------------------|----------------------------------------------------|
| `project_name`     | string    | Name of the project                              | `"my_novel_project"`                               |
| `title`            | string    | Book title                                       | `"The Dragon's Shadow"`                            |
| `genre`            | string    | Book genre                                       | `"Fantasy"`, `"Science Fiction"`, `"Mystery"`, etc.|
| `category`         | string    | Book category                                    | `"Fiction"`, `"Non-Fiction"`, `"Business"`, etc.   |
| `language`         | string    | Language of the book                             | `"English"`, `"Spanish"`, etc.                     |
| `book_length`      | string    | Book length/type                                 | `"Short Story"`, `"Novella"`, `"Novel"`            |
| `num_chapters`     | int/range | Number of chapters (int or range, e.g. 5-8)      | `8`, `"5-8"`, `"20+"`                              |
| `num_characters`   | int/range | Number of main characters                        | `3`, `"2-4"`                                       |
| `logline`          | string    | One-sentence summary of the book                  | `"A daemon finds a dragon egg in Neo-London..."`   |
| `tone`             | string    | Tone of the book                                 | `"Informative"`, `"Dark"`, `"Humorous"`, etc.      |
| `target_audience`  | string    | Intended audience                                | `"General"`, `"Young Adult"`, `"Children"`, etc.   |
| `llm_provider`     | string    | LLM provider used                                | `"openai"`, `"anthropic"`, etc.                    |
| `worldbuilding_needed` | bool  | Whether worldbuilding is required                | `true`, `false`                                    |
| ...                | ...       | ...                                              | ...                                                |

**Note:** Some fields accept either a single value or a range (e.g., `"5-8"` for chapters).

---

### 2. Update `ProjectKnowledgeBase` Model with Field Choices and Docstrings

Add comments or Pydantic `Field` descriptions to clarify the options for each field:

````python
# filepath: [knowledge_base.py](http://_vscodecontentref_/6)
# ...existing code...

class ProjectKnowledgeBase(BaseModel):
    project_name: str
    title: str = Field("Untitled", description="Book title")
    genre: str = Field("Unknown Genre", description="Book genre (e.g., 'Fantasy', 'Science Fiction', 'Mystery')")
    description: str = Field("No description provided.", description="Book description")
    category: str = Field("Unknown Category", description="Book category (e.g., 'Fiction', 'Non-Fiction', 'Business')")
    language: str = Field("English", description="Book language (e.g., 'English', 'Spanish')")
    num_characters: Union[int, Tuple[int, int]] = Field(0, description="Number of main characters (int or range, e.g., 2-4)")
    num_characters_str: str = Field("", description="String version of num_characters for advanced use")
    worldbuilding_needed: bool = Field(False, description="Whether worldbuilding is required")
    review_preference: str = Field("AI", description="Preferred review method ('AI', 'Human', etc.)")
    book_length: str = Field("", description="Book length/type ('Short Story', 'Novella', 'Novel')")
    logline: str = Field("No logline available", description="One-sentence summary of the book")
    tone: str = Field("Informative", description="Book tone ('Informative', 'Dark', 'Humorous', etc.)")
    target_audience: str = Field("General", description="Intended audience ('General', 'Young Adult', etc.)")
    num_chapters: Union[int, Tuple[int, int]] = Field(1, description="Number of chapters (int or range, e.g., 5-8)")
    num_chapters_str: str = Field("", description="String version of num_chapters for advanced use")
    llm_provider: str = Field("openai", description="LLM provider ('openai', 'anthropic', etc.)")
    dynamic_questions: Dict[str, str] = Field(default_factory=dict, description="Advanced: dynamic questions for the project")

````
