# LibriScribe Validation Utils API Documentation

## Overview

The `libriscribe2.validation.utils` package provides utility classes and functions used across the LibriScribe validation system. This package contains implementations of utility interfaces defined in the validation system for resource management, health monitoring, AI usage tracking, and report generation.

## Module Structure

```
src/libriscribe2/validation/utils/
├── __init__.py                 # Package initialization and exports
├── resource_manager.py         # Resource management implementation (planned)
├── health_monitor.py          # System health monitoring (planned)
├── ai_usage_tracker.py        # AI usage tracking implementation (planned)
└── report_generator.py        # Report generation utilities (planned)
```

## Current Status

The utils package is currently in the initial setup phase. The `__init__.py` file provides the foundation for future utility implementations with proper type annotations and documentation structure.

## Package Exports

### Current Exports

```python
__all__: list[str] = [
    # Utility classes will be added here as they are implemented
]
```

Currently, the package does not export any classes or functions as the utility implementations are still being developed.

### Planned Exports

The following utility classes will be implemented and exported:

- `ResourceManagerImpl` - Implementation of the ResourceManager interface
- `HealthMonitorImpl` - Implementation of the HealthMonitor interface
- `AIUsageTrackerImpl` - Implementation of the AIUsageTracker interface
- `ReportGeneratorImpl` - Implementation of the ReportGenerator interface

## Interface Implementations (Planned)

### ResourceManagerImpl

Will implement the `ResourceManager` interface for managing validation resources:

```python
class ResourceManagerImpl(ResourceManager):
    """Implementation of resource management for validation processes."""

    async def create_workspace(self, project_id: str) -> str:
        """Create unique workspace for validation process."""

    async def cleanup_workspace(self, workspace_path: str) -> None:
        """Clean up workspace and temporary files."""

    async def get_unique_temp_file(self, workspace: str, suffix: str = "") -> str:
        """Get unique temporary file path within workspace."""
```

### HealthMonitorImpl

Will implement the `HealthMonitor` interface for system health monitoring:

```python
class HealthMonitorImpl(HealthMonitor):
    """Implementation of system health monitoring."""

    async def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status."""

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""

    async def check_ai_connectivity(self) -> bool:
        """Check AI service connectivity status."""
```

### AIUsageTrackerImpl

Will implement the `AIUsageTracker` interface for tracking AI usage and costs:

```python
class AIUsageTrackerImpl(AIUsageTracker):
    """Implementation of AI usage tracking and cost monitoring."""

    async def track_request(
        self,
        project_id: str,
        validator_id: str,
        tokens_used: int,
        cost: float,
        model: str,
    ) -> None:
        """Track AI request usage and costs."""

    async def get_project_usage(self, project_id: str) -> Dict[str, Any]:
        """Get AI usage statistics for specific project."""

    async def get_usage_report(self, project_id: str) -> Dict[str, Any]:
        """Generate comprehensive usage report."""
```

### ReportGeneratorImpl

Will implement the `ReportGenerator` interface for generating validation reports:

```python
class ReportGeneratorImpl(ReportGenerator):
    """Implementation of validation report generation."""

    async def generate_report(
        self, result: ValidationResult, format: str
    ) -> Dict[str, Any]:
        """Generate validation report in specified format."""

    async def get_supported_formats(self) -> List[str]:
        """Get list of supported report formats."""
```

## Usage Examples

### Basic Import (Current)

```python
from libriscribe2.validation.utils import *
# Currently no exports available
```

### Future Usage (Planned)

```python
from libriscribe2.validation.utils import (
    ResourceManagerImpl,
    HealthMonitorImpl,
    AIUsageTrackerImpl,
    ReportGeneratorImpl
)

# Initialize resource manager
resource_manager = ResourceManagerImpl()
workspace = await resource_manager.create_workspace("project_123")

# Monitor system health
health_monitor = HealthMonitorImpl()
health_status = await health_monitor.get_health_status()

# Track AI usage
usage_tracker = AIUsageTrackerImpl()
await usage_tracker.track_request(
    project_id="project_123",
    validator_id="content_validator",
    tokens_used=1500,
    cost=0.03,
    model="gpt-4o-mini"
)

# Generate reports
report_generator = ReportGeneratorImpl()
report = await report_generator.generate_report(validation_result, "html")
```

## Integration with Validation System

The utility classes integrate with the main validation system through the interfaces defined in `libriscribe2.validation.interfaces`:

```python
from libriscribe2.validation import ValidationEngineImpl
from libriscribe2.validation.utils import (
    ResourceManagerImpl,
    HealthMonitorImpl,
    AIUsageTrackerImpl,
    ReportGeneratorImpl
)

# Initialize validation engine with utility implementations
engine = ValidationEngineImpl()
await engine.initialize_utilities(
    resource_manager=ResourceManagerImpl(),
    health_monitor=HealthMonitorImpl(),
    usage_tracker=AIUsageTrackerImpl(),
    report_generator=ReportGeneratorImpl()
)
```

## Development Guidelines

### Adding New Utilities

When implementing new utility classes:

1. **Follow Interface Contracts**: Implement the corresponding interface from `libriscribe2.validation.interfaces`
2. **Add Type Annotations**: Use proper type hints for all parameters and return values
3. **Update Exports**: Add new classes to the `__all__` list in `__init__.py`
4. **Document Thoroughly**: Include comprehensive docstrings and examples
5. **Add Tests**: Create corresponding test files in the testing directory

### Code Style

```python
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

class UtilityImpl(UtilityInterface):
    """
    Implementation of utility interface.

    This class provides [specific functionality] for the validation system.

    Args:
        config: Configuration dictionary for the utility

    Example:
        >>> utility = UtilityImpl(config={"setting": "value"})
        >>> result = await utility.method()
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.initialized = False

    async def method(self) -> Dict[str, Any]:
        """
        Method description.

        Returns:
            Dictionary containing method results

        Raises:
            ValidationError: If method fails
        """
        pass
```

## Error Handling

All utility implementations should handle errors gracefully and use the validation system's exception hierarchy:

```python
from libriscribe2.validation.interfaces import (
    ValidationError,
    ResourceError,
    ConfigurationError
)

class UtilityImpl:
    async def method(self) -> Any:
        try:
            # Implementation logic
            pass
        except FileNotFoundError as e:
            raise ResourceError(f"Resource not found: {e}")
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration: {e}")
        except Exception as e:
            raise ValidationError(f"Utility operation failed: {e}")
```

## Configuration

Utility classes should accept configuration through the validation system's configuration management:

```python
from libriscribe2.validation.interfaces import ValidationConfig

class UtilityImpl:
    def __init__(self, config: ValidationConfig) -> None:
        self.temp_directory = config.temp_directory
        self.cleanup_on_completion = config.cleanup_on_completion
        self.health_check_enabled = config.health_check_enabled
```

## Testing

Each utility implementation should have comprehensive tests:

```python
import pytest
from libriscribe2.validation.utils import UtilityImpl

@pytest.mark.asyncio
async def test_utility_method():
    """Test utility method functionality."""
    utility = UtilityImpl(config={"test": True})
    result = await utility.method()
    assert result is not None

@pytest.mark.asyncio
async def test_utility_error_handling():
    """Test utility error handling."""
    utility = UtilityImpl(config={})
    with pytest.raises(ValidationError):
        await utility.invalid_method()
```

## Related Documentation

- [Validation System Overview](validation_system.md)
- [Validation Interfaces API](validation_interfaces_api.md)
- [Validation Engine API](validation_engine_api.md)
- [AI Mock System](ai_mock_system.md)

## Version History

- **1.0.0**: Initial package structure with type annotations and documentation framework
