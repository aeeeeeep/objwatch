# file: objwatch/tracer.py:340-359
# asked: {"lines": [340, 341, 351, 352, 354, 355, 357, 358], "branches": [[351, 352], [351, 354], [354, 355], [354, 357]]}
# gained: {"lines": [340, 341, 351, 352, 354, 355, 357, 358], "branches": [[351, 352], [351, 354], [354, 355], [354, 357]]}

import pytest
from unittest.mock import Mock, patch
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerShouldTraceGlobal:
    """Test cases for Tracer._should_trace_global method to achieve full coverage."""

    def test_should_trace_global_with_globals_disabled(self):
        """Test that _should_trace_global returns False when with_globals is False."""
        config = ObjWatchConfig(targets=["test_module"], with_globals=False)
        tracer = Tracer(config)

        result = tracer._should_trace_global("test_module", "test_global")
        assert result is False

    def test_should_trace_global_with_empty_global_index(self):
        """Test that _should_trace_global returns True for non-builtin globals when global_index is empty."""
        config = ObjWatchConfig(targets=["test_module"], with_globals=True)
        tracer = Tracer(config)
        tracer.global_index = {}
        tracer.builtin_fields = {"__builtins__", "self", "__name__"}

        # Test with non-builtin global
        result = tracer._should_trace_global("test_module", "custom_global")
        assert result is True

        # Test with builtin global
        result = tracer._should_trace_global("test_module", "__builtins__")
        assert result is False

    def test_should_trace_global_with_global_index(self):
        """Test that _should_trace_global correctly checks global_index and exclude_global_index."""
        config = ObjWatchConfig(targets=["test_module"], with_globals=True)
        tracer = Tracer(config)
        tracer.global_index = {"test_module": {"global1", "global2", "global3"}}
        tracer.exclude_global_index = {"test_module": {"global2"}}
        tracer.builtin_fields = set()

        # Test global in global_index and not in exclude_global_index
        result = tracer._should_trace_global("test_module", "global1")
        assert result is True

        # Test global in global_index but also in exclude_global_index
        result = tracer._should_trace_global("test_module", "global2")
        assert result is False

        # Test global not in global_index
        result = tracer._should_trace_global("test_module", "unknown_global")
        assert result is False

        # Test global in different module
        result = tracer._should_trace_global("other_module", "global1")
        assert result is False

    def test_should_trace_global_with_module_not_in_indices(self):
        """Test that _should_trace_global handles modules not present in indices."""
        config = ObjWatchConfig(targets=["test_module"], with_globals=True)
        tracer = Tracer(config)
        tracer.global_index = {"existing_module": {"some_global"}}
        tracer.exclude_global_index = {"existing_module": set()}
        tracer.builtin_fields = set()

        # Test module not in global_index
        result = tracer._should_trace_global("non_existent_module", "any_global")
        assert result is False

        # Test module not in exclude_global_index
        result = tracer._should_trace_global("non_existent_module", "any_global")
        assert result is False
