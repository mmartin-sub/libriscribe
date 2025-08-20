# ProjectManagerAgent - Function Signatures

## Complete API Reference

### Class Definition

```python
class ProjectManagerAgent:
    """Manages the book creation process."""
```

### Constructor

```python
def __init__(
    self,
    settings: Settings,
    llm_client: LLMClient | None = None,
    model_config: dict[str, str] | None = None,
    use_autogen: bool = False,
) -> None
```

### Initialization Methods

#### initialize_llm_client()

```python
def initialize_llm_client(self, llm_provider: str, user: str | None = None) -> None
```

Initialize the LLM client and all specialized agents.

### Project Management Methods

#### initialize_project_with_data()

```python
def initialize_project_with_data(self, project_data: ProjectKnowledgeBase) -> None
```

Initialize a project using a ProjectKnowledgeBase object.

#### create_project_from_kb()

```python
def create_project_from_kb(self, project_kb: ProjectKnowledgeBase, output_path: str = "") -> None
```

Create a project from a ProjectKnowledgeBase object with optional custom path.

#### load_project_data()

```python
def load_project_data(self, project_name: str) -> None
```

Load project data from the file system.

**Raises:**
- `FileNotFoundError`: If project directory or project_data.json doesn't exist
- `ValueError`: If project data is corrupted or cannot be loaded

#### save_project_data()

```python
def save_project_data() -> None
```

Save the current project data to project_data.json.

### Agent Execution Methods

#### run_agent()

```python
async def run_agent(self, agent_name: str, **kwargs) -> None
```

Execute a specific agent with provided arguments.

**Raises:**
- `ValueError`: If agent not found or project knowledge base not initialized

### Content Generation Methods

#### generate_concept()

```python
async def generate_concept() -> None
```

Generate a book concept and save to concept.json.

#### generate_outline()

```python
async def generate_outline() -> None
```

Generate a comprehensive book outline.

#### generate_characters()

```python
async def generate_characters() -> None
```

Generate character profiles for the book.

#### generate_worldbuilding()

```python
async def generate_worldbuilding() -> None
```

Generate worldbuilding details including settings and cultures.

### Chapter Management Methods

#### write_chapter()

```python
async def write_chapter(self, chapter_number: int) -> None
```

Write a specific chapter and save as `chapter_{number}.md`.

#### write_and_review_chapter()

```python
async def write_and_review_chapter(self, chapter_number: int) -> None
```

Write a chapter and automatically review it for content issues.

#### review_content()

```python
async def review_content(self, chapter_number: int) -> None
```

Review a specific chapter for quality and consistency.

#### edit_chapter()

```python
async def edit_chapter(self, chapter_number: int) -> None
```

Edit a chapter for improved quality and style.

### Quality Assurance Methods

#### check_plagiarism()

```python
async def check_plagiarism(self, chapter_number: int) -> None
```

Check a chapter for potential plagiarism issues.

#### fact_check()

```python
async def fact_check(self, chapter_number: int) -> None
```

Perform fact-checking on a chapter's content.

#### research_topic()

```python
async def research_topic(self, topic: str) -> None
```

Research a specific topic and save results.

### Publishing Methods

#### format_book()

```python
async def format_book() -> None
```

Format the complete book for publication.

### AutoGen Integration Methods

#### run_autogen_workflow()

```python
async def run_autogen_workflow() -> bool
```

Run the complete book creation workflow using AutoGen.

#### run_hybrid_workflow()

```python
async def run_hybrid_workflow() -> bool
```

Run a hybrid workflow using AutoGen coordination with LibriScribe agents.

#### get_autogen_analytics()

```python
def get_autogen_analytics() -> dict[str, Any]
```

Get analytics data from AutoGen service.

#### export_autogen_logs()

```python
def export_autogen_logs(self, output_path: str) -> None
```

Export AutoGen conversation logs to specified path.

### Configuration Methods

#### get_autogen_configuration()

```python
def get_autogen_configuration(self, use_case: str) -> dict[str, Any]
```

Get recommended AutoGen configuration for a specific use case.

#### validate_autogen_configuration()

```python
def validate_autogen_configuration(self, config: dict[str, Any]) -> list[str]
```

Validate AutoGen configuration and return any issues.

### Utility Methods

#### checkpoint()

```python
def checkpoint() -> None
```

Save the current state of the project.

#### needs_title_generation()

```python
def needs_title_generation() -> bool
```

Check if automatic title generation is needed.

#### generate_project_title()

```python
async def generate_project_title() -> bool
```

Generate a title for the project if auto-title is enabled.

## Type Annotations Summary

### Common Parameter Types

```python
# Basic types
project_name: str
chapter_number: int
topic: str
output_path: str
use_case: str

# Complex types
settings: Settings
project_data: ProjectKnowledgeBase
project_kb: ProjectKnowledgeBase
llm_client: LLMClient | None
model_config: dict[str, str] | None
config: dict[str, Any]

# Optional types
user: str | None = None
output_path: str = ""
use_autogen: bool = False
```

### Return Types

```python
# Void methods
-> None                    # Most initialization and execution methods

# Boolean returns
-> bool                    # Workflow and generation success indicators

# Data returns
-> dict[str, Any]         # Configuration and analytics data
-> list[str]              # Validation issues and error lists
```

### Exception Types

```python
# File system errors
FileNotFoundError         # Missing project files or directories
ValueError               # Invalid data, missing agents, or corrupted files

# Agent execution errors
Exception                # Generic agent execution failures (re-raised)
```

## Usage Patterns

### Basic Initialization Pattern

```python
project_manager = ProjectManagerAgent(settings)
project_manager.initialize_llm_client("openai")
```

### Project Creation Pattern

```python
project_kb = ProjectKnowledgeBase(project_name="my-book")
project_manager.initialize_project_with_data(project_kb)
```

### Project Loading Pattern

```python
try:
    project_manager.load_project_data("existing-project")
except FileNotFoundError:
    # Handle missing project
    pass
except ValueError:
    # Handle corrupted data
    pass
```

### Agent Execution Pattern

```python
await project_manager.run_agent("agent_name", param1=value1, param2=value2)
```

### Chapter Writing Pattern

```python
for chapter_num in range(1, total_chapters + 1):
    await project_manager.write_and_review_chapter(chapter_num)
    project_manager.checkpoint()
```

### AutoGen Workflow Pattern

```python
if project_manager.use_autogen:
    success = await project_manager.run_autogen_workflow()
    if success:
        analytics = project_manager.get_autogen_analytics()
```

## Import Requirements

```python
from pathlib import Path
from typing import Any
from rich.console import Console

# LibriScribe imports
from ..agent_frameworks.autogen import AutoGenConfigurationManager, AutoGenService
from ..knowledge_base import ProjectKnowledgeBase
from ..settings import Settings
from ..utils.llm_client import LLMClient

# Agent imports
from .chapter_writer import ChapterWriterAgent
from .character_generator import CharacterGeneratorAgent
from .concept_generator import ConceptGeneratorAgent
from .content_reviewer import ContentReviewerAgent
from .editor import EditorAgent
from .fact_checker import FactCheckerAgent
from .formatting import FormattingAgent
from .outliner import OutlinerAgent
from .plagiarism_checker import PlagiarismCheckerAgent
from .researcher import ResearcherAgent
from .style_editor import StyleEditorAgent
from .worldbuilding import WorldbuildingAgent
```

## Agent Registry

The ProjectManagerAgent manages the following specialized agents:

```python
self.agents = {
    "content_reviewer": ContentReviewerAgent,
    "concept_generator": ConceptGeneratorAgent,
    "outliner": OutlinerAgent,
    "character_generator": CharacterGeneratorAgent,
    "worldbuilding": WorldbuildingAgent,
    "chapter_writer": ChapterWriterAgent,
    "editor": EditorAgent,
    "researcher": ResearcherAgent,
    "formatting": FormattingAgent,
    "style_editor": StyleEditorAgent,
    "plagiarism_checker": PlagiarismCheckerAgent,
    "fact_checker": FactCheckerAgent,
}
```

## Properties

```python
# Core properties
self.settings: Settings
self.model_config: dict[str, str]
self.project_knowledge_base: ProjectKnowledgeBase | None
self.project_dir: Path | None
self.llm_client: LLMClient | None
self.agents: dict[str, Any]
self.logger: logging.Logger

# AutoGen properties
self.use_autogen: bool
self.autogen_service: AutoGenService | None
self.autogen_config_manager: AutoGenConfigurationManager
```
