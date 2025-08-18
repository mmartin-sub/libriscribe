# TODOs and Technical Debt Tracker

This file tracks all unimplemented features, modernization tasks, and mypy errors in the codebase. Each entry references the file and line number, with a brief description.

---

## src/libriscribe2/services/book_creator.py

- [x] Line ~277: # TODO: Handle None project_manager (mypy error [attr-defined])
- [x] Line ~285: # TODO: Modernize tuple/int comparison logic if not already modern
- [x] Line ~292: # TODO: Handle None project_manager.project_dir (mypy error [attr-defined])

## src/libriscribe2/main.py

- [ ] # TODO: interactive_create method is not implemented in ProjectManagerAgent (mypy error [attr-defined])
      - Clear error message now shown in main.py when called.
- [ ] # TODO: create_project_non_interactive method is not implemented in ProjectManagerAgent (mypy error [attr-defined])
      - Clear error message now shown in main.py when called.

## Pydantic v1 Migration

- [x] ✅ Migrate knowledge_base.py to Pydantic v2 syntax
      - Line 4: Replaced `from pydantic import validator` with `from pydantic import field_validator`
      - Line 120: Replaced `@validator` with `@field_validator`
      - Line 210: Replaced `@validator` with `@field_validator`
      - All validators now use Pydantic v2 syntax with `mode="before"` and `@classmethod`
      - Pre-commit hook updated to properly detect v1 vs v2 syntax

## Pre-commit Hooks

- [x] ✅ Pydantic v1 syntax check hook installed and working
      - Custom hook in `scripts/check_pydantic_v1.py`
      - Prevents committing v1 syntax patterns
      - Runs automatically on `git commit`
      - Updated to properly distinguish between v1 and v2 syntax
      - Correctly handles `pydantic_settings` imports (v2) vs `pydantic.BaseSettings` (v1)
      - Excludes the check script itself from being checked
      - Fixed: Now uses `hatch run` instead of `python` directly
      - Fixed: Uses `language: system` instead of `language: python`

- [x] ✅ MyPy hook fixed and working with Python 3.12
      - **Environment Setup**: Hatch environment uses Python 3.12.11 (correctly configured)
      - **Pre-commit Configuration**: Now uses Python 3.12 via `default_language_version: python: python3.12`
      - **Version Compatibility**: Using MyPy 1.17.0 (latest version compatible with Python 3.12)
      - Removed problematic `types-all` dependency, using specific type stubs instead
      - Hook now works correctly (module path issue is expected and skipped)

## MyPy Error Fixes

- [x] ✅ Fixed editor.py Path/None issues
      - Line 43: Added null check for `project_knowledge_base.project_dir`
      - Line 138: Same issue already handled by the first fix
      - Added proper error handling for None project directory

- [x] ✅ Fixed test_framework.py type issues
      - Line 283: Fixed `List[TestResult]` type annotation for `valid_results`
      - Line 400: Added return type annotation `-> ValidatorResult` to validate method
      - Line 402: Removed invalid `use_mock=True` parameter from `get_ai_response` call
      - Line 457: Fixed `Finding` constructor to use `FindingType` enum instead of string
      - Line 666: Added type annotation `Dict[str, List[Any]]` for `regression_results`
      - Added proper type checking for `asyncio.gather` results

## Multi-LLM Support Implementation

### Current Status

- [x] ✅ OpenAI Integration: Fully implemented with GPT-4o and GPT-4o-mini
- [x] ✅ Mock LLM Provider: Comprehensive testing framework
- [ ] 🔄 Anthropic Claude Integration: Framework exists, implementation pending
- [ ] 🔄 Google Gemini Integration: Framework exists, implementation pending
- [ ] 🔄 Mistral AI Integration: Framework exists, implementation pending
- [ ] 🔄 Deepseek Integration: Framework exists, implementation pending

### Required Tasks

- [ ] Implement `_generate_anthropic_content()` method in `src/libriscribe2/utils/llm_client.py`
- [ ] Implement `_generate_google_content()` method in `src/libriscribe2/utils/llm_client.py`
- [ ] Implement `_generate_mistral_content()` method in `src/libriscribe2/utils/llm_client.py`
- [ ] Implement `_generate_deepseek_content()` method in `src/libriscribe2/utils/llm_client.py`
- [ ] Add corresponding streaming methods for each provider
- [ ] Update settings.py to include new provider configurations
- [ ] Add new API key environment variables
- [ ] Update configuration loading in config.py
- [ ] Add provider-specific error handling and fallback logic
- [ ] Update tests to cover new providers

## Remaining Tasks

- [ ] # TODO: Implement missing ProjectManagerAgent methods
      - `interactive_create()` method
      - `create_project_non_interactive()` method
      - These are called in main.py but not implemented

## Completed Modernization

- [x] ✅ Security: Fixed MD5 hash usage with `usedforsecurity=False`
- [x] ✅ Linting: Updated Ruff configuration to use `lint.ignore`
- [x] ✅ Type Safety: Fixed most Mypy errors across the codebase
- [x] ✅ Dependencies: Updated to use latest libraries compatible with Python 3.12
- [x] ✅ Pydantic: Migrated from v1 to v2 syntax throughout the codebase
- [x] ✅ Pre-commit: Fixed hook configuration and version compatibility issues
- [x] ✅ Environment: Hatch environment now correctly uses Python 3.12
- [x] ✅ Pre-commit: Now uses Python 3.12 and MyPy 1.17.0

---

**Instructions:**

- When you address a TODO, check it off and describe the resolution.
- When you add a new TODO or FIXME in the code, update this file accordingly.
- The Pydantic v1 check will run automatically on commit and prevent v1 syntax from being committed.
- Update multi-LLM support status as providers are implemented.
