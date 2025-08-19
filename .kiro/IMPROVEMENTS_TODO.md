# Project Improvement TODO List

This document outlines a list of tasks to improve the overall quality, maintainability, and professionalism of the LibriScribe2 project.

## 1. Improve Test Coverage

The current test coverage is 54%, which is quite low. The following files have very low or no test coverage and should be prioritized:

- [ ] `src/libriscribe2/agents/title_generator.py` (0%)
- [ ] `src/libriscribe2/process.py` (0%)
- [ ] `src/libriscribe2/utils/markdown_utils.py` (0%)
- [ ] `src/libriscribe2/utils/performance_improvements.py` (0%)
- [ ] `src/libriscribe2/utils/type_improvements.py` (0%)
- [ ] `src/libriscribe2/validation/utils/__init__.py` (0%)
- [ ] `src/libriscribe2/agents/researcher.py` (19%)
- [ ] `src/libriscribe2/validation/config.py` (20%)
- [ ] `src/libriscribe2/agent_frameworks/autogen/service.py` (23%)
- [ ] `src/libriscribe2/agents/fact_checker.py` (23%)
- [ ] `src/libriscribe2/agents/style_editor.py` (23%)
- [ ] `src/libriscribe2/validation/ai_mock.py` (24%)
- [ ] `src/libriscribe2/agents/plagiarism_checker.py` (26%)
- [ ] `src/libriscribe2/validation/validation_engine.py` (29%)
- [ ] `src/libriscribe2/cli.py` (32%)

## 2. Improve Documentation

- [ ] **Review and update all documentation:** Ensure that all documentation in the `.kiro` and `docs` directories is up-to-date with the current implementation.
- [ ] **Add a "Best Practices" guide:** Create a new document in `docs/development` that outlines best practices for git commit messages, GitHub workflows, and Pip publishing.
- [ ] **Improve API documentation:** The API documentation in `docs/api` is generated from the code. Review the docstrings in the code to ensure that the generated documentation is clear and comprehensive.

## 3. Implement Missing Features

- [ ] **Multi-LLM Support:** Implement support for other LLM providers, such as Anthropic Claude, Google Gemini, and Mistral.
- [ ] **Interactive Commands:** Implement the interactive commands that are currently missing, such as `start`, `concept`, `outline`, etc.
- [ ] **Vector Store & Search:** Implement the vector store and search functionality.

## 4. Professionalize the Project

- [ ] **Create a `CONTRIBUTING.md` file:** Create a comprehensive `CONTRIBUTING.md` file that outlines how to contribute to the project.
- [ ] **Set up GitHub Actions for automated testing:** Set up GitHub Actions to automatically run the tests on every push and pull request.
- [ ] **Publish the library to PyPI:** Create a workflow to automatically publish the library to PyPI on every new release.

## 5. Skipped Tests

The following files have been skipped for testing for now. They should be revisited in the future.

- [ ] `src/libriscribe2/utils/markdown_utils.py`
- [ ] `src/libriscribe2/agents/style_editor.py`
