# file: objwatch/tracer.py:238-254
# asked: {"lines": [238, 248, 249, 250, 251, 252, 253, 254], "branches": [[248, 249], [248, 254], [249, 250], [249, 252]]}
# gained: {"lines": [238, 248, 249, 250, 251, 252, 253, 254], "branches": [[248, 249], [248, 254], [249, 250], [249, 252]]}

import pytest
from unittest.mock import Mock, patch
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig
from objwatch.wrappers import ABCWrapper
from objwatch.utils.logger import log_warn, log_error


class TestWrapper(ABCWrapper):
    """Test wrapper implementation for testing."""

    def wrap_call(self, func_name, frame):
        return f"call:{func_name}"

    def wrap_return(self, func_name, result):
        return f"return:{func_name}:{result}"

    def wrap_upd(self, old_value, current_value):
        return f"old:{old_value}", f"new:{current_value}"


class InvalidWrapper:
    """Invalid wrapper that is not a subclass of ABCWrapper."""

    pass


class TestTracerLoadWrapper:
    """Test cases for Tracer.load_wrapper method."""

    def test_load_wrapper_with_valid_subclass(self, monkeypatch):
        """Test loading a valid wrapper subclass of ABCWrapper."""
        config = ObjWatchConfig(targets=["test_module"])
        tracer = Tracer(config)

        # Mock the log_warn function to verify it's called
        mock_log_warn = Mock()
        monkeypatch.setattr('objwatch.tracer.log_warn', mock_log_warn)

        # Load the valid wrapper
        result = tracer.load_wrapper(TestWrapper)

        # Verify the wrapper was initialized and returned
        assert isinstance(result, TestWrapper)

        # Verify log_warn was called with the correct message
        mock_log_warn.assert_called_once_with(f"wrapper 'TestWrapper' loaded")

    def test_load_wrapper_with_invalid_wrapper(self, monkeypatch):
        """Test loading an invalid wrapper that is not a subclass of ABCWrapper."""
        config = ObjWatchConfig(targets=["test_module"])
        tracer = Tracer(config)

        # Mock the log_error function to verify it's called
        mock_log_error = Mock()
        monkeypatch.setattr('objwatch.tracer.log_error', mock_log_error)

        # Attempt to load invalid wrapper and expect ValueError
        with pytest.raises(ValueError, match="wrapper 'InvalidWrapper' is not a subclass of ABCWrapper"):
            tracer.load_wrapper(InvalidWrapper)

        # Verify log_error was called with the correct message
        mock_log_error.assert_called_once_with(f"wrapper 'InvalidWrapper' is not a subclass of ABCWrapper")

    def test_load_wrapper_with_none(self):
        """Test loading None as wrapper (should return None)."""
        config = ObjWatchConfig(targets=["test_module"])
        tracer = Tracer(config)

        # Load None wrapper
        result = tracer.load_wrapper(None)

        # Verify None is returned
        assert result is None

    def test_load_wrapper_with_false(self):
        """Test loading False as wrapper (should return None)."""
        config = ObjWatchConfig(targets=["test_module"])
        tracer = Tracer(config)

        # Load False wrapper
        result = tracer.load_wrapper(False)

        # Verify None is returned
        assert result is None
