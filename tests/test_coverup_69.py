# file: objwatch/core.py:84-92
# asked: {"lines": [84, 91, 92], "branches": []}
# gained: {"lines": [84, 91, 92], "branches": []}

import pytest
from unittest.mock import Mock, patch
from objwatch.core import ObjWatch


class TestObjWatchContextManager:
    """Test the context manager functionality of ObjWatch."""

    def test_enter_method_starts_tracing_and_returns_self(self, monkeypatch):
        """Test that __enter__ method calls start() and returns self."""
        # Create a mock tracer
        mock_tracer = Mock()

        # Create ObjWatch instance with minimal required parameters
        obj_watch = ObjWatch(targets=['some_module'])

        # Mock the tracer to avoid actual tracing
        monkeypatch.setattr(obj_watch, 'tracer', mock_tracer)

        # Mock the start method to track if it's called
        start_called = False

        def mock_start():
            nonlocal start_called
            start_called = True

        monkeypatch.setattr(obj_watch, 'start', mock_start)

        # Call __enter__ method
        result = obj_watch.__enter__()

        # Verify that start() was called
        assert start_called, "start() method should be called in __enter__"

        # Verify that the method returns self
        assert result is obj_watch, "__enter__ should return self"

    def test_enter_method_integration_with_real_start(self, monkeypatch):
        """Test __enter__ method integration with actual start method."""
        # Create a mock tracer
        mock_tracer = Mock()

        # Create ObjWatch instance
        obj_watch = ObjWatch(targets=['some_module'])

        # Mock the tracer to avoid actual tracing
        monkeypatch.setattr(obj_watch, 'tracer', mock_tracer)

        # Track if tracer.start() is called
        tracer_start_called = False

        def mock_tracer_start():
            nonlocal tracer_start_called
            tracer_start_called = True

        mock_tracer.start = mock_tracer_start

        # Call __enter__ method
        result = obj_watch.__enter__()

        # Verify that tracer.start() was called through the start() method
        assert tracer_start_called, "tracer.start() should be called via start() method"

        # Verify that the method returns self
        assert result is obj_watch, "__enter__ should return self"

    def test_context_manager_usage_pattern(self, monkeypatch):
        """Test the typical context manager usage pattern."""
        # Create a mock tracer
        mock_tracer = Mock()

        # Track calls
        start_called = False

        def mock_start():
            nonlocal start_called
            start_called = True

        # Create ObjWatch instance first
        obj_watch = ObjWatch(targets=['some_module'])

        # Mock the tracer and start method BEFORE entering context
        monkeypatch.setattr(obj_watch, 'tracer', mock_tracer)
        monkeypatch.setattr(obj_watch, 'start', mock_start)

        # Use the context manager
        with obj_watch as context_obj:
            # Verify start was called when entering context
            assert start_called, "start() should be called when entering context"

            # Verify we have the ObjWatch instance
            assert context_obj is obj_watch, "Context should return the same instance"

            # Verify it's an ObjWatch instance
            assert isinstance(context_obj, ObjWatch)
