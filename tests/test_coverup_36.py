# file: objwatch/targets.py:156-201
# asked: {"lines": [156, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 197, 198, 199, 200, 201], "branches": [[166, 167], [166, 180], [180, 181], [180, 197], [183, 184], [183, 197], [185, 186], [185, 197]]}
# gained: {"lines": [156, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 197, 198, 199, 200, 201], "branches": [[166, 167], [166, 180], [180, 181], [180, 197], [183, 184], [183, 197], [185, 186]]}

import pytest
import inspect
from types import MethodType, FunctionType
from objwatch.targets import Targets


class TestClass:
    def instance_method(self):
        pass

    @classmethod
    def class_method(cls):
        pass

    @staticmethod
    def static_method():
        pass


def regular_function():
    pass


class TestTargetsParseFunction:
    def test_parse_class_method(self):
        """Test parsing a class method (bound to class)"""
        targets = Targets([])
        result = targets._parse_function(TestClass.class_method)

        assert isinstance(result, tuple)
        assert len(result) == 2
        module_name, structure = result

        assert module_name == __name__
        assert structure == {
            'classes': {'TestClass': {'methods': ['class_method'], 'attributes': [], 'track_all': False}},
            'functions': [],
            'globals': [],
        }

    def test_parse_static_method_via_qualname(self):
        """Test parsing a static method using qualname path"""
        targets = Targets([])
        result = targets._parse_function(TestClass.static_method)

        assert isinstance(result, tuple)
        assert len(result) == 2
        module_name, structure = result

        assert module_name == __name__
        assert structure == {
            'classes': {'TestClass': {'methods': ['static_method'], 'attributes': [], 'track_all': False}},
            'functions': [],
            'globals': [],
        }

    def test_parse_regular_function(self):
        """Test parsing a regular function"""
        targets = Targets([])
        result = targets._parse_function(regular_function)

        assert isinstance(result, tuple)
        assert len(result) == 2
        module_name, structure = result

        assert module_name == __name__
        assert structure == {'classes': {}, 'functions': ['regular_function'], 'globals': []}

    def test_parse_function_without_module(self, monkeypatch):
        """Test parsing a function without a module"""
        targets = Targets([])

        # Create a function without a module
        func = lambda x: x

        # Mock inspect.getmodule to return None
        monkeypatch.setattr(inspect, 'getmodule', lambda x: None)

        result = targets._parse_function(func)

        assert isinstance(result, tuple)
        assert len(result) == 2
        module_name, structure = result

        assert module_name == ''
        assert structure == {'classes': {}, 'functions': [func.__name__], 'globals': []}

    def test_parse_class_method_without_module(self, monkeypatch):
        """Test parsing a class method without a module"""
        targets = Targets([])

        # Mock inspect.getmodule to return None for class
        original_getmodule = inspect.getmodule

        def mock_getmodule(obj):
            if obj == TestClass:
                return None
            return original_getmodule(obj)

        monkeypatch.setattr(inspect, 'getmodule', mock_getmodule)

        result = targets._parse_function(TestClass.class_method)

        assert isinstance(result, tuple)
        assert len(result) == 2
        module_name, structure = result

        assert module_name == ''
        assert structure == {
            'classes': {'TestClass': {'methods': ['class_method'], 'attributes': [], 'track_all': False}},
            'functions': [],
            'globals': [],
        }

    def test_parse_method_via_qualname_without_module(self, monkeypatch):
        """Test parsing a method via qualname without module"""
        targets = Targets([])

        # Create a mock function with qualname but no module
        class MockFunc:
            __qualname__ = 'SomeClass.some_method'
            __name__ = 'some_method'

        func = MockFunc()

        # Mock inspect.getmodule to return None
        monkeypatch.setattr(inspect, 'getmodule', lambda x: None)

        result = targets._parse_function(func)

        assert isinstance(result, tuple)
        assert len(result) == 2
        module_name, structure = result

        assert module_name == ''
        assert structure == {'classes': {}, 'functions': ['some_method'], 'globals': []}

    def test_parse_method_via_qualname_module_no_class(self, monkeypatch):
        """Test parsing a method via qualname where module exists but class doesn't"""
        targets = Targets([])

        # Create a mock function with qualname
        class MockFunc:
            __qualname__ = 'NonExistentClass.some_method'
            __name__ = 'some_method'

        func = MockFunc()

        # Mock inspect.getmodule to return a mock module with __name__ attribute
        mock_module = type('MockModule', (), {'__name__': 'test_module'})()

        monkeypatch.setattr(inspect, 'getmodule', lambda x: mock_module)

        result = targets._parse_function(func)

        assert isinstance(result, tuple)
        assert len(result) == 2
        module_name, structure = result

        # Should fall back to regular function handling
        assert module_name == 'test_module'
        assert structure == {'classes': {}, 'functions': ['some_method'], 'globals': []}

    def test_parse_method_via_qualname_module_class_not_type(self, monkeypatch):
        """Test parsing a method via qualname where class exists but is not a type"""
        targets = Targets([])

        # Create a mock function with qualname
        class MockFunc:
            __qualname__ = 'some_attr.some_method'
            __name__ = 'some_method'

        func = MockFunc()

        # Mock module with a non-type attribute and __name__
        mock_module = type('MockModule', (), {'__name__': 'test_module', 'some_attr': 'not_a_class'})()

        monkeypatch.setattr(inspect, 'getmodule', lambda x: mock_module)

        result = targets._parse_function(func)

        assert isinstance(result, tuple)
        assert len(result) == 2
        module_name, structure = result

        # Should fall back to regular function handling
        assert module_name == 'test_module'
        assert structure == {'classes': {}, 'functions': ['some_method'], 'globals': []}
