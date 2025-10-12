# file: objwatch/targets.py:138-154
# asked: {"lines": [138, 148, 149, 150, 151, 152, 153, 154], "branches": [[148, 149], [148, 150], [150, 151], [150, 152], [152, 153], [152, 154]]}
# gained: {"lines": [138, 148, 149, 150, 151, 152, 153, 154], "branches": [[148, 149], [148, 150], [150, 151], [150, 152], [152, 153], [152, 154]]}

import pytest
from types import ModuleType, FunctionType, MethodType
import sys
import types


class TestTargetsParseTarget:

    def test_parse_target_module_type(self, monkeypatch):
        """Test _parse_target with ModuleType target"""
        from objwatch.targets import Targets

        # Create a mock module
        mock_module = ModuleType('test_module')
        mock_module.__name__ = 'test_module'

        # Mock the _parse_module method
        targets = Targets([])
        expected_result = ('test_module', {'parsed': 'structure'})
        monkeypatch.setattr(targets, '_parse_module', lambda x: expected_result)

        result = targets._parse_target(mock_module)
        assert result == expected_result

    def test_parse_target_class_type(self, monkeypatch):
        """Test _parse_target with ClassType target"""
        from objwatch.targets import Targets

        # Create a mock class
        class MockClass:
            pass

        # Mock the _parse_class method
        targets = Targets([])
        expected_result = (
            'test_module',
            {'classes': {'MockClass': {'methods': [], 'attributes': [], 'track_all': True}}},
        )
        monkeypatch.setattr(targets, '_parse_class', lambda x: expected_result)

        result = targets._parse_target(MockClass)
        assert result == expected_result

    def test_parse_target_function_type(self, monkeypatch):
        """Test _parse_target with FunctionType target"""
        from objwatch.targets import Targets

        # Create a mock function
        def mock_function():
            pass

        # Mock the _parse_function method
        targets = Targets([])
        expected_result = ('test_module', {'classes': {}, 'functions': ['mock_function'], 'globals': []})
        monkeypatch.setattr(targets, '_parse_function', lambda x: expected_result)

        result = targets._parse_target(mock_function)
        assert result == expected_result

    def test_parse_target_method_type(self, monkeypatch):
        """Test _parse_target with MethodType target"""
        from objwatch.targets import Targets

        # Create a mock class with method
        class MockClass:
            def mock_method(self):
                pass

        mock_method = MockClass().mock_method

        # Mock the _parse_function method
        targets = Targets([])
        expected_result = (
            'test_module',
            {
                'classes': {'MockClass': {'methods': ['mock_method'], 'attributes': [], 'track_all': False}},
                'functions': [],
                'globals': [],
            },
        )
        monkeypatch.setattr(targets, '_parse_function', lambda x: expected_result)

        result = targets._parse_target(mock_method)
        assert result == expected_result

    def test_parse_target_string(self, monkeypatch):
        """Test _parse_target with string target"""
        from objwatch.targets import Targets

        # Mock the _parse_string method
        targets = Targets([])
        expected_result = ('test_module', {'classes': {}, 'functions': [], 'globals': []})
        monkeypatch.setattr(targets, '_parse_string', lambda x: expected_result)

        result = targets._parse_target('test_module:SomeClass')
        assert result == expected_result
