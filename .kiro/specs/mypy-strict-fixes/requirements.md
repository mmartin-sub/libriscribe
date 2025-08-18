# Requirements Document

## Introduction

This feature addresses the mypy strict type checking issues in the libriscribe2 codebase. The goal is to improve code quality and type safety by fixing all type annotation issues that appear when running `hatch run typing --strict`. This includes adding missing type annotations, fixing generic type parameters, and reorganizing test-related files to appropriate locations.

## Requirements

### Requirement 1

**User Story:** As a developer, I want all functions to have proper type annotations, so that the codebase maintains high type safety standards.

#### Acceptance Criteria

1. WHEN running `hatch run typing --strict` THEN the system SHALL show no `no-untyped-def` errors
2. WHEN a function returns None THEN the system SHALL have explicit `-> None` return type annotation
3. WHEN a function has parameters THEN the system SHALL have type annotations for all parameters
4. WHEN a function returns a value THEN the system SHALL have proper return type annotation

### Requirement 2

**User Story:** As a developer, I want all generic types to have proper type parameters, so that type checking is more precise and catches potential bugs.

#### Acceptance Criteria

1. WHEN using generic types like `dict`, `list`, `tuple`, `set` THEN the system SHALL specify type parameters (e.g., `dict[str, Any]`, `list[str]`)
2. WHEN encountering `type-arg` errors THEN the system SHALL add appropriate type parameters
3. WHEN type parameters are complex THEN the system SHALL use appropriate type aliases or imports from `typing`

### Requirement 3

**User Story:** As a developer, I want test-related files to be properly organized, so that they don't interfere with production code type checking.

#### Acceptance Criteria

1. WHEN a file is primarily for testing purposes THEN the system SHALL move it to the appropriate test directory
2. WHEN test files are moved THEN the system SHALL update any imports that reference them
3. WHEN test files are excluded from mypy THEN the system SHALL update the mypy configuration appropriately

### Requirement 4

**User Story:** As a developer, I want to eliminate all `no-untyped-call` errors, so that all function calls are properly typed.

#### Acceptance Criteria

1. WHEN calling functions that lack type annotations THEN the system SHALL add proper type annotations to those functions
2. WHEN encountering `no-untyped-call` errors THEN the system SHALL ensure the called function has proper type annotations
3. WHEN functions are in different modules THEN the system SHALL ensure consistent typing across module boundaries

### Requirement 5

**User Story:** As a developer, I want the mypy configuration to be optimized, so that it provides strict checking without being overly broad in exclusions.

#### Acceptance Criteria

1. WHEN configuring mypy THEN the system SHALL remove or limit the scope of `follow_imports = "skip"`
2. WHEN excluding modules from type checking THEN the system SHALL be specific rather than using broad exclusions
3. WHEN running `hatch run typing --strict` THEN the system SHALL pass without errors
4. WHEN running regular `hatch run typing` THEN the system SHALL continue to work as before
