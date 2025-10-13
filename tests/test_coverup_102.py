# file: objwatch/utils/weak.py:108-109
# asked: {"lines": [108, 109], "branches": []}
# gained: {"lines": [108, 109], "branches": []}

import pytest
import weakref
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionaryGetItem:
    def test_getitem_with_existing_key(self):
        """Test __getitem__ with an existing key to cover lines 108-109"""

        # Create a dictionary and add a key-value pair using a class instance
        # that can be weakly referenced
        class TestObject:
            def __init__(self, value):
                self.value = value

        obj = TestObject("test")
        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj] = "test_value"

        # Test that we can retrieve the value using the same object
        result = weak_dict[obj]
        assert result == "test_value"

    def test_getitem_with_nonexistent_key(self):
        """Test __getitem__ with a non-existent key to ensure KeyError is raised"""

        # Use a class instance that can be weakly referenced
        class TestObject:
            pass

        obj = TestObject()
        weak_dict = WeakIdKeyDictionary()

        # Test that accessing a non-existent key raises KeyError
        with pytest.raises(KeyError):
            _ = weak_dict[obj]

    def test_getitem_with_different_ref_type(self, monkeypatch):
        """Test __getitem__ with a custom ref_type to ensure ref_type is used"""
        # Create a custom ref_type that tracks calls
        call_count = 0

        class TrackingRefType:
            def __init__(self, key, callback=None):
                nonlocal call_count
                call_count += 1
                self.key = key
                self.callback = callback

            def __hash__(self):
                return hash(self.key)

            def __eq__(self, other):
                return isinstance(other, TrackingRefType) and self.key == other.key

        # Create dictionary with custom ref_type
        weak_dict = WeakIdKeyDictionary(ref_type=TrackingRefType)

        # Use a class instance that can be weakly referenced
        class TestObject:
            pass

        obj = TestObject()
        weak_dict[obj] = "test_value"

        # Reset call count and test __getitem__
        call_count = 0
        result = weak_dict[obj]

        # Verify ref_type was called and value was retrieved
        assert call_count == 1
        assert result == "test_value"
