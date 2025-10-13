# file: objwatch/utils/logger.py:101-114
# asked: {"lines": [101, 111, 112, 114], "branches": [[111, 112], [111, 114]]}
# gained: {"lines": [101, 111, 112, 114], "branches": [[111, 112], [111, 114]]}

import pytest
from unittest.mock import patch, MagicMock
import objwatch.utils.logger as logger_module


class TestLogWarn:
    """Test cases for log_warn function to achieve full coverage."""

    def test_log_warn_with_force_true(self, monkeypatch):
        """Test log_warn when FORCE is True - should print to stdout."""
        # Save original FORCE value
        original_force = logger_module.FORCE

        try:
            # Set FORCE to True
            monkeypatch.setattr(logger_module, 'FORCE', True)

            # Mock print to capture output
            with patch('builtins.print') as mock_print:
                test_msg = "Test warning message with FORCE=True"
                logger_module.log_warn(test_msg)

                # Verify print was called with correct arguments
                mock_print.assert_called_once_with(test_msg, flush=True)
        finally:
            # Restore original FORCE value
            monkeypatch.setattr(logger_module, 'FORCE', original_force)

    def test_log_warn_with_force_false(self, monkeypatch):
        """Test log_warn when FORCE is False - should use logger.warning."""
        # Save original FORCE value
        original_force = logger_module.FORCE

        try:
            # Set FORCE to False
            monkeypatch.setattr(logger_module, 'FORCE', False)

            # Mock logger.warning to verify it's called
            with patch.object(logger_module.logger, 'warning') as mock_warning:
                test_msg = "Test warning message with FORCE=False"
                test_args = ("arg1", "arg2")
                test_kwargs = {"key": "value"}

                logger_module.log_warn(test_msg, *test_args, **test_kwargs)

                # Verify logger.warning was called with correct arguments
                mock_warning.assert_called_once_with(test_msg, *test_args, **test_kwargs)
        finally:
            # Restore original FORCE value
            monkeypatch.setattr(logger_module, 'FORCE', original_force)

    def test_log_warn_with_force_false_no_args(self, monkeypatch):
        """Test log_warn when FORCE is False with no additional arguments."""
        # Save original FORCE value
        original_force = logger_module.FORCE

        try:
            # Set FORCE to False
            monkeypatch.setattr(logger_module, 'FORCE', False)

            # Mock logger.warning to verify it's called
            with patch.object(logger_module.logger, 'warning') as mock_warning:
                test_msg = "Simple warning message"

                logger_module.log_warn(test_msg)

                # Verify logger.warning was called with correct arguments
                mock_warning.assert_called_once_with(test_msg)
        finally:
            # Restore original FORCE value
            monkeypatch.setattr(logger_module, 'FORCE', original_force)
