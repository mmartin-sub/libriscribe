# Requirements Document

## Introduction

The CLI Book Creation feature will enhance LibriScribe by providing a command-line interface approach to create new books. This will allow users to create books without going through the interactive prompts, making it suitable for automation, scripting, and CI/CD pipelines. The feature will also include testing capabilities with support for both live and mock environments through configurable .env files.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to create a new book using command-line arguments, so that I can automate the book creation process without interactive prompts.

#### Acceptance Criteria

1. WHEN the user runs the CLI with all required parameters THEN the system SHALL create a new book without requiring interactive input
2. WHEN the user provides incomplete parameters THEN the system SHALL prompt for the missing information
3. WHEN the user provides the `--help` flag THEN the system SHALL display comprehensive usage information
4. WHEN the user creates a book via CLI THEN the system SHALL generate the same output files as the interactive mode

### Requirement 2

**User Story:** As a developer, I want to specify book metadata via command-line arguments, so that I can customize the book properties without interactive prompts.

#### Acceptance Criteria

1. WHEN the user provides the `--title` parameter THEN the system SHALL set the book title accordingly
2. WHEN the user provides the `--category` parameter THEN the system SHALL set the book category accordingly
3. WHEN the user provides the `--genre` parameter THEN the system SHALL set the book genre accordingly
4. WHEN the user provides the `--description` parameter THEN the system SHALL set the book description accordingly
5. WHEN the user provides the `--language` parameter THEN the system SHALL set the book language accordingly
6. WHEN the user provides the `--chapters` parameter THEN the system SHALL set the number of chapters accordingly
7. WHEN the user provides the `--characters` parameter THEN the system SHALL set the number of characters accordingly
8. WHEN the user provides the `--worldbuilding` flag THEN the system SHALL enable worldbuilding for the book

### Requirement 3

**User Story:** As a developer, I want to specify the LLM provider and models via command-line arguments, so that I can choose which AI models to use for different parts of the book generation process.

#### Acceptance Criteria

1. WHEN the user provides the `--llm` parameter THEN the system SHALL use the specified LLM provider
2. WHEN the user does not provide the `--llm` parameter THEN the system SHALL use the default LLM provider from settings
3. WHEN the user provides the `--model-config` parameter THEN the system SHALL load model configurations from the specified file
4. WHEN the user provides the `--default-model` parameter THEN the system SHALL use the specified model as the default
5. WHEN the system needs to generate content THEN the system SHALL use the appropriate model for each prompt type based on configuration

### Requirement 4

**User Story:** As a developer, I want to control the book generation workflow via command-line arguments, so that I can customize which parts of the book are generated.

#### Acceptance Criteria

1. WHEN the user provides the `--generate-concept` flag THEN the system SHALL generate a book concept
2. WHEN the user provides the `--generate-outline` flag THEN the system SHALL generate a book outline
3. WHEN the user provides the `--generate-characters` flag THEN the system SHALL generate character profiles
4. WHEN the user provides the `--generate-worldbuilding` flag THEN the system SHALL generate worldbuilding details
5. WHEN the user provides the `--write-chapters` flag THEN the system SHALL write all chapters
6. WHEN the user provides the `--format-book` flag THEN the system SHALL format the book
7. WHEN the user provides the `--all` flag THEN the system SHALL perform all generation steps

### Requirement 5

**User Story:** As a tester, I want to use different environment configurations for testing, so that I can test the system with both live and mock LLM providers.

#### Acceptance Criteria

1. WHEN the user provides the `--env-file` parameter THEN the system SHALL load environment variables from the specified file
2. WHEN the user provides the `--mock` flag THEN the system SHALL use mock LLM providers instead of real ones
3. WHEN the system is in mock mode THEN the system SHALL not make actual API calls to external LLM services
4. WHEN the system is in mock mode THEN the system SHALL generate deterministic outputs for testing purposes