# file: objwatch/wrappers/cpu_memory_wrapper.py:64-72
# asked: {"lines": [64, 71, 72], "branches": []}
# gained: {"lines": [64, 71, 72], "branches": []}

import pytest
from unittest.mock import Mock, patch
from objwatch.wrappers.cpu_memory_wrapper import CPUMemoryWrapper


class TestCPUMemoryWrapper:
    def test_capture_memory_default_mem_types(self):
        """Test _capture_memory with default mem_types configuration."""
        wrapper = CPUMemoryWrapper()

        # Mock psutil.virtual_memory to return a predictable result
        mock_virtual_memory = Mock()
        mock_virtual_memory._asdict.return_value = {
            'total': 8589934592,  # 8GB
            'available': 4294967296,  # 4GB
            'percent': 50.0,
            'used': 4294967296,
            'free': 4294967296,
            'active': 3221225472,
            'inactive': 1073741824,
            'buffers': 268435456,
            'cached': 1073741824,
            'shared': 134217728,
            'slab': 67108864,
            'wired': 1610612736,
        }

        with patch('objwatch.wrappers.cpu_memory_wrapper.psutil.virtual_memory', return_value=mock_virtual_memory):
            result = wrapper._capture_memory()

        # Should only include the default mem_types
        expected_keys = {'total', 'available', 'percent'}
        assert set(result.keys()) == expected_keys
        assert result['total'] == 8589934592
        assert result['available'] == 4294967296
        assert result['percent'] == 50.0

    def test_capture_memory_custom_mem_types(self):
        """Test _capture_memory with custom mem_types configuration."""
        # Set custom mem_types before creating wrapper
        CPUMemoryWrapper.mem_types = ['used', 'free', 'buffers']
        wrapper = CPUMemoryWrapper()

        # Mock psutil.virtual_memory to return a predictable result
        mock_virtual_memory = Mock()
        mock_virtual_memory._asdict.return_value = {
            'total': 8589934592,
            'available': 4294967296,
            'percent': 50.0,
            'used': 4294967296,
            'free': 4294967296,
            'active': 3221225472,
            'inactive': 1073741824,
            'buffers': 268435456,
            'cached': 1073741824,
            'shared': 134217728,
            'slab': 67108864,
            'wired': 1610612736,
        }

        with patch('objwatch.wrappers.cpu_memory_wrapper.psutil.virtual_memory', return_value=mock_virtual_memory):
            result = wrapper._capture_memory()

        # Should only include the custom mem_types
        expected_keys = {'used', 'free', 'buffers'}
        assert set(result.keys()) == expected_keys
        assert result['used'] == 4294967296
        assert result['free'] == 4294967296
        assert result['buffers'] == 268435456

    def test_capture_memory_missing_mem_type(self):
        """Test _capture_memory when a requested mem_type is not in psutil result."""
        # Set mem_types to include a non-existent field
        CPUMemoryWrapper.mem_types = ['total', 'available', 'nonexistent_field']
        wrapper = CPUMemoryWrapper()

        # Mock psutil.virtual_memory to return a result without the nonexistent field
        mock_virtual_memory = Mock()
        mock_virtual_memory._asdict.return_value = {
            'total': 8589934592,
            'available': 4294967296,
            'percent': 50.0,
            'used': 4294967296,
            'free': 4294967296,
        }

        with patch('objwatch.wrappers.cpu_memory_wrapper.psutil.virtual_memory', return_value=mock_virtual_memory):
            with pytest.raises(KeyError, match='nonexistent_field'):
                wrapper._capture_memory()

    def test_capture_memory_empty_mem_types(self):
        """Test _capture_memory with empty mem_types configuration."""
        # Set empty mem_types
        CPUMemoryWrapper.mem_types = []
        wrapper = CPUMemoryWrapper()

        # Mock psutil.virtual_memory
        mock_virtual_memory = Mock()
        mock_virtual_memory._asdict.return_value = {'total': 8589934592, 'available': 4294967296, 'percent': 50.0}

        with patch('objwatch.wrappers.cpu_memory_wrapper.psutil.virtual_memory', return_value=mock_virtual_memory):
            result = wrapper._capture_memory()

        # Should return empty dict when no mem_types are configured
        assert result == {}

    def test_capture_memory_all_available_fields(self):
        """Test _capture_memory when requesting all available memory fields."""
        # Set mem_types to include all possible fields
        CPUMemoryWrapper.mem_types = [
            'total',
            'available',
            'percent',
            'used',
            'free',
            'active',
            'inactive',
            'buffers',
            'cached',
            'shared',
            'slab',
            'wired',
        ]
        wrapper = CPUMemoryWrapper()

        # Mock psutil.virtual_memory to return all fields
        mock_virtual_memory = Mock()
        mock_virtual_memory._asdict.return_value = {
            'total': 8589934592,
            'available': 4294967296,
            'percent': 50.0,
            'used': 4294967296,
            'free': 4294967296,
            'active': 3221225472,
            'inactive': 1073741824,
            'buffers': 268435456,
            'cached': 1073741824,
            'shared': 134217728,
            'slab': 67108864,
            'wired': 1610612736,
        }

        with patch('objwatch.wrappers.cpu_memory_wrapper.psutil.virtual_memory', return_value=mock_virtual_memory):
            result = wrapper._capture_memory()

        # Should include all requested fields that exist in the psutil result
        expected_keys = {
            'total',
            'available',
            'percent',
            'used',
            'free',
            'active',
            'inactive',
            'buffers',
            'cached',
            'shared',
            'slab',
            'wired',
        }
        assert set(result.keys()) == expected_keys
        assert result['total'] == 8589934592
        assert result['available'] == 4294967296
        assert result['percent'] == 50.0
        assert result['used'] == 4294967296
        assert result['free'] == 4294967296
        assert result['active'] == 3221225472
        assert result['inactive'] == 1073741824
        assert result['buffers'] == 268435456
        assert result['cached'] == 1073741824
        assert result['shared'] == 134217728
        assert result['slab'] == 67108864
        assert result['wired'] == 1610612736
