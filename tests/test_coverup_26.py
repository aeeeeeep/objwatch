# file: objwatch/mp_handls.py:73-82
# asked: {"lines": [73, 80, 81, 82], "branches": [[80, 81], [80, 82]]}
# gained: {"lines": [73, 80, 81, 82], "branches": [[80, 81], [80, 82]]}

import pytest
from unittest.mock import Mock, patch
from objwatch.mp_handls import MPHandls


class TestMPHandlsIsInitialized:
    """Test cases for MPHandls.is_initialized method to achieve full coverage."""

    def test_is_initialized_framework_not_none_not_initialized_calls_check_initialized(self, monkeypatch):
        """Test that _check_initialized is called when framework is not None and not initialized."""
        # Create instance with framework but not initialized
        handler = MPHandls(framework='multiprocessing')
        handler.initialized = False

        # Mock _check_initialized to track calls
        mock_check_initialized = Mock()
        monkeypatch.setattr(handler, '_check_initialized', mock_check_initialized)

        # Call is_initialized
        result = handler.is_initialized()

        # Verify _check_initialized was called
        mock_check_initialized.assert_called_once()
        # Verify return value is False (since we didn't actually initialize)
        assert result is False

    def test_is_initialized_framework_none_returns_current_state(self):
        """Test that is_initialized returns current state when framework is None."""
        # Create instance with no framework
        handler = MPHandls(framework=None)

        # Test when initialized is True
        handler.initialized = True
        assert handler.is_initialized() is True

        # Test when initialized is False
        handler.initialized = False
        assert handler.is_initialized() is False

    def test_is_initialized_already_initialized_returns_true(self):
        """Test that is_initialized returns True when already initialized."""
        # Create instance that is already initialized
        handler = MPHandls(framework='multiprocessing')
        handler.initialized = True

        # Should return True without calling _check_initialized
        assert handler.is_initialized() is True
