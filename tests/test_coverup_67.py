# file: objwatch/event_handls.py:21-48
# asked: {"lines": [21, 28, 29, 30, 31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 48], "branches": [[29, 0], [29, 30], [47, 0], [47, 48]]}
# gained: {"lines": [21, 28, 29, 30, 31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 48], "branches": [[29, 0], [29, 30], [47, 0], [47, 48]]}

import pytest
import signal
import tempfile
import os
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
from objwatch.event_handls import EventHandls


class TestEventHandls:
    """Test cases for EventHandls class initialization and XML output functionality."""

    def test_init_without_xml_output(self):
        """Test EventHandls initialization without XML output."""
        handler = EventHandls(output_xml=None)
        assert handler.output_xml is None
        # Verify no XML-related attributes are set
        assert not hasattr(handler, 'is_xml_saved')
        assert not hasattr(handler, 'stack_root')
        assert not hasattr(handler, 'current_node')

    def test_init_with_xml_output(self):
        """Test EventHandls initialization with XML output."""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp_file:
            xml_path = tmp_file.name

        try:
            handler = EventHandls(output_xml=xml_path)
            assert handler.output_xml == xml_path
            assert handler.is_xml_saved is False
            assert isinstance(handler.stack_root, ET.Element)
            assert handler.stack_root.tag == 'ObjWatch'
            assert isinstance(handler.current_node, list)
            assert len(handler.current_node) == 1
            assert handler.current_node[0] is handler.stack_root
        finally:
            if os.path.exists(xml_path):
                os.unlink(xml_path)

    def test_signal_handlers_registered(self):
        """Test that signal handlers are registered when XML output is enabled."""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp_file:
            xml_path = tmp_file.name

        try:
            with patch('signal.signal') as mock_signal:
                handler = EventHandls(output_xml=xml_path)

                # Verify signal.signal was called for each signal type
                expected_signals = [
                    signal.SIGTERM,
                    signal.SIGINT,
                    signal.SIGABRT,
                    signal.SIGHUP,
                    signal.SIGQUIT,
                    signal.SIGUSR1,
                    signal.SIGUSR2,
                    signal.SIGALRM,
                    signal.SIGSEGV,
                ]

                # Check that signal.signal was called the correct number of times
                assert mock_signal.call_count == len(expected_signals)

                # Verify each call was made with the correct signal and handler
                for call in mock_signal.call_args_list:
                    args = call[0]
                    assert len(args) == 2
                    assert args[0] in expected_signals
                    assert args[1] == handler.signal_handler

        finally:
            if os.path.exists(xml_path):
                os.unlink(xml_path)

    def test_save_xml_not_called_when_already_saved(self):
        """Test that save_xml doesn't save when is_xml_saved is True."""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp_file:
            xml_path = tmp_file.name

        try:
            handler = EventHandls(output_xml=xml_path)
            handler.is_xml_saved = True

            with patch.object(ET, 'ElementTree') as mock_tree:
                with patch('objwatch.utils.logger.log_info') as mock_log_info:
                    handler.save_xml()

                    # Verify no XML operations were performed
                    mock_tree.assert_not_called()
                    # Verify no log messages about saving
                    for call in mock_log_info.call_args_list:
                        args = call[0]
                        if len(args) > 0:
                            assert 'save' not in args[0].lower()

        finally:
            if os.path.exists(xml_path):
                os.unlink(xml_path)

    def test_save_xml_with_output_disabled(self):
        """Test that save_xml does nothing when output_xml is None."""
        handler = EventHandls(output_xml=None)

        # Add XML attributes manually to test the condition
        handler.output_xml = None
        handler.is_xml_saved = False

        with patch.object(ET, 'ElementTree') as mock_tree:
            with patch('objwatch.utils.logger.log_info') as mock_log_info:
                handler.save_xml()

                # Verify no XML operations were performed
                mock_tree.assert_not_called()
                # Verify no log messages about saving
                for call in mock_log_info.call_args_list:
                    args = call[0]
                    if len(args) > 0:
                        assert 'save' not in args[0].lower()

    def test_signal_handler_skips_when_xml_already_saved(self):
        """Test that signal_handler does nothing when XML is already saved."""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp_file:
            xml_path = tmp_file.name

        try:
            handler = EventHandls(output_xml=xml_path)
            handler.is_xml_saved = True

            with patch.object(handler, 'save_xml') as mock_save_xml:
                with patch('sys.exit') as mock_exit:
                    with patch('objwatch.event_handls.log_error') as mock_log_error:
                        handler.signal_handler(signal.SIGINT, None)

                        # Verify save_xml was NOT called
                        mock_save_xml.assert_not_called()
                        # Verify exit was NOT called
                        mock_exit.assert_not_called()
                        # Verify no error was logged
                        mock_log_error.assert_not_called()

        finally:
            if os.path.exists(xml_path):
                os.unlink(xml_path)
