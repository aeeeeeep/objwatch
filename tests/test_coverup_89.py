# file: objwatch/utils/logger.py:59-66
# asked: {"lines": [59, 66], "branches": []}
# gained: {"lines": [59, 66], "branches": []}

import pytest
import logging
from objwatch.utils.logger import get_logger, logger, create_logger


class TestGetLogger:
    def test_get_logger_returns_configured_logger(self):
        """Test that get_logger returns the configured logger instance."""
        # Ensure logger is properly configured
        create_logger()
        result = get_logger()
        assert result is logger
        assert result.name == 'objwatch'
        assert isinstance(result, logging.Logger)

    def test_get_logger_without_previous_configuration(self, monkeypatch):
        """Test that get_logger works even without previous create_logger call."""
        # Clear any existing handlers to simulate fresh state
        logger.handlers.clear()
        result = get_logger()
        assert result is logger
        assert result.name == 'objwatch'
        assert isinstance(result, logging.Logger)

    def test_get_logger_after_force_level(self, monkeypatch):
        """Test that get_logger works after setting level to 'force'."""
        create_logger(level='force')
        result = get_logger()
        assert result is logger
        assert result.name == 'objwatch'
        assert isinstance(result, logging.Logger)

    def test_get_logger_with_file_output(self, tmp_path):
        """Test that get_logger works with file output configuration."""
        log_file = tmp_path / "test.log"
        create_logger(output=str(log_file))
        result = get_logger()
        assert result is logger
        assert result.name == 'objwatch'
        assert isinstance(result, logging.Logger)
        # Clean up
        logger.handlers.clear()

    def test_get_logger_with_simple_format(self):
        """Test that get_logger works with simple format configuration."""
        create_logger(simple=True)
        result = get_logger()
        assert result is logger
        assert result.name == 'objwatch'
        assert isinstance(result, logging.Logger)
        # Clean up
        logger.handlers.clear()
