# file: objwatch/wrappers/cpu_memory_wrapper.py:55-62
# asked: {"lines": [55, 62], "branches": []}
# gained: {"lines": [55, 62], "branches": []}

import pytest
from objwatch.wrappers.cpu_memory_wrapper import CPUMemoryWrapper


class TestCPUMemoryWrapper:
    """Test cases for CPUMemoryWrapper class."""

    def test_init_with_custom_class_mem_types(self):
        """Test that CPUMemoryWrapper uses class-level mem_types attribute."""
        # Save original class mem_types
        original_mem_types = CPUMemoryWrapper.mem_types.copy()

        try:
            # Set custom mem_types at class level
            CPUMemoryWrapper.mem_types = ['total', 'used', 'free']

            # Create wrapper instance
            wrapper = CPUMemoryWrapper()

            # Verify instance uses class-level mem_types
            assert wrapper.mem_types == {'total', 'used', 'free'}
        finally:
            # Restore original class mem_types
            CPUMemoryWrapper.mem_types = original_mem_types

    def test_init_with_empty_class_mem_types(self):
        """Test that CPUMemoryWrapper handles empty class mem_types."""
        # Save original class mem_types
        original_mem_types = CPUMemoryWrapper.mem_types.copy()

        try:
            # Set empty mem_types at class level
            CPUMemoryWrapper.mem_types = []

            # Create wrapper instance
            wrapper = CPUMemoryWrapper()

            # Verify instance uses empty set
            assert wrapper.mem_types == set()
        finally:
            # Restore original class mem_types
            CPUMemoryWrapper.mem_types = original_mem_types
