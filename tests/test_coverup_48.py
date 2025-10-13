# file: objwatch/targets.py:214-228
# asked: {"lines": [214, 223, 224, 225, 226, 227, 228], "branches": []}
# gained: {"lines": [214, 223, 224, 225, 226, 227, 228], "branches": []}

import pytest
import inspect
from unittest.mock import Mock, patch
import sys


class TestTargetsParseClass:
    """Test cases for Targets._parse_class method"""

    def test_parse_class_with_module(self):
        """Test _parse_class with a class that has a module"""
        from objwatch.targets import Targets

        # Create a mock class with a module
        mock_module = Mock()
        mock_module.__name__ = 'test_module'

        class MockClass:
            pass

        # Mock inspect.getmodule to return our mock module
        with patch('objwatch.targets.inspect.getmodule', return_value=mock_module):
            targets = Targets(targets=[])
            module_name, parsed_structure = targets._parse_class(MockClass)

            assert module_name == 'test_module'
            assert parsed_structure == {
                'classes': {'MockClass': {'methods': [], 'attributes': [], 'track_all': True}},
                'functions': [],
                'globals': [],
            }

    def test_parse_class_without_module(self):
        """Test _parse_class with a class that has no module"""
        from objwatch.targets import Targets

        class MockClass:
            pass

        # Mock inspect.getmodule to return None (no module)
        with patch('objwatch.targets.inspect.getmodule', return_value=None):
            targets = Targets(targets=[])
            module_name, parsed_structure = targets._parse_class(MockClass)

            assert module_name == ''
            assert parsed_structure == {
                'classes': {'MockClass': {'methods': [], 'attributes': [], 'track_all': True}},
                'functions': [],
                'globals': [],
            }

    def test_parse_class_with_builtin_type(self):
        """Test _parse_class with a built-in type"""
        from objwatch.targets import Targets

        # Test with a built-in type like int
        targets = Targets(targets=[])
        module_name, parsed_structure = targets._parse_class(int)

        # int should have a module (builtins)
        assert module_name == 'builtins'
        assert parsed_structure == {
            'classes': {'int': {'methods': [], 'attributes': [], 'track_all': True}},
            'functions': [],
            'globals': [],
        }

    def test_parse_class_with_custom_class_name(self):
        """Test _parse_class with a class that has a custom name"""
        from objwatch.targets import Targets

        class CustomClassName:
            pass

        targets = Targets(targets=[])
        module_name, parsed_structure = targets._parse_class(CustomClassName)

        assert parsed_structure['classes']['CustomClassName'] == {'methods': [], 'attributes': [], 'track_all': True}
