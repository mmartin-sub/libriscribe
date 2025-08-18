# Performance Improvements API Documentation

## Overview

The `performance_improvements.py` module provides Python 3.12-specific performance enhancements for LibriScribe2. It includes optimized classes and utilities for async operations, memory management, string processing, file I/O, and performance monitoring.

## Key Features

- **Python 3.12 Optimizations**: Leverages latest Python performance improvements
- **Async Performance**: Enhanced async task management with task groups
- **Memory Efficiency**: Improved memory usage with slots and weak references
- **Performance Monitoring**: Comprehensive metrics and profiling capabilities
- **String Processing**: Optimized string operations and formatting
- **File I/O**: Async file operations with better performance

## Classes and Functions

### PerformanceMetrics

A dataclass for tracking operation performance metrics using Python 3.12 slots for better memory usage.

```python
@dataclass(slots=True)
class PerformanceMetrics:
    operation_name: str
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    success: bool = True
    error_message: str = ""
```

#### Properties

##### duration

```python
@property
def duration(self) -> float
```

Calculate operation duration in seconds.

**Returns:**
- `float`: Duration between start_time and end_time

#### Methods

##### complete()

```python
def complete(self, success: bool = True, error_message: str = "") -> None
```

Mark operation as complete and record end time.

**Parameters:**
- `success` (bool): Whether the operation succeeded. Defaults to True
- `error_message` (str): Error message if operation failed. Defaults to empty string

**Example:**
```python
metric = PerformanceMetrics("data_processing")
# ... perform operation ...
metric.complete(success=True)
print(f"Operation took {metric.duration:.2f} seconds")
```

### AsyncPerformanceMonitor

Monitor async operations with timing and error tracking.

```python
class AsyncPerformanceMonitor:
    def __init__(self) -> None
```

#### Methods

##### monitor_operation()

```python
async def monitor_operation(
    self,
    operation_name: str,
    operation: Callable[[], Awaitable[T]],
    timeout: float = DEFAULT_TIMEOUT
) -> T
```

Monitor an async operation with timing and timeout handling.

**Parameters:**
- `operation_name` (str): Name of the operation for tracking
- `operation` (Callable[[], Awaitable[T]]): Async function to monitor
- `timeout` (float): Timeout in seconds. Defaults to DEFAULT_TIMEOUT

**Returns:**
- `T`: Result of the operation

**Raises:**
- `asyncio.TimeoutError`: If operation exceeds timeout
- `Exception`: Any exception raised by the operation

**Example:**
```python
monitor = AsyncPerformanceMonitor()

async def fetch_data():
    await asyncio.sleep(1)
    return "data"

result = await monitor.monitor_operation("fetch_data", fetch_data, timeout=5.0)
```

##### get_performance_summary()

```python
def get_performance_summary(self) -> dict[str, Any]
```

Get comprehensive performance summary of all monitored operations.

**Returns:**
- `dict[str, Any]`: Performance summary containing:
  - `total_operations` (int): Total number of operations
  - `successful_operations` (int): Number of successful operations
  - `failed_operations` (int): Number of failed operations
  - `success_rate` (float): Success rate as decimal (0.0-1.0)
  - `average_duration` (float): Average duration of successful operations
  - `total_duration` (float): Total duration of all operations
  - `slowest_operation` (str): Name of the slowest operation

**Example:**
```python
summary = monitor.get_performance_summary()
print(f"Success rate: {summary['success_rate']:.2%}")
print(f"Average duration: {summary['average_duration']:.2f}s")
```

### AgentCache

Agent cache with improved memory management using weak references.

```python
class AgentCache:
    def __init__(self) -> None
```

#### Methods

##### get()

```python
def get(self, key: str) -> Any | None
```

Get item from cache with access tracking.

**Parameters:**
- `key` (str): Cache key

**Returns:**
- `Any | None`: Cached value or None if not found

##### set()

```python
def set(self, key: str, value: Any) -> None
```

Set item in cache.

**Parameters:**
- `key` (str): Cache key
- `value` (Any): Value to cache

##### get_cache_stats()

```python
def get_cache_stats(self) -> dict[str, Any]
```

Get cache statistics.

**Returns:**
- `dict[str, Any]`: Cache statistics containing:
  - `cache_size` (int): Current cache size
  - `access_counts` (dict): Access count per key
  - `most_accessed` (str): Most frequently accessed key

**Example:**
```python
cache = AgentCache()
cache.set("user_data", {"name": "John"})
data = cache.get("user_data")
stats = cache.get_cache_stats()
```

### StringProcessor

String processor using Python 3.12 string operation optimizations.

#### Static Methods

##### fast_string_concatenation()

```python
@staticmethod
def fast_string_concatenation(strings: list[str]) -> str
```

Fast string concatenation using Python 3.12 optimizations.

**Parameters:**
- `strings` (list[str]): List of strings to concatenate

**Returns:**
- `str`: Concatenated string

##### efficient_string_formatting()

```python
@staticmethod
def efficient_string_formatting(template: str, **kwargs: Any) -> str
```

Efficient string formatting using Python 3.12 features.

**Parameters:**
- `template` (str): Template string with format placeholders
- `**kwargs` (Any): Keyword arguments for formatting

**Returns:**
- `str`: Formatted string

##### fast_string_search()

```python
@staticmethod
def fast_string_search(text: str, patterns: list[str]) -> list[str]
```

Fast string search using Python 3.12 optimizations.

**Parameters:**
- `text` (str): Text to search in
- `patterns` (list[str]): Patterns to search for

**Returns:**
- `list[str]`: List of found patterns

**Example:**
```python
# String concatenation
parts = ["Hello", " ", "World", "!"]
result = StringProcessor.fast_string_concatenation(parts)

# String formatting
template = "Hello {name}, you have {count} messages"
formatted = StringProcessor.efficient_string_formatting(
    template, name="John", count=5
)

# String search
text = "The quick brown fox jumps over the lazy dog"
patterns = ["quick", "fox", "cat"]
found = StringProcessor.fast_string_search(text, patterns)
```

### AsyncTaskManager

Async task manager using Python 3.12 task groups for improved performance.

```python
class AsyncTaskManager:
    def __init__(self) -> None
```

#### Methods

##### execute_parallel_tasks()

```python
async def execute_parallel_tasks(
    self,
    tasks: list[Callable[[], Awaitable[T]]],
    max_concurrent: int = 10
) -> list[T]
```

Execute tasks in parallel with concurrency control.

**Parameters:**
- `tasks` (list[Callable[[], Awaitable[T]]]): List of async tasks to execute
- `max_concurrent` (int): Maximum concurrent tasks. Defaults to 10

**Returns:**
- `list[T]`: List of successful results (exceptions are filtered out)

##### execute_with_retry()

```python
async def execute_with_retry(
    self,
    task: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    delay: float = 1.0
) -> T
```

Execute task with retry logic and exponential backoff.

**Parameters:**
- `task` (Callable[[], Awaitable[T]]): Async task to execute
- `max_retries` (int): Maximum retry attempts. Defaults to 3
- `delay` (float): Initial delay between retries. Defaults to 1.0

**Returns:**
- `T`: Result of the task

**Raises:**
- `Exception`: Last exception if all retries fail

**Example:**
```python
task_manager = AsyncTaskManager()

# Parallel execution
async def fetch_url(url):
    # Simulate API call
    await asyncio.sleep(1)
    return f"Data from {url}"

tasks = [
    lambda: fetch_url("http://api1.com"),
    lambda: fetch_url("http://api2.com"),
    lambda: fetch_url("http://api3.com")
]

results = await task_manager.execute_parallel_tasks(tasks, max_concurrent=2)

# Retry execution
async def unreliable_task():
    if random.random() < 0.7:  # 70% failure rate
        raise Exception("Network error")
    return "Success"

result = await task_manager.execute_with_retry(
    unreliable_task, max_retries=5, delay=0.5
)
```

### FileProcessor

File processor using Python 3.12 I/O improvements.

```python
class FileProcessor:
    def __init__(self) -> None
```

#### Methods

##### read_file_async()

```python
async def read_file_async(self, file_path: Path) -> str
```

Read file asynchronously with Python 3.12 optimizations.

**Parameters:**
- `file_path` (Path): Path to the file to read

**Returns:**
- `str`: File contents

**Raises:**
- `Exception`: If file reading fails

##### write_file_async()

```python
async def write_file_async(self, file_path: Path, content: str) -> None
```

Write file asynchronously with Python 3.12 optimizations.

**Parameters:**
- `file_path` (Path): Path to the file to write
- `content` (str): Content to write

**Raises:**
- `Exception`: If file writing fails

##### process_files_batch()

```python
def process_files_batch(
    self,
    file_paths: list[Path],
    processor: Callable[[str], str]
) -> dict[Path, str]
```

Process multiple files in batch with Python 3.12 optimizations.

**Parameters:**
- `file_paths` (list[Path]): List of file paths to process
- `processor` (Callable[[str], str]): Function to process file content

**Returns:**
- `dict[Path, str]`: Mapping of file paths to processed content or error messages

**Example:**
```python
file_processor = FileProcessor()

# Async file operations
content = await file_processor.read_file_async(Path("data.txt"))
await file_processor.write_file_async(Path("output.txt"), "processed data")

# Batch processing
def uppercase_processor(content: str) -> str:
    return content.upper()

files = [Path("file1.txt"), Path("file2.txt")]
results = file_processor.process_files_batch(files, uppercase_processor)
```

### JSONProcessor

JSON processor using Python 3.12 JSON performance improvements.

```python
class JSONProcessor:
    def __init__(self) -> None
```

#### Methods

##### fast_json_parse()

```python
def fast_json_parse(self, json_str: str) -> dict[str, Any]
```

Fast JSON parsing using Python 3.12 optimizations.

**Parameters:**
- `json_str` (str): JSON string to parse

**Returns:**
- `dict[str, Any]`: Parsed JSON data

**Raises:**
- `json.JSONDecodeError`: If JSON parsing fails

##### fast_json_serialize()

```python
def fast_json_serialize(self, data: dict[str, Any]) -> str
```

Fast JSON serialization using Python 3.12 optimizations.

**Parameters:**
- `data` (dict[str, Any]): Data to serialize

**Returns:**
- `str`: JSON string

**Raises:**
- `Exception`: If JSON serialization fails

##### validate_json_structure()

```python
def validate_json_structure(self, data: dict[str, Any], required_keys: list[str]) -> bool
```

Validate JSON structure using Python 3.12 features.

**Parameters:**
- `data` (dict[str, Any]): JSON data to validate
- `required_keys` (list[str]): List of required keys

**Returns:**
- `bool`: True if all required keys are present

**Example:**
```python
json_processor = JSONProcessor()

# Parse JSON
json_str = '{"name": "John", "age": 30}'
data = json_processor.fast_json_parse(json_str)

# Serialize JSON
serialized = json_processor.fast_json_serialize(data)

# Validate structure
is_valid = json_processor.validate_json_structure(
    data, ["name", "age"]
)
```

### MemoryProfiler

Memory profiler using Python 3.12 improvements for tracking memory usage.

```python
class MemoryProfiler:
    def __init__(self) -> None
```

#### Methods

##### take_snapshot()

```python
def take_snapshot(self, label: str) -> None
```

Take a memory snapshot with the given label.

**Parameters:**
- `label` (str): Label for the snapshot

##### get_memory_summary()

```python
def get_memory_summary(self) -> dict[str, Any]
```

Get memory usage summary across all snapshots.

**Returns:**
- `dict[str, Any]`: Memory summary containing:
  - `total_snapshots` (int): Number of snapshots taken
  - `initial_memory` (int): Memory usage at first snapshot
  - `final_memory` (int): Memory usage at last snapshot
  - `memory_change` (int): Change in memory usage
  - `peak_memory` (int): Peak memory usage
  - `average_memory` (float): Average memory usage

**Example:**
```python
profiler = MemoryProfiler()

profiler.take_snapshot("start")
# ... perform memory-intensive operations ...
profiler.take_snapshot("after_processing")

summary = profiler.get_memory_summary()
print(f"Memory change: {summary['memory_change']} bytes")
```

### PerformanceUtils

Utility functions for performance optimization and measurement.

#### Static Methods

##### measure_execution_time()

```python
@staticmethod
def measure_execution_time(func: Callable[[], T]) -> tuple[T, float]
```

Measure execution time of a synchronous function.

**Parameters:**
- `func` (Callable[[], T]): Function to measure

**Returns:**
- `tuple[T, float]`: Tuple of (result, execution_time_seconds)

##### measure_async_execution_time()

```python
@staticmethod
async def measure_async_execution_time(func: Callable[[], Awaitable[T]]) -> tuple[T, float]
```

Measure execution time of an async function.

**Parameters:**
- `func` (Callable[[], Awaitable[T]]): Async function to measure

**Returns:**
- `tuple[T, float]`: Tuple of (result, execution_time_seconds)

##### optimize_list_operations()

```python
@staticmethod
def optimize_list_operations(items: list[Any]) -> list[Any]
```

Optimize list operations using Python 3.12 features.

**Parameters:**
- `items` (list[Any]): List to optimize

**Returns:**
- `list[Any]`: Optimized list with None values removed

##### fast_dict_merge()

```python
@staticmethod
def fast_dict_merge(dicts: list[dict[str, Any]]) -> dict[str, Any]
```

Fast dictionary merging using Python 3.12 optimizations.

**Parameters:**
- `dicts` (list[dict[str, Any]]): List of dictionaries to merge

**Returns:**
- `dict[str, Any]`: Merged dictionary

**Example:**
```python
# Measure execution time
def slow_operation():
    time.sleep(1)
    return "done"

result, duration = PerformanceUtils.measure_execution_time(slow_operation)
print(f"Operation took {duration:.2f} seconds")

# Async measurement
async def async_operation():
    await asyncio.sleep(1)
    return "done"

result, duration = await PerformanceUtils.measure_async_execution_time(async_operation)

# List optimization
items = [1, None, 2, None, 3]
optimized = PerformanceUtils.optimize_list_operations(items)  # [1, 2, 3]

# Dictionary merging
dicts = [{"a": 1}, {"b": 2}, {"c": 3}]
merged = PerformanceUtils.fast_dict_merge(dicts)  # {"a": 1, "b": 2, "c": 3}
```

## Usage Examples

### Complete Performance Monitoring Example

```python
import asyncio
from pathlib import Path
from libriscribe2.utils.performance_improvements import (
    AsyncPerformanceMonitor,
    AsyncTaskManager,
    MemoryProfiler,
    PerformanceUtils
)

async def main():
    # Initialize components
    monitor = AsyncPerformanceMonitor()
    task_manager = AsyncTaskManager()
    profiler = MemoryProfiler()

    # Take initial memory snapshot
    profiler.take_snapshot("start")

    # Define some async operations
    async def process_data(data_id: int):
        await asyncio.sleep(0.1)  # Simulate processing
        return f"processed_{data_id}"

    # Monitor individual operation
    result = await monitor.monitor_operation(
        "single_process",
        lambda: process_data(1),
        timeout=5.0
    )

    # Execute multiple tasks in parallel
    tasks = [lambda i=i: process_data(i) for i in range(10)]
    results = await task_manager.execute_parallel_tasks(tasks, max_concurrent=3)

    # Take final memory snapshot
    profiler.take_snapshot("end")

    # Get performance summary
    perf_summary = monitor.get_performance_summary()
    memory_summary = profiler.get_memory_summary()

    print(f"Processed {len(results)} items")
    print(f"Success rate: {perf_summary['success_rate']:.2%}")
    print(f"Memory change: {memory_summary['memory_change']} bytes")

# Run the example
asyncio.run(main())
```

### File Processing with Performance Monitoring

```python
import asyncio
from pathlib import Path
from libriscribe2.utils.performance_improvements import (
    FileProcessor,
    JSONProcessor,
    StringProcessor,
    PerformanceUtils
)

async def process_files_example():
    file_processor = FileProcessor()
    json_processor = JSONProcessor()

    # Process files with timing
    def process_content(content: str) -> str:
        # Clean and format content
        lines = content.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return StringProcessor.fast_string_concatenation(cleaned_lines)

    # Measure file processing time
    files = [Path("file1.txt"), Path("file2.txt")]

    result, duration = PerformanceUtils.measure_execution_time(
        lambda: file_processor.process_files_batch(files, process_content)
    )

    print(f"Processed {len(result)} files in {duration:.2f} seconds")

    # Process JSON data
    json_data = {"items": [1, 2, 3], "status": "active"}
    json_str = json_processor.fast_json_serialize(json_data)
    parsed_data = json_processor.fast_json_parse(json_str)

    is_valid = json_processor.validate_json_structure(
        parsed_data, ["items", "status"]
    )
    print(f"JSON validation: {'passed' if is_valid else 'failed'}")

# Run the example
asyncio.run(process_files_example())
```

## Integration with LibriScribe2

The performance improvements module integrates seamlessly with other LibriScribe2 components:

- **Agent Framework**: Use `AsyncTaskManager` for parallel agent execution
- **File Operations**: Use `FileProcessor` for efficient I/O operations
- **Caching**: Use `AgentCache` for agent result caching
- **Monitoring**: Use `AsyncPerformanceMonitor` for operation tracking
- **Memory Management**: Use `MemoryProfiler` for memory usage analysis

## Python 3.12 Features Utilized

- **Slots**: Better memory usage in dataclasses
- **Improved Async**: Enhanced async performance and task groups
- **String Optimizations**: Faster string operations and formatting
- **JSON Performance**: Improved JSON parsing and serialization
- **Memory Management**: Better garbage collection and weak references
- **Type Annotations**: Enhanced type system with generics

## Best Practices

1. **Use Async Operations**: Prefer async methods for I/O operations
2. **Monitor Performance**: Use performance monitoring for critical operations
3. **Manage Memory**: Take memory snapshots for memory-intensive operations
4. **Cache Results**: Use caching for expensive computations
5. **Batch Operations**: Process multiple items together when possible
6. **Handle Errors**: Use retry mechanisms for unreliable operations

## See Also

- [Timestamp Utils API](timestamp-utils-api.md)
- [LLM Client API](llm-client-api.md)
- [File Utils Documentation](../development/file-utils.md)
