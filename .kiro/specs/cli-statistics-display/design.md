# Design Document

## Overview

This feature implements the missing project loading functionality and fixes the broken `book-stats` command. The current CLI commands are broken because they depend on a global `project_manager` variable, but the `ProjectManagerAgent` class is missing a `load_project_data` method to load existing projects from the file system.

## Architecture

The solution involves three main changes:

1. **Implement missing load_project_data method**: Add the missing method to ProjectManagerAgent
2. **Fix CLI commands**: Update book-stats and other commands to use the loading functionality
3. **Add automatic statistics display**: Call statistics display after successful book creation

### Key Components

1. **ProjectManagerAgent.load_project_data()**: Load project data from file system
2. **Fixed CLI Commands**: Use proper project loading instead of relying on global state
3. **Statistics Display**: Reuse existing statistics display logic

## Components and Interfaces

### ProjectManagerAgent.load_project_data()

Add the missing method to ProjectManagerAgent:

```python
def load_project_data(self, project_name: str) -> None:
    """Load project data from file system."""
    # Construct project directory path using settings.projects_dir
    # Load project_data.json file
    # Set self.project_knowledge_base and self.project_dir
    # Raise appropriate exceptions for missing/corrupted data
```

### Fixed CLI Commands

Update CLI commands to use proper project loading:

```python
@app.command(name="book-stats")
def book_stats(project_name: str = typer.Option(..., prompt="Project name")) -> None:
    # Initialize project manager with settings
    # Call load_project_data(project_name)
    # Display statistics using loaded data
```

### BookCreatorService Integration

The `BookCreatorService.create_book()` method will display statistics after successful creation by reusing the same logic as book-stats.

## Data Models

The statistics display will use existing data structures:

- **ProjectKnowledgeBase**: Loaded from `project_data.json` file in project directory
- **Project Directory Path**: File system path to the created project

## Error Handling

- **Project Not Found**: Display clear error message if project directory doesn't exist
- **Invalid Project Data**: Display clear error message if project_data.json is missing or corrupted
- **Display Errors**: Log errors but don't fail the overall book creation process

## Testing Strategy

### Unit Tests

- Test statistics display function with valid project directory
- Test error handling for missing project directory
- Test error handling for corrupted project data
- Test statistics display with mock data

### Integration Tests

- Test fixed book-stats command with existing projects
- Test end-to-end book creation with automatic statistics display
- Test statistics display with various project types

### Manual Testing

- Verify book-stats command works independently
- Verify statistics appear after create-book command
- Verify error messages are clear and helpful
