# file: objwatch/utils/weak.py:163-168
# asked: {"lines": [163, 164, 165, 166, 167, 168], "branches": [[165, 0], [165, 166], [167, 165], [167, 168]]}
# gained: {"lines": [163, 164, 165, 166, 167, 168], "branches": [[165, 0], [165, 166], [167, 168]]}

import pytest
import weakref
from objwatch.utils.weak import WeakIdKeyDictionary, _IterationGuard


class TestWeakIdKeyDictionaryKeys:
    def test_keys_iterates_over_valid_objects(self):
        """Test that keys() yields only valid objects and handles iteration guard properly."""
        # Create a WeakIdKeyDictionary
        weak_dict = WeakIdKeyDictionary()

        # Add some objects that can be weakly referenced (like custom classes)
        class TestObj:
            def __init__(self, name):
                self.name = name

        obj1 = TestObj("obj1")
        obj2 = TestObj("obj2")
        obj3 = TestObj("obj3")

        weak_dict[obj1] = "value1"
        weak_dict[obj2] = "value2"
        weak_dict[obj3] = "value3"

        # Collect keys and verify they match our objects
        keys = list(weak_dict.keys())

        assert len(keys) == 3
        assert obj1 in keys
        assert obj2 in keys
        assert obj3 in keys

        # Verify iteration guard was properly managed
        assert len(weak_dict._iterating) == 0

    def test_keys_skips_collected_objects(self):
        """Test that keys() skips objects that have been garbage collected."""
        weak_dict = WeakIdKeyDictionary()

        # Add an object and then let it be collected
        class TestObj:
            pass

        obj1 = TestObj()
        weak_dict[obj1] = "value1"

        # Create a weak reference to track when obj1 is collected
        obj1_ref = weakref.ref(obj1)

        # Force garbage collection to collect obj1
        del obj1
        import gc

        gc.collect()

        # Now obj1 should be collected, so keys() should yield nothing
        keys = list(weak_dict.keys())

        assert len(keys) == 0
        assert obj1_ref() is None

        # Verify iteration guard was properly managed
        assert len(weak_dict._iterating) == 0

    def test_keys_with_mixed_valid_and_collected_objects(self):
        """Test that keys() properly handles a mix of valid and collected objects."""
        weak_dict = WeakIdKeyDictionary()

        # Add some objects
        class TestObj:
            def __init__(self, name):
                self.name = name

        obj1 = TestObj("obj1")
        obj2 = TestObj("obj2")
        obj3 = TestObj("obj3")

        weak_dict[obj1] = "value1"
        weak_dict[obj2] = "value2"
        weak_dict[obj3] = "value3"

        # Create weak references
        obj2_ref = weakref.ref(obj2)

        # Remove reference to obj2 and force collection
        del obj2
        import gc

        gc.collect()

        # Now obj2 should be collected, but obj1 and obj3 should remain
        keys = list(weak_dict.keys())

        assert len(keys) == 2
        assert obj1 in keys
        assert obj3 in keys
        assert obj2_ref() is None

        # Verify iteration guard was properly managed
        assert len(weak_dict._iterating) == 0

    def test_keys_empty_dictionary(self):
        """Test that keys() works correctly on an empty dictionary."""
        weak_dict = WeakIdKeyDictionary()

        keys = list(weak_dict.keys())

        assert len(keys) == 0
        assert len(weak_dict._iterating) == 0

    def test_keys_iteration_guard_context_manager(self):
        """Test that the iteration guard properly manages the _iterating set."""
        weak_dict = WeakIdKeyDictionary()

        # Add an object
        class TestObj:
            pass

        obj = TestObj()
        weak_dict[obj] = "value"

        # Manually check the iteration guard behavior
        with _IterationGuard(weak_dict):
            # During iteration, the guard should be in _iterating
            assert len(weak_dict._iterating) == 1

            # Call keys() which should use the iteration guard
            keys = list(weak_dict.keys())
            assert keys == [obj]

        # After iteration, the guard should be removed
        assert len(weak_dict._iterating) == 0
