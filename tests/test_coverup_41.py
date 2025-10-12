# file: objwatch/mp_handls.py:56-61
# asked: {"lines": [56, 60, 61], "branches": [[60, 0], [60, 61]]}
# gained: {"lines": [56, 60, 61], "branches": [[60, 0], [60, 61]]}

import pytest
from unittest.mock import Mock, patch
from objwatch.mp_handls import MPHandls


class TestMPHandlsSync:
    """Test cases for MPHandls.sync method to achieve full coverage."""

    def test_sync_when_initialized_and_sync_fn_exists(self):
        """Test sync() when both initialized is True and sync_fn is not None."""
        # Create MPHandls instance
        handler = MPHandls(framework=None)

        # Set up the conditions for the branch to execute
        handler.initialized = True
        mock_sync_fn = Mock()
        handler.sync_fn = mock_sync_fn

        # Call sync method
        handler.sync()

        # Verify sync_fn was called
        mock_sync_fn.assert_called_once()

    def test_sync_when_not_initialized(self):
        """Test sync() when initialized is False (sync_fn should not be called)."""
        # Create MPHandls instance
        handler = MPHandls(framework=None)

        # Set up conditions where initialized is False
        handler.initialized = False
        mock_sync_fn = Mock()
        handler.sync_fn = mock_sync_fn

        # Call sync method
        handler.sync()

        # Verify sync_fn was NOT called
        mock_sync_fn.assert_not_called()

    def test_sync_when_sync_fn_is_none(self):
        """Test sync() when sync_fn is None (should not call anything)."""
        # Create MPHandls instance
        handler = MPHandls(framework=None)

        # Set up conditions where initialized is True but sync_fn is None
        handler.initialized = True
        handler.sync_fn = None

        # Call sync method - should not raise any exceptions
        handler.sync()

        # No assertions needed - just verifying no exceptions are raised
