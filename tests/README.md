# Testing Structure and Coverage

## Current Test Coverage Analysis

Based on the coverage report, here are the areas that need more testing:

### High Priority (0-30% coverage)

- **Services**: `book_creator.py` (0% coverage)
- **Agents**: Most agents have 6-31% coverage
- **Utils**: Many utility modules need more testing
- **Main**: `main.py` (0% coverage)

### Medium Priority (30-60% coverage)

- **Settings**: `settings.py` (69% coverage)
- **Knowledge Base**: `knowledge_base.py` (71% coverage)

### Good Coverage (60%+)

- **Commands**: `create_book_command.py` (59% coverage)
- **Validation**: `validation_engine.py` (good coverage)

## Testing Structure

```
tests/
├── README.md                           # This file
├── conftest.py                         # Shared fixtures
├── unit/                               # Unit tests
│   ├── agents/                         # Agent tests
│   │   ├── test_project_manager.py
│   │   ├── test_concept_generator.py
│   │   ├── test_outliner.py
│   │   ├── test_character_generator.py
│   │   ├── test_chapter_writer.py
│   │   ├── test_editor.py
│   │   ├── test_formatting.py
│   │   └── test_agent_base.py
│   ├── services/                       # Service tests
│   │   ├── test_book_creator.py
│   │   └── test_autogen_service.py
│   ├── utils/                          # Utility tests
│   │   ├── test_llm_client.py
│   │   ├── test_file_utils.py
│   │   ├── test_json_utils.py
│   │   └── test_mock_llm_client.py
│   ├── knowledge_base/                 # Knowledge base tests
│   │   └── test_knowledge_base.py
│   └── settings/                       # Settings tests
│       └── test_settings.py
├── integration/                        # Integration tests
│   ├── test_end_to_end.py
│   ├── test_workflow.py
│   └── test_agent_interactions.py
├── commands/                           # Command tests
│   ├── test_create_book_command.py
│   └── test_main.py
└── validation/                         # Validation tests
    └── test_validation_engine.py
```

## Testing Goals

### Unit Tests (80%+ coverage target)

- **Agents**: Test each agent's core functionality
- **Services**: Test service layer interactions
- **Utils**: Test utility functions thoroughly
- **Knowledge Base**: Test data management
- **Settings**: Test configuration loading

### Integration Tests

- **End-to-end workflows**: Complete book creation process
- **Agent interactions**: How agents work together
- **Error handling**: System behavior under failure

### Command Tests

- **CLI commands**: Test all command-line interfaces
- **Argument validation**: Test input validation
- **Error scenarios**: Test error handling

## Coverage Targets

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| agents/project_manager.py | 30% | 80% | High |
| agents/concept_generator.py | 17% | 80% | High |
| agents/outliner.py | 6% | 80% | High |
| agents/character_generator.py | 25% | 80% | High |
| agents/chapter_writer.py | 24% | 80% | High |
| agents/editor.py | 20% | 80% | High |
| agents/formatting.py | 21% | 80% | High |
| services/book_creator.py | 0% | 80% | High |
| utils/llm_client.py | 23% | 80% | High |
| utils/file_utils.py | 19% | 80% | High |
| utils/json_utils.py | 27% | 80% | High |
| knowledge_base.py | 71% | 90% | Medium |
| settings.py | 69% | 90% | Medium |
| create_book_command.py | 59% | 90% | Medium |

## Testing Strategy

### 1. Unit Tests

- Mock external dependencies
- Test individual functions/methods
- Test edge cases and error conditions
- Use parameterized tests for multiple scenarios

### 2. Integration Tests

- Test real interactions between components
- Use test databases/files
- Test complete workflows
- Test error propagation

### 3. Performance Tests

- Test with large datasets
- Test memory usage
- Test response times

### 4. Security Tests

- Test input validation
- Test file system access
- Test API key handling

## Running Tests

```bash
# Run all tests
hatch run pytest

# Run specific test categories
hatch run pytest tests/unit/
hatch run pytest tests/integration/
hatch run pytest tests/commands/

# Run with coverage
hatch run pytest --cov=src/libriscribe2

# Run specific module tests
hatch run pytest tests/unit/agents/test_project_manager.py
```

## Test Data Management

- Use fixtures for common test data
- Create mock LLM responses
- Use temporary files/directories
- Clean up after tests

## Continuous Integration

- Run tests on every commit
- Generate coverage reports
- Fail builds on coverage regression
- Track coverage trends over time
