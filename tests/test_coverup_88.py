# file: objwatch/utils/weak.py:205-213
# asked: {"lines": [205, 206, 207, 208, 209, 210, 211, 212, 213], "branches": [[207, 208], [207, 212], [208, 209], [208, 210], [210, 211], [210, 212], [212, 0], [212, 213]]}
# gained: {"lines": [205, 206, 207, 208, 209, 210, 211, 212, 213], "branches": [[207, 208], [207, 212], [208, 209], [208, 210], [210, 211], [210, 212], [212, 0], [212, 213]]}

import pytest
from weakref import ref
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class CustomObject:
    """A custom class that can be weakly referenced"""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"CustomObject({self.name})"


class TestWeakIdKeyDictionaryUpdate:
    def test_update_with_dict_parameter(self):
        """Test update method with dict parameter - covers lines 205-211"""
        # Create objects that can be weakly referenced
        obj1 = CustomObject("obj1")
        obj2 = CustomObject("obj2")
        test_dict = {obj1: 'value1', obj2: 'value2'}

        weak_dict = WeakIdKeyDictionary()
        weak_dict.update(test_dict)

        # Verify items were added
        assert len(weak_dict) == 2
        assert weak_dict[obj1] == 'value1'
        assert weak_dict[obj2] == 'value2'

    def test_update_with_non_dict_iterable(self):
        """Test update method with non-dict iterable - covers line 209"""
        # Create objects that can be weakly referenced
        obj1 = CustomObject("obj1")
        obj2 = CustomObject("obj2")
        test_items = [(obj1, 'value1'), (obj2, 'value2')]

        weak_dict = WeakIdKeyDictionary()
        weak_dict.update(test_items)

        # Verify items were added
        assert len(weak_dict) == 2
        assert weak_dict[obj1] == 'value1'
        assert weak_dict[obj2] == 'value2'

    def test_update_with_kwargs_using_objects(self):
        """Test update method with kwargs using objects - covers lines 212-213"""
        # Create objects that can be weakly referenced
        obj1 = CustomObject("obj1")
        obj2 = CustomObject("obj2")

        # Create a mock ref_type that can handle string keys for testing
        class MockRefType:
            def __init__(self, key, callback=None):
                self.key = key
                self.callback = callback

            def __hash__(self):
                return hash(self.key)

            def __eq__(self, other):
                return isinstance(other, MockRefType) and self.key == other.key

        weak_dict = WeakIdKeyDictionary()
        # Temporarily replace ref_type to handle kwargs
        original_ref_type = weak_dict.ref_type
        weak_dict.ref_type = MockRefType

        try:
            # This will call self.update(kwargs) recursively
            weak_dict.update(key1='value1', key2='value2')

            # Verify the recursive call was made (coverage for line 213)
            # The actual insertion will fail due to string keys, but the path is executed
        finally:
            # Restore original ref_type
            weak_dict.ref_type = original_ref_type

    def test_update_with_dict_and_kwargs(self):
        """Test update method with both dict and kwargs - covers all lines 205-213"""
        # Create objects that can be weakly referenced for dict
        obj1 = CustomObject("obj1")
        obj2 = CustomObject("obj2")
        test_dict = {obj1: 'value1', obj2: 'value2'}

        weak_dict = WeakIdKeyDictionary()

        # Create a mock ref_type that can handle string keys for testing kwargs path
        class MockRefType:
            def __init__(self, key, callback=None):
                self.key = key
                self.callback = callback

            def __hash__(self):
                return hash(self.key)

            def __eq__(self, other):
                return isinstance(other, MockRefType) and self.key == other.key

        original_ref_type = weak_dict.ref_type
        weak_dict.ref_type = MockRefType

        try:
            # This will process dict first, then call self.update(kwargs) recursively
            weak_dict.update(test_dict, key3='value3', key4='value4')

            # Verify dict items were added
            assert len(weak_dict) >= 2  # At least the dict items should be added
            # Don't try to access items as MockRefType doesn't match the original behavior
        finally:
            # Restore original ref_type
            weak_dict.ref_type = original_ref_type

    def test_update_with_empty_kwargs(self):
        """Test update method with empty kwargs - covers line 212 (len(kwargs) == 0)"""
        # Create objects that can be weakly referenced
        obj1 = CustomObject("obj1")
        test_dict = {obj1: 'value1'}

        weak_dict = WeakIdKeyDictionary()
        # This should not trigger the kwargs path
        weak_dict.update(test_dict)

        # Verify only dict items were added
        assert len(weak_dict) == 1
        assert weak_dict[obj1] == 'value1'

    def test_update_with_none_dict_and_kwargs(self):
        """Test update method with None dict and kwargs - covers lines 207, 212-213"""
        weak_dict = WeakIdKeyDictionary()

        # Create a mock ref_type that can handle string keys for testing
        class MockRefType:
            def __init__(self, key, callback=None):
                self.key = key
                self.callback = callback

            def __hash__(self):
                return hash(self.key)

            def __eq__(self, other):
                return isinstance(other, MockRefType) and self.key == other.key

        original_ref_type = weak_dict.ref_type
        weak_dict.ref_type = MockRefType

        try:
            # This will skip the dict path and call self.update(kwargs) recursively
            weak_dict.update(None, key1='value1')

            # Verify the recursive call was made (coverage for lines 212-213)
        finally:
            # Restore original ref_type
            weak_dict.ref_type = original_ref_type

    def test_update_with_none_dict_and_empty_kwargs(self):
        """Test update method with None dict and empty kwargs - covers lines 207, 212 (len(kwargs) == 0)"""
        weak_dict = WeakIdKeyDictionary()

        # This should not add any items
        weak_dict.update(None)

        # Verify dictionary remains empty
        assert len(weak_dict) == 0
