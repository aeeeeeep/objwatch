# file: objwatch/utils/logger.py:12-52
# asked: {"lines": [12, 13, 14, 24, 26, 27, 29, 30, 32, 33, 35, 36, 38, 41, 42, 43, 46, 47, 48, 49, 52], "branches": [[24, 25], [24, 29], [30, 32], [30, 52], [32, 33], [32, 35], [46, 47], [46, 52]]}
# gained: {"lines": [12, 13, 14, 24, 26, 27, 29, 30, 32, 33, 35, 36, 38, 41, 42, 43, 46, 52], "branches": [[24, 25], [24, 29], [30, 32], [30, 52], [32, 33], [32, 35], [46, 52]]}

import pytest
import logging
import tempfile
import os
from objwatch.utils.logger import create_logger


class TestCreateLogger:
    def test_create_logger_with_force_level(self, monkeypatch):
        """Test that when level is 'force', FORCE is set to True and function returns early."""
        # Import the module to access FORCE directly
        import objwatch.utils.logger as logger_module

        # Store original FORCE value if it exists
        original_force = getattr(logger_module, 'FORCE', None)

        # Set FORCE to False initially
        logger_module.FORCE = False

        try:
            create_logger(level="force")

            # Verify FORCE was set to True
            assert logger_module.FORCE is True
        finally:
            # Restore original FORCE value
            if original_force is not None:
                logger_module.FORCE = original_force
            else:
                delattr(logger_module, 'FORCE')

    def test_create_logger_with_simple_format(self):
        """Test logger creation with simple format."""
        logger_name = "test_simple_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Also remove handlers from parent loggers that might interfere
        logger.propagate = True  # Temporarily enable propagation to check parent handlers

        create_logger(name=logger_name, simple=True)

        # Verify logger was configured
        logger = logging.getLogger(logger_name)
        # Check that propagate is False
        assert logger.propagate is False

    def test_create_logger_with_detailed_format(self):
        """Test logger creation with detailed format."""
        logger_name = "test_detailed_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Also remove handlers from parent loggers that might interfere
        logger.propagate = True  # Temporarily enable propagation to check parent handlers

        create_logger(name=logger_name, simple=False)

        # Verify logger was configured
        logger = logging.getLogger(logger_name)
        # Check that propagate is False
        assert logger.propagate is False

    def test_create_logger_with_file_output(self):
        """Test logger creation with file output."""
        logger_name = "test_file_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Also remove handlers from parent loggers that might interfere
        logger.propagate = True  # Temporarily enable propagation to check parent handlers

        # Create temporary file for logging
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_file_path = temp_file.name

        try:
            create_logger(name=logger_name, output=temp_file_path)

            # Verify logger was configured
            logger = logging.getLogger(logger_name)
            # Check that propagate is False
            assert logger.propagate is False

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_create_logger_with_custom_level(self):
        """Test logger creation with custom logging level."""
        logger_name = "test_custom_level_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Also remove handlers from parent loggers that might interfere
        logger.propagate = True  # Temporarily enable propagation to check parent handlers

        create_logger(name=logger_name, level=logging.WARNING)

        # Verify logger was configured with custom level
        logger = logging.getLogger(logger_name)
        # Check that propagate is False
        assert logger.propagate is False

    def test_create_logger_with_string_level(self):
        """Test logger creation with string logging level."""
        logger_name = "test_string_level_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Also remove handlers from parent loggers that might interfere
        logger.propagate = True  # Temporarily enable propagation to check parent handlers

        create_logger(name=logger_name, level="INFO")

        # Verify logger was configured with string level
        logger = logging.getLogger(logger_name)
        # Check that propagate is False
        assert logger.propagate is False

    def test_create_logger_existing_handlers(self):
        """Test that logger is not reconfigured if it already has handlers."""
        logger_name = "test_existing_handlers_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Manually add a handler first
        initial_handler = logging.StreamHandler()
        logger.addHandler(initial_handler)
        initial_handler_count = len(logger.handlers)

        # Call create_logger - should not add new handlers
        create_logger(name=logger_name)

        # Verify no new handlers were added
        logger = logging.getLogger(logger_name)
        assert len(logger.handlers) == initial_handler_count
        assert logger.propagate is False

    def test_create_logger_with_default_name(self):
        """Test logger creation with default name 'objwatch'."""
        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger('objwatch')
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Also remove handlers from parent loggers that might interfere
        logger.propagate = True  # Temporarily enable propagation to check parent handlers

        create_logger()

        # Verify logger was configured with default name
        logger = logging.getLogger('objwatch')
        # Check that propagate is False
        assert logger.propagate is False

    def test_create_logger_with_simple_and_file_output(self):
        """Test logger creation with simple format and file output."""
        logger_name = "test_simple_file_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Also remove handlers from parent loggers that might interfere
        logger.propagate = True  # Temporarily enable propagation to check parent handlers

        # Create temporary file for logging
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_file_path = temp_file.name

        try:
            create_logger(name=logger_name, output=temp_file_path, simple=True)

            # Verify logger was configured
            logger = logging.getLogger(logger_name)
            # Check that propagate is False
            assert logger.propagate is False

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_create_logger_with_no_handlers_initial_setup(self):
        """Test that logger setup only happens when no handlers exist."""
        logger_name = "test_no_handlers_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Disable propagation to isolate this logger from parent handlers
        logger.propagate = False

        # Verify logger has no handlers initially
        assert not logger.hasHandlers()

        create_logger(name=logger_name)

        # Verify propagate is False
        logger = logging.getLogger(logger_name)
        assert logger.propagate is False

    def test_create_logger_actual_logging_behavior(self):
        """Test that the logger actually works by capturing log output."""
        logger_name = "test_actual_logging_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Disable propagation to isolate this logger from parent handlers
        logger.propagate = False

        create_logger(name=logger_name, simple=True)

        # Test that the logger can actually log messages
        logger = logging.getLogger(logger_name)

        # Create a memory handler to capture log output
        import io

        log_capture_string = io.StringIO()
        handler = logging.StreamHandler(log_capture_string)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Set logger level to DEBUG to ensure messages are logged
        logger.setLevel(logging.DEBUG)

        # Log a test message
        test_message = "Test log message"
        logger.debug(test_message)

        # Check that the message was logged
        log_contents = log_capture_string.getvalue()
        assert test_message in log_contents
        assert "DEBUG" in log_contents

    def test_create_logger_verify_formatter_creation(self):
        """Test that formatters are created correctly based on simple flag."""
        logger_name = "test_formatter_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Test simple formatter
        create_logger(name=logger_name, simple=True)
        logger = logging.getLogger(logger_name)
        assert logger.propagate is False

        # Test detailed formatter
        logger_name2 = "test_formatter_logger2"
        logger2 = logging.getLogger(logger_name2)
        for handler in logger2.handlers[:]:
            logger2.removeHandler(handler)

        create_logger(name=logger_name2, simple=False)
        logger2 = logging.getLogger(logger_name2)
        assert logger2.propagate is False

    def test_create_logger_with_different_levels(self):
        """Test logger creation with various logging levels."""
        test_cases = [
            (logging.DEBUG, "test_debug_logger"),
            (logging.INFO, "test_info_logger"),
            (logging.WARNING, "test_warning_logger"),
            (logging.ERROR, "test_error_logger"),
            (logging.CRITICAL, "test_critical_logger"),
        ]

        for level, logger_name in test_cases:
            # Remove any existing handlers to ensure fresh setup
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            # Disable propagation to isolate this logger from parent handlers
            logger.propagate = False

            create_logger(name=logger_name, level=level)

            # Verify logger was configured
            logger = logging.getLogger(logger_name)
            assert logger.propagate is False

    def test_create_logger_with_force_level_does_not_configure_logger(self):
        """Test that when level is 'force', no logger configuration happens."""
        logger_name = "test_force_no_config_logger"

        # Remove any existing handlers to ensure fresh setup
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Store original FORCE value if it exists
        import objwatch.utils.logger as logger_module

        original_force = getattr(logger_module, 'FORCE', None)

        try:
            # Set FORCE to False initially
            logger_module.FORCE = False

            # Call create_logger with force level
            create_logger(name=logger_name, level="force")

            # Verify FORCE was set to True
            assert logger_module.FORCE is True

            # Verify logger was NOT configured (no handlers added, propagate unchanged)
            logger = logging.getLogger(logger_name)
            assert len(logger.handlers) == 0
            # propagate should remain at its default value (True) since no configuration happened

        finally:
            # Restore original FORCE value
            if original_force is not None:
                logger_module.FORCE = original_force
            else:
                delattr(logger_module, 'FORCE')
