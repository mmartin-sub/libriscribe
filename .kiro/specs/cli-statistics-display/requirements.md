# Requirements Document

## Introduction

This feature will fix the broken `book-stats` command and add automatic display of book statistics after successful book creation in the CLI, providing users with immediate feedback about their created book.

## Requirements

### Requirement 1

**User Story:** As a developer, I want the ProjectManagerAgent to have a load_project_data method, so that CLI commands can load existing projects from the file system.

#### Acceptance Criteria

1. WHEN load_project_data is called with a project name THEN the system SHALL load the ProjectKnowledgeBase from the project's project_data.json file
2. WHEN the project is loaded THEN the system SHALL set the project_dir and project_knowledge_base properties
3. WHEN the project directory does not exist THEN the system SHALL raise an appropriate exception
4. WHEN the project_data.json file is missing or corrupted THEN the system SHALL raise an appropriate exception

### Requirement 2

**User Story:** As a user running the book-stats command, I want it to work correctly by loading the project data from the file system, so that I can view statistics for any created project.

#### Acceptance Criteria

1. WHEN the book-stats command is run with a project name THEN the system SHALL use load_project_data to load the project
2. WHEN the project data is loaded THEN the system SHALL display statistics using the loaded ProjectKnowledgeBase
3. WHEN the project cannot be loaded THEN the system SHALL display an appropriate error message

### Requirement 3

**User Story:** As a user running the create-book command, I want to see book statistics automatically displayed after successful creation, so that I can immediately understand what was generated without running a separate command.

#### Acceptance Criteria

1. WHEN the create-book command completes successfully THEN the system SHALL display book statistics in the console
2. WHEN book statistics are displayed THEN the system SHALL show title, genre, language, category, number of chapters, number of characters, and scenes per chapter
3. WHEN book statistics are displayed THEN the system SHALL show the project directory path
4. WHEN the --mock flag is used THEN the system SHALL still display statistics with mock data

### Requirement 4

**User Story:** As a user, I want the statistics to only display when book creation is successful, so that I don't see confusing information when errors occur.

#### Acceptance Criteria

1. WHEN book creation fails THEN the system SHALL NOT display statistics
2. WHEN book creation is interrupted THEN the system SHALL NOT display statistics
3. WHEN book creation succeeds THEN the system SHALL display statistics before the final success message
