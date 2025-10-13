# file: objwatch/core.py:94-103
# asked: {"lines": [94, 103], "branches": []}
# gained: {"lines": [94, 103], "branches": []}

import pytest
from unittest.mock import Mock, patch
from objwatch.core import ObjWatch


class TestObjWatchExit:
    """Test cases for ObjWatch.__exit__ method."""

    def test_exit_calls_stop(self):
        """Test that __exit__ method calls stop() method."""
        # Create a mock ObjWatch instance
        objwatch = ObjWatch(targets=['some_module'])

        # Mock the stop method to track if it's called
        with patch.object(objwatch, 'stop') as mock_stop:
            # Call __exit__ with various parameters
            objwatch.__exit__(None, None, None)

            # Verify that stop was called exactly once
            mock_stop.assert_called_once()

    def test_exit_with_exception(self):
        """Test that __exit__ method calls stop() even when exceptions are present."""
        # Create a mock ObjWatch instance
        objwatch = ObjWatch(targets=['some_module'])

        # Mock the stop method to track if it's called
        with patch.object(objwatch, 'stop') as mock_stop:
            # Call __exit__ with exception parameters
            objwatch.__exit__(ValueError, ValueError("test error"), "traceback")

            # Verify that stop was called exactly once
            mock_stop.assert_called_once()

    def test_exit_cleanup(self):
        """Test that __exit__ properly cleans up resources."""
        # Create a real ObjWatch instance
        objwatch = ObjWatch(targets=['some_module'])

        # Mock the tracer to avoid actual tracing
        with patch.object(objwatch.tracer, 'stop'):
            # Enter context first to set up properly
            objwatch.__enter__()

            # Then exit context
            objwatch.__exit__(None, None, None)

            # Verify that tracer.stop was called
            objwatch.tracer.stop.assert_called_once()
