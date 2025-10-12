# file: objwatch/utils/weak.py:215-217
# asked: {"lines": [215, 216, 217], "branches": []}
# gained: {"lines": [215, 216, 217], "branches": []}

import pytest
from objwatch.utils.weak import WeakIdKeyDictionary


class TestWeakIdKeyDictionaryIor:
    def test_ior_with_dict(self):
        """Test __ior__ method with a dictionary."""

        # Create objects that can be weakly referenced
        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")

        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj1] = "value1"

        other_dict = {obj2: "value2"}
        result = weak_dict.__ior__(other_dict)

        assert result is weak_dict
        assert weak_dict[obj1] == "value1"
        assert weak_dict[obj2] == "value2"

    def test_ior_with_empty_dict(self):
        """Test __ior__ method with an empty dictionary."""

        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")

        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj1] = "value1"

        empty_dict = {}
        result = weak_dict.__ior__(empty_dict)

        assert result is weak_dict
        assert weak_dict[obj1] == "value1"
        assert len(weak_dict) == 1

    def test_ior_with_weak_dict(self):
        """Test __ior__ method with another WeakIdKeyDictionary."""

        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")
        obj3 = TestObject("obj3")

        weak_dict1 = WeakIdKeyDictionary()
        weak_dict2 = WeakIdKeyDictionary()

        weak_dict1[obj1] = "value1"
        weak_dict2[obj2] = "value2"
        weak_dict2[obj3] = "value3"

        result = weak_dict1.__ior__(weak_dict2)

        assert result is weak_dict1
        assert weak_dict1[obj1] == "value1"
        assert weak_dict1[obj2] == "value2"
        assert weak_dict1[obj3] == "value3"
        assert len(weak_dict1) == 3
