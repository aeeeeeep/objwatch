# file: objwatch/utils/weak.py:236-239
# asked: {"lines": [236, 237, 238, 239], "branches": [[237, 238], [237, 239]]}
# gained: {"lines": [236, 237, 238, 239], "branches": [[237, 238], [237, 239]]}

import pytest
from collections.abc import Mapping
from objwatch.utils.weak import WeakIdKeyDictionary


class TestWeakIdKeyDictionaryEq:
    def test_eq_with_mapping_same_content(self):
        """Test __eq__ returns True when comparing with another Mapping with same content"""

        # Create objects that can be weakly referenced
        class TestObject:
            def __init__(self, name):
                self.name = name

        dict1 = WeakIdKeyDictionary()
        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")
        dict1[obj1] = "value1"
        dict1[obj2] = "value2"

        dict2 = WeakIdKeyDictionary()
        dict2[obj1] = "value1"
        dict2[obj2] = "value2"

        assert dict1 == dict2
        assert dict2 == dict1

    def test_eq_with_mapping_different_content(self):
        """Test __eq__ returns False when comparing with another Mapping with different content"""

        class TestObject:
            def __init__(self, name):
                self.name = name

        dict1 = WeakIdKeyDictionary()
        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")
        dict1[obj1] = "value1"
        dict1[obj2] = "value2"

        dict2 = WeakIdKeyDictionary()
        dict2[obj1] = "value1"
        dict2[obj2] = "different_value"

        assert not (dict1 == dict2)
        assert not (dict2 == dict1)

    def test_eq_with_non_mapping_returns_notimplemented(self):
        """Test __eq__ returns NotImplemented when comparing with non-Mapping object"""

        class TestObject:
            def __init__(self, name):
                self.name = name

        dict1 = WeakIdKeyDictionary()
        obj1 = TestObject("obj1")
        dict1[obj1] = "value1"

        # Test with non-Mapping object
        result = dict1.__eq__("not_a_mapping")
        assert result is NotImplemented

        # Test with integer
        result = dict1.__eq__(42)
        assert result is NotImplemented

        # Test with list
        result = dict1.__eq__(["a", "b"])
        assert result is NotImplemented

    def test_eq_with_regular_dict_same_content(self):
        """Test __eq__ works correctly with regular dict containing same objects"""

        class TestObject:
            def __init__(self, name):
                self.name = name

        dict1 = WeakIdKeyDictionary()
        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")
        dict1[obj1] = "value1"
        dict1[obj2] = "value2"

        regular_dict = {obj1: "value1", obj2: "value2"}

        assert dict1 == regular_dict
        assert regular_dict == dict1

    def test_eq_with_regular_dict_different_content(self):
        """Test __eq__ returns False when comparing with regular dict with different content"""

        class TestObject:
            def __init__(self, name):
                self.name = name

        dict1 = WeakIdKeyDictionary()
        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")
        dict1[obj1] = "value1"
        dict1[obj2] = "value2"

        regular_dict = {obj1: "value1", obj2: "different_value"}

        assert not (dict1 == regular_dict)
        assert not (regular_dict == dict1)
