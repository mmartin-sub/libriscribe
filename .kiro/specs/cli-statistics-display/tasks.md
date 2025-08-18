# Implementation Plan

- [x] 1. Implement missing load_project_data method in ProjectManagerAgent
  - Add `load_project_data(self, project_name: str) -> None` method to ProjectManagerAgent class
  - Load ProjectKnowledgeBase from `project_data.json` file in project directory using settings.projects_dir
  - Set self.project_knowledge_base and self.project_dir properties after successful loading
  - Raise FileNotFoundError for missing project directory, ValueError for corrupted project data
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Fix book-stats command to use project loading
  - Modify `book_stats()` function to initialize ProjectManagerAgent with Settings
  - Call `load_project_data(project_name)` instead of relying on global project_manager
  - Update error handling to catch and display appropriate error messages
  - Remove dependency on global project_manager variable
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 3. Add automatic statistics display to book creation
  - Modify `BookCreatorService.create_book()` to display statistics after successful creation
  - Reuse the same statistics display logic as the fixed book-stats command
  - Ensure statistics display occurs before final success message and only when success=True
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3_

- [x] 4. Add tests for the new functionality
  - Create unit test for `load_project_data()` method with valid project data
  - Create unit test for error handling with missing project directory and corrupted data
  - Create integration test for fixed book-stats command
  - Create integration test for automatic statistics display in create-book command
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4_
