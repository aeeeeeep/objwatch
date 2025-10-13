# file: objwatch/utils/weak.py:124-131
# asked: {"lines": [124, 125, 126, 127, 128, 129, 130, 131], "branches": [[127, 128], [127, 131], [129, 127], [129, 130]]}
# gained: {"lines": [124, 125, 126, 127, 128, 129, 130, 131], "branches": [[127, 128], [127, 131], [129, 130]]}

import pytest
import weakref
from objwatch.utils.weak import WeakIdKeyDictionary, _IterationGuard


class TestWeakIdKeyDictionaryCopy:
    def test_copy_with_valid_weak_references(self):
        """Test copy method with valid weak references that survive the copy process."""
        # Create original dictionary
        original = WeakIdKeyDictionary()

        # Create objects that support weak references
        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")

        original[obj1] = "value1"
        original[obj2] = "value2"

        # Create a copy
        copied = original.copy()

        # Verify the copy contains the same objects and values
        assert len(copied) == 2
        assert copied[obj1] == "value1"
        assert copied[obj2] == "value2"

        # Verify original is unchanged
        assert len(original) == 2
        assert original[obj1] == "value1"
        assert original[obj2] == "value2"

        # Verify they are separate instances
        original[obj1] = "modified"
        assert copied[obj1] == "value1"  # Copy should not be affected

    def test_copy_with_expired_weak_references(self):
        """Test copy method where some weak references have expired."""
        # Create original dictionary
        original = WeakIdKeyDictionary()

        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("persistent_object")
        original[obj1] = "value1"

        # Create a weak reference that will be expired
        def create_expired_reference():
            temp_obj = TestObject("temporary_object")
            original[temp_obj] = "expired_value"
            # temp_obj goes out of scope here and will be garbage collected

        create_expired_reference()

        # Force garbage collection to clean up the expired reference
        import gc

        gc.collect()

        # Create a copy - should only copy the valid reference
        copied = original.copy()

        # Verify only the valid object was copied
        assert len(copied) == 1
        assert copied[obj1] == "value1"
        # The expired reference should not be in the copy

    def test_copy_empty_dictionary(self):
        """Test copy method on an empty dictionary."""
        original = WeakIdKeyDictionary()
        copied = original.copy()

        assert len(copied) == 0
        assert isinstance(copied, WeakIdKeyDictionary)
        assert copied is not original

    def test_copy_preserves_iteration_guard_context(self):
        """Test that copy works correctly within iteration guard context."""
        original = WeakIdKeyDictionary()

        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("guard_object_1")
        obj2 = TestObject("guard_object_2")
        original[obj1] = "value1"
        original[obj2] = "value2"

        # Test that copy can be called while iterating (simulating the guard context)
        with _IterationGuard(original):
            copied = original.copy()

        # Verify the copy is correct
        assert len(copied) == 2
        assert copied[obj1] == "value1"
        assert copied[obj2] == "value2"

    def test_copy_with_mixed_valid_and_expired_references(self):
        """Test copy with a mix of valid and expired weak references."""
        original = WeakIdKeyDictionary()

        class TestObject:
            def __init__(self, name):
                self.name = name

        # Add some valid references
        valid_obj1 = TestObject("valid_object_1")
        valid_obj2 = TestObject("valid_object_2")
        original[valid_obj1] = "valid1"
        original[valid_obj2] = "valid2"

        # Add an expired reference
        def add_expired():
            expired_obj = TestObject("expired_object")
            original[expired_obj] = "expired"
            # expired_obj goes out of scope

        add_expired()

        # Force garbage collection
        import gc

        gc.collect()

        # Create copy
        copied = original.copy()

        # Verify only valid objects were copied
        assert len(copied) == 2
        assert copied[valid_obj1] == "valid1"
        assert copied[valid_obj2] == "valid2"
        # The expired reference should not be in the copy
