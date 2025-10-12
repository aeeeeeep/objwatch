# file: objwatch/tracer.py:256-266
# asked: {"lines": [256, 257, 266], "branches": []}
# gained: {"lines": [256, 257, 266], "branches": []}

import pytest
from unittest.mock import Mock, patch
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerShouldTraceModule:
    """Test cases for Tracer._should_trace_module method."""

    def test_should_trace_module_in_module_index_not_in_exclude(self):
        """Test that module in module_index and not in exclude_module_index returns True."""
        config = ObjWatchConfig(targets=["test_module"], exclude_targets=[])
        tracer = Tracer(config)

        # Mock the module_index to contain our test module
        tracer.module_index = {"test_module"}
        tracer.exclude_module_index = set()

        # Clear the cache to ensure fresh test
        tracer._should_trace_module.cache_clear()

        result = tracer._should_trace_module("test_module")
        assert result is True

    def test_should_trace_module_in_module_index_and_in_exclude(self):
        """Test that module in module_index but also in exclude_module_index returns False."""
        config = ObjWatchConfig(targets=["test_module"], exclude_targets=["test_module"])
        tracer = Tracer(config)

        # Mock the module_index and exclude_module_index
        tracer.module_index = {"test_module"}
        tracer.exclude_module_index = {"test_module"}

        # Clear the cache to ensure fresh test
        tracer._should_trace_module.cache_clear()

        result = tracer._should_trace_module("test_module")
        assert result is False

    def test_should_trace_module_not_in_module_index(self):
        """Test that module not in module_index returns False."""
        config = ObjWatchConfig(targets=["other_module"], exclude_targets=[])
        tracer = Tracer(config)

        # Mock the module_index to not contain our test module
        tracer.module_index = {"other_module"}
        tracer.exclude_module_index = set()

        # Clear the cache to ensure fresh test
        tracer._should_trace_module.cache_clear()

        result = tracer._should_trace_module("test_module")
        assert result is False

    def test_should_trace_module_not_in_module_index_but_in_exclude(self):
        """Test that module not in module_index but in exclude_module_index returns False."""
        config = ObjWatchConfig(targets=["other_module"], exclude_targets=["test_module"])
        tracer = Tracer(config)

        # Mock the module_index to not contain our test module
        tracer.module_index = {"other_module"}
        tracer.exclude_module_index = {"test_module"}

        # Clear the cache to ensure fresh test
        tracer._should_trace_module.cache_clear()

        result = tracer._should_trace_module("test_module")
        assert result is False

    def test_should_trace_module_lru_cache_behavior(self):
        """Test that LRU cache works correctly for repeated calls."""
        config = ObjWatchConfig(targets=["test_module"], exclude_targets=[])
        tracer = Tracer(config)

        # Mock the module_index to contain our test module
        tracer.module_index = {"test_module"}
        tracer.exclude_module_index = set()

        # Clear the cache to ensure fresh test
        tracer._should_trace_module.cache_clear()

        # First call should compute the result
        result1 = tracer._should_trace_module("test_module")
        assert result1 is True

        # Second call with same module should use cache
        result2 = tracer._should_trace_module("test_module")
        assert result2 is True

        # Verify cache info shows hits
        cache_info = tracer._should_trace_module.cache_info()
        assert cache_info.hits >= 1

    def test_should_trace_module_with_empty_module_index(self):
        """Test that module tracing with empty module_index returns False."""
        config = ObjWatchConfig(targets=["test_module"], exclude_targets=[])
        tracer = Tracer(config)

        # Mock empty module_index (simulating no targets after processing)
        tracer.module_index = set()
        tracer.exclude_module_index = set()

        # Clear the cache to ensure fresh test
        tracer._should_trace_module.cache_clear()

        result = tracer._should_trace_module("any_module")
        assert result is False
