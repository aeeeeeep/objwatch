# file: objwatch/tracer.py:781-787
# asked: {"lines": [781, 785, 786, 787], "branches": []}
# gained: {"lines": [781, 785, 786, 787], "branches": []}

import pytest
import sys
from unittest.mock import Mock, patch
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerStop:
    """Test cases for Tracer.stop() method to achieve full coverage."""

    def test_stop_method_calls_sys_settrace_and_save_xml(self, monkeypatch):
        """Test that stop() calls sys.settrace(None) and event_handlers.save_xml()."""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = []
        mock_config.exclude_targets = []
        mock_config.output_xml = None
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        # Create tracer instance
        tracer = Tracer(mock_config)

        # Mock the event_handlers.save_xml method
        mock_save_xml = Mock()
        tracer.event_handlers.save_xml = mock_save_xml

        # Mock sys.settrace to track calls
        mock_settrace = Mock()
        monkeypatch.setattr(sys, 'settrace', mock_settrace)

        # Mock log_info to avoid side effects
        mock_log_info = Mock()
        monkeypatch.setattr('objwatch.tracer.log_info', mock_log_info)

        # Call the stop method
        tracer.stop()

        # Verify the method calls
        mock_log_info.assert_called_once_with("Stopping tracing.")
        mock_settrace.assert_called_once_with(None)
        mock_save_xml.assert_called_once()

    def test_stop_method_with_xml_output(self, monkeypatch):
        """Test stop() when XML output is configured."""
        # Create a mock config with XML output
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = []
        mock_config.exclude_targets = []
        mock_config.output_xml = "test_output.xml"
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        # Create tracer instance
        tracer = Tracer(mock_config)

        # Mock the event_handlers.save_xml method
        mock_save_xml = Mock()
        tracer.event_handlers.save_xml = mock_save_xml

        # Mock sys.settrace to track calls
        mock_settrace = Mock()
        monkeypatch.setattr(sys, 'settrace', mock_settrace)

        # Mock log_info to avoid side effects
        mock_log_info = Mock()
        monkeypatch.setattr('objwatch.tracer.log_info', mock_log_info)

        # Call the stop method
        tracer.stop()

        # Verify the method calls
        mock_log_info.assert_called_once_with("Stopping tracing.")
        mock_settrace.assert_called_once_with(None)
        mock_save_xml.assert_called_once()
