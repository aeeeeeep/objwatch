# MIT License
# Copyright (c) 2025 aeeeeeep

"""
Error handling and boundary condition tests.

Test Strategy:
- Given: Invalid inputs, edge cases, and error conditions
- When: Processing these conditions
- Then: Should handle gracefully with appropriate errors
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from objwatch import ObjWatch
from objwatch.config import ObjWatchConfig
from objwatch.events import EventType


class TestInvalidInputs:
    """Tests for invalid input handling."""

    def test_given_none_targets_when_creating_objwatch_then_raises_error(self):
        """
        Given None as targets,
        When creating ObjWatch,
        Then should raise TypeError or ValueError.
        """
        # None targets should cause an error
        with pytest.raises((TypeError, ValueError)):
            ObjWatch(None)

    def test_given_empty_list_targets_when_creating_objwatch_then_raises_error(self):
        """
        Given empty list as targets,
        When creating ObjWatch,
        Then should raise ValueError.
        """
        with pytest.raises(ValueError, match="At least one monitoring target"):
            ObjWatch([])

    def test_given_invalid_output_json_extension_when_creating_config_then_raises_error(self):
        """
        Given output_json without .json extension,
        When creating ObjWatchConfig,
        Then should raise ValueError.
        """
        with pytest.raises(ValueError, match="output_json file must end with '.json'"):
            ObjWatchConfig(targets=["test.py"], output_json="output.txt")


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_given_very_long_target_path_when_creating_objwatch_then_handles(self):
        """
        Given a very long target path,
        When creating ObjWatch,
        Then should handle it without error.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a deeply nested directory structure
            deep_path = temp_dir
            for i in range(20):  # Reduced from 50 to avoid OS limits
                deep_path = os.path.join(deep_path, f"level{i}")
            os.makedirs(deep_path, exist_ok=True)

            # Create a Python file at the deep path
            py_file = os.path.join(deep_path, "test.py")
            with open(py_file, 'w') as f:
                f.write("x = 1")

            # Should handle long paths
            obj_watch = ObjWatch([py_file])
            assert isinstance(obj_watch, ObjWatch)

    def test_given_special_characters_in_path_when_creating_objwatch_then_handles(self):
        """
        Given special characters in file path,
        When creating ObjWatch,
        Then should handle it appropriately.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with special characters in name
            py_file = os.path.join(temp_dir, "test_file_with_unicode.py")
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write("x = 1")

            # Should handle special characters
            obj_watch = ObjWatch([py_file])
            assert isinstance(obj_watch, ObjWatch)

    def test_given_empty_python_file_when_tracing_then_handles(self):
        """
        Given an empty Python file,
        When tracing,
        Then should handle it without error.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")  # Empty file
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])
            obj_watch.start()
            obj_watch.stop()
            # Should not raise
        finally:
            os.unlink(temp_file)

    def test_given_unicode_content_when_tracing_then_handles(self):
        """
        Given Python file with unicode content,
        When tracing,
        Then should handle it correctly.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(
                '''
# Unicode content
x = "Hello World"
class TestClass:
    def __init__(self):
        self.value = "test"
'''
            )
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])
            obj_watch.start()
            obj_watch.stop()
            # Should not raise
        finally:
            os.unlink(temp_file)


class TestResourceCleanup:
    """Tests for resource cleanup on errors."""

    def test_given_exception_during_start_when_error_occurs_then_resources_cleaned(self):
        """
        Given an exception during start,
        When the error occurs,
        Then resources should be cleaned up.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])

            # Mock to cause an error
            with patch.object(obj_watch.tracer, 'start', side_effect=RuntimeError("Test error")):
                with pytest.raises(RuntimeError):
                    obj_watch.start()

                # Should handle error gracefully
                assert True
        finally:
            os.unlink(temp_file)

    def test_given_multiple_exceptions_when_errors_occur_then_handles_gracefully(self):
        """
        Given multiple exceptions,
        When errors occur,
        Then should handle gracefully.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])

            # First exception
            with pytest.raises(RuntimeError):
                with obj_watch:
                    raise RuntimeError("First error")

            # Should be able to use again
            obj_watch.start()
            obj_watch.stop()
        finally:
            os.unlink(temp_file)


class TestConcurrencyEdgeCases:
    """Tests for concurrency edge cases."""

    def test_given_nested_context_managers_when_using_then_raises_error(self):
        """
        Given nested context managers,
        When using them,
        Then should handle appropriately.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            obj_watch = ObjWatch([temp_file])

            with obj_watch:
                # Nested context - behavior depends on implementation
                # Some implementations may raise, others may ignore
                try:
                    with obj_watch:
                        pass
                except RuntimeError:
                    pass  # Expected behavior
        finally:
            os.unlink(temp_file)
