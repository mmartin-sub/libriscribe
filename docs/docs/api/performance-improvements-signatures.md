# Performance Improvements - Function Signatures

## Complete API Reference

### PerformanceMetrics Class

#### Constructor

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

```python
@property
def duration(self) -> float
```

#### Methods

```python
def complete(self, success: bool = True, error_message: str = "") -> None
```

### AsyncPerformanceMonitor Class

#### Constructor

```python
def __init__(self) -> None
```

#### Methods

```python
async def monitor_operation(
    self,
    operation_name: str,
    operation: Callable[[], Awaitable[T]],
    timeout: float = DEFAULT_TIMEOUT
) -> T

def get_performance_summary(self) -> dict[str, Any]
```

### AgentCache Class

#### Constructor

```python
def __init__(self) -> None
```

#### Methods

```python
def get(self, key: str) -> Any | None

def set(self, key: str, value: Any) -> None

def get_cache_stats(self) -> dict[str, Any]
```

### StringProcessor Class

#### Static Methods

```python
@staticmethod
def fast_string_concatenation(strings: list[str]) -> str

@staticmethod
def efficient_string_formatting(template: str, **kwargs: Any) -> str

@staticmethod
def fast_string_search(text: str, patterns: list[str]) -> list[str]
```

### AsyncTaskManager Class

#### Constructor

```python
def __init__(self) -> None
```

#### Methods

```python
async def execute_parallel_tasks(
    self,
    tasks: list[Callable[[], Awaitable[T]]],
    max_concurrent: int = 10
) -> list[T]

async def execute_with_retry(
    self,
    task: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    delay: float = 1.0
) -> T
```

### FileProcessor Class

#### Constructor

```python
def __init__(self) -> None
```

#### Methods

```python
async def read_file_async(self, file_path: Path) -> str

async def write_file_async(self, file_path: Path, content: str) -> None

def process_files_batch(
    self,
    file_paths: list[Path],
    processor: Callable[[str], str]
) -> dict[Path, str]
```

### JSONProcessor Class

#### Constructor

```python
def __init__(self) -> None
```

#### Methods

```python
def fast_json_parse(self, json_str: str) -> dict[str, Any]

def fast_json_serialize(self, data: dict[str, Any]) -> str

def validate_json_structure(
    self,
    data: dict[str, Any],
    required_keys: list[str]
) -> bool
```

### MemoryProfiler Class

#### Constructor

```python
def __init__(self) -> None
```

#### Methods

```python
def take_snapshot(self, label: str) -> None

def get_memory_summary(self) -> dict[str, Any]
```

### PerformanceUtils Class

#### Static Methods

```python
@staticmethod
def measure_execution_time(func: Callable[[], T]) -> tuple[T, float]

@staticmethod
async def measure_async_execution_time(
    func: Callable[[], Awaitable[T]]
) -> tuple[T, float]

@staticmethod
def optimize_list_operations(items: list[Any]) -> list[Any]

@staticmethod
def fast_dict_merge(dicts: list[dict[str, Any]]) -> dict[str, Any]
```

## Type Definitions

### Type Variables

```python
T = TypeVar("T")
```

### Import Requirements

```python
import asyncio
import json
import logging
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar, cast
from weakref import WeakValueDictionary

from ..settings import DEFAULT_TIMEOUT
```

## Return Type Patterns

### Common Return Types

```python
# Synchronous operations
-> None                          # Initialization, configuration
-> str                          # String processing, file content
-> bool                         # Validation, checks
-> float                        # Timing, measurements
-> dict[str, Any]              # Statistics, summaries
-> list[str]                   # String collections
-> list[Any]                   # Generic collections
-> tuple[T, float]             # Result with timing

# Asynchronous operations
-> Awaitable[T]                # Generic async result
-> Awaitable[str]              # Async string operations
-> Awaitable[None]             # Async void operations
-> Awaitable[list[T]]          # Async collections

# Optional types
-> Any | None                  # Cache operations
-> Optional[T]                 # Nullable results
```

### Parameter Patterns

```python
# Required parameters
operation_name: str
file_path: Path
json_str: str
data: dict[str, Any]

# Optional parameters with defaults
timeout: float = DEFAULT_TIMEOUT
max_concurrent: int = 10
max_retries: int = 3
delay: float = 1.0
success: bool = True
error_message: str = ""

# Callable parameters
operation: Callable[[], Awaitable[T]]
task: Callable[[], Awaitable[T]]
processor: Callable[[str], str]
func: Callable[[], T]

# Collection parameters
strings: list[str]
patterns: list[str]
tasks: list[Callable[[], Awaitable[T]]]
file_paths: list[Path]
required_keys: list[str]
items: list[Any]
dicts: list[dict[str, Any]]

# Keyword arguments
**kwargs: Any
```

## Usage Pattern Examples

### Basic Performance Monitoring

```python
monitor = AsyncPerformanceMonitor()

async def my_operation():
    await asyncio.sleep(1)
    return "result"

result = await monitor.monitor_operation(
    "my_operation",
    my_operation,
    timeout=5.0
)

summary = monitor.get_performance_summary()
```

### Async Task Management

```python
task_manager = AsyncTaskManager()

tasks = [
    lambda: fetch_data(1),
    lambda: fetch_data(2),
    lambda: fetch_data(3)
]

results = await task_manager.execute_parallel_tasks(
    tasks,
    max_concurrent=2
)

# With retry
result = await task_manager.execute_with_retry(
    unreliable_task,
    max_retries=3,
    delay=1.0
)
```

### String Processing

```python
# Concatenation
strings = ["Hello", " ", "World"]
result = StringProcessor.fast_string_concatenation(strings)

# Formatting
template = "Hello {name}"
formatted = StringProcessor.efficient_string_formatting(
    template,
    name="John"
)

# Search
text = "The quick brown fox"
patterns = ["quick", "fox"]
found = StringProcessor.fast_string_search(text, patterns)
```

### File Operations

```python
processor = FileProcessor()

# Async operations
content = await processor.read_file_async(Path("file.txt"))
await processor.write_file_async(Path("output.txt"), "content")

# Batch processing
def uppercase(content: str) -> str:
    return content.upper()

files = [Path("file1.txt"), Path("file2.txt")]
results = processor.process_files_batch(files, uppercase)
```

### JSON Processing

```python
json_processor = JSONProcessor()

# Parse and serialize
data = json_processor.fast_json_parse('{"key": "value"}')
json_str = json_processor.fast_json_serialize(data)

# Validate structure
is_valid = json_processor.validate_json_structure(
    data,
    ["key"]
)
```

### Memory Profiling

```python
profiler = MemoryProfiler()

profiler.take_snapshot("start")
# ... operations ...
profiler.take_snapshot("end")

summary = profiler.get_memory_summary()
```

### Performance Utilities

```python
# Measure sync function
def slow_function():
    time.sleep(1)
    return "done"

result, duration = PerformanceUtils.measure_execution_time(slow_function)

# Measure async function
async def async_function():
    await asyncio.sleep(1)
    return "done"

result, duration = await PerformanceUtils.measure_async_execution_time(async_function)

# Optimize collections
items = [1, None, 2, None, 3]
optimized = PerformanceUtils.optimize_list_operations(items)

# Merge dictionaries
dicts = [{"a": 1}, {"b": 2}]
merged = PerformanceUtils.fast_dict_merge(dicts)
```

### Caching

```python
cache = AgentCache()

# Store and retrieve
cache.set("key", "value")
value = cache.get("key")

# Get statistics
stats = cache.get_cache_stats()
```

## Error Handling Patterns

```python
# AsyncPerformanceMonitor
try:
    result = await monitor.monitor_operation("op", operation, timeout=5.0)
except asyncio.TimeoutError:
    print("Operation timed out")
except Exception as e:
    print(f"Operation failed: {e}")

# AsyncTaskManager
try:
    result = await task_manager.execute_with_retry(task, max_retries=3)
except Exception as e:
    print(f"All retries failed: {e}")

# FileProcessor
try:
    content = await processor.read_file_async(path)
except Exception as e:
    print(f"File read failed: {e}")

# JSONProcessor
try:
    data = json_processor.fast_json_parse(json_str)
except json.JSONDecodeError as e:
    print(f"JSON parsing failed: {e}")
```

## Integration Patterns

### With LibriScribe2 Components

```python
# Agent execution with performance monitoring
from libriscribe2.agents import ConceptGeneratorAgent
from libriscribe2.utils.performance_improvements import AsyncPerformanceMonitor

monitor = AsyncPerformanceMonitor()
agent = ConceptGeneratorAgent()

async def generate_concept():
    return await agent.generate_concept(prompt="Create a story concept")

result = await monitor.monitor_operation(
    "concept_generation",
    generate_concept,
    timeout=30.0
)

# File processing with caching
from libriscribe2.utils.performance_improvements import AgentCache, FileProcessor

cache = AgentCache()
processor = FileProcessor()

async def cached_file_read(path: Path) -> str:
    cached = cache.get(str(path))
    if cached:
        return cached

    content = await processor.read_file_async(path)
    cache.set(str(path), content)
    return content
```
