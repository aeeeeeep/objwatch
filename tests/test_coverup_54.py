# file: objwatch/tracer.py:773-779
# asked: {"lines": [773, 777, 778, 779], "branches": []}
# gained: {"lines": [773, 777, 778, 779], "branches": []}

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerStart:
    """Test cases for Tracer.start() method to achieve full coverage."""

    def test_start_sets_trace_and_calls_sync(self, monkeypatch):
        """Test that start() sets trace function and calls mp_handlers.sync()"""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = []
        mock_config.exclude_targets = []
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        # Create tracer instance
        tracer = Tracer(mock_config)

        # Mock the trace_factory to return a dummy function
        mock_trace_func = Mock()
        tracer.trace_factory = Mock(return_value=mock_trace_func)

        # Mock sys.settrace and mp_handlers.sync
        mock_settrace = Mock()
        mock_sync = Mock()

        monkeypatch.setattr(sys, 'settrace', mock_settrace)
        tracer.mp_handlers.sync = mock_sync

        # Mock log_info to verify it's called
        mock_log_info = Mock()
        monkeypatch.setattr('objwatch.tracer.log_info', mock_log_info)

        # Call the start method
        tracer.start()

        # Verify the method calls
        mock_log_info.assert_called_once_with("Starting tracing.")
        tracer.trace_factory.assert_called_once()
        mock_settrace.assert_called_once_with(mock_trace_func)
        mock_sync.assert_called_once()

    def test_start_with_mock_trace_factory(self, monkeypatch):
        """Test start() with a more realistic trace_factory mock"""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = []
        mock_config.exclude_targets = []
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        # Create tracer instance
        tracer = Tracer(mock_config)

        # Create a real trace function that we can verify gets set
        def mock_trace_func(frame, event, arg):
            return mock_trace_func

        tracer.trace_factory = Mock(return_value=mock_trace_func)

        # Track what gets passed to settrace
        captured_trace_func = None

        def mock_settrace(func):
            nonlocal captured_trace_func
            captured_trace_func = func

        mock_sync = Mock()

        monkeypatch.setattr(sys, 'settrace', mock_settrace)
        tracer.mp_handlers.sync = mock_sync

        # Mock log_info
        mock_log_info = Mock()
        monkeypatch.setattr('objwatch.tracer.log_info', mock_log_info)

        # Call the start method
        tracer.start()

        # Verify the method calls
        mock_log_info.assert_called_once_with("Starting tracing.")
        tracer.trace_factory.assert_called_once()
        assert captured_trace_func is mock_trace_func
        mock_sync.assert_called_once()
