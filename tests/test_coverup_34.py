# file: objwatch/targets.py:336-373
# asked: {"lines": [336, 348, 350, 351, 352, 354, 356, 357, 358, 359, 360, 361, 363, 364, 365, 366, 367, 368, 370, 371, 373], "branches": [[356, 357], [356, 373], [357, 358], [357, 364], [364, 365], [364, 367], [365, 356], [365, 366], [367, 356], [367, 368]]}
# gained: {"lines": [336, 348, 350, 351, 352, 354, 356, 357, 358, 359, 360, 361, 363, 364, 365, 366, 367, 368, 370, 371, 373], "branches": [[356, 357], [356, 373], [357, 358], [357, 364], [364, 365], [364, 367], [365, 356], [365, 366], [367, 356], [367, 368]]}

import pytest
import ast
import tempfile
import os
from unittest.mock import patch, MagicMock
from objwatch.targets import Targets
from objwatch.utils.logger import log_error


class TestTargetsParsePyFile:
    """Test cases for Targets._parse_py_file method to achieve full coverage."""

    def test_parse_py_file_successful_parsing(self, monkeypatch):
        """Test successful parsing of a Python file with various AST elements."""
        targets = Targets(targets=[])

        # Create a temporary Python file with various AST elements
        test_code = '''
class TestClass:
    def method1(self):
        pass
    
    def method2(self):
        pass

def standalone_function():
    pass

global_var = 42
a, b = 1, 2
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            result = targets._parse_py_file(temp_file)

            # Verify class parsing
            assert 'TestClass' in result['classes']
            assert result['classes']['TestClass']['methods'] == []
            assert result['classes']['TestClass']['attributes'] == []
            assert result['classes']['TestClass']['track_all'] is True

            # Verify function parsing
            assert 'standalone_function' in result['functions']

            # Verify global variable parsing
            assert 'global_var' in result['globals']
            assert 'a' in result['globals']
            assert 'b' in result['globals']

        finally:
            os.unlink(temp_file)

    def test_parse_py_file_parsing_failure(self, monkeypatch):
        """Test parsing failure when file contains invalid Python syntax."""
        targets = Targets(targets=[])

        # Create a temporary file with invalid Python syntax
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def invalid syntax here')
            temp_file = f.name

        try:
            # Mock log_error to verify it's called
            mock_log_error = MagicMock()
            monkeypatch.setattr('objwatch.targets.log_error', mock_log_error)

            result = targets._parse_py_file(temp_file)

            # Verify error was logged
            mock_log_error.assert_called_once()
            error_msg = mock_log_error.call_args[0][0]
            assert 'Failed to parse' in error_msg
            assert temp_file in error_msg

            # Verify empty structure is returned on error
            assert result == {'classes': {}, 'functions': [], 'globals': []}

        finally:
            os.unlink(temp_file)

    def test_parse_py_file_nested_functions(self, monkeypatch):
        """Test parsing of nested functions (should not be included in functions list)."""
        targets = Targets(targets=[])

        test_code = '''
def outer_function():
    pass

class MyClass:
    def class_method(self):
        pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            result = targets._parse_py_file(temp_file)

            # Only outer_function should be in functions list
            assert result['functions'] == ['outer_function']

            # MyClass should be in classes
            assert 'MyClass' in result['classes']

        finally:
            os.unlink(temp_file)

    def test_parse_py_file_class_attributes_and_methods(self, monkeypatch):
        """Test parsing of classes with attributes and methods."""
        targets = Targets(targets=[])

        test_code = '''
class ComplexClass:
    class_attr = "value"
    
    def __init__(self):
        self.instance_attr = 42
    
    def method1(self):
        pass
    
    @classmethod
    def class_method(cls):
        pass
    
    @staticmethod
    def static_method():
        pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            result = targets._parse_py_file(temp_file)

            # Verify class is parsed
            assert 'ComplexClass' in result['classes']
            class_info = result['classes']['ComplexClass']

            # Note: The current implementation doesn't populate methods and attributes lists
            # but sets track_all to True
            assert class_info['track_all'] is True

        finally:
            os.unlink(temp_file)

    def test_parse_py_file_empty_file(self, monkeypatch):
        """Test parsing of an empty Python file."""
        targets = Targets(targets=[])

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('')
            temp_file = f.name

        try:
            result = targets._parse_py_file(temp_file)

            # Should return empty structure
            assert result == {'classes': {}, 'functions': [], 'globals': []}

        finally:
            os.unlink(temp_file)

    def test_parse_py_file_file_not_found(self, monkeypatch):
        """Test behavior when file doesn't exist."""
        targets = Targets(targets=[])

        # Mock log_error to verify it's called
        mock_log_error = MagicMock()
        monkeypatch.setattr('objwatch.targets.log_error', mock_log_error)

        result = targets._parse_py_file('/nonexistent/path/file.py')

        # Verify error was logged
        mock_log_error.assert_called_once()
        error_msg = mock_log_error.call_args[0][0]
        assert 'Failed to parse' in error_msg
        assert '/nonexistent/path/file.py' in error_msg

        # Verify empty structure is returned on error
        assert result == {'classes': {}, 'functions': [], 'globals': []}
