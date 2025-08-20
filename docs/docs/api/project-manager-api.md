# ProjectManagerAgent API Documentation

## Overview

The `ProjectManagerAgent` class is the central orchestrator for LibriScribe's book creation process. It manages the entire workflow from concept generation to final formatting, coordinating multiple specialized agents and handling project state management.

## Class Definition

```python
class ProjectManagerAgent:
    """Manages the book creation process."""
```

## Constructor

```python
def __init__(
    self,
    settings: Settings,
    llm_client: LLMClient | None = None,
    model_config: dict[str, str] | None = None,
    use_autogen: bool = False,
) -> None
```

**Parameters:**

- `settings` (Settings): LibriScribe settings configuration
- `llm_client` (LLMClient | None): Optional pre-initialized LLM client
- `model_config` (dict[str, str] | None): Model configuration overrides
- `use_autogen` (bool): Enable AutoGen multi-agent framework integration

**Description:**
Initializes the ProjectManagerAgent with the specified configuration. The agent manages a collection of specialized agents for different aspects of book creation.

## Core Methods

### initialize_llm_client()

```python
def initialize_llm_client(self, llm_provider: str, user: str | None = None) -> None
```

**Parameters:**

- `llm_provider` (str): LLM provider identifier (e.g., "openai", "anthropic")
- `user` (str | None): Optional user identifier for tracking

**Description:**
Initializes the LLM client and all specialized agents. This method must be called before using any agent functionality.

**Example:**

```python
project_manager = ProjectManagerAgent(settings)
project_manager.initialize_llm_client("openai", user="author123")
```

### Project Management Methods

#### initialize_project_with_data()

```python
def initialize_project_with_data(self, project_data: ProjectKnowledgeBase) -> None
```

**Parameters:**

- `project_data` (ProjectKnowledgeBase): Complete project data structure

**Description:**
Initializes a new project using an existing ProjectKnowledgeBase object. Creates the project directory and saves initial data.

#### create_project_from_kb()

```python
def create_project_from_kb(self, project_kb: ProjectKnowledgeBase, output_path: str = "") -> None
```

**Parameters:**

- `project_kb` (ProjectKnowledgeBase): Project knowledge base to create from
- `output_path` (str): Optional custom output directory path

**Description:**
Creates a project from a ProjectKnowledgeBase object with optional custom output path.

#### load_project_data()

```python
def load_project_data(self, project_name: str) -> None
```

**Parameters:**

- `project_name` (str): Name of the project to load

**Returns:** None

**Raises:**

- `FileNotFoundError`: If project directory or project_data.json doesn't exist
- `ValueError`: If project data is corrupted or cannot be loaded

**Description:**
Loads an existing project from the file system. This method locates the project directory, loads the project_data.json file, and initializes the ProjectManagerAgent with the loaded data.

**Example:**

```python
project_manager = ProjectManagerAgent(settings)
project_manager.initialize_llm_client("openai")

try:
    project_manager.load_project_data("my-awesome-book")
    print(f"Loaded project: {project_manager.project_knowledge_base.title}")
except FileNotFoundError as e:
    print(f"Project not found: {e}")
except ValueError as e:
    print(f"Invalid project data: {e}")
```

#### save_project_data()

```python
def save_project_data(self) -> None
```

**Description:**
Saves the current project data to the project_data.json file in the project directory.

### Agent Execution Methods

#### run_agent()

```python
async def run_agent(self, agent_name: str, **kwargs) -> None
```

**Parameters:**

- `agent_name` (str): Name of the agent to run
- `**kwargs`: Additional arguments passed to the agent

**Raises:**

- `ValueError`: If agent not found or project knowledge base not initialized

**Description:**
Executes a specific agent with the provided arguments. Automatically saves project data after successful execution.

**Available Agents:**

- `content_reviewer`: Reviews content for quality and consistency
- `concept_generator`: Generates book concepts
- `outliner`: Creates book outlines
- `character_generator`: Generates character profiles
- `worldbuilding`: Creates worldbuilding details
- `chapter_writer`: Writes individual chapters
- `editor`: Edits content for quality and style
- `researcher`: Researches topics
- `formatting`: Formats the final book
- `style_editor`: Applies style editing
- `plagiarism_checker`: Checks for plagiarism
- `fact_checker`: Verifies factual accuracy

### Content Generation Methods

#### generate_concept()

```python
async def generate_concept() -> None
```

**Description:**
Generates a book concept and saves it to concept.json in the project directory.

#### generate_outline()

```python
async def generate_outline() -> None
```

**Description:**
Generates a comprehensive book outline based on the concept.

#### generate_characters()

```python
async def generate_characters() -> None
```

**Description:**
Generates character profiles for the book.

#### generate_worldbuilding()

```python
async def generate_worldbuilding() -> None
```

**Description:**
Generates worldbuilding details including settings, cultures, and history.

### Chapter Management Methods

#### write_chapter()

```python
async def write_chapter(self, chapter_number: int) -> None
```

**Parameters:**

- `chapter_number` (int): Chapter number to write

**Description:**
Writes a specific chapter and saves it as `chapter_{number}.md`.

#### write_and_review_chapter()

```python
async def write_and_review_chapter(self, chapter_number: int) -> None
```

**Parameters:**

- `chapter_number` (int): Chapter number to write and review

**Description:**
Writes a chapter and automatically reviews it for content issues. This is the recommended method for chapter creation as it includes quality control.

#### review_content()

```python
async def review_content(self, chapter_number: int) -> None
```

**Parameters:**

- `chapter_number` (int): Chapter number to review

**Description:**
Reviews a specific chapter for quality and consistency issues.

#### edit_chapter()

```python
async def edit_chapter(self, chapter_number: int) -> None
```

**Parameters:**

- `chapter_number` (int): Chapter number to edit

**Description:**
Edits a chapter for improved quality and style.

### Quality Assurance Methods

#### check_plagiarism()

```python
async def check_plagiarism(self, chapter_number: int) -> None
```

**Parameters:**

- `chapter_number` (int): Chapter number to check

**Description:**
Checks a chapter for potential plagiarism issues.

#### fact_check()

```python
async def fact_check(self, chapter_number: int) -> None
```

**Parameters:**

- `chapter_number` (int): Chapter number to fact-check

**Description:**
Performs fact-checking on a chapter's content.

#### research_topic()

```python
async def research_topic(self, topic: str) -> None
```

**Parameters:**

- `topic` (str): Topic to research

**Description:**
Researches a specific topic and saves the results.

### Publishing Methods

#### format_book()

```python
async def format_book() -> None
```

**Description:**
Formats the complete book for publication, creating formatted_book.md.

### AutoGen Integration Methods

#### run_autogen_workflow()

```python
async def run_autogen_workflow() -> bool
```

**Returns:**

- `bool`: True if workflow completed successfully, False otherwise

**Description:**
Runs the complete book creation workflow using the AutoGen multi-agent framework.

#### run_hybrid_workflow()

```python
async def run_hybrid_workflow() -> bool
```

**Returns:**

- `bool`: True if workflow completed successfully, False otherwise

**Description:**
Runs a hybrid workflow using AutoGen for coordination and LibriScribe agents for execution.

#### get_autogen_analytics()

```python
def get_autogen_analytics() -> dict[str, Any]
```

**Returns:**

- `dict[str, Any]`: Analytics data from AutoGen service

**Description:**
Retrieves analytics and metrics from the AutoGen service if available.

#### export_autogen_logs()

```python
def export_autogen_logs(self, output_path: str) -> None
```

**Parameters:**

- `output_path` (str): Path to save the exported logs

**Description:**
Exports AutoGen conversation logs to the specified path.

### Configuration Methods

#### get_autogen_configuration()

```python
def get_autogen_configuration(self, use_case: str) -> dict[str, Any]
```

**Parameters:**

- `use_case` (str): Specific use case for configuration

**Returns:**

- `dict[str, Any]`: Recommended AutoGen configuration

**Description:**
Gets recommended AutoGen configuration for a specific use case.

#### validate_autogen_configuration()

```python
def validate_autogen_configuration(self, config: dict[str, Any]) -> list[str]
```

**Parameters:**

- `config` (dict[str, Any]): Configuration to validate

**Returns:**

- `list[str]`: List of validation issues (empty if valid)

**Description:**
Validates an AutoGen configuration and returns any issues found.

### Utility Methods

#### checkpoint()

```python
def checkpoint() -> None
```

**Description:**
Saves the current state of the project as a checkpoint.

#### needs_title_generation()

```python
def needs_title_generation() -> bool
```

**Returns:**

- `bool`: True if title generation is needed

**Description:**
Checks if automatic title generation is needed for the current project.

#### generate_project_title()

```python
async def generate_project_title() -> bool
```

**Returns:**

- `bool`: True if title was generated successfully

**Description:**
Generates a title for the project if auto-title is enabled and conditions are met.

## Usage Examples

### Basic Project Creation

```python
from libriscribe2.agents.project_manager import ProjectManagerAgent
from libriscribe2.settings import Settings
from libriscribe2.knowledge_base import ProjectKnowledgeBase

# Initialize settings and project manager
settings = Settings()
project_manager = ProjectManagerAgent(settings)
project_manager.initialize_llm_client("openai")

# Create a new project
project_kb = ProjectKnowledgeBase(
    project_name="my-fantasy-novel",
    title="The Dragon's Quest",
    genre="fantasy",
    description="An epic fantasy adventure"
)

project_manager.initialize_project_with_data(project_kb)

# Generate content
await project_manager.generate_concept()
await project_manager.generate_outline()
await project_manager.generate_characters()
await project_manager.generate_worldbuilding()

# Write chapters
for chapter_num in range(1, 11):
    await project_manager.write_and_review_chapter(chapter_num)

# Format final book
await project_manager.format_book()
```

### Loading and Continuing Existing Project

```python
# Load existing project
project_manager = ProjectManagerAgent(settings)
project_manager.initialize_llm_client("openai")

try:
    project_manager.load_project_data("my-fantasy-novel")

    # Continue writing from where we left off
    current_chapter = len(project_manager.project_knowledge_base.chapters) + 1
    await project_manager.write_and_review_chapter(current_chapter)

    # Perform quality checks
    await project_manager.check_plagiarism(current_chapter)
    await project_manager.fact_check(current_chapter)

except FileNotFoundError:
    print("Project not found")
except ValueError as e:
    print(f"Error loading project: {e}")
```

### AutoGen Integration

```python
# Use AutoGen for coordinated book creation
project_manager = ProjectManagerAgent(settings, use_autogen=True)
project_manager.initialize_llm_client("openai")

# Create project
project_kb = ProjectKnowledgeBase(project_name="ai-coordinated-book")
project_manager.initialize_project_with_data(project_kb)

# Run AutoGen workflow
success = await project_manager.run_autogen_workflow()

if success:
    # Get analytics
    analytics = project_manager.get_autogen_analytics()
    print(f"Workflow completed with {analytics.get('total_messages', 0)} messages")

    # Export logs
    project_manager.export_autogen_logs("autogen_conversation.json")
```

### Error Handling Best Practices

```python
async def create_book_with_error_handling():
    project_manager = ProjectManagerAgent(settings)

    try:
        project_manager.initialize_llm_client("openai")

        # Load or create project
        try:
            project_manager.load_project_data("existing-project")
        except FileNotFoundError:
            # Create new project if not found
            project_kb = ProjectKnowledgeBase(project_name="existing-project")
            project_manager.initialize_project_with_data(project_kb)

        # Generate content with checkpoints
        await project_manager.generate_concept()
        project_manager.checkpoint()

        await project_manager.generate_outline()
        project_manager.checkpoint()

        # Write chapters with error recovery
        for chapter_num in range(1, 6):
            try:
                await project_manager.write_and_review_chapter(chapter_num)
                project_manager.checkpoint()
            except Exception as e:
                logger.error(f"Failed to write chapter {chapter_num}: {e}")
                # Continue with next chapter
                continue

        await project_manager.format_book()

    except Exception as e:
        logger.error(f"Book creation failed: {e}")
        raise
```

## Integration with Other Components

### Settings Integration

The ProjectManagerAgent integrates closely with the Settings system:

```python
# Settings affect LLM configuration, timeouts, and project directories
settings = Settings()
settings.llm_timeout = 300  # 5 minute timeout
settings.projects_dir = "/custom/projects/path"

project_manager = ProjectManagerAgent(settings)
```

### Knowledge Base Integration

The agent works directly with ProjectKnowledgeBase objects:

```python
# Access project data
kb = project_manager.project_knowledge_base
print(f"Title: {kb.title}")
print(f"Chapters: {len(kb.chapters)}")
print(f"Characters: {len(kb.characters)}")

# Modify project data
kb.genre = "science fiction"
project_manager.save_project_data()
```

## Error Handling

The ProjectManagerAgent implements comprehensive error handling:

- **FileNotFoundError**: Raised when project files cannot be found
- **ValueError**: Raised for invalid project data or missing agents
- **Agent-specific exceptions**: Propagated from individual agents
- **Automatic cleanup**: Resources are cleaned up on errors
- **Detailed logging**: All errors are logged with context

## Performance Considerations

- **Async operations**: All agent operations are asynchronous
- **Checkpointing**: Regular saves prevent data loss
- **Resource management**: Proper cleanup of temporary files
- **Timeout handling**: Configurable timeouts for LLM operations
- **Memory efficiency**: Large projects are handled efficiently

