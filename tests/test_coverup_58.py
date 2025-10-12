# file: objwatch/utils/weak.py:190-196
# asked: {"lines": [190, 191, 192, 193, 194, 195, 196], "branches": [[192, 193], [195, 192], [195, 196]]}
# gained: {"lines": [190, 191, 192, 193, 194, 195, 196], "branches": [[192, 193], [195, 196]]}

import pytest
import weakref
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionaryPopitem:
    def test_popitem_returns_valid_object(self):
        """Test that popitem returns a valid object when the weak reference is still alive."""

        # Create an object that can be weakly referenced
        class TestObject:
            def __init__(self, value):
                self.value = value

        obj = TestObject("test")
        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj] = "test_value"

        # The object should still be alive, so popitem should return it
        key, value = weak_dict.popitem()
        assert key is obj
        assert value == "test_value"
        assert len(weak_dict) == 0

    def test_popitem_skips_dead_references(self):
        """Test that popitem skips dead references and continues until finding a valid one."""
        weak_dict = WeakIdKeyDictionary()

        # Create objects that can be weakly referenced
        class TestObject:
            pass

        # Create an object and add it to the dictionary
        obj1 = TestObject()
        weak_dict[obj1] = "value1"

        # Create another object and add it, then let it be garbage collected
        obj2 = TestObject()
        weak_dict[obj2] = "value2"

        # Remove the reference to obj2 so it becomes garbage collected
        del obj2

        # Force garbage collection to clean up the dead reference
        import gc

        gc.collect()

        # Now popitem should skip the dead reference for obj2 and return obj1
        key, value = weak_dict.popitem()
        assert key is obj1
        assert value == "value1"
        assert len(weak_dict) == 0

    def test_popitem_with_multiple_dead_references(self):
        """Test that popitem handles multiple dead references before finding a valid one."""
        weak_dict = WeakIdKeyDictionary()

        # Create objects that can be weakly referenced
        class TestObject:
            pass

        # Create multiple objects that will become dead references
        dead_objects = []
        for i in range(3):
            obj = TestObject()
            weak_dict[obj] = f"dead_value_{i}"
            dead_objects.append(obj)

        # Create one valid object
        valid_obj = TestObject()
        weak_dict[valid_obj] = "valid_value"

        # Remove references to the dead objects
        del dead_objects

        # Force garbage collection
        import gc

        gc.collect()

        # popitem should skip all dead references and return the valid one
        key, value = weak_dict.popitem()
        assert key is valid_obj
        assert value == "valid_value"

        # The dictionary should now be empty
        # We need to manually check if there are any remaining items
        # by calling popitem until we get an exception
        try:
            while True:
                weak_dict.popitem()
        except KeyError:
            pass  # Expected when dictionary is empty

        assert len(weak_dict) == 0

    def test_popitem_sets_dirty_len_flag(self):
        """Test that popitem sets the _dirty_len flag to True."""

        # Create an object that can be weakly referenced
        class TestObject:
            pass

        obj = TestObject()
        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj] = "test_value"

        # Initially, _dirty_len should be False
        assert not weak_dict._dirty_len

        # After popitem, _dirty_len should be True
        weak_dict.popitem()
        assert weak_dict._dirty_len

    def test_popitem_cleans_up_dead_references_after_valid_pop(self):
        """Test that popitem properly cleans up after finding a valid object."""
        weak_dict = WeakIdKeyDictionary()

        # Create objects that can be weakly referenced
        class TestObject:
            pass

        # Add some dead references
        dead_obj1 = TestObject()
        dead_obj2 = TestObject()
        weak_dict[dead_obj1] = "dead1"
        weak_dict[dead_obj2] = "dead2"

        # Add a valid object
        valid_obj = TestObject()
        weak_dict[valid_obj] = "valid"

        # Remove references to dead objects
        del dead_obj1, dead_obj2

        # Force garbage collection
        import gc

        gc.collect()

        # popitem should return the valid object
        key, value = weak_dict.popitem()
        assert key is valid_obj
        assert value == "valid"

        # The dictionary should be empty after popitem
        # Check by trying to popitem again (should raise KeyError)
        try:
            weak_dict.popitem()
            assert False, "popitem should have raised KeyError for empty dictionary"
        except KeyError:
            pass  # Expected

    def test_popitem_empty_dictionary_raises_keyerror(self):
        """Test that popitem raises KeyError when the dictionary is empty."""
        weak_dict = WeakIdKeyDictionary()

        with pytest.raises(KeyError):
            weak_dict.popitem()
