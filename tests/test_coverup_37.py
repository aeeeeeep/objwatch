# file: objwatch/utils/weak.py:172-176
# asked: {"lines": [172, 173, 174, 175, 176], "branches": [[174, 0], [174, 175], [175, 174], [175, 176]]}
# gained: {"lines": [172, 173, 174, 175, 176], "branches": [[174, 0], [174, 175], [175, 176]]}

import pytest
import weakref
from objwatch.utils.weak import WeakIdKeyDictionary, _IterationGuard


class TestWeakIdKeyDictionaryValues:
    def test_values_with_live_objects(self):
        """Test that values() yields values for live objects only."""

        # Use objects that can be weakly referenced
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

        # Collect values from the generator
        values_list = list(weak_dict.values())

        # All values should be present since objects are still alive
        assert len(values_list) == 3
        assert "value1" in values_list
        assert "value2" in values_list
        assert "value3" in values_list

    def test_values_with_dead_objects(self):
        """Test that values() skips values for dead objects."""

        class TestObject:
            def __init__(self, name):
                self.name = name

        obj1 = TestObject("obj1")
        obj2 = TestObject("obj2")

        weak_dict = WeakIdKeyDictionary()
        weak_dict[obj1] = "value1"
        weak_dict[obj2] = "value2"

        # Create a reference to obj2 and then delete it
        obj2_ref = weakref.ref(obj2)
        del obj2

        # Force garbage collection to clean up obj2
        import gc

        gc.collect()

        # obj2 should be dead now
        assert obj2_ref() is None

        # Collect values from the generator
        values_list = list(weak_dict.values())

        # Only value1 should be present since obj2 is dead
        assert len(values_list) == 1
        assert "value1" in values_list
        assert "value2" not in values_list

    def test_values_empty_dict(self):
        """Test that values() works correctly with an empty dictionary."""
        weak_dict = WeakIdKeyDictionary()

        # Collect values from the generator
        values_list = list(weak_dict.values())

        # Should be empty
        assert len(values_list) == 0

    def test_values_iteration_guard_context(self, monkeypatch):
        """Test that values() properly uses _IterationGuard context manager."""
        weak_dict = WeakIdKeyDictionary()

        # Track if _IterationGuard was used
        iteration_guard_used = False

        def mock_iteration_guard_init(self, container):
            nonlocal iteration_guard_used
            iteration_guard_used = True

        def mock_iteration_guard_enter(self):
            return self

        def mock_iteration_guard_exit(self, exc_type, exc_val, exc_tb):
            pass

        # Monkeypatch _IterationGuard
        monkeypatch.setattr('objwatch.utils.weak._IterationGuard.__init__', mock_iteration_guard_init)
        monkeypatch.setattr('objwatch.utils.weak._IterationGuard.__enter__', mock_iteration_guard_enter)
        monkeypatch.setattr('objwatch.utils.weak._IterationGuard.__exit__', mock_iteration_guard_exit)

        # Call values() and consume the generator
        values_gen = weak_dict.values()
        list(values_gen)

        # Verify _IterationGuard was used
        assert iteration_guard_used

    def test_values_mixed_live_dead_objects(self):
        """Test values() with a mix of live and dead objects."""

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

        # Create references and delete obj2
        obj2_ref = weakref.ref(obj2)
        del obj2

        # Force garbage collection
        import gc

        gc.collect()

        # Verify obj2 is dead
        assert obj2_ref() is None

        # Collect values
        values_list = list(weak_dict.values())

        # Should only contain values for live objects
        assert len(values_list) == 2
        assert "value1" in values_list
        assert "value3" in values_list
        assert "value2" not in values_list
