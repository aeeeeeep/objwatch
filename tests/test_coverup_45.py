# file: objwatch/event_handls.py:348-360
# asked: {"lines": [348, 357, 358, 359, 360], "branches": [[357, 0], [357, 358]]}
# gained: {"lines": [348, 357, 358, 359, 360], "branches": [[357, 0], [357, 358]]}

import pytest
import signal
import tempfile
import os
import builtins
from unittest.mock import Mock, patch, call
from objwatch.event_handls import EventHandls


class TestEventHandlsSignalHandler:
    """Test cases for EventHandls.signal_handler method."""

    def test_signal_handler_when_xml_not_saved(self, monkeypatch):
        """Test signal_handler when XML has not been saved yet."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create EventHandls instance with XML output
            event_handls = EventHandls(output_xml=temp_path)

            # Mock dependencies
            mock_log_error = Mock()
            mock_save_xml = Mock()
            mock_exit = Mock()

            monkeypatch.setattr('objwatch.event_handls.log_error', mock_log_error)
            monkeypatch.setattr(event_handls, 'save_xml', mock_save_xml)
            monkeypatch.setattr('builtins.exit', mock_exit)

            # Set initial state
            event_handls.is_xml_saved = False

            # Call signal_handler
            test_signal = signal.SIGTERM
            test_frame = Mock()
            event_handls.signal_handler(test_signal, test_frame)

            # Verify the calls
            mock_log_error.assert_called_once_with(f"Received signal {test_signal}, saving XML before exiting.")
            mock_save_xml.assert_called_once()
            mock_exit.assert_called_once_with(1)

        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_signal_handler_when_xml_already_saved(self, monkeypatch):
        """Test signal_handler when XML has already been saved."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create EventHandls instance with XML output
            event_handls = EventHandls(output_xml=temp_path)

            # Mock dependencies
            mock_log_error = Mock()
            mock_save_xml = Mock()
            mock_exit = Mock()

            monkeypatch.setattr('objwatch.event_handls.log_error', mock_log_error)
            monkeypatch.setattr(event_handls, 'save_xml', mock_save_xml)
            monkeypatch.setattr('builtins.exit', mock_exit)

            # Set initial state - XML already saved
            event_handls.is_xml_saved = True

            # Call signal_handler
            test_signal = signal.SIGINT
            test_frame = Mock()
            event_handls.signal_handler(test_signal, test_frame)

            # Verify no calls were made
            mock_log_error.assert_not_called()
            mock_save_xml.assert_not_called()
            mock_exit.assert_not_called()

        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_signal_handler_with_different_signals(self, monkeypatch):
        """Test signal_handler with various signal types."""
        test_signals = [
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

        for test_signal in test_signals:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
                temp_path = temp_file.name

            try:
                # Create EventHandls instance with XML output
                event_handls = EventHandls(output_xml=temp_path)

                # Mock dependencies
                mock_log_error = Mock()
                mock_save_xml = Mock()
                mock_exit = Mock()

                monkeypatch.setattr('objwatch.event_handls.log_error', mock_log_error)
                monkeypatch.setattr(event_handls, 'save_xml', mock_save_xml)
                monkeypatch.setattr('builtins.exit', mock_exit)

                # Set initial state
                event_handls.is_xml_saved = False

                # Call signal_handler
                test_frame = Mock()
                event_handls.signal_handler(test_signal, test_frame)

                # Verify the calls
                mock_log_error.assert_called_once_with(f"Received signal {test_signal}, saving XML before exiting.")
                mock_save_xml.assert_called_once()
                mock_exit.assert_called_once_with(1)

            finally:
                # Cleanup
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
