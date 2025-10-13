# file: objwatch/targets.py:297-334
# asked: {"lines": [297, 307, 308, 309, 310, 313, 314, 315, 318, 319, 320, 321, 322, 324, 325, 326, 327, 328, 330, 331, 332, 334], "branches": [[308, 309], [308, 313], [314, 315], [314, 318], [318, 319], [318, 334], [320, 321], [320, 325], [321, 322], [321, 324], [325, 326], [325, 334]]}
# gained: {"lines": [297, 307, 308, 309, 310, 313, 314, 315, 318, 319, 320, 321, 322, 324, 325, 326, 327, 328, 330, 331, 332, 334], "branches": [[308, 309], [308, 313], [314, 315], [314, 318], [318, 319], [318, 334], [320, 321], [320, 325], [321, 322], [321, 324], [325, 326], [325, 334]]}

import pytest
import importlib
import pkgutil
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import PosixPath
import tempfile
import os


class TestTargetsParseModuleByName:
    """Test cases for Targets._parse_module_by_name method to achieve full coverage."""

    def test_parse_module_by_name_nonexistent_module(self, monkeypatch):
        """Test parsing a non-existent module returns empty structure with warning."""
        from objwatch.targets import Targets
        from objwatch.utils.logger import log_warn

        # Mock find_spec to return None for non-existent module
        mock_find_spec = Mock(return_value=None)
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)

        # Mock log_warn to capture the warning
        mock_log_warn = Mock()
        monkeypatch.setattr('objwatch.targets.log_warn', mock_log_warn)

        targets = Targets([])
        result = targets._parse_module_by_name('nonexistent.module')

        # Verify empty structure is returned
        assert result == {'classes': {}, 'functions': [], 'globals': []}
        # Verify warning was logged
        mock_log_warn.assert_called_once_with("Module nonexistent.module not found")

    def test_parse_module_by_name_non_python_file(self, monkeypatch):
        """Test parsing a module that doesn't have a .py origin file."""
        from objwatch.targets import Targets

        # Create a mock spec with non-Python origin
        mock_spec = Mock()
        mock_spec.origin = '/some/path/module.so'  # Compiled module
        mock_spec.submodule_search_locations = None

        mock_find_spec = Mock(return_value=mock_spec)
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)

        targets = Targets([])
        result = targets._parse_module_by_name('compiled.module')

        # Should return empty structure since origin is not .py
        assert result == {'classes': {}, 'functions': [], 'globals': []}

    def test_parse_module_by_name_with_python_file(self, monkeypatch):
        """Test parsing a module with a Python file origin."""
        from objwatch.targets import Targets

        # Create a temporary Python file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(
                """
class TestClass:
    def method(self):
        pass

def test_function():
    pass

GLOBAL_VAR = 42
"""
            )
            temp_file = f.name

        try:
            # Mock find_spec to return our temp file
            mock_spec = Mock()
            mock_spec.origin = temp_file
            mock_spec.submodule_search_locations = None

            mock_find_spec = Mock(return_value=mock_spec)
            monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)

            # Mock _parse_py_file to return expected structure
            targets = Targets([])
            expected_structure = {
                'classes': {'TestClass': {'methods': ['method'], 'attributes': [], 'track_all': True}},
                'functions': ['test_function'],
                'globals': ['GLOBAL_VAR'],
            }
            monkeypatch.setattr(targets, '_parse_py_file', Mock(return_value=expected_structure))

            result = targets._parse_module_by_name('test.module')

            # Verify _parse_py_file was called with the correct file path
            targets._parse_py_file.assert_called_once_with(temp_file)
            # Verify the returned structure matches
            assert result == expected_structure

        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_parse_module_by_name_recursive_with_posix_path(self, monkeypatch):
        """Test recursive parsing with PosixPath submodule locations."""
        from objwatch.targets import Targets
        from objwatch.utils.logger import log_warn

        # Create mock spec with submodule search locations containing PosixPath
        mock_spec = Mock()
        mock_spec.origin = '/some/path/__init__.py'
        mock_spec.submodule_search_locations = [PosixPath('/some/path/submodules')]

        mock_find_spec = Mock(return_value=mock_spec)
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)

        # Mock pkgutil.iter_modules to return a submodule
        mock_iter_modules = Mock(return_value=[(Mock(), 'submodule1', True)])  # (module_finder, name, is_pkg)
        monkeypatch.setattr(pkgutil, 'iter_modules', mock_iter_modules)

        # Mock _parse_py_file to return base structure
        targets = Targets([])
        base_structure = {'classes': {}, 'functions': [], 'globals': []}
        monkeypatch.setattr(targets, '_parse_py_file', Mock(return_value=base_structure))

        # Track recursive calls to submodules
        recursive_calls = []

        # Create a separate mock for recursive calls
        def mock_recursive_submodule(module_name, recursive=True):
            recursive_calls.append((module_name, recursive))
            if module_name == 'test.package.submodule1':
                return {'classes': {'SubClass': {}}, 'functions': [], 'globals': []}
            return base_structure

        # Mock the recursive calls only
        original_method = targets._parse_module_by_name

        def wrapped_method(module_name, recursive=True):
            if module_name.startswith('test.package.'):
                return mock_recursive_submodule(module_name, recursive)
            return original_method(module_name, recursive)

        monkeypatch.setattr(targets, '_parse_module_by_name', wrapped_method)

        result = targets._parse_module_by_name('test.package', recursive=True)

        # Verify recursive parsing was attempted for submodules
        assert len(recursive_calls) == 1
        assert recursive_calls[0] == ('test.package.submodule1', True)
        # Verify submodule structure was added
        assert 'submodule1' in result
        assert result['submodule1'] == {'classes': {'SubClass': {}}, 'functions': [], 'globals': []}

    def test_parse_module_by_name_recursive_with_string_path(self, monkeypatch):
        """Test recursive parsing with string submodule locations."""
        from objwatch.targets import Targets

        # Create mock spec with string submodule search locations
        mock_spec = Mock()
        mock_spec.origin = '/some/path/__init__.py'
        mock_spec.submodule_search_locations = ['/some/path/submodules']

        mock_find_spec = Mock(return_value=mock_spec)
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)

        # Mock pkgutil.iter_modules
        mock_iter_modules = Mock(return_value=[(Mock(), 'submodule2', False)])  # Not a package
        monkeypatch.setattr(pkgutil, 'iter_modules', mock_iter_modules)

        targets = Targets([])
        base_structure = {'classes': {}, 'functions': [], 'globals': []}
        monkeypatch.setattr(targets, '_parse_py_file', Mock(return_value=base_structure))

        # Track recursive calls to submodules
        recursive_calls = []

        # Create a separate mock for recursive calls
        def mock_recursive_submodule(module_name, recursive=True):
            recursive_calls.append((module_name, recursive))
            if module_name == 'test.package.submodule2':
                return {'classes': {}, 'functions': ['sub_func'], 'globals': []}
            return base_structure

        # Mock the recursive calls only
        original_method = targets._parse_module_by_name

        def wrapped_method(module_name, recursive=True):
            if module_name.startswith('test.package.'):
                return mock_recursive_submodule(module_name, recursive)
            return original_method(module_name, recursive)

        monkeypatch.setattr(targets, '_parse_module_by_name', wrapped_method)

        result = targets._parse_module_by_name('test.package', recursive=True)

        # Verify string path was used directly
        mock_iter_modules.assert_called_once_with(['/some/path/submodules'])
        # Verify recursive parsing was called for submodule
        assert len(recursive_calls) == 1
        assert recursive_calls[0] == ('test.package.submodule2', True)
        assert result['submodule2'] == {'classes': {}, 'functions': ['sub_func'], 'globals': []}

    def test_parse_module_by_name_recursive_submodule_failure(self, monkeypatch):
        """Test recursive parsing when submodule parsing fails."""
        from objwatch.targets import Targets
        from objwatch.utils.logger import log_warn

        # Create mock spec with submodule search locations
        mock_spec = Mock()
        mock_spec.origin = '/some/path/__init__.py'
        mock_spec.submodule_search_locations = ['/some/path/submodules']

        mock_find_spec = Mock(return_value=mock_spec)
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)

        # Mock pkgutil.iter_modules
        mock_iter_modules = Mock(return_value=[(Mock(), 'failing_module', True)])
        monkeypatch.setattr(pkgutil, 'iter_modules', mock_iter_modules)

        # Mock log_warn to capture the error
        mock_log_warn = Mock()
        monkeypatch.setattr('objwatch.targets.log_warn', mock_log_warn)

        targets = Targets([])
        base_structure = {'classes': {}, 'functions': [], 'globals': []}
        monkeypatch.setattr(targets, '_parse_py_file', Mock(return_value=base_structure))

        # Track recursive calls and simulate failure
        recursive_calls = []

        # Create a separate mock for recursive calls
        def mock_recursive_submodule(module_name, recursive=True):
            recursive_calls.append((module_name, recursive))
            if module_name == 'test.package.failing_module':
                raise ImportError("No module named 'failing_module'")
            return base_structure

        # Mock the recursive calls only
        original_method = targets._parse_module_by_name

        def wrapped_method(module_name, recursive=True):
            if module_name.startswith('test.package.'):
                return mock_recursive_submodule(module_name, recursive)
            return original_method(module_name, recursive)

        monkeypatch.setattr(targets, '_parse_module_by_name', wrapped_method)

        result = targets._parse_module_by_name('test.package', recursive=True)

        # Verify recursive call was made and failed
        assert len(recursive_calls) == 1
        assert recursive_calls[0] == ('test.package.failing_module', True)
        # Verify warning was logged for the failed submodule
        mock_log_warn.assert_called_once_with(
            "Failed to parse submodule 'test.package.failing_module': No module named 'failing_module'"
        )
        # Verify base structure is still returned
        assert result == base_structure

    def test_parse_module_by_name_non_recursive(self, monkeypatch):
        """Test parsing with recursive=False skips submodule parsing."""
        from objwatch.targets import Targets

        # Create mock spec that has submodule search locations
        mock_spec = Mock()
        mock_spec.origin = '/some/path/__init__.py'
        mock_spec.submodule_search_locations = ['/some/path/submodules']

        mock_find_spec = Mock(return_value=mock_spec)
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)

        targets = Targets([])
        base_structure = {'classes': {}, 'functions': [], 'globals': []}
        monkeypatch.setattr(targets, '_parse_py_file', Mock(return_value=base_structure))

        # Track if pkgutil.iter_modules was called
        iter_modules_called = False
        original_iter_modules = pkgutil.iter_modules

        def mock_iter_modules(*args, **kwargs):
            nonlocal iter_modules_called
            iter_modules_called = True
            return original_iter_modules(*args, **kwargs)

        monkeypatch.setattr(pkgutil, 'iter_modules', mock_iter_modules)

        result = targets._parse_module_by_name('test.package', recursive=False)

        # Verify pkgutil.iter_modules was NOT called (no recursive parsing)
        assert not iter_modules_called
        # Verify only base structure is returned
        assert result == base_structure

    def test_parse_module_by_name_no_submodule_locations(self, monkeypatch):
        """Test parsing when module has no submodule search locations."""
        from objwatch.targets import Targets

        # Create mock spec without submodule search locations
        mock_spec = Mock()
        mock_spec.origin = '/some/path/module.py'
        mock_spec.submodule_search_locations = None  # No submodules

        mock_find_spec = Mock(return_value=mock_spec)
        monkeypatch.setattr(importlib.util, 'find_spec', mock_find_spec)

        targets = Targets([])
        base_structure = {'classes': {}, 'functions': [], 'globals': []}
        monkeypatch.setattr(targets, '_parse_py_file', Mock(return_value=base_structure))

        # Track if pkgutil.iter_modules was called
        iter_modules_called = False
        original_iter_modules = pkgutil.iter_modules

        def mock_iter_modules(*args, **kwargs):
            nonlocal iter_modules_called
            iter_modules_called = True
            return original_iter_modules(*args, **kwargs)

        monkeypatch.setattr(pkgutil, 'iter_modules', mock_iter_modules)

        result = targets._parse_module_by_name('test.module', recursive=True)

        # Verify no recursive parsing attempted
        assert not iter_modules_called
        assert result == base_structure
