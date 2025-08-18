# LibriScribe Validation Utils - Function and Class Signatures

## Overview

This document provides detailed function and class signatures for the LibriScribe validation utils package. The utils package contains utility implementations that support the core validation system.

## Current Module Structure

### `src/libriscribe2/validation/utils/__init__.py`

```python
"""
Utility modules for the LibriScribe validation system.

This package contains utility classes and functions used across the validation system.
"""

# Type-annotated exports list
__all__: list[str] = [
    # Utility classes will be added here as they are implemented
]
```

**Current Exports**: None (package is in initial setup phase)

## Planned Interface Implementations

### ResourceManagerImpl

**Interface**: `libriscribe2.validation.interfaces.ResourceManager`

```python
class ResourceManagerImpl(ResourceManager):
    """
    Implementation of resource management for validation processes.

    Manages temporary workspaces, file operations, and resource cleanup
    for validation operations.
    """

    def __init__(
        self,
        base_temp_dir: Optional[str] = None,
        auto_cleanup: bool = True,
        max_workspace_age: int = 3600
    ) -> None:
        """
        Initialize resource manager.

        Args:
            base_temp_dir: Base directory for temporary workspaces
            auto_cleanup: Whether to automatically cleanup old workspaces
            max_workspace_age: Maximum age of workspace in seconds before cleanup
        """

    async def create_workspace(self, project_id: str) -> str:
        """
        Create unique workspace for validation process.

        Args:
            project_id: Unique identifier for the project

        Returns:
            Path to created workspace directory

        Raises:
            ResourceError: If workspace creation fails
        """

    async def cleanup_workspace(self, workspace_path: str) -> None:
        """
        Clean up workspace and temporary files.

        Args:
            workspace_path: Path to workspace to clean up

        Raises:
            ResourceError: If cleanup fails
        """

    async def get_unique_temp_file(
        self,
        workspace: str,
        suffix: str = "",
        prefix: str = "temp_"
    ) -> str:
        """
        Get unique temporary file path within workspace.

        Args:
            workspace: Workspace directory path
            suffix: File suffix/extension
            prefix: File prefix

        Returns:
            Path to unique temporary file

        Raises:
            ResourceError: If file creation fails
        """

    async def get_workspace_info(self, workspace_path: str) -> Dict[str, Any]:
        """
        Get information about workspace.

        Args:
            workspace_path: Path to workspace

        Returns:
            Dictionary containing workspace information:
            - created_at: Workspace creation timestamp
            - size_bytes: Total size of workspace in bytes
            - file_count: Number of files in workspace
            - project_id: Associated project ID
        """

    async def list_workspaces(self) -> List[Dict[str, Any]]:
        """
        List all active workspaces.

        Returns:
            List of workspace information dictionaries
        """

    async def cleanup_old_workspaces(self, max_age: Optional[int] = None) -> int:
        """
        Clean up workspaces older than specified age.

        Args:
            max_age: Maximum age in seconds (uses instance default if None)

        Returns:
            Number of workspaces cleaned up
        """
```

### HealthMonitorImpl

**Interface**: `libriscribe2.validation.interfaces.HealthMonitor`

```python
class HealthMonitorImpl(HealthMonitor):
    """
    Implementation of system health monitoring.

    Monitors system resources, AI service connectivity, and validation
    system performance metrics.
    """

    def __init__(
        self,
        check_interval: int = 60,
        ai_timeout: int = 30,
        memory_threshold: float = 0.8,
        disk_threshold: float = 0.9
    ) -> None:
        """
        Initialize health monitor.

        Args:
            check_interval: Health check interval in seconds
            ai_timeout: AI connectivity check timeout in seconds
            memory_threshold: Memory usage threshold (0.0-1.0)
            disk_threshold: Disk usage threshold (0.0-1.0)
        """

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get current system health status.

        Returns:
            Dictionary containing health status:
            - overall_status: "healthy" | "warning" | "critical"
            - timestamp: Current timestamp
            - system_resources: CPU, memory, disk usage
            - ai_services: AI service connectivity status
            - validation_engine: Validation engine status
            - active_validations: Number of active validation processes
        """

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive system metrics.

        Returns:
            Dictionary containing detailed metrics:
            - performance: Response times, throughput
            - resources: Detailed resource usage
            - errors: Error rates and types
            - ai_usage: AI service usage statistics
            - validation_stats: Validation success/failure rates
        """

    async def check_ai_connectivity(self) -> bool:
        """
        Check AI service connectivity status.

        Returns:
            True if AI services are accessible, False otherwise
        """

    async def get_system_resources(self) -> Dict[str, Any]:
        """
        Get current system resource usage.

        Returns:
            Dictionary containing:
            - cpu_percent: CPU usage percentage
            - memory_percent: Memory usage percentage
            - disk_percent: Disk usage percentage
            - network_io: Network I/O statistics
        """

    async def start_monitoring(self) -> None:
        """Start continuous health monitoring."""

    async def stop_monitoring(self) -> None:
        """Stop continuous health monitoring."""

    async def get_health_history(
        self,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get health status history.

        Args:
            hours: Number of hours of history to retrieve

        Returns:
            List of historical health status entries
        """
```

### AIUsageTrackerImpl

**Interface**: `libriscribe2.validation.interfaces.AIUsageTracker`

```python
class AIUsageTrackerImpl(AIUsageTracker):
    """
    Implementation of AI usage tracking and cost monitoring.

    Tracks AI API usage, costs, and performance metrics across
    validation processes.
    """

    def __init__(
        self,
        storage_backend: str = "sqlite",
        cost_tracking: bool = True,
        performance_tracking: bool = True
    ) -> None:
        """
        Initialize AI usage tracker.

        Args:
            storage_backend: Storage backend for usage data
            cost_tracking: Whether to track costs
            performance_tracking: Whether to track performance metrics
        """

    async def track_request(
        self,
        project_id: str,
        validator_id: str,
        tokens_used: int,
        cost: float,
        model: str,
        request_id: Optional[str] = None,
        response_time: Optional[float] = None,
        success: bool = True
    ) -> None:
        """
        Track AI request usage and costs.

        Args:
            project_id: Project identifier
            validator_id: Validator that made the request
            tokens_used: Number of tokens consumed
            cost: Cost of the request in USD
            model: AI model used
            request_id: Optional request identifier
            response_time: Request response time in seconds
            success: Whether the request was successful
        """

    async def get_project_usage(self, project_id: str) -> Dict[str, Any]:
        """
        Get AI usage statistics for specific project.

        Args:
            project_id: Project identifier

        Returns:
            Dictionary containing:
            - total_requests: Total number of requests
            - total_tokens: Total tokens used
            - total_cost: Total cost in USD
            - models_used: List of models used
            - validators: Usage by validator
            - time_range: First and last request timestamps
        """

    async def get_usage_report(
        self,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive usage report.

        Args:
            project_id: Project identifier
            start_date: Report start date (optional)
            end_date: Report end date (optional)

        Returns:
            Detailed usage report with charts and analytics
        """

    async def get_cost_breakdown(
        self,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed cost breakdown for project.

        Args:
            project_id: Project identifier

        Returns:
            Cost breakdown by model, validator, and time period
        """

    async def get_performance_metrics(
        self,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Get AI performance metrics for project.

        Args:
            project_id: Project identifier

        Returns:
            Performance metrics including response times and success rates
        """

    async def export_usage_data(
        self,
        project_id: str,
        format: str = "csv"
    ) -> str:
        """
        Export usage data in specified format.

        Args:
            project_id: Project identifier
            format: Export format ("csv", "json", "xlsx")

        Returns:
            Path to exported file
        """
```

### ReportGeneratorImpl

**Interface**: `libriscribe2.validation.interfaces.ReportGenerator`

```python
class ReportGeneratorImpl(ReportGenerator):
    """
    Implementation of validation report generation.

    Generates validation reports in multiple formats with customizable
    templates and styling.
    """

    def __init__(
        self,
        template_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        default_format: str = "html"
    ) -> None:
        """
        Initialize report generator.

        Args:
            template_dir: Directory containing report templates
            output_dir: Default output directory for reports
            default_format: Default report format
        """

    async def generate_report(
        self,
        result: ValidationResult,
        format: str,
        output_path: Optional[str] = None,
        template: Optional[str] = None,
        include_charts: bool = True
    ) -> Dict[str, Any]:
        """
        Generate validation report in specified format.

        Args:
            result: Validation result to generate report for
            format: Output format ("html", "pdf", "json", "csv")
            output_path: Custom output path (optional)
            template: Custom template name (optional)
            include_charts: Whether to include charts and visualizations

        Returns:
            Dictionary containing:
            - report_path: Path to generated report
            - format: Report format
            - size_bytes: Report file size
            - generation_time: Time taken to generate report
        """

    async def get_supported_formats(self) -> List[str]:
        """
        Get list of supported report formats.

        Returns:
            List of supported format strings
        """

    async def generate_summary_report(
        self,
        results: List[ValidationResult],
        format: str = "html"
    ) -> Dict[str, Any]:
        """
        Generate summary report for multiple validation results.

        Args:
            results: List of validation results
            format: Output format

        Returns:
            Generated summary report information
        """

    async def create_custom_template(
        self,
        template_name: str,
        template_content: str,
        format: str
    ) -> bool:
        """
        Create custom report template.

        Args:
            template_name: Name for the template
            template_content: Template content/markup
            format: Target format for template

        Returns:
            True if template was created successfully
        """

    async def list_templates(self) -> Dict[str, List[str]]:
        """
        List available report templates.

        Returns:
            Dictionary mapping formats to available template names
        """

    async def generate_chart_data(
        self,
        result: ValidationResult
    ) -> Dict[str, Any]:
        """
        Generate chart data for visualization.

        Args:
            result: Validation result

        Returns:
            Chart data suitable for visualization libraries
        """
```

## Utility Functions

### File and Path Utilities

```python
def get_project_workspace_path(project_id: str, base_dir: str) -> str:
    """
    Get standardized workspace path for project.

    Args:
        project_id: Project identifier
        base_dir: Base directory for workspaces

    Returns:
        Standardized workspace path
    """

def ensure_directory_exists(path: str) -> None:
    """
    Ensure directory exists, creating if necessary.

    Args:
        path: Directory path to ensure exists

    Raises:
        ResourceError: If directory cannot be created
    """

def safe_file_operation(
    operation: Callable[[], Any],
    error_message: str
) -> Any:
    """
    Safely execute file operation with error handling.

    Args:
        operation: File operation to execute
        error_message: Error message for failures

    Returns:
        Operation result

    Raises:
        ResourceError: If operation fails
    """
```

### Configuration Utilities

```python
def load_utility_config(
    config_path: str,
    utility_name: str
) -> Dict[str, Any]:
    """
    Load configuration for specific utility.

    Args:
        config_path: Path to configuration file
        utility_name: Name of utility to load config for

    Returns:
        Utility-specific configuration
    """

def validate_config_schema(
    config: Dict[str, Any],
    schema: Dict[str, Any]
) -> bool:
    """
    Validate configuration against schema.

    Args:
        config: Configuration to validate
        schema: Configuration schema

    Returns:
        True if configuration is valid

    Raises:
        ConfigurationError: If configuration is invalid
    """
```

### Monitoring Utilities

```python
def format_bytes(bytes_value: int) -> str:
    """
    Format byte value as human-readable string.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 GB")
    """

def calculate_health_score(metrics: Dict[str, Any]) -> float:
    """
    Calculate overall health score from metrics.

    Args:
        metrics: System metrics dictionary

    Returns:
        Health score between 0.0 and 1.0
    """

def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information.

    Returns:
        Dictionary containing system information
    """
```

## Type Definitions

```python
from typing import TypedDict, Literal, Union
from datetime import datetime

class WorkspaceInfo(TypedDict):
    """Type definition for workspace information."""
    path: str
    project_id: str
    created_at: datetime
    size_bytes: int
    file_count: int

class HealthStatus(TypedDict):
    """Type definition for health status."""
    overall_status: Literal["healthy", "warning", "critical"]
    timestamp: datetime
    system_resources: Dict[str, float]
    ai_services: bool
    validation_engine: str
    active_validations: int

class UsageMetrics(TypedDict):
    """Type definition for AI usage metrics."""
    total_requests: int
    total_tokens: int
    total_cost: float
    models_used: List[str]
    validators: Dict[str, Dict[str, Union[int, float]]]
    time_range: Dict[str, datetime]

ReportFormat = Literal["html", "pdf", "json", "csv", "xlsx"]
StorageBackend = Literal["sqlite", "postgresql", "memory"]
```

## Error Handling

All utility implementations use the validation system's exception hierarchy:

```python
from libriscribe2.validation.interfaces import (
    ValidationError,
    ResourceError,
    ConfigurationError
)

# Resource-related errors
class WorkspaceError(ResourceError):
    """Raised when workspace operations fail."""

class FileOperationError(ResourceError):
    """Raised when file operations fail."""

# Monitoring-related errors
class HealthCheckError(ValidationError):
    """Raised when health checks fail."""

class MetricsError(ValidationError):
    """Raised when metrics collection fails."""

# Usage tracking errors
class UsageTrackingError(ValidationError):
    """Raised when usage tracking fails."""

class ReportGenerationError(ValidationError):
    """Raised when report generation fails."""
```

## Integration Points

The utility implementations integrate with the validation system through:

1. **Configuration System**: All utilities accept `ValidationConfig` objects
2. **Interface Contracts**: Implement abstract interfaces from `validation.interfaces`
3. **Error Handling**: Use validation system exception hierarchy
4. **Logging**: Integrate with validation system logging
5. **Async Support**: All operations are async-compatible

## Version Information

- **Package Version**: 1.0.0
- **Python Compatibility**: 3.8+
- **Dependencies**: See `pyproject.toml` for full dependency list
- **Interface Compatibility**: Compatible with `libriscribe2.validation.interfaces` v1.0.0
