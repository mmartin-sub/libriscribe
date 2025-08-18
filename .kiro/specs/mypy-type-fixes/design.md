# Design Document

## Overview

This design addresses the specific mypy strict mode issues identified in the LibriScribe codebase. The solution focuses on resolving untyped function bodies, missing library stubs, and ensuring all functions have proper type annotations to pass mypy strict checking.

## Architecture

### Type Annotation Strategy

The design follows a systematic approach to resolve mypy strict issues:

1. **Function Type Annotation**: Add explicit type annotations to all function parameters and return types
2. **Library Stub Management**: Install and configure type stubs for external libraries
3. **Import Organization**: Add necessary typing imports and organize them properly
4. **Incremental Validation**: Apply fixes incrementally with validation at each step

### Error Classification

The identified mypy errors fall into these categories:

1. **Untyped Function Bodies** (`annotation-unchecked`):
   - Functions without proper type annotations
   - Affects: `base.py:110-111`, `performance_improvements.py:57,102-103,289`

2. **Missing Library Stubs** (`import-untyped`):
   - External libraries without type information
   - Affects: `mistletoe` imports in `markdown_validator.py` and `markdown_processor.py`

## Components and Interfaces

### Type Annotation Component

**Purpose**: Add comprehensive type annotations to untyped functions

**Interface**:

```python
def add_function_annotations(
    file_path: Path,
    function_signatures: dict[str, FunctionSignature]
) -> bool
```

**Responsibilities**:

- Parse Python files to identify untyped functions
- Infer appropriate types from function usage
- Add explicit parameter and return type annotations
- Maintain backward compatibility

### Library Stub Manager

**Purpose**: Install and configure type stubs for external libraries

**Interface**:

```python
def install_library_stubs(
    libraries: list[str],
    package_manager: str = "uv"
) -> bool
```

**Responsibilities**:

- Install type stub packages (e.g., `types-mistletoe`)
- Update pyproject.toml with new dependencies
- Configure mypy to recognize installed stubs
- Handle stub installation failures gracefully

### Import Organizer

**Purpose**: Add and organize typing imports

**Interface**:

```python
def organize_typing_imports(
    file_path: Path,
    required_types: set[str]
) -> bool
```

**Responsibilities**:

- Add missing typing imports (Any, Optional, Union, etc.)
- Organize imports according to PEP 8
- Remove unused imports
- Handle conditional imports for different Python versions

## Data Models

### Function Signature Model

```python
@dataclass
class FunctionSignature:
    name: str
    parameters: list[Parameter]
    return_type: str
    is_async: bool = False
    decorators: list[str] = field(default_factory=list)

@dataclass
class Parameter:
    name: str
    type_annotation: str
    default_value: str | None = None
    is_variadic: bool = False
    is_keyword_only: bool = False
```

### Type Inference Model

```python
@dataclass
class TypeInference:
    variable_name: str
    inferred_type: str
    confidence: float
    source_location: tuple[int, int]  # line, column
    usage_patterns: list[str]
```

## Error Handling

### Type Annotation Errors

- **Invalid Type Inference**: Fall back to `Any` type with warning
- **Circular Import Issues**: Use string literals for forward references
- **Complex Generic Types**: Simplify to base types when necessary

### Library Stub Errors

- **Missing Stub Packages**: Install available stubs, ignore missing ones
- **Stub Installation Failures**: Continue with `# type: ignore` comments
- **Version Compatibility**: Use version-specific stub packages

### File Processing Errors

- **Syntax Errors**: Skip files with syntax issues, report errors
- **Permission Errors**: Skip read-only files, log warnings
- **Encoding Issues**: Use UTF-8 with error handling

## Testing Strategy

### Unit Testing

1. **Function Annotation Tests**:
   - Test type inference accuracy
   - Verify annotation syntax correctness
   - Check backward compatibility

2. **Library Stub Tests**:
   - Test stub installation process
   - Verify mypy recognizes installed stubs
   - Check dependency management

3. **Import Organization Tests**:
   - Test import addition and removal
   - Verify import ordering
   - Check for import conflicts

### Integration Testing

1. **End-to-End Mypy Validation**:
   - Run mypy strict on fixed files
   - Verify no new errors introduced
   - Check overall error reduction

2. **Development Environment Testing**:
   - Test within hatch shell environment
   - Verify uv package management integration
   - Check CI/CD compatibility

### Validation Strategy

1. **Pre-fix Validation**:
   - Backup original files
   - Run baseline mypy check
   - Document current error count

2. **Incremental Validation**:
   - Validate each file after fixing
   - Run mypy on modified files
   - Check for new errors

3. **Post-fix Validation**:
   - Run full mypy strict check
   - Verify error reduction
   - Test runtime functionality

## Implementation Approach

### Phase 1: Library Stub Resolution

1. Install type stubs for `mistletoe`
2. Update pyproject.toml dependencies
3. Verify mypy recognizes stubs

### Phase 2: Function Type Annotations

1. Add type annotations to `base.py` functions (lines 110-111)
2. Add type annotations to `performance_improvements.py` functions (lines 57, 102-103, 289)
3. Validate each file after annotation

### Phase 3: Import Organization

1. Add necessary typing imports
2. Organize imports per PEP 8
3. Remove unused imports

### Phase 4: Validation and Testing

1. Run comprehensive mypy strict check
2. Verify no runtime behavior changes
3. Update documentation as needed

## Dependencies

### External Dependencies

- **mistletoe type stubs**: For markdown processing type safety
- **mypy**: For type checking validation
- **ast module**: For Python code parsing
- **pathlib**: For file system operations

### Internal Dependencies

- **LibriScribe settings**: For configuration management
- **Logging utilities**: For error reporting
- **File utilities**: For backup and restoration

## Performance Considerations

### Type Checking Performance

- Use incremental mypy checking where possible
- Cache type inference results
- Process files in dependency order

### Memory Usage

- Process files individually to limit memory usage
- Use generators for large file collections
- Clean up temporary data structures

### Development Workflow

- Integrate with existing hatch/uv workflow
- Maintain compatibility with pre-commit hooks
- Support parallel processing where safe
