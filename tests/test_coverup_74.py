# file: objwatch/mp_handls.py:63-71
# asked: {"lines": [63, 71], "branches": []}
# gained: {"lines": [63, 71], "branches": []}

import pytest
from unittest.mock import Mock, patch
from objwatch.mp_handls import MPHandls


class TestMPHandlsGetIndex:
    """Test cases for MPHandls.get_index method."""

    def test_get_index_initialized_with_index(self):
        """Test get_index returns the correct index when initialized with a valid index."""
        # Setup
        handler = MPHandls(framework=None)
        handler.initialized = True
        handler.index = 5

        # Execute
        result = handler.get_index()

        # Assert
        assert result == 5

    def test_get_index_initialized_with_none_index(self):
        """Test get_index returns None when initialized but index is None."""
        # Setup
        handler = MPHandls(framework=None)
        handler.initialized = True
        handler.index = None

        # Execute
        result = handler.get_index()

        # Assert
        assert result is None

    def test_get_index_not_initialized(self):
        """Test get_index returns the index value regardless of initialization status."""
        # Setup
        handler = MPHandls(framework=None)
        handler.initialized = False
        handler.index = 42

        # Execute
        result = handler.get_index()

        # Assert
        assert result == 42
