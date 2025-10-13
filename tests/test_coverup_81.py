# file: objwatch/wrappers/cpu_memory_wrapper.py:86-97
# asked: {"lines": [86, 97], "branches": []}
# gained: {"lines": [86, 97], "branches": []}

import pytest
from types import FrameType
from unittest.mock import Mock, patch
from objwatch.wrappers.cpu_memory_wrapper import CPUMemoryWrapper


class TestCPUMemoryWrapper:
    """Test cases for CPUMemoryWrapper class."""

    def test_wrap_call_executes_all_lines(self):
        """Test that wrap_call method executes all lines including the return statement."""
        # Create a CPUMemoryWrapper instance
        wrapper = CPUMemoryWrapper()

        # Mock a frame object
        mock_frame = Mock(spec=FrameType)

        # Test with a sample function name
        func_name = "test_function"

        # Mock the internal methods to verify they are called
        with patch.object(wrapper, '_capture_memory') as mock_capture, patch.object(
            wrapper, '_format_memory'
        ) as mock_format:

            # Set up the mock return values
            mock_capture.return_value = {'total': 8589934592, 'available': 4294967296, 'percent': 50.0}
            mock_format.return_value = "total: 8589934592 | available: 4294967296 | percent: 50.0"

            # Call the method under test
            result = wrapper.wrap_call(func_name, mock_frame)

            # Verify the internal methods were called correctly
            mock_capture.assert_called_once()
            mock_format.assert_called_once_with({'total': 8589934592, 'available': 4294967296, 'percent': 50.0})

            # Verify the result
            assert result == "total: 8589934592 | available: 4294967296 | percent: 50.0"

    def test_wrap_call_with_different_mem_types(self):
        """Test wrap_call with different memory type configurations."""
        # Create a CPUMemoryWrapper instance with custom memory types
        wrapper = CPUMemoryWrapper()
        wrapper.mem_types = {'used', 'free'}  # Use different memory types

        # Mock a frame object
        mock_frame = Mock(spec=FrameType)

        # Test with a sample function name
        func_name = "another_function"

        # Mock the internal methods
        with patch.object(wrapper, '_capture_memory') as mock_capture, patch.object(
            wrapper, '_format_memory'
        ) as mock_format:

            # Set up the mock return values for different memory types
            mock_capture.return_value = {'used': 4294967296, 'free': 4294967296}
            mock_format.return_value = "used: 4294967296 | free: 4294967296"

            # Call the method under test
            result = wrapper.wrap_call(func_name, mock_frame)

            # Verify the internal methods were called correctly
            mock_capture.assert_called_once()
            mock_format.assert_called_once_with({'used': 4294967296, 'free': 4294967296})

            # Verify the result
            assert result == "used: 4294967296 | free: 4294967296"
