# file: objwatch/utils/weak.py:104-106
# asked: {"lines": [104, 105, 106], "branches": []}
# gained: {"lines": [104, 105, 106], "branches": []}

import pytest
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionaryDelItem:

    def test_delitem_sets_dirty_len_and_deletes_key(self):
        # Create a dictionary with test data using objects that can be weakly referenced
        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")
        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj1] = "value1"
        weak_dict[obj2] = "value2"

        # Verify initial state
        assert obj1 in weak_dict
        assert obj2 in weak_dict
        assert not weak_dict._dirty_len

        # Delete an item
        del weak_dict[obj1]

        # Verify postconditions
        assert obj1 not in weak_dict
        assert obj2 in weak_dict
        assert weak_dict._dirty_len

    def test_delitem_with_nonexistent_key_raises_keyerror(self):
        # Create a dictionary and test object
        class TestObject:
            pass

        weak_dict = WeakIdKeyDictionary()
        obj = TestObject()

        # Verify the key doesn't exist
        assert obj not in weak_dict

        # Attempt to delete non-existent key should raise KeyError
        with pytest.raises(KeyError):
            del weak_dict[obj]

        # Verify _dirty_len was still set
        assert weak_dict._dirty_len
