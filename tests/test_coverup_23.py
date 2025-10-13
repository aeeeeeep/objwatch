# file: objwatch/utils/weak.py:57-79
# asked: {"lines": [57, 58, 60, 62, 63, 64, 65, 66, 68, 69, 70, 71, 73, 75, 76, 77, 78, 79], "branches": [[64, 0], [64, 65], [65, 66], [65, 68], [78, 0], [78, 79]]}
# gained: {"lines": [57, 58, 60, 62, 63, 64, 65, 66, 68, 69, 70, 71, 73, 75, 76, 77, 78, 79], "branches": [[64, 0], [64, 65], [65, 66], [65, 68], [78, 0], [78, 79]]}

import pytest
import gc
from weakref import ref
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionaryInit:

    def test_init_with_dict_parameter(self):
        """Test that __init__ processes dict parameter correctly (lines 78-79)"""

        # Create a custom class that can be weakly referenced
        class TestKey:
            def __init__(self, name):
                self.name = name

        key1 = TestKey("key1")
        key2 = TestKey("key2")
        test_dict = {key1: "value1", key2: "value2"}
        weak_dict = WeakIdKeyDictionary(dict=test_dict)

        # Verify the dictionary was updated with the provided dict
        assert len(weak_dict) == 2
        assert weak_dict[key1] == "value1"
        assert weak_dict[key2] == "value2"

    def test_remove_callback_during_iteration(self, monkeypatch):
        """Test remove callback when _iterating is True (lines 65-66)"""
        weak_dict = WeakIdKeyDictionary()

        # Mock _iterating to be True to trigger the pending removals path
        weak_dict._iterating = True
        weak_dict._pending_removals = []

        # Create a test key and add it to data
        test_key = object()
        weak_dict.data[test_key] = "test_value"

        # Call the remove callback directly
        weak_dict._remove(test_key)

        # Verify the key was added to pending removals instead of being deleted
        assert test_key in weak_dict._pending_removals
        assert test_key in weak_dict.data  # Should still be in data

    def test_remove_callback_key_not_found(self, monkeypatch):
        """Test remove callback when key doesn't exist in data (lines 68-71)"""
        weak_dict = WeakIdKeyDictionary()

        # Ensure _iterating is False to trigger the deletion path
        weak_dict._iterating = False

        # Create a test key that is NOT in data
        test_key = object()

        # This should not raise an exception due to the KeyError catch
        weak_dict._remove(test_key)

        # Verify no side effects
        assert len(weak_dict.data) == 0

    def test_remove_callback_successful_deletion(self):
        """Test remove callback successfully deletes existing key (lines 68-69)"""
        weak_dict = WeakIdKeyDictionary()

        # Ensure _iterating is False to trigger the deletion path
        weak_dict._iterating = False

        # Create a test key and add it to data
        test_key = object()
        weak_dict.data[test_key] = "test_value"

        # Call the remove callback
        weak_dict._remove(test_key)

        # Verify the key was deleted from data
        assert test_key not in weak_dict.data
        assert len(weak_dict.data) == 0

    def test_remove_callback_self_destroyed(self):
        """Test remove callback when self has been garbage collected (lines 63-64)"""
        # Create a weak reference to track the dictionary
        weak_dict = WeakIdKeyDictionary()
        weak_ref = ref(weak_dict)

        # Add some data
        test_key = object()
        weak_dict.data[test_key] = "test_value"

        # Get the remove callback function
        remove_callback = weak_dict._remove

        # Delete the dictionary to trigger garbage collection
        del weak_dict
        gc.collect()

        # Verify the dictionary was destroyed
        assert weak_ref() is None

        # Call the remove callback - should do nothing since self is None
        remove_callback(test_key)
        # No assertions needed - just verifying no exceptions are raised

    def test_custom_ref_type(self):
        """Test initialization with custom ref_type parameter (line 60)"""

        class CustomRefType:
            def __init__(self, key, callback=None):
                self.key = key
                self.callback = callback

        weak_dict = WeakIdKeyDictionary(ref_type=CustomRefType)
        assert weak_dict.ref_type is CustomRefType
