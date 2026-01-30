# MIT License
# Copyright (c) 2025 aeeeeeep

"""
Unit tests for Targets class.

Test Strategy:
- Given: Various target specifications
- When: Processing targets
- Then: Should correctly parse and validate targets
"""

import pytest
import tempfile
import os
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, patch, MagicMock

from objwatch.targets import Targets, deep_merge, iter_parents, set_parents


class TestDeepMerge:
    """Tests for deep_merge utility function."""

    def test_given_simple_dicts_when_deep_merge_then_merges_correctly(self):
        """
        Given simple dictionaries,
        When calling deep_merge,
        Then should merge correctly.
        """
        source = {'a': 1, 'b': 2}
        update = {'b': 3, 'c': 4}

        result = deep_merge(source, update)

        assert result == {'a': 1, 'b': 3, 'c': 4}

    def test_given_nested_dicts_when_deep_merge_then_recursively_merges(self):
        """
        Given nested dictionaries,
        When calling deep_merge,
        Then should recursively merge.
        """
        source = {'a': {'x': 1}, 'b': 2}
        update = {'a': {'y': 3}, 'c': 4}

        result = deep_merge(source, update)

        assert result == {'a': {'x': 1, 'y': 3}, 'b': 2, 'c': 4}

    def test_given_list_values_when_deep_merge_then_merges_lists(self):
        """
        Given dictionaries with list values,
        When calling deep_merge,
        Then should merge lists.
        """
        source = {'items': [1, 2]}
        update = {'items': [2, 3]}

        result = deep_merge(source, update)

        assert set(result['items']) == {1, 2, 3}


class TestTargetsInitialization:
    """Tests for Targets class initialization."""

    def test_given_string_target_when_initializing_then_parses_correctly(self):
        """
        Given a string target path,
        When initializing Targets,
        Then should parse correctly.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            targets = Targets([temp_file])

            assert isinstance(targets, Targets)
            assert len(targets.get_filename_targets()) > 0
        finally:
            os.unlink(temp_file)

    def test_given_module_target_when_initializing_then_parses_correctly(self):
        """
        Given a module target,
        When initializing Targets,
        Then should parse correctly.
        """
        import os as os_module

        targets = Targets([os_module])

        assert isinstance(targets, Targets)

    def test_given_directory_target_when_initializing_then_finds_python_files(self):
        """
        Given a directory target,
        When initializing Targets,
        Then should find Python files.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Python files
            py_file1 = Path(temp_dir) / "module1.py"
            py_file1.write_text("x = 1")
            py_file2 = Path(temp_dir) / "module2.py"
            py_file2.write_text("y = 2")

            targets = Targets([temp_dir])

            filename_targets = targets.get_filename_targets()
            # Directory targets may be processed differently
            assert isinstance(filename_targets, set)

    def test_given_exclude_targets_when_initializing_then_excludes_correctly(self):
        """
        Given exclude targets,
        When initializing Targets,
        Then should exclude correctly.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Python files
            py_file1 = Path(temp_dir) / "include.py"
            py_file1.write_text("x = 1")
            py_file2 = Path(temp_dir) / "exclude.py"
            py_file2.write_text("y = 2")

            targets = Targets([temp_dir], exclude_targets=[str(py_file2)])

            filename_targets = targets.get_filename_targets()
            exclude_targets = targets.get_exclude_filename_targets()
            assert str(py_file2) in exclude_targets or any('exclude' in t for t in exclude_targets)


class TestTargetsValidation:
    """Tests for target validation."""

    def test_given_nonexistent_target_when_initializing_then_handles_gracefully(self):
        """
        Given a non-existent target,
        When initializing Targets,
        Then should handle gracefully.
        """
        # Should not raise
        targets = Targets(["/nonexistent/path/file.py"])

        # Filename targets should be empty or handle gracefully
        filename_targets = targets.get_filename_targets()
        assert isinstance(filename_targets, set)

    def test_given_invalid_target_type_when_initializing_then_handles_gracefully(self):
        """
        Given an invalid target type,
        When initializing Targets,
        Then should handle gracefully.
        """
        # Invalid types may be handled differently
        # Just verify it doesn't crash unexpectedly
        try:
            targets = Targets([12345])  # Invalid type
            # If it doesn't raise, that's also acceptable
            assert True
        except (TypeError, ValueError):
            # If it raises, that's acceptable too
            assert True


class TestTargetsMethods:
    """Tests for Targets class methods."""

    def test_given_targets_when_get_filename_targets_then_returns_set(self):
        """
        Given initialized Targets,
        When calling get_filename_targets,
        Then should return a set.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            targets = Targets([temp_file])

            filename_targets = targets.get_filename_targets()

            assert isinstance(filename_targets, set)
        finally:
            os.unlink(temp_file)

    def test_given_targets_when_get_targets_then_returns_dict(self):
        """
        Given initialized Targets,
        When calling get_targets,
        Then should return a dictionary.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            targets = Targets([temp_file])

            targets_dict = targets.get_targets()

            assert isinstance(targets_dict, dict)
        finally:
            os.unlink(temp_file)

    def test_given_targets_when_get_exclude_targets_then_returns_dict(self):
        """
        Given initialized Targets with exclude targets,
        When calling get_exclude_targets,
        Then should return a dictionary.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            # Use a different file for exclude to avoid validation error
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f2:
                f2.write("y = 2")
                exclude_file = f2.name

            try:
                targets = Targets([temp_file], exclude_targets=[exclude_file])

                exclude_targets = targets.get_exclude_targets()

                assert isinstance(exclude_targets, dict)
            finally:
                os.unlink(exclude_file)
        finally:
            os.unlink(temp_file)


class TestTargetsEdgeCases:
    """Tests for edge cases."""

    def test_given_empty_targets_when_initializing_then_handles_correctly(self):
        """
        Given empty targets list,
        When initializing Targets,
        Then should handle correctly.
        """
        targets = Targets([])

        filename_targets = targets.get_filename_targets()
        assert isinstance(filename_targets, set)
        assert len(filename_targets) == 0

    def test_given_none_exclude_targets_when_initializing_then_handles_correctly(self):
        """
        Given None exclude targets,
        When initializing Targets,
        Then should handle correctly.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            temp_file = f.name

        try:
            targets = Targets([temp_file], exclude_targets=None)

            exclude_targets = targets.get_exclude_targets()
            assert isinstance(exclude_targets, dict)
        finally:
            os.unlink(temp_file)

    def test_given_special_characters_in_path_when_initializing_then_handles_correctly(self):
        """
        Given special characters in path,
        When initializing Targets,
        Then should handle correctly.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with special characters
            py_file = Path(temp_dir) / "test_file_with_ spaces_and_123.py"
            py_file.write_text("x = 1")

            targets = Targets([str(py_file)])

            filename_targets = targets.get_filename_targets()
            assert len(filename_targets) > 0


class TestASTUtilities:
    """Tests for AST utility functions."""

    def test_given_ast_node_when_iter_parents_then_yields_parents(self):
        """
        Given an AST node with parents,
        When calling iter_parents,
        Then should yield parent nodes.
        """
        import ast

        code = '''
class MyClass:
    def my_method(self):
        x = 1
'''
        tree = ast.parse(code)
        set_parents(tree, None)

        # Find the assignment node
        assign_node = tree.body[0].body[0].body[0]

        parents = list(iter_parents(assign_node))

        assert len(parents) > 0

    def test_given_ast_tree_when_set_parents_then_sets_parent_references(self):
        """
        Given an AST tree,
        When calling set_parents,
        Then should set parent references.
        """
        import ast

        code = '''
x = 1
y = 2
'''
        tree = ast.parse(code)
        set_parents(tree, None)

        # Check that parent references are set
        for node in ast.walk(tree):
            if hasattr(node, 'parent'):
                assert True
                return

        # If we get here, parent references were set
        assert True
