# Implementation Plan

- [x] 1. Move test-related files to appropriate test directories
  - Move `src/libriscribe2/validation/testing/test_framework.py` to `tests/` directory structure
  - Move `src/libriscribe2/validation/testing/test_data.py` to `tests/` directory structure
  - Update any imports that reference these moved files
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 2. Fix generic type parameter issues
  - Add type parameters to `dict` types in `src/libriscribe2/agents/worldbuilding.py`
  - Add type parameters to `list` types in `src/libriscribe2/agents/outliner.py` and `src/libriscribe2/agents/project_manager.py`
  - Add type parameters to `set` types in `src/libriscribe2/validation/testing/coverage.py`
  - Add type parameters to `tuple` types in validation files
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 3. Add missing return type annotations to main CLI functions
  - Fix return type annotations in `src/libriscribe2/main.py` for all functions missing them
  - Add `-> None` annotations where functions don't return values
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 4. Add missing return type annotations to agent functions
  - Fix return type annotations in `src/libriscribe2/agents/project_manager.py`
  - Fix return type annotations in `src/libriscribe2/agent_frameworks/autogen/wrapper.py`
  - Fix return type annotations in `src/libriscribe2/agent_frameworks/autogen/service.py`
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 5. Add missing return type annotations to service functions
  - Fix return type annotations in `src/libriscribe2/create_book_command.py`
  - Fix return type annotations in `src/libriscribe2/services/book_creator.py`
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 6. Add missing parameter type annotations
  - Fix parameter type annotations in `src/libriscribe2/create_book_command.py`
  - Fix parameter type annotations in `src/libriscribe2/main.py`
  - Fix parameter type annotations in validation engine files
  - _Requirements: 1.3_

- [x] 7. Fix untyped function calls by adding type annotations to called functions
  - Add type annotations to utility functions called from main modules
  - Add type annotations to agent functions that are called from other modules
  - Add type annotations to service functions that are called from CLI
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 8. Update mypy configuration to remove broad exclusions
  - Remove or limit the scope of `follow_imports = "skip"` in pyproject.toml
  - Update mypy configuration to be more specific about exclusions
  - Test that both `hatch run typing` and `hatch run typing --strict` work correctly
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 9. Verify all mypy strict issues are resolved
  - Run `hatch run typing --strict` to confirm no errors remain
  - Run `hatch run typing` to ensure regular type checking still works
  - Run tests to ensure no functionality was broken during type annotation additions
  - _Requirements: 5.3, 5.4_
