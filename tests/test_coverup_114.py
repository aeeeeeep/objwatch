# file: objwatch/utils/weak.py:226-232
# asked: {"lines": [226, 227, 228, 229, 230, 231, 232], "branches": [[227, 228], [227, 232]]}
# gained: {"lines": [226, 227, 228, 229, 230, 231, 232], "branches": [[227, 228], [227, 232]]}

import pytest
from collections.abc import Mapping
from collections import OrderedDict


class TestWeakIdKeyDictionaryRor:

    def test_ror_with_mapping(self):
        """Test __ror__ with a regular mapping object containing only weak-referenceable objects"""
        from objwatch.utils.weak import WeakIdKeyDictionary

        # Create a WeakIdKeyDictionary with some data
        # Use objects that can be weakly referenced (like custom classes)
        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")
        obj3 = TestObject("obj3")

        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj1] = "value1"
        weak_dict[obj2] = "value2"

        # Create a regular mapping with only weak-referenceable objects
        regular_dict = {obj1: "regular_value1", obj3: "value3"}

        # Test the reverse or operation: weak_dict.__ror__(regular_dict)
        # This is called when doing: regular_dict | weak_dict
        result = weak_dict.__ror__(regular_dict)

        # The result should be a new WeakIdKeyDictionary containing merged data
        # Note: The order of updates matters - self.update(other) then self.update(self)
        # So self values should take precedence over other values
        assert isinstance(result, WeakIdKeyDictionary)
        assert result[obj1] == "value1"  # weak_dict value takes precedence (self.update(self) last)
        assert result[obj2] == "value2"  # weak_dict value
        assert result[obj3] == "value3"  # regular_dict value

        # Clean up - ensure no references remain
        del obj1, obj2, obj3, regular_dict, weak_dict, result

    def test_ror_with_non_mapping(self):
        """Test __ror__ with a non-mapping object returns NotImplemented"""
        from objwatch.utils.weak import WeakIdKeyDictionary

        weak_dict = WeakIdKeyDictionary()

        # Test with a non-mapping object (list)
        non_mapping = [1, 2, 3]
        result = weak_dict.__ror__(non_mapping)

        # Should return NotImplemented for non-mapping types
        assert result is NotImplemented

        # Clean up
        del weak_dict, non_mapping

    def test_ror_with_ordered_dict(self):
        """Test __ror__ with OrderedDict containing only weak-referenceable objects"""
        from objwatch.utils.weak import WeakIdKeyDictionary

        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")
        obj3 = TestObject("obj3")

        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj1] = "weak_value1"
        weak_dict[obj2] = "weak_value2"

        # Use OrderedDict with only weak-referenceable objects
        ordered_dict = OrderedDict([(obj1, "ordered_value1"), (obj3, "value3")])

        result = weak_dict.__ror__(ordered_dict)

        assert isinstance(result, WeakIdKeyDictionary)
        assert result[obj1] == "weak_value1"  # weak_dict value takes precedence (self.update(self) last)
        assert result[obj2] == "weak_value2"  # weak_dict value
        assert result[obj3] == "value3"  # ordered_dict value

        # Clean up
        del obj1, obj2, obj3, weak_dict, ordered_dict, result

    def test_ror_empty_weak_dict(self):
        """Test __ror__ when WeakIdKeyDictionary is empty"""
        from objwatch.utils.weak import WeakIdKeyDictionary

        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")

        weak_dict = WeakIdKeyDictionary()
        regular_dict = {obj1: "value1", obj2: "value2"}

        result = weak_dict.__ror__(regular_dict)

        assert isinstance(result, WeakIdKeyDictionary)
        assert len(result) == 2
        assert result[obj1] == "value1"
        assert result[obj2] == "value2"

        # Clean up
        del obj1, obj2, weak_dict, regular_dict, result

    def test_ror_empty_other_dict(self):
        """Test __ror__ when the other mapping is empty"""
        from objwatch.utils.weak import WeakIdKeyDictionary

        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")

        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj1] = "value1"
        weak_dict[obj2] = "value2"

        empty_dict = {}

        result = weak_dict.__ror__(empty_dict)

        assert isinstance(result, WeakIdKeyDictionary)
        assert len(result) == 2
        assert result[obj1] == "value1"
        assert result[obj2] == "value2"

        # Clean up
        del obj1, obj2, weak_dict, empty_dict, result
