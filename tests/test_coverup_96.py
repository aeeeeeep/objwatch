# file: objwatch/targets.py:81-92
# asked: {"lines": [81, 89, 90, 91, 92], "branches": []}
# gained: {"lines": [81, 89, 90, 91, 92], "branches": []}

import pytest
from objwatch.targets import Targets
from types import ModuleType, FunctionType, MethodType
from typing import Optional, Set


class TestTargetsInit:
    """Test cases for Targets.__init__ method to achieve full coverage."""

    def test_init_with_none_exclude_targets(self):
        """Test initialization with None exclude_targets parameter."""
        targets = ["module1", "module2"]
        exclude_targets = None

        obj = Targets(targets, exclude_targets)

        assert obj.filename_targets == set()
        assert isinstance(obj.targets, dict)
        assert isinstance(obj.exclude_targets, dict)
        assert obj.exclude_targets == {}

    def test_init_with_empty_exclude_targets(self):
        """Test initialization with empty exclude_targets list."""
        targets = ["module1", "module2"]
        exclude_targets = []

        obj = Targets(targets, exclude_targets)

        assert obj.filename_targets == set()
        assert isinstance(obj.targets, dict)
        assert isinstance(obj.exclude_targets, dict)
        assert obj.exclude_targets == {}

    def test_init_with_string_targets(self):
        """Test initialization with string targets (not list)."""
        targets = "single_module"
        exclude_targets = ["excluded_module"]

        obj = Targets(targets, exclude_targets)

        assert obj.filename_targets == set()
        assert isinstance(obj.targets, dict)
        assert isinstance(obj.exclude_targets, dict)

    def test_init_with_string_exclude_targets(self):
        """Test initialization with string exclude_targets (not list)."""
        targets = ["module1", "module2"]
        exclude_targets = "single_excluded_module"

        obj = Targets(targets, exclude_targets)

        assert obj.filename_targets == set()
        assert isinstance(obj.targets, dict)
        assert isinstance(obj.exclude_targets, dict)

    def test_init_with_py_file_targets(self):
        """Test initialization with .py file targets."""
        targets = ["test_file.py", "another_file.py"]
        exclude_targets = ["excluded_module"]  # Changed from .py file to avoid error

        obj = Targets(targets, exclude_targets)

        assert obj.filename_targets == {"test_file.py", "another_file.py"}
        assert isinstance(obj.targets, dict)
        assert isinstance(obj.exclude_targets, dict)

    def test_init_with_mixed_target_types(self):
        """Test initialization with mixed target types."""
        targets = ["module1", "test.py", "module2:Class.method()"]
        exclude_targets = ["excluded_module"]  # Changed from .py file to avoid error

        obj = Targets(targets, exclude_targets)

        assert obj.filename_targets == {"test.py"}
        assert isinstance(obj.targets, dict)
        assert isinstance(obj.exclude_targets, dict)

    def test_init_with_empty_targets(self):
        """Test initialization with empty targets list."""
        targets = []
        exclude_targets = ["excluded_module"]

        obj = Targets(targets, exclude_targets)

        assert obj.filename_targets == set()
        assert isinstance(obj.targets, dict)
        assert obj.targets == {}
        assert isinstance(obj.exclude_targets, dict)

    def test_init_with_none_targets(self):
        """Test initialization with None targets."""
        targets = None
        exclude_targets = ["excluded_module"]

        obj = Targets(targets, exclude_targets)

        assert obj.filename_targets == set()
        assert isinstance(obj.targets, dict)
        assert obj.targets == {}
        assert isinstance(obj.exclude_targets, dict)
