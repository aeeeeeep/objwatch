# file: objwatch/utils/weak.py:156-161
# asked: {"lines": [156, 157, 158, 159, 160, 161], "branches": [[158, 0], [158, 159], [160, 158], [160, 161]]}
# gained: {"lines": [156, 157, 158, 159, 160, 161], "branches": [[158, 0], [158, 159], [160, 161]]}

import pytest
import weakref
from objwatch.utils.weak import WeakIdKeyDictionary, _IterationGuard


class TestWeakIdKeyDictionaryItems:
    def test_items_yields_live_objects(self):
        """Test that items() yields only live objects and skips dead references."""

        # Create a dictionary with objects that can be weakly referenced
        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")
        obj3 = TestObject("obj3")

        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj1] = "value1"
        weak_dict[obj2] = "value2"
        weak_dict[obj3] = "value3"

        # Delete one object to create a dead reference
        del obj2

        # Collect garbage to ensure the weak reference is cleared
        import gc

        gc.collect()

        # Get items and verify only live objects are yielded
        items = list(weak_dict.items())

        # Should contain only obj1 and obj3
        expected_items = [(obj1, "value1"), (obj3, "value3")]
        assert len(items) == 2
        assert set(items) == set(expected_items)

        # Verify the dead reference (obj2) is not in the result
        for key, value in items:
            assert key is not None
            assert key in [obj1, obj3]

    def test_items_with_iteration_guard(self):
        """Test that items() properly uses _IterationGuard context manager."""
        weak_dict = WeakIdKeyDictionary()

        # Add some items with objects that can be weakly referenced
        class TestObject:
            pass

        obj1 = TestObject()
        obj2 = TestObject()
        weak_dict[obj1] = "test1"
        weak_dict[obj2] = "test2"

        # Call items() and verify it works within iteration guard
        items = list(weak_dict.items())

        assert len(items) == 2
        assert (obj1, "test1") in items
        assert (obj2, "test2") in items

        # Verify iteration guard was properly cleaned up
        assert len(weak_dict._iterating) == 0

    def test_items_empty_dict(self):
        """Test items() on an empty dictionary."""
        weak_dict = WeakIdKeyDictionary()
        items = list(weak_dict.items())
        assert items == []

    def test_items_with_mixed_live_dead_references(self):
        """Test items() with a mix of live and dead references in the data dict."""
        weak_dict = WeakIdKeyDictionary()

        # Create objects that can be weakly referenced
        class TestObject:
            pass

        live_obj1 = TestObject()
        live_obj2 = TestObject()
        dead_obj = TestObject()

        weak_dict[live_obj1] = "live1"
        weak_dict[live_obj2] = "live2"
        weak_dict[dead_obj] = "dead"

        # Create a dead reference by deleting the object and forcing garbage collection
        del dead_obj
        import gc

        gc.collect()

        # Get items - should only yield live objects
        items = list(weak_dict.items())

        assert len(items) == 2
        assert (live_obj1, "live1") in items
        assert (live_obj2, "live2") in items

        # Verify no dead references are returned
        for key, value in items:
            assert key is not None
            assert key in [live_obj1, live_obj2]

    def test_items_generator_behavior(self):
        """Test that items() returns a generator that can be consumed incrementally."""
        weak_dict = WeakIdKeyDictionary()

        class TestObject:
            pass

        obj1 = TestObject()
        obj2 = TestObject()
        obj3 = TestObject()

        weak_dict[obj1] = 1
        weak_dict[obj2] = 2
        weak_dict[obj3] = 3

        # Get the generator
        items_gen = weak_dict.items()

        # Consume first item
        first = next(items_gen)
        assert first in [(obj1, 1), (obj2, 2), (obj3, 3)]

        # Consume remaining items
        remaining = list(items_gen)
        assert len(remaining) == 2

        # All items should be unique
        all_items = [first] + remaining
        assert len(set(all_items)) == 3
