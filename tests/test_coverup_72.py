# file: objwatch/wrappers/cpu_memory_wrapper.py:74-84
# asked: {"lines": [74, 84], "branches": []}
# gained: {"lines": [74, 84], "branches": []}

import pytest
from objwatch.wrappers.cpu_memory_wrapper import CPUMemoryWrapper


class TestCPUMemoryWrapper:
    """Test cases for CPUMemoryWrapper._format_memory method."""

    def test_format_memory_empty_dict(self):
        """Test _format_memory with empty dictionary."""
        wrapper = CPUMemoryWrapper()
        result = wrapper._format_memory({})
        assert result == ""

    def test_format_memory_single_item(self):
        """Test _format_memory with single key-value pair."""
        wrapper = CPUMemoryWrapper()
        stats = {"total": 8589934592}
        result = wrapper._format_memory(stats)
        assert result == "total: 8589934592"

    def test_format_memory_multiple_items(self):
        """Test _format_memory with multiple key-value pairs."""
        wrapper = CPUMemoryWrapper()
        stats = {"total": 8589934592, "available": 4294967296, "percent": 50.0}
        result = wrapper._format_memory(stats)
        expected_parts = ["total: 8589934592", "available: 4294967296", "percent: 50.0"]
        assert all(part in result for part in expected_parts)
        assert result.count(" | ") == 2
