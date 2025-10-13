# file: objwatch/tracer.py:95-104
# asked: {"lines": [95, 96, 97, 98, 99, 100, 104], "branches": [[97, 98], [97, 104]]}
# gained: {"lines": [95, 96, 97, 98, 99, 100, 104], "branches": [[97, 98], [97, 104]]}

import pytest
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerCallDepthSetter:
    """Test cases for Tracer.call_depth setter to achieve full coverage."""

    def test_call_depth_setter_valid_positive_value(self):
        """Test setting call_depth with a valid positive value."""
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Set a valid positive call depth
        tracer.call_depth = 5

        # Verify the value was set correctly
        assert tracer._call_depth == 5

    def test_call_depth_setter_valid_zero_value(self):
        """Test setting call_depth with zero value."""
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Set call depth to zero
        tracer.call_depth = 0

        # Verify the value was set correctly
        assert tracer._call_depth == 0

    def test_call_depth_setter_negative_value_raises_value_error(self):
        """Test setting call_depth with negative value raises ValueError."""
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Attempt to set negative call depth and verify it raises ValueError
        with pytest.raises(ValueError) as exc_info:
            tracer.call_depth = -1

        # Verify the error message contains expected content
        assert "call_depth cannot be negative" in str(exc_info.value)
        assert "Received invalid value: -1" in str(exc_info.value)
        assert "potential issue in the call stack tracking logic" in str(exc_info.value)
        assert "Please report this issue to the developers" in str(exc_info.value)
