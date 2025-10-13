# file: objwatch/utils/weak.py:219-224
# asked: {"lines": [219, 220, 221, 222, 223, 224], "branches": [[220, 221], [220, 224]]}
# gained: {"lines": [219, 220, 221, 222, 223, 224], "branches": [[220, 221], [220, 224]]}

import pytest
from collections.abc import MutableMapping
import collections.abc as _collections_abc


class MockMapping(MutableMapping):
    def __init__(self, data=None):
        self._data = data or {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


class TestWeakIdKeyDictionaryOr:
    def test_or_with_mapping(self, monkeypatch):
        """Test __or__ method with a valid Mapping object"""
        from objwatch.utils.weak import WeakIdKeyDictionary

        # Mock the ref_type to avoid weak reference issues
        class MockRef:
            def __init__(self, key, callback=None):
                self.key = key
                self.callback = callback

            def __hash__(self):
                return id(self.key)

            def __eq__(self, other):
                return isinstance(other, MockRef) and self.key == other.key

            def __call__(self):
                return self.key

        # Create a WeakIdKeyDictionary with mocked ref_type
        dict1 = WeakIdKeyDictionary()
        monkeypatch.setattr(dict1, 'ref_type', MockRef)

        # Create test objects that can be weakly referenced
        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")
        obj3 = TestObject("obj3")

        dict1[obj1] = "value1"
        dict1[obj2] = "value2"

        dict2 = MockMapping({obj3: "value3"})

        result = dict1 | dict2

        assert obj1 in result
        assert obj2 in result
        assert obj3 in result
        assert result[obj1] == "value1"
        assert result[obj2] == "value2"
        assert result[obj3] == "value3"
        assert len(result) == 3

    def test_or_with_non_mapping(self):
        """Test __or__ method with a non-Mapping object returns NotImplemented"""
        from objwatch.utils.weak import WeakIdKeyDictionary

        dict1 = WeakIdKeyDictionary()
        non_mapping = "not_a_mapping"

        result = dict1.__or__(non_mapping)
        assert result is NotImplemented
