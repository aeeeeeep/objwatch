# file: objwatch/wrappers/cpu_memory_wrapper.py:99-110
# asked: {"lines": [99, 110], "branches": []}
# gained: {"lines": [99, 110], "branches": []}

import pytest
from unittest.mock import Mock, patch
from objwatch.wrappers.cpu_memory_wrapper import CPUMemoryWrapper


class TestCPUMemoryWrapperWrapReturn:
    """Test cases for CPUMemoryWrapper.wrap_return method."""

    def test_wrap_return_calls_capture_and_format_memory(self, monkeypatch):
        """Test that wrap_return calls _capture_memory and _format_memory correctly."""
        wrapper = CPUMemoryWrapper()

        # Mock the internal methods
        mock_capture = Mock(return_value={'total': 8589934592, 'available': 4294967296, 'percent': 50.0})
        mock_format = Mock(return_value="total: 8589934592 | available: 4294967296 | percent: 50.0")

        monkeypatch.setattr(wrapper, '_capture_memory', mock_capture)
        monkeypatch.setattr(wrapper, '_format_memory', mock_format)

        # Call the method
        func_name = "test_function"
        result = "test_result"
        formatted_output = wrapper.wrap_return(func_name, result)

        # Verify the calls
        mock_capture.assert_called_once()
        mock_format.assert_called_once_with({'total': 8589934592, 'available': 4294967296, 'percent': 50.0})

        # Verify the output
        assert formatted_output == "total: 8589934592 | available: 4294967296 | percent: 50.0"

    def test_wrap_return_with_different_memory_stats(self, monkeypatch):
        """Test wrap_return with different memory statistics."""
        wrapper = CPUMemoryWrapper()

        # Mock with different memory stats
        mock_capture = Mock(return_value={'total': 17179869184, 'available': 8589934592, 'percent': 25.5})
        mock_format = Mock(return_value="total: 17179869184 | available: 8589934592 | percent: 25.5")

        monkeypatch.setattr(wrapper, '_capture_memory', mock_capture)
        monkeypatch.setattr(wrapper, '_format_memory', mock_format)

        # Call the method
        func_name = "another_function"
        result = {"data": [1, 2, 3]}
        formatted_output = wrapper.wrap_return(func_name, result)

        # Verify the calls
        mock_capture.assert_called_once()
        mock_format.assert_called_once_with({'total': 17179869184, 'available': 8589934592, 'percent': 25.5})

        # Verify the output
        assert formatted_output == "total: 17179869184 | available: 8589934592 | percent: 25.5"

    def test_wrap_return_with_custom_mem_types(self, monkeypatch):
        """Test wrap_return with custom memory types configuration."""
        wrapper = CPUMemoryWrapper()
        wrapper.mem_types = {'used', 'free'}  # Custom memory types

        # Mock with custom memory stats
        mock_capture = Mock(return_value={'used': 4294967296, 'free': 4294967296})
        mock_format = Mock(return_value="used: 4294967296 | free: 4294967296")

        monkeypatch.setattr(wrapper, '_capture_memory', mock_capture)
        monkeypatch.setattr(wrapper, '_format_memory', mock_format)

        # Call the method
        func_name = "custom_function"
        result = None
        formatted_output = wrapper.wrap_return(func_name, result)

        # Verify the calls
        mock_capture.assert_called_once()
        mock_format.assert_called_once_with({'used': 4294967296, 'free': 4294967296})

        # Verify the output
        assert formatted_output == "used: 4294967296 | free: 4294967296"
