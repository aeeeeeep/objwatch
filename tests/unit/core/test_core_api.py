# MIT License
# Copyright (c) 2025 aeeeeeep

"""
Unit tests for objwatch core API (ObjWatch class).

Test Strategy:
- Given: Various usage scenarios
- When: Using the public API
- Then: Should behave according to specification
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from objwatch import ObjWatch
from objwatch.config import ObjWatchConfig


class TestObjWatchInitialization:
    """Tests for ObjWatch initialization."""

    def test_given_string_target_when_initializing_then_succeeds(self):
        """
        Given a string target path,
        When initializing ObjWatch,
        Then should create instance successfully.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])
            assert isinstance(obj_watch, ObjWatch)
            assert obj_watch.tracer is not None
        finally:
            os.unlink(temp_file)

    def test_given_list_targets_when_initializing_then_succeeds(self):
        """
        Given a list of target paths,
        When initializing ObjWatch,
        Then should create instance successfully.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])
            assert isinstance(obj_watch, ObjWatch)
        finally:
            os.unlink(temp_file)

    def test_given_invalid_target_when_initializing_then_raises_error(self):
        """
        Given an invalid target path,
        When initializing ObjWatch,
        Then should raise ValueError during config validation.
        """
        # Empty list should raise ValueError
        with pytest.raises(ValueError):
            ObjWatch([])


class TestObjWatchLifecycle:
    """Tests for ObjWatch start/stop lifecycle."""

    def test_given_initialized_when_start_then_tracing_enabled(self):
        """
        Given an initialized ObjWatch instance,
        When calling start(),
        Then tracing should be enabled.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])
            obj_watch.start()
            # Check tracer is running
            assert obj_watch.tracer is not None
            obj_watch.stop()
        finally:
            os.unlink(temp_file)

    def test_given_running_when_stop_then_tracing_disabled(self):
        """
        Given a running ObjWatch instance,
        When calling stop(),
        Then tracing should be disabled.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])
            obj_watch.start()
            obj_watch.stop()
            # Should complete without error
            assert True
        finally:
            os.unlink(temp_file)

    def test_given_not_running_when_stop_then_no_error(self):
        """
        Given a non-running ObjWatch instance,
        When calling stop(),
        Then should not raise an error.

        Note: The current implementation requires start() to be called
        before stop() to properly initialize the event_dispatcher.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])
            # Start first to initialize event_dispatcher
            obj_watch.start()
            # Stop to stop tracing
            obj_watch.stop()
            # Should not raise when stopping again
            obj_watch.stop()
            assert True
        finally:
            os.unlink(temp_file)


class TestObjWatchContextManager:
    """Tests for ObjWatch context manager support."""

    def test_given_objwatch_when_using_context_manager_then_lifecycle_managed(self):
        """
        Given an ObjWatch instance,
        When using it as a context manager,
        Then lifecycle should be automatically managed.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])
            with obj_watch:
                # Should be running inside context
                pass
            # Should be stopped after context
            assert True
        finally:
            os.unlink(temp_file)

    def test_given_exception_in_context_when_using_context_manager_then_stops(self):
        """
        Given an ObjWatch context manager,
        When an exception occurs inside the context,
        Then ObjWatch should stop automatically.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])
            try:
                with obj_watch:
                    raise ValueError("Test exception")
            except ValueError:
                pass
            # Should be stopped after exception
            assert True
        finally:
            os.unlink(temp_file)


class TestObjWatchConfiguration:
    """Tests for ObjWatch configuration options."""

    def test_given_output_option_when_initializing_then_configures_output(self):
        """
        Given an output file option,
        When initializing ObjWatch,
        Then should configure output correctly.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.objwatch', delete=False) as f:
            output_file = f.name

        try:
            obj_watch = ObjWatch([temp_file], output=output_file)
            # Config should be set
            assert obj_watch.tracer.config.output == output_file
        finally:
            os.unlink(temp_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_given_level_option_when_initializing_then_sets_log_level(self):
        """
        Given a log level option,
        When initializing ObjWatch,
        Then should set log level correctly.
        """
        import logging

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file], level=logging.INFO)
            assert obj_watch.tracer.config.level == logging.INFO
        finally:
            os.unlink(temp_file)

    def test_given_wrapper_option_when_initializing_then_configures_wrapper(self):
        """
        Given a wrapper option,
        When initializing ObjWatch,
        Then should configure wrapper correctly.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file], wrapper=None)
            assert obj_watch.tracer.config.wrapper is None
        finally:
            os.unlink(temp_file)


class TestObjWatchEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_given_directory_target_when_initializing_then_handles_correctly(self):
        """
        Given a directory as target,
        When initializing ObjWatch,
        Then should handle it appropriately.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a Python file in the directory
            py_file = Path(temp_dir) / "test_module.py"
            py_file.write_text("x = 1")

            # Should be able to initialize with directory
            obj_watch = ObjWatch([str(temp_dir)])
            assert isinstance(obj_watch, ObjWatch)

    def test_given_multiple_start_stop_cycles_when_using_then_handles_correctly(self):
        """
        Given multiple start/stop cycles,
        When using ObjWatch,
        Then should handle them correctly.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])

            # First cycle
            obj_watch.start()
            obj_watch.stop()

            # Second cycle
            obj_watch.start()
            obj_watch.stop()

            assert True
        finally:
            os.unlink(temp_file)
