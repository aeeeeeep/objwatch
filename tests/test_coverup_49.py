# file: objwatch/core.py:70-75
# asked: {"lines": [70, 74, 75], "branches": []}
# gained: {"lines": [70, 74, 75], "branches": []}

import pytest
from unittest.mock import Mock, patch
from objwatch.core import ObjWatch
from objwatch.utils.logger import log_info


class TestObjWatchStart:
    def test_start_calls_log_info_and_tracer_start(self, monkeypatch):
        # Mock the log_info function
        mock_log_info = Mock()
        monkeypatch.setattr("objwatch.core.log_info", mock_log_info)

        # Mock the tracer's start method
        mock_tracer_start = Mock()

        # Create ObjWatch instance with minimal configuration
        objwatch = ObjWatch(targets=["some_module"])
        objwatch.tracer.start = mock_tracer_start

        # Call the start method
        objwatch.start()

        # Verify log_info was called with the expected message
        mock_log_info.assert_called_once_with("Starting ObjWatch tracing.")

        # Verify tracer.start was called
        mock_tracer_start.assert_called_once()
