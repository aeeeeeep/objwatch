# file: objwatch/utils/weak.py:121-122
# asked: {"lines": [121, 122], "branches": []}
# gained: {"lines": [121, 122], "branches": []}

import pytest
import weakref
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionarySetItem:

    def test_setitem_creates_weak_ref(self):
        """Test that __setitem__ creates a WeakIdRef and stores the value"""

        # Create a test object that can be weakly referenced
        class TestKey:
            def __init__(self, value):
                self.value = value

        key_obj = TestKey("test_key")
        value = "test_value"

        # Create dictionary and set item
        weak_dict = WeakIdKeyDictionary()
        weak_dict[key_obj] = value

        # Verify the value was stored
        assert weak_dict[key_obj] == value

        # Verify a WeakIdRef was created and stored in data
        assert len(weak_dict.data) == 1
        stored_ref = next(iter(weak_dict.data.keys()))
        assert isinstance(stored_ref, WeakIdRef)
        assert stored_ref() is key_obj  # Verify the weak ref points to our key

    def test_setitem_overwrites_existing_key(self):
        """Test that __setitem__ overwrites existing key with new value"""

        class TestKey:
            def __init__(self, value):
                self.value = value

        key_obj = TestKey("test_key")
        initial_value = "initial_value"
        new_value = "new_value"

        weak_dict = WeakIdKeyDictionary()
        weak_dict[key_obj] = initial_value
        assert weak_dict[key_obj] == initial_value

        # Overwrite with new value
        weak_dict[key_obj] = new_value
        assert weak_dict[key_obj] == new_value
        assert len(weak_dict.data) == 1  # Still only one entry

    def test_setitem_with_custom_ref_type(self):
        """Test that __setitem__ uses the custom ref_type when provided"""

        class TestKey:
            def __init__(self, value):
                self.value = value

        key_obj = TestKey("test_key")
        value = "test_value"

        # Create a custom ref_type that tracks calls
        class TrackingRefType:
            def __init__(self):
                self.calls = []

            def __call__(self, key, callback=None):
                self.calls.append((key, callback))
                return WeakIdRef(key, callback)

        tracking_ref_type = TrackingRefType()

        # Create dictionary with custom ref_type
        weak_dict = WeakIdKeyDictionary(ref_type=tracking_ref_type)
        weak_dict[key_obj] = value

        # Verify custom ref_type was called
        assert len(tracking_ref_type.calls) == 1
        called_key, called_callback = tracking_ref_type.calls[0]
        assert called_key is key_obj
        assert called_callback is weak_dict._remove

        # Verify value was stored correctly
        assert weak_dict[key_obj] == value

    def test_setitem_cleanup_after_key_garbage_collected(self):
        """Test that setting an item and then garbage collecting the key cleans up properly"""
        import gc

        weak_dict = WeakIdKeyDictionary()

        # Create key in separate scope to allow garbage collection
        def create_and_set():
            class TestKey:
                def __init__(self, value):
                    self.value = value

            key_obj = TestKey("test_key")
            value = "test_value"
            weak_dict[key_obj] = value
            return weakref.ref(key_obj)

        key_ref = create_and_set()

        # Force garbage collection to clean up the key
        gc.collect()

        # The dictionary should be empty after key is garbage collected
        assert len(weak_dict) == 0
        assert len(weak_dict.data) == 0
