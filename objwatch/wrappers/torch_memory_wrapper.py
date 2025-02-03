# MIT License
# Copyright (c) 2025 aeeeeeep

import torch
from types import FrameType
from typing import Any, Dict, List, Tuple
from .abc_wrapper import ABCWrapper


class TorchMemoryWrapper(ABCWrapper):
    """
    TorchMemoryWrapper extends ABCWrapper to log memory statistics from GPU.

    This class is designed to gather memory statistics for the GPU memory allocator
    and track various memory metrics associated with memory allocation, reservation,
    and freeing. It utilizes the `memory_stats` function to fetch these statistics
    and organizes them for further use.

    If you want to capture specific GPU memory metrics, you can configure the `mem_types`
    variable before starting the tracking. For example, to capture the current and peak
    allocated memory across all pools, you can add the following code before instantiation of
    objwatch wrappers:

      ```python
      from objwatch.wrappers import TorchMemoryWrapper
      TorchMemoryWrapper.mem_types = ["allocation.all.current", "allocation.all.peak"]
      ```

    `mem_types` define which statistics should be captured. The
    available statistics are:

    - ``"allocation.{all,large_pool,small_pool}.{current,peak,allocated,freed}"``:
      number of allocation requests received by the memory allocator.
    - ``"allocated_bytes.{all,large_pool,small_pool}.{current,peak,allocated,freed}"``:
      amount of allocated memory.
    - ``"segment.{all,large_pool,small_pool}.{current,peak,allocated,freed}"``:
      number of reserved segments from ``cudaMalloc()``.
    - ``"reserved_bytes.{all,large_pool,small_pool}.{current,peak,allocated,freed}"``:
      amount of reserved memory.
    - ``"active.{all,large_pool,small_pool}.{current,peak,allocated,freed}"``:
      number of active memory blocks.
    - ``"active_bytes.{all,large_pool,small_pool}.{current,peak,allocated,freed}"``:
      amount of active memory.
    - ``"inactive_split.{all,large_pool,small_pool}.{current,peak,allocated,freed}"``:
      number of inactive, non-releasable memory blocks.
    - ``"inactive_split_bytes.{all,large_pool,small_pool}.{current,peak,allocated,freed}"``:
      amount of inactive, non-releasable memory.

    For these statistics, values are broken down as follows.

    Pool type:

    - ``all``: combined statistics across all memory pools.
    - ``large_pool``: statistics for the large allocation pool
      (as of October 2019, for size >= 1MB allocations).
    - ``small_pool``: statistics for the small allocation pool
      (as of October 2019, for size < 1MB allocations).

    Metric type:

    - ``current``: current value of this metric.
    - ``peak``: maximum value of this metric.
    - ``allocated``: historical total increase in this metric.
    - ``freed``: historical total decrease in this metric.

    In addition to the core statistics, torch also provide some simple event
    counters:

    - ``"num_alloc_retries"``: number of failed ``cudaMalloc`` calls that
      result in a cache flush and retry.
    - ``"num_ooms"``: number of out-of-memory errors thrown.
    - ``"num_sync_all_streams"``: number of ``synchronize_and_free_events`` calls.
    - ``"num_device_alloc"``: number of GPU allocation calls. This includes both
      cuMemMap and cudaMalloc.
    - ``"num_device_free"``: number of GPU free calls. This includes both cuMemUnmap
      and cudaFree.

    The caching allocator can be configured via ENV to not split blocks larger than a
    defined size (see Memory Management section of the Gpu Semantics documentation).
    This helps avoid memory fragmentation but may have a performance
    penalty. Additional outputs to assist with tuning and evaluating impact:

    - ``"max_split_size"``: blocks above this size will not be split.
    - ``"oversize_allocations.{current,peak,allocated,freed}"``:
      number of over-size allocation requests received by the memory allocator.
    - ``"oversize_segments.{current,peak,allocated,freed}"``:
      number of over-size reserved segments from ``cudaMalloc()``.

    The caching allocator can be configured via ENV to round memory allocations in order
    to reduce fragmentation. Sometimes the overhead from rounding can be higher than
    the fragmentation it helps reduce. The following stat can be used to check if
    rounding adds too much overhead:

    - ``"requested_bytes.{all,large_pool,small_pool}.{current,peak,allocated,freed}"``:
      memory requested by client code, compare this with allocated_bytes to check if
      allocation rounding adds too much overhead.

    For the latest help and more detailed information, please refer to the official
    PyTorch documentation at:
    https://pytorch.org/docs/stable/generated/torch.cuda.memory_stats.html#torch-cuda-memory-stats
    """

    mem_types: List[str] = ["allocation.all.current", "allocation.all.peak"]

    def __init__(self):
        """
        Initialize the TorchMemoryWrapper with optional memory types to capture stats.

        Args:
            mem_types (List[str]): A list of memory types to capture.
        """
        self.mem_types = set(__class__.mem_types)

    def _capture_memory(self) -> Dict[str, Any]:
        """
        Capture the current GPU memory statistics.

        Returns:
            Dict[str, Any]: A dictionary of GPU memory stats.
        """
        stats = torch.cuda.memory_stats()
        return {k: stats[k] for k in self.mem_types}

    def _format_memory(self, stats: Dict[str, Any]) -> str:
        """
        Format the memory statistics into a string.

        Args:
            stats (Dict[str, Any]): The memory stats to format.

        Returns:
            str: A formatted string representing the memory stats.
        """
        return " | ".join(f"{k}: {v}" for k, v in stats.items())

    def wrap_call(self, func_name: str, frame: FrameType) -> str:
        """
        Wrap the function call to log memory stats before the function is executed.

        Args:
            func_name (str): Name of the function being called.
            frame (FrameType): The current stack frame.

        Returns:
            str: A string representing the formatted memory stats.
        """
        return self._format_memory(self._capture_memory())

    def wrap_return(self, func_name: str, result: Any) -> str:
        """
        Wrap the function return to log memory stats after the function is executed.

        Args:
            func_name (str): Name of the function returning.
            result (Any): The result returned by the function.

        Returns:
            str: A string representing the formatted memory stats.
        """
        return self._format_memory(self._capture_memory())

    def wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]:
        """
        Wrap the update of a variable to log memory stats after the update.

        Args:
            old_value (Any): The old value of the variable.
            current_value (Any): The new value of the variable.

        Returns:
            Tuple[str, str]: Formatted old and new values with memory stats.
        """
        return "", self._format_memory(self._capture_memory())
