# file: objwatch/utils/logger.py:117-130
# asked: {"lines": [117, 127, 128, 130], "branches": [[127, 128], [127, 130]]}
# gained: {"lines": [117, 127, 128, 130], "branches": [[127, 128], [127, 130]]}

import pytest
from unittest.mock import patch, MagicMock
from objwatch.utils.logger import log_error, FORCE


class TestLogError:
    def test_log_error_with_force_enabled(self, monkeypatch):
        """Test log_error when FORCE is True - should print to stdout"""
        # Save original FORCE value
        original_force = FORCE

        try:
            # Set FORCE to True
            monkeypatch.setattr('objwatch.utils.logger.FORCE', True)

            # Mock print to capture output
            with patch('builtins.print') as mock_print:
                test_msg = "Test error message"
                log_error(test_msg)

                # Verify print was called with the message and flush=True
                mock_print.assert_called_once_with(test_msg, flush=True)
        finally:
            # Restore original FORCE value
            monkeypatch.setattr('objwatch.utils.logger.FORCE', original_force)

    def test_log_error_with_force_disabled(self, monkeypatch):
        """Test log_error when FORCE is False - should use logger.error"""
        # Save original FORCE value
        original_force = FORCE

        try:
            # Set FORCE to False
            monkeypatch.setattr('objwatch.utils.logger.FORCE', False)

            # Mock logger.error
            with patch('objwatch.utils.logger.logger') as mock_logger:
                test_msg = "Test error message"
                test_args = ("arg1", "arg2")
                test_kwargs = {"key1": "value1", "key2": "value2"}

                log_error(test_msg, *test_args, **test_kwargs)

                # Verify logger.error was called with all arguments
                mock_logger.error.assert_called_once_with(test_msg, *test_args, **test_kwargs)
        finally:
            # Restore original FORCE value
            monkeypatch.setattr('objwatch.utils.logger.FORCE', original_force)

    def test_log_error_with_force_disabled_no_extra_args(self, monkeypatch):
        """Test log_error when FORCE is False with no extra arguments"""
        # Save original FORCE value
        original_force = FORCE

        try:
            # Set FORCE to False
            monkeypatch.setattr('objwatch.utils.logger.FORCE', False)

            # Mock logger.error
            with patch('objwatch.utils.logger.logger') as mock_logger:
                test_msg = "Simple error message"

                log_error(test_msg)

                # Verify logger.error was called with just the message
                mock_logger.error.assert_called_once_with(test_msg)
        finally:
            # Restore original FORCE value
            monkeypatch.setattr('objwatch.utils.logger.FORCE', original_force)
