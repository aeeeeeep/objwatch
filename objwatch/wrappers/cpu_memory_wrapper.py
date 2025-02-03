# MIT License
# Copyright (c) 2025 aeeeeeep

import psutil
from types import FrameType
from typing import Any, Dict, List, Tuple
from .abc_wrapper import ABCWrapper


class CPUMemoryWrapper(ABCWrapper):
    """
    CPUMemoryWrapper extends ABCWrapper to log memory statistics for the system's CPU memory usage.

    This class gathers memory statistics about the system's memory usage using the `psutil.virtual_memory()` method.
    The following statistics are tracked, expressed in bytes:

    Main metrics:
      - total: total physical memory (exclusive swap).
      - available: the memory that can be given instantly to processes without the system going into swap.
        This is calculated by summing different memory metrics that vary depending on the platform.
        It is supposed to be used to monitor actual memory usage in a cross platform fashion.
      - percent: the percentage usage calculated as (total - available) / total * 100.

    Other metrics:
      - used: memory used, calculated differently depending on the platform and designed for informational
        purposes only. total - free does not necessarily match used.
      - free: memory not being used at all (zeroed) that is readily available; note that this doesn’t reflect
        the actual memory available (use available instead). total - used does not necessarily match free.
      - active (UNIX): memory currently in use or very recently used, and so it is in RAM.
      - inactive (UNIX): memory that is marked as not used.
      - buffers (Linux, BSD): cache for things like file system metadata.
      - cached (Linux, BSD): cache for various things.
      - shared (Linux, BSD): memory that may be simultaneously accessed by multiple processes.
      - slab (Linux): in-kernel data structures cache.
      - wired (BSD, macOS): memory that is marked to always stay in RAM. It is never moved to disk.

    If you want to capture specific CPU memory metrics, you can configure the `mem_types`
    variable before starting the tracking. For example, to capture the total memory,
    available memory, and memory usage percentage, you can add the following code before instantiation of
    objwatch wrappers:

      ```python
      from objwatch.wrappers import CPUMemoryWrapper
      CPUMemoryWrapper.mem_types = ["total", "available", "percent"]
      ```
    """

    mem_types: List[str] = ["total", "available", "percent"]

    def __init__(self):
        """
        Initialize the CPUMemoryWrapper with optional memory types to capture stats.

        Args:
            mem_types (List[str]): A list of memory types to capture.
        """
        self.mem_types = set(__class__.mem_types)

    def _capture_memory(self) -> Dict[str, Any]:
        """
        Capture the current system memory statistics.

        Returns:
            Dict[str, Any]: A dictionary of memory stats from psutil.
        """
        stats = psutil.virtual_memory()._asdict()
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
