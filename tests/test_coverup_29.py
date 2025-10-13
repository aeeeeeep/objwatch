# file: objwatch/utils/logger.py:69-82
# asked: {"lines": [69, 79, 80, 82], "branches": [[79, 80], [79, 82]]}
# gained: {"lines": [69, 79, 80, 82], "branches": [[79, 80], [79, 82]]}

import pytest
from unittest.mock import patch, MagicMock
from objwatch.utils.logger import log_info, FORCE


class TestLogInfo:
    def test_log_info_with_force_enabled(self, monkeypatch):
        """Test log_info when FORCE is True - should print to stdout"""
        original_force = FORCE
        monkeypatch.setattr('objwatch.utils.logger.FORCE', True)

        with patch('builtins.print') as mock_print:
            test_msg = "Test message with FORCE enabled"
            log_info(test_msg)

            mock_print.assert_called_once_with(test_msg, flush=True)

        monkeypatch.setattr('objwatch.utils.logger.FORCE', original_force)

    def test_log_info_with_force_disabled(self, monkeypatch):
        """Test log_info when FORCE is False - should use logger.info"""
        original_force = FORCE
        monkeypatch.setattr('objwatch.utils.logger.FORCE', False)

        with patch('objwatch.utils.logger.logger') as mock_logger:
            test_msg = "Test message with FORCE disabled"
            test_args = ("arg1", "arg2")
            test_kwargs = {"key": "value"}

            log_info(test_msg, *test_args, **test_kwargs)

            mock_logger.info.assert_called_once_with(test_msg, *test_args, **test_kwargs)

        monkeypatch.setattr('objwatch.utils.logger.FORCE', original_force)

    def test_log_info_with_args_and_kwargs_force_enabled(self, monkeypatch):
        """Test log_info with args and kwargs when FORCE is True - should print only the message"""
        original_force = FORCE
        monkeypatch.setattr('objwatch.utils.logger.FORCE', True)

        with patch('builtins.print') as mock_print:
            test_msg = "Test message with args"
            test_args = ("arg1", 42)
            test_kwargs = {"key1": "value1", "key2": 123}

            log_info(test_msg, *test_args, **test_kwargs)

            # When FORCE is True, only the message should be printed, args and kwargs are ignored
            mock_print.assert_called_once_with(test_msg, flush=True)

        monkeypatch.setattr('objwatch.utils.logger.FORCE', original_force)
