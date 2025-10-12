# file: objwatch/utils/logger.py:85-98
# asked: {"lines": [85, 95, 96, 98], "branches": [[95, 96], [95, 98]]}
# gained: {"lines": [85, 95, 96, 98], "branches": [[95, 96], [95, 98]]}

import pytest
from unittest.mock import patch, MagicMock
from objwatch.utils.logger import log_debug, FORCE


class TestLogDebug:
    """Test cases for log_debug function to achieve full coverage."""

    def test_log_debug_with_force_enabled(self, monkeypatch):
        """Test log_debug when FORCE is True - should print to stdout."""
        # Save original FORCE value
        original_force = FORCE

        try:
            # Set FORCE to True
            monkeypatch.setattr('objwatch.utils.logger.FORCE', True)

            # Mock print function to capture output
            with patch('builtins.print') as mock_print:
                test_msg = "Test debug message with FORCE enabled"
                log_debug(test_msg)

                # Verify print was called with correct arguments
                mock_print.assert_called_once_with(test_msg, flush=True)
        finally:
            # Restore original FORCE value
            monkeypatch.setattr('objwatch.utils.logger.FORCE', original_force)

    def test_log_debug_with_force_disabled(self, monkeypatch):
        """Test log_debug when FORCE is False - should use logger.debug."""
        # Save original FORCE value
        original_force = FORCE

        try:
            # Set FORCE to False
            monkeypatch.setattr('objwatch.utils.logger.FORCE', False)

            # Mock logger.debug
            with patch('objwatch.utils.logger.logger') as mock_logger:
                test_msg = "Test debug message with FORCE disabled"
                test_args = ("arg1", "arg2")
                test_kwargs = {"key1": "value1", "key2": "value2"}

                log_debug(test_msg, *test_args, **test_kwargs)

                # Verify logger.debug was called with correct arguments
                mock_logger.debug.assert_called_once_with(test_msg, *test_args, **test_kwargs)
        finally:
            # Restore original FORCE value
            monkeypatch.setattr('objwatch.utils.logger.FORCE', original_force)

    def test_log_debug_with_force_disabled_no_args(self, monkeypatch):
        """Test log_debug when FORCE is False with no additional arguments."""
        # Save original FORCE value
        original_force = FORCE

        try:
            # Set FORCE to False
            monkeypatch.setattr('objwatch.utils.logger.FORCE', False)

            # Mock logger.debug
            with patch('objwatch.utils.logger.logger') as mock_logger:
                test_msg = "Simple debug message"

                log_debug(test_msg)

                # Verify logger.debug was called with correct arguments
                mock_logger.debug.assert_called_once_with(test_msg)
        finally:
            # Restore original FORCE value
            monkeypatch.setattr('objwatch.utils.logger.FORCE', original_force)
