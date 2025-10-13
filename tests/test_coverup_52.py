# file: objwatch/tracer.py:91-93
# asked: {"lines": [91, 92, 93], "branches": []}
# gained: {"lines": [91, 92, 93], "branches": []}

import pytest
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerCallDepth:
    """Test cases for Tracer call_depth property."""

    def test_call_depth_property_returns_initial_value(self):
        """Test that call_depth property returns the initial _call_depth value."""
        # Arrange
        config = ObjWatchConfig(targets=["some_module"])
        tracer = Tracer(config)

        # Act
        result = tracer.call_depth

        # Assert
        assert result == 0
        assert result == tracer._call_depth

    def test_call_depth_property_returns_updated_value(self):
        """Test that call_depth property returns updated _call_depth value."""
        # Arrange
        config = ObjWatchConfig(targets=["some_module"])
        tracer = Tracer(config)
        tracer._call_depth = 5

        # Act
        result = tracer.call_depth

        # Assert
        assert result == 5
        assert result == tracer._call_depth

    def test_call_depth_property_returns_negative_value(self):
        """Test that call_depth property returns negative _call_depth value."""
        # Arrange
        config = ObjWatchConfig(targets=["some_module"])
        tracer = Tracer(config)
        tracer._call_depth = -3

        # Act
        result = tracer.call_depth

        # Assert
        assert result == -3
        assert result == tracer._call_depth
