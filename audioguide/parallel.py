"""
AudioGuide Parallel Processing Module

Provides parallel processing utilities for multi-core descriptor calculation.
"""

import os
import concurrent.futures
from typing import Callable, List, Any, Optional, Iterable
from functools import partial
import multiprocessing


def get_default_workers() -> int:
    """Get default number of workers based on CPU count."""
    cpu_count = os.cpu_count() or 4
    # Leave one core free for system
    return max(1, cpu_count - 1)


def parallel_map(func: Callable, items: List[Any], 
                 workers: Optional[int] = None,
                 use_processes: bool = False,
                 progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Any]:
    """
    Apply function to items in parallel.
    
    Args:
        func: Function to apply to each item
        items: List of items to process
        workers: Number of workers (None = auto)
        use_processes: Use processes instead of threads
        progress_callback: Called with (completed, total)
        
    Returns:
        List of results in same order as input
    """
    if workers is None:
        workers = get_default_workers()
    
    if len(items) <= 1 or workers <= 1:
        # No parallelization needed
        results = []
        for item in items:
            results.append(func(item))
            if progress_callback:
                progress_callback(len(results), len(items))
        return results
    
    # Choose executor type
    executor_class = concurrent.futures.ProcessPoolExecutor if use_processes else concurrent.futures.ThreadPoolExecutor
    
    results = [None] * len(items)
    completed = 0
    
    def process_item(idx_and_item):
        idx, item = idx_and_item
        result = func(item)
        return idx, result
    
    with executor_class(max_workers=workers) as executor:
        # Submit all tasks
        futures = {executor.submit(process_item, (i, item)): i for i, item in enumerate(items)}
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            idx, result = future.result()
            results[idx] = result
            completed += 1
            if progress_callback:
                progress_callback(completed, len(items))
    
    return results


def parallel_map_unordered(func: Callable, items: List[Any],
                           workers: Optional[int] = None,
                           use_processes: bool = False) -> List[Any]:
    """
    Apply function to items in parallel (results in completion order).
    
    Faster than parallel_map when order doesn't matter.
    """
    if workers is None:
        workers = get_default_workers()
    
    if len(items) <= 1 or workers <= 1:
        return [func(item) for item in items]
    
    executor_class = concurrent.futures.ProcessPoolExecutor if use_processes else concurrent.futures.ThreadPoolExecutor
    
    results = []
    with executor_class(max_workers=workers) as executor:
        futures = [executor.submit(func, item) for item in items]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    return results


class ThreadPool:
    """Thread pool for parallel task execution."""
    
    def __init__(self, workers: Optional[int] = None):
        self.workers = workers or get_default_workers()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.workers)
        self._futures = []
    
    def submit(self, func: Callable, *args, **kwargs):
        """Submit a task to the pool."""
        future = self.executor.submit(func, *args, **kwargs)
        self._futures.append(future)
        return future
    
    def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """Map func over items."""
        return list(self.executor.map(func, items))
    
    def wait_all(self) -> List[Any]:
        """Wait for all tasks and return results."""
        results = []
        for future in concurrent.futures.as_completed(self._futures):
            results.append(future.result())
        return results
    
    def shutdown(self, wait: bool = True):
        """Shutdown the pool."""
        self.executor.shutdown(wait=wait)


class ProcessPool:
    """Process pool for parallel task execution (bypasses GIL)."""
    
    def __init__(self, workers: Optional[int] = None):
        self.workers = workers or get_default_workers()
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=self.workers)
        self._futures = []
    
    def submit(self, func: Callable, *args, **kwargs):
        """Submit a task to the pool."""
        future = self.executor.submit(func, *args, **kwargs)
        self._futures.append(future)
        return future
    
    def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """Map func over items."""
        return list(self.executor.map(func, items))
    
    def wait_all(self) -> List[Any]:
        """Wait for all tasks and return results."""
        results = []
        for future in concurrent.futures.as_completed(self._futures):
            results.append(future.result())
        return results
    
    def shutdown(self, wait: bool = True):
        """Shutdown the pool."""
        self.executor.shutdown(wait=wait)


def analyze_files_parallel(analyze_func: Callable, 
                          file_paths: List[str],
                          workers: Optional[int] = None,
                          progress_callback: Optional[Callable[[int, int], None]] = None,
                          error_handler: Optional[Callable[[str, Exception], None]] = None) -> List[Any]:
    """
    Analyze multiple files in parallel.
    
    Args:
        analyze_func: Function that takes a file path and returns analysis result
        file_paths: List of file paths to analyze
        workers: Number of parallel workers
        progress_callback: Called with (completed, total)
        error_handler: Called with (file_path, exception) on error
        
    Returns:
        List of results (None for failed files)
    """
    results = [None] * len(file_paths)
    completed = 0
    errors = 0
    
    def safe_analyze(idx_and_path):
        nonlocal errors
        idx, path = idx_and_path
        try:
            return idx, analyze_func(path), None
        except Exception as e:
            errors += 1
            return idx, None, (path, e)
    
    if workers is None:
        workers = get_default_workers()
    
    # Use threads for I/O-bound tasks
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(safe_analyze, (i, p)): i for i, p in enumerate(file_paths)}
        
        for future in concurrent.futures.as_completed(futures):
            idx, result, error = future.result()
            results[idx] = result
            
            if error and error_handler:
                error_handler(*error)
            
            completed += 1
            if progress_callback:
                progress_callback(completed, len(file_paths))
    
    return results
