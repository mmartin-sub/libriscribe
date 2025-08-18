# ProjectManagerAgent - Documentation Summary

## Overview

The `ProjectManagerAgent` is the central orchestrator for LibriScribe's book creation workflow. This document provides a comprehensive summary of the recent enhancements, particularly the new `load_project_data` method.

## Recent Changes

### New Method: `load_project_data()`

**Added:** A new method to load existing projects from the file system.

```python
def load_project_data(self, project_name: str) -> None
```

**Purpose:** Enables loading and resuming work on existing LibriScribe projects.

**Key Features:**
- Loads project data from `project_data.json` in the project directory
- Validates project directory and file existence
- Handles corrupted data gracefully with appropriate error messages
- Sets up the project environment for continued work
- Integrates with the existing settings system

## Method Documentation

### Parameters
- `project_name` (str): Name of the project to load from the projects directory

### Raises
- `FileNotFoundError`: When project directory or `project_data.json` doesn't exist
- `ValueError`: When project data is corrupted or cannot be loaded

### Behavior
1. Constructs project directory path using `settings.projects_dir`
2. Validates project directory exists
3. Validates `project_data.json` file exists
4. Loads `ProjectKnowledgeBase` from the JSON file
5. Sets up internal state (`project_knowledge_base`, `project_dir`)
6. Configures the knowledge base with the project directory
7. Logs successful loading

### Error Handling
- **Missing Directory**: Clear error message indicating project not found
- **Missing File**: Specific error about missing `project_data.json`
- **Corrupted Data**: Wraps parsing errors with context about corruption
- **Preserves Original Errors**: FileNotFoundError and ValueError from loading are preserved
- **Detailed Logging**: All operations are logged for debugging

## Usage Examples

### Basic Loading
```python
project_manager = ProjectManagerAgent(settings)
project_manager.initialize_llm_client("openai")

try:
    project_manager.load_project_data("my-book-project")
    print(f"Loaded: {project_manager.project_knowledge_base.title}")
except FileNotFoundError:
    print("Project not found")
except ValueError as e:
    print(f"Corrupted project: {e}")
```

### Resume Workflow
```python
# Load existing project
project_manager.load_project_data("fantasy-novel")

# Continue where we left off
current_chapter = len(project_manager.project_knowledge_base.chapters) + 1
await project_manager.write_and_review_chapter(current_chapter)

# Save progress
project_manager.checkpoint()
```

### Error Recovery
```python
def load_project_with_fallback(project_name: str):
    try:
        project_manager.load_project_data(project_name)
        return True
    except FileNotFoundError:
        logger.warning(f"Project {project_name} not found, creating new")
        # Create new project logic here
        return False
    except ValueError as e:
        logger.error(f"Project {project_name} corrupted: {e}")
        # Handle corruption - backup, recreate, etc.
        return False
```

## Integration Points

### Settings Integration
- Uses `settings.projects_dir` to locate projects
- Respects user-configured project directory paths
- Works with both default and custom project locations

### Knowledge Base Integration
- Loads complete `ProjectKnowledgeBase` objects
- Preserves all project metadata, chapters, characters, etc.
- Sets up bidirectional references between manager and knowledge base

### Agent Integration
- Loaded projects are immediately available to all agents
- Agents can access project directory through knowledge base
- Seamless continuation of multi-agent workflows

### Logging Integration
- Comprehensive logging of load operations
- Error context for debugging
- Success confirmation with project details

## Testing Coverage

### Unit Tests Added
- **Success Path**: Loading valid projects
- **Error Handling**: Missing directories, files, corrupted data
- **Edge Cases**: Empty files, permission issues, invalid paths
- **Integration**: Settings directory configuration
- **State Management**: Proper setup of internal state

### Test Scenarios
```python
# Success cases
test_load_project_data_success()
test_load_project_data_with_existing_project_dir()

# Error cases
test_load_project_data_project_not_found()
test_load_project_data_file_not_found()
test_load_project_data_corrupted_file()
test_load_project_data_load_returns_none()

# Error preservation
test_load_project_data_preserves_file_not_found_error()
test_load_project_data_preserves_value_error()

# Integration
test_load_project_data_integration_with_settings()
```

## CLI Integration

The new method enables CLI commands for project management:

```bash
# Resume existing project
hatch run python -m libriscribe2.main resume --project-name my-book

# Continue writing chapters
hatch run python -m libriscribe2.main write-chapter --project-name my-book --chapter 5

# View project statistics
hatch run python -m libriscribe2.main book-stats --project-name my-book
```

## Best Practices

### Error Handling
```python
# Always handle both error types
try:
    project_manager.load_project_data(project_name)
except FileNotFoundError:
    # Handle missing project
    pass
except ValueError:
    # Handle corrupted data
    pass
```

### Logging
```python
# Enable logging to see load progress
import logging
logging.basicConfig(level=logging.INFO)

# Load operations will be logged automatically
project_manager.load_project_data("my-project")
```

### State Validation
```python
# Verify project loaded correctly
if project_manager.project_knowledge_base:
    print(f"Project loaded: {project_manager.project_knowledge_base.title}")
    print(f"Chapters: {len(project_manager.project_knowledge_base.chapters)}")
else:
    print("No project loaded")
```

## Future Enhancements

### Potential Improvements
1. **Project Validation**: Validate project structure and required files
2. **Backup Creation**: Automatic backup before loading corrupted projects
3. **Migration Support**: Handle projects from older LibriScribe versions
4. **Partial Loading**: Load only specific project components
5. **Caching**: Cache frequently accessed projects for performance

### API Extensions
```python
# Potential future methods
def validate_project_structure(self, project_name: str) -> bool
def backup_project(self, project_name: str) -> str
def migrate_project(self, project_name: str, from_version: str) -> bool
def list_available_projects(self) -> list[str]
```

## Related Documentation

- [ProjectManagerAgent API Documentation](project-manager-api.md)
- [ProjectManagerAgent Function Signatures](project-manager-signatures.md)
- [ProjectKnowledgeBase API Documentation](knowledge-base-api.md)
- [Settings API Documentation](settings-api.md)
- [Usage Examples](../examples/project_manager_usage.py)

## Changelog

### Version 2.1.0
- **Added**: `load_project_data()` method for loading existing projects
- **Enhanced**: Error handling with specific error types and messages
- **Improved**: Integration with settings system for project directory configuration
- **Added**: Comprehensive test coverage for new functionality
- **Updated**: Documentation with usage examples and best practices
