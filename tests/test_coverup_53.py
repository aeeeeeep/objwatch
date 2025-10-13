# file: objwatch/core.py:77-82
# asked: {"lines": [77, 81, 82], "branches": []}
# gained: {"lines": [77, 81, 82], "branches": []}

import pytest
from unittest.mock import Mock, patch
from objwatch.core import ObjWatch
from objwatch.tracer import Tracer
from objwatch.utils.logger import log_info


class TestObjWatchStop:
    """Test cases for ObjWatch.stop() method to achieve full coverage."""

    def test_stop_method_calls_tracer_stop(self, monkeypatch):
        """Test that ObjWatch.stop() calls tracer.stop() and logs the stop message."""
        # Mock the tracer and log_info
        mock_tracer = Mock(spec=Tracer)
        mock_log_info = Mock()

        # Create ObjWatch instance with minimal configuration
        objwatch = ObjWatch(targets=["some_module"])
        objwatch.tracer = mock_tracer

        # Patch log_info to verify it's called
        monkeypatch.setattr("objwatch.core.log_info", mock_log_info)

        # Call the stop method
        objwatch.stop()

        # Verify log_info was called with the expected message
        mock_log_info.assert_called_once_with("Stopping ObjWatch tracing.")

        # Verify tracer.stop() was called
        mock_tracer.stop.assert_called_once()

    def test_stop_method_with_context_manager_cleanup(self):
        """Test that stop works correctly when used with context manager pattern."""
        # Create ObjWatch instance
        objwatch = ObjWatch(targets=["some_module"])

        # Mock the tracer
        mock_tracer = Mock(spec=Tracer)
        objwatch.tracer = mock_tracer

        # Mock log_info to avoid actual logging
        with patch("objwatch.core.log_info") as mock_log_info:
            # Call stop method
            objwatch.stop()

            # Verify the calls
            mock_log_info.assert_called_once_with("Stopping ObjWatch tracing.")
            mock_tracer.stop.assert_called_once()
