# file: objwatch/wrappers/cpu_memory_wrapper.py:112-123
# asked: {"lines": [112, 123], "branches": []}
# gained: {"lines": [112, 123], "branches": []}

import pytest
from unittest.mock import Mock, patch
from objwatch.wrappers.cpu_memory_wrapper import CPUMemoryWrapper


class TestCPUMemoryWrapperWrapUpd:
    """Test cases for CPUMemoryWrapper.wrap_upd method."""

    def test_wrap_upd_returns_empty_old_and_formatted_memory(self, monkeypatch):
        """Test that wrap_upd returns empty string for old value and formatted memory for new value."""
        # Setup
        wrapper = CPUMemoryWrapper()
        old_value = "old_value"
        current_value = "current_value"

        # Mock the memory capture and formatting
        mock_memory_stats = {'total': 8589934592, 'available': 4294967296, 'percent': 50.0}
        mock_formatted = "total: 8589934592 | available: 4294967296 | percent: 50.0"

        # Patch the internal methods
        monkeypatch.setattr(wrapper, '_capture_memory', Mock(return_value=mock_memory_stats))
        monkeypatch.setattr(wrapper, '_format_memory', Mock(return_value=mock_formatted))

        # Execute
        result = wrapper.wrap_upd(old_value, current_value)

        # Assert
        assert result == ("", mock_formatted)
        wrapper._capture_memory.assert_called_once()
        wrapper._format_memory.assert_called_once_with(mock_memory_stats)

    def test_wrap_upd_with_different_memory_types(self, monkeypatch):
        """Test wrap_upd with different memory type configurations."""
        # Setup - modify mem_types to test different configurations
        original_mem_types = CPUMemoryWrapper.mem_types.copy()
        CPUMemoryWrapper.mem_types = ['used', 'free']

        try:
            wrapper = CPUMemoryWrapper()
            old_value = 42
            current_value = 100

            # Mock memory stats for different configuration
            mock_memory_stats = {'used': 4294967296, 'free': 4294967296}
            mock_formatted = "used: 4294967296 | free: 4294967296"

            # Patch the internal methods
            monkeypatch.setattr(wrapper, '_capture_memory', Mock(return_value=mock_memory_stats))
            monkeypatch.setattr(wrapper, '_format_memory', Mock(return_value=mock_formatted))

            # Execute
            result = wrapper.wrap_upd(old_value, current_value)

            # Assert
            assert result == ("", mock_formatted)
            wrapper._capture_memory.assert_called_once()
            wrapper._format_memory.assert_called_once_with(mock_memory_stats)
        finally:
            # Cleanup - restore original mem_types
            CPUMemoryWrapper.mem_types = original_mem_types

    def test_wrap_upd_with_none_values(self, monkeypatch):
        """Test wrap_upd with None values for old and current values."""
        # Setup
        wrapper = CPUMemoryWrapper()

        # Mock memory capture and formatting
        mock_memory_stats = {'total': 8589934592, 'available': 4294967296, 'percent': 50.0}
        mock_formatted = "total: 8589934592 | available: 4294967296 | percent: 50.0"

        # Patch the internal methods
        monkeypatch.setattr(wrapper, '_capture_memory', Mock(return_value=mock_memory_stats))
        monkeypatch.setattr(wrapper, '_format_memory', Mock(return_value=mock_formatted))

        # Execute
        result = wrapper.wrap_upd(None, None)

        # Assert
        assert result == ("", mock_formatted)
        wrapper._capture_memory.assert_called_once()
        wrapper._format_memory.assert_called_once_with(mock_memory_stats)

    def test_wrap_upd_with_complex_objects(self, monkeypatch):
        """Test wrap_upd with complex objects as values."""
        # Setup
        wrapper = CPUMemoryWrapper()
        old_value = {"key": "old_value", "nested": {"data": [1, 2, 3]}}
        current_value = {"key": "new_value", "nested": {"data": [4, 5, 6]}}

        # Mock memory capture and formatting
        mock_memory_stats = {'total': 8589934592, 'available': 4294967296, 'percent': 50.0}
        mock_formatted = "total: 8589934592 | available: 4294967296 | percent: 50.0"

        # Patch the internal methods
        monkeypatch.setattr(wrapper, '_capture_memory', Mock(return_value=mock_memory_stats))
        monkeypatch.setattr(wrapper, '_format_memory', Mock(return_value=mock_formatted))

        # Execute
        result = wrapper.wrap_upd(old_value, current_value)

        # Assert
        assert result == ("", mock_formatted)
        wrapper._capture_memory.assert_called_once()
        wrapper._format_memory.assert_called_once_with(mock_memory_stats)
