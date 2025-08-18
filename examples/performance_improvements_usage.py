#!/usr/bin/env python3
"""
Performance Improvements Usage Example

This example demonstrates the Python 3.12 performance improvements available
in LibriScribe2, including async operations, memory management, string processing,
and performance monitoring.

Features Demonstrated:
1. Async performance monitoring with timing and error tracking
2. Parallel task execution with concurrency control
3. Memory profiling and optimization
4. String processing optimizations
5. File I/O performance improvements
6. JSON processing enhancements
7. Caching with weak references
8. Performance measurement utilities
"""

import asyncio
import logging
import random
import time
from pathlib import Path
from typing import Any

# Import performance improvement components
from src.libriscribe2.utils.performance_improvements import (
    AgentCache,
    AsyncPerformanceMonitor,
    AsyncTaskManager,
    FileProcessor,
    JSONProcessor,
    MemoryProfiler,
    PerformanceUtils,
    StringProcessor,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def demonstrate_async_performance_monitoring():
    """
    Demonstrate async performance monitoring capabilities
    """

    print("🚀 Async Performance Monitoring Demonstration")
    print("=" * 50)

    monitor = AsyncPerformanceMonitor()

    # Define some sample async operations
    async def fast_operation():
        """Fast operation that completes quickly"""
        await asyncio.sleep(0.1)
        return "fast_result"

    async def slow_operation():
        """Slower operation for comparison"""
        await asyncio.sleep(0.5)
        return "slow_result"

    async def failing_operation():
        """Operation that fails for error handling demo"""
        await asyncio.sleep(0.2)
        raise ValueError("Simulated failure")

    async def timeout_operation():
        """Operation that times out"""
        await asyncio.sleep(2.0)
        return "timeout_result"

    print("📊 Running monitored operations...")

    # Monitor successful operations
    try:
        result1 = await monitor.monitor_operation("fast_op", fast_operation, timeout=1.0)
        print(f"✅ Fast operation result: {result1}")
    except Exception as e:
        print(f"❌ Fast operation failed: {e}")

    try:
        result2 = await monitor.monitor_operation("slow_op", slow_operation, timeout=1.0)
        print(f"✅ Slow operation result: {result2}")
    except Exception as e:
        print(f"❌ Slow operation failed: {e}")

    # Monitor failing operation
    try:
        result3 = await monitor.monitor_operation("failing_op", failing_operation, timeout=1.0)
        print(f"✅ Failing operation result: {result3}")
    except Exception as e:
        print(f"❌ Failing operation failed: {e}")

    # Monitor timeout operation
    try:
        result4 = await monitor.monitor_operation("timeout_op", timeout_operation, timeout=0.5)
        print(f"✅ Timeout operation result: {result4}")
    except Exception as e:
        print(f"❌ Timeout operation failed: {e}")

    # Get performance summary
    summary = monitor.get_performance_summary()
    print("\n📈 Performance Summary:")
    print(f"   Total operations: {summary['total_operations']}")
    print(f"   Successful operations: {summary['successful_operations']}")
    print(f"   Failed operations: {summary['failed_operations']}")
    print(f"   Success rate: {summary['success_rate']:.2%}")
    print(f"   Average duration: {summary['average_duration']:.3f}s")
    print(f"   Total duration: {summary['total_duration']:.3f}s")
    if summary["slowest_operation"]:
        print(f"   Slowest operation: {summary['slowest_operation']}")


async def demonstrate_parallel_task_execution():
    """
    Demonstrate parallel task execution with concurrency control
    """

    print("\n🔄 Parallel Task Execution Demonstration")
    print("=" * 50)

    task_manager = AsyncTaskManager()

    # Define sample tasks
    async def process_item(item_id: int) -> str:
        """Simulate processing an item"""
        processing_time = random.uniform(0.1, 0.3)
        await asyncio.sleep(processing_time)

        # Simulate occasional failures
        if random.random() < 0.1:  # 10% failure rate
            raise Exception(f"Processing failed for item {item_id}")

        return f"processed_item_{item_id}"

    # Create tasks
    tasks = [lambda i=i: process_item(i) for i in range(20)]

    print(f"📋 Executing {len(tasks)} tasks with max concurrency of 5...")

    start_time = time.time()
    results = await task_manager.execute_parallel_tasks(tasks, max_concurrent=5)
    end_time = time.time()

    print(f"✅ Completed {len(results)} tasks successfully in {end_time - start_time:.2f}s")
    print(f"   Success rate: {len(results) / len(tasks):.2%}")

    # Demonstrate retry mechanism
    print("\n🔄 Demonstrating retry mechanism...")

    async def unreliable_task():
        """Task that fails 70% of the time"""
        if random.random() < 0.7:
            raise ConnectionError("Network connection failed")
        return "success"

    try:
        result = await task_manager.execute_with_retry(unreliable_task, max_retries=5, delay=0.1)
        print(f"✅ Retry task succeeded: {result}")
    except Exception as e:
        print(f"❌ Retry task failed after all attempts: {e}")


def demonstrate_memory_profiling():
    """
    Demonstrate memory profiling capabilities
    """

    print("\n🧠 Memory Profiling Demonstration")
    print("=" * 50)

    profiler = MemoryProfiler()

    # Take initial snapshot
    profiler.take_snapshot("initial")

    # Simulate memory-intensive operations
    print("📊 Performing memory-intensive operations...")

    # Create large data structures
    large_list = list(range(100000))
    profiler.take_snapshot("after_large_list")

    large_dict = {f"key_{i}": f"value_{i}" * 10 for i in range(10000)}
    profiler.take_snapshot("after_large_dict")

    # Create nested structures
    nested_data = [[i] * 100 for i in range(1000)]
    profiler.take_snapshot("after_nested_data")

    # Clean up some data
    del large_list
    profiler.take_snapshot("after_cleanup")

    # Get memory summary
    summary = profiler.get_memory_summary()
    print("\n📈 Memory Usage Summary:")
    print(f"   Total snapshots: {summary['total_snapshots']}")
    print(f"   Initial memory: {summary['initial_memory']:,} bytes")
    print(f"   Final memory: {summary['final_memory']:,} bytes")
    print(f"   Memory change: {summary['memory_change']:,} bytes")
    print(f"   Peak memory: {summary['peak_memory']:,} bytes")
    print(f"   Average memory: {summary['average_memory']:,.0f} bytes")


def demonstrate_string_processing():
    """
    Demonstrate string processing optimizations
    """

    print("\n📝 String Processing Demonstration")
    print("=" * 50)

    # String concatenation
    print("🔗 String concatenation performance...")
    strings = [f"Part {i}" for i in range(1000)]

    result, duration = PerformanceUtils.measure_execution_time(
        lambda: StringProcessor.fast_string_concatenation(strings)
    )

    print(f"   Concatenated {len(strings)} strings in {duration:.4f}s")
    print(f"   Result length: {len(result)} characters")

    # String formatting
    print("\n📋 String formatting performance...")
    template = "Hello {name}, you have {count} messages from {sender}"

    def format_strings():
        results = []
        for i in range(1000):
            formatted = StringProcessor.efficient_string_formatting(
                template, name=f"User{i}", count=random.randint(1, 10), sender=f"Sender{i}"
            )
            results.append(formatted)
        return results

    results, duration = PerformanceUtils.measure_execution_time(format_strings)
    print(f"   Formatted {len(results)} strings in {duration:.4f}s")

    # String search
    print("\n🔍 String search performance...")
    text = "The quick brown fox jumps over the lazy dog. " * 1000
    patterns = ["quick", "fox", "lazy", "cat", "elephant", "jumps"]

    found_patterns, duration = PerformanceUtils.measure_execution_time(
        lambda: StringProcessor.fast_string_search(text, patterns)
    )

    print(f"   Searched for {len(patterns)} patterns in {duration:.4f}s")
    print(f"   Found patterns: {found_patterns}")


async def demonstrate_file_processing():
    """
    Demonstrate file processing improvements
    """

    print("\n📁 File Processing Demonstration")
    print("=" * 50)

    processor = FileProcessor()

    # Create demo directory
    demo_dir = Path(".demo/file_processing")
    demo_dir.mkdir(parents=True, exist_ok=True)

    # Create sample files
    sample_files = []
    for i in range(5):
        file_path = demo_dir / f"sample_{i}.txt"
        content = f"This is sample file {i}\n" + "Sample content line\n" * 100

        # Write file asynchronously
        await processor.write_file_async(file_path, content)
        sample_files.append(file_path)

    print(f"✅ Created {len(sample_files)} sample files")

    # Read files asynchronously
    print("📖 Reading files asynchronously...")

    async def read_all_files():
        contents = []
        for file_path in sample_files:
            content = await processor.read_file_async(file_path)
            contents.append(content)
        return contents

    contents, duration = await PerformanceUtils.measure_async_execution_time(read_all_files)
    print(f"   Read {len(contents)} files in {duration:.4f}s")

    # Batch processing
    print("🔄 Batch processing files...")

    def uppercase_processor(content: str) -> str:
        return content.upper()

    results, duration = PerformanceUtils.measure_execution_time(
        lambda: processor.process_files_batch(sample_files, uppercase_processor)
    )

    print(f"   Processed {len(results)} files in {duration:.4f}s")

    # Show processing results
    for file_path, result in list(results.items())[:2]:  # Show first 2
        if not result.startswith("Error:"):
            print(f"   {file_path.name}: {len(result)} characters processed")


def demonstrate_json_processing():
    """
    Demonstrate JSON processing improvements
    """

    print("\n📋 JSON Processing Demonstration")
    print("=" * 50)

    processor = JSONProcessor()

    # Create sample JSON data
    sample_data = {
        "users": [{"id": i, "name": f"User {i}", "email": f"user{i}@example.com"} for i in range(1000)],
        "metadata": {"version": "1.0", "created": "2024-01-01", "total_users": 1000},
    }

    # JSON serialization performance
    print("📤 JSON serialization performance...")

    json_str, duration = PerformanceUtils.measure_execution_time(lambda: processor.fast_json_serialize(sample_data))

    print(f"   Serialized JSON in {duration:.4f}s")
    print(f"   JSON size: {len(json_str):,} characters")

    # JSON parsing performance
    print("📥 JSON parsing performance...")

    parsed_data, duration = PerformanceUtils.measure_execution_time(lambda: processor.fast_json_parse(json_str))

    print(f"   Parsed JSON in {duration:.4f}s")
    print(f"   Parsed {len(parsed_data['users'])} user records")

    # JSON validation
    print("✅ JSON structure validation...")

    required_keys = ["users", "metadata"]
    is_valid = processor.validate_json_structure(parsed_data, required_keys)

    print(f"   Structure validation: {'✅ Valid' if is_valid else '❌ Invalid'}")

    # Test with invalid structure
    invalid_data = {"users": [], "missing_metadata": True}
    is_invalid = processor.validate_json_structure(invalid_data, required_keys)
    print(
        f"   Invalid structure test: {'❌ Correctly identified as invalid' if not is_invalid else '⚠️ False positive'}"
    )


def demonstrate_caching():
    """
    Demonstrate caching with weak references
    """

    print("\n💾 Caching Demonstration")
    print("=" * 50)

    cache = AgentCache()

    # Store various types of data
    print("📝 Storing data in cache...")

    cache.set("user_data", {"name": "John", "age": 30})
    cache.set("config", {"theme": "dark", "language": "en"})
    cache.set("large_data", list(range(10000)))

    # Access data multiple times
    for _ in range(5):
        user_data = cache.get("user_data")
        config = cache.get("config")

    for _ in range(3):
        large_data = cache.get("large_data")

    # Try to access non-existent data
    missing_data = cache.get("non_existent")

    # Get cache statistics
    stats = cache.get_cache_stats()
    print("📊 Cache Statistics:")
    print(f"   Cache size: {stats['cache_size']}")
    print(f"   Access counts: {stats['access_counts']}")
    print(f"   Most accessed: {stats['most_accessed']}")
    print(f"   Missing data result: {'None' if missing_data is None else 'Found'}")


def demonstrate_performance_utilities():
    """
    Demonstrate performance utility functions
    """

    print("\n⚡ Performance Utilities Demonstration")
    print("=" * 50)

    # Measure synchronous function
    print("⏱️ Measuring synchronous function performance...")

    def cpu_intensive_task():
        """Simulate CPU-intensive work"""
        result = 0
        for i in range(1000000):
            result += i**0.5
        return result

    result, duration = PerformanceUtils.measure_execution_time(cpu_intensive_task)
    print(f"   CPU task completed in {duration:.4f}s, result: {result:.0f}")

    # List optimization
    print("📋 List optimization...")

    messy_list = [1, None, 2, None, 3, None, 4, 5, None]
    optimized_list, duration = PerformanceUtils.measure_execution_time(
        lambda: PerformanceUtils.optimize_list_operations(messy_list)
    )

    print(f"   Optimized list in {duration:.6f}s")
    print(f"   Original: {messy_list}")
    print(f"   Optimized: {optimized_list}")

    # Dictionary merging
    print("🔗 Dictionary merging...")

    dicts_to_merge = [{"a": 1, "b": 2}, {"c": 3, "d": 4}, {"e": 5, "f": 6}, {"g": 7, "h": 8}]

    merged_dict, duration = PerformanceUtils.measure_execution_time(
        lambda: PerformanceUtils.fast_dict_merge(dicts_to_merge)
    )

    print(f"   Merged {len(dicts_to_merge)} dictionaries in {duration:.6f}s")
    print(f"   Result: {merged_dict}")


async def demonstrate_comprehensive_workflow():
    """
    Demonstrate a comprehensive workflow using multiple performance components
    """

    print("\n🔧 Comprehensive Workflow Demonstration")
    print("=" * 50)

    # Initialize all components
    monitor = AsyncPerformanceMonitor()
    task_manager = AsyncTaskManager()
    profiler = MemoryProfiler()
    cache = AgentCache()
    file_processor = FileProcessor()
    json_processor = JSONProcessor()

    profiler.take_snapshot("workflow_start")

    # Define a complex workflow
    async def process_data_workflow(data_id: int) -> dict[str, Any]:
        """Complex workflow that processes data through multiple stages"""

        # Stage 1: Generate data
        await asyncio.sleep(0.1)
        raw_data = {"id": data_id, "values": [random.randint(1, 100) for _ in range(100)]}

        # Stage 2: Process data
        processed_data = {
            "id": raw_data["id"],
            "sum": sum(raw_data["values"]),
            "avg": sum(raw_data["values"]) / len(raw_data["values"]),
            "max": max(raw_data["values"]),
            "min": min(raw_data["values"]),
        }

        # Stage 3: Cache result
        cache_key = f"processed_{data_id}"
        cache.set(cache_key, processed_data)

        return processed_data

    print("🚀 Executing comprehensive workflow...")

    # Execute workflow with monitoring
    workflow_tasks = [
        lambda i=i: monitor.monitor_operation(f"workflow_{i}", lambda: process_data_workflow(i), timeout=5.0)
        for i in range(10)
    ]

    results = await task_manager.execute_parallel_tasks(workflow_tasks, max_concurrent=3)

    profiler.take_snapshot("workflow_complete")

    # Generate comprehensive report
    print("\n📊 Comprehensive Workflow Results:")
    print(f"   Processed items: {len(results)}")

    # Performance summary
    perf_summary = monitor.get_performance_summary()
    print(f"   Success rate: {perf_summary['success_rate']:.2%}")
    print(f"   Average duration: {perf_summary['average_duration']:.3f}s")

    # Memory summary
    memory_summary = profiler.get_memory_summary()
    print(f"   Memory change: {memory_summary['memory_change']:,} bytes")

    # Cache statistics
    cache_stats = cache.get_cache_stats()
    print(f"   Cache size: {cache_stats['cache_size']}")

    # Save results to file
    demo_dir = Path(".demo/workflow_results")
    demo_dir.mkdir(parents=True, exist_ok=True)

    report_data = {
        "performance": perf_summary,
        "memory": memory_summary,
        "cache": cache_stats,
        "results": results[:5],  # First 5 results
    }

    report_json = json_processor.fast_json_serialize(report_data)
    await file_processor.write_file_async(demo_dir / "workflow_report.json", report_json)

    print(f"   Report saved to: {demo_dir / 'workflow_report.json'}")


async def main():
    """
    Main demonstration function
    """

    print("🚀 LibriScribe2 Performance Improvements Demonstration")
    print("=" * 60)

    # Create demo directory
    Path(".demo").mkdir(exist_ok=True)

    try:
        # Run all demonstrations
        await demonstrate_async_performance_monitoring()
        await demonstrate_parallel_task_execution()
        demonstrate_memory_profiling()
        demonstrate_string_processing()
        await demonstrate_file_processing()
        demonstrate_json_processing()
        demonstrate_caching()
        demonstrate_performance_utilities()
        await demonstrate_comprehensive_workflow()

        print("\n🎉 Performance Improvements Demonstration Complete!")
        print("📁 Demo files saved to: .demo/")

        print("\n💡 Key Performance Benefits:")
        print("   ✅ Python 3.12 optimizations for better performance")
        print("   ✅ Async operations with proper concurrency control")
        print("   ✅ Memory-efficient caching with weak references")
        print("   ✅ Comprehensive performance monitoring and profiling")
        print("   ✅ Optimized string, file, and JSON operations")
        print("   ✅ Parallel task execution with retry mechanisms")

    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
