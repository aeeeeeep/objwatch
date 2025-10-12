# file: objwatch/utils/weak.py:111-116
# asked: {"lines": [111, 112, 115, 116], "branches": [[112, 115], [112, 116]]}
# gained: {"lines": [111, 112, 115, 116], "branches": [[112, 115], [112, 116]]}

import pytest
import weakref
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionaryLen:
    def test_len_with_dirty_len_and_pending_removals(self):
        """Test __len__ when _dirty_len is True and _pending_removals is not empty."""
        # Create a dictionary and add some items using proper weak reference keys
        d = WeakIdKeyDictionary()

        # Create objects that can be weakly referenced
        class TestObject:
            pass

        key1 = TestObject()
        key2 = TestObject()

        # Manually add to data dict using proper WeakIdRef keys
        ref1 = WeakIdRef(key1, d._remove)
        ref2 = WeakIdRef(key2, d._remove)
        d.data[ref1] = "value1"
        d.data[ref2] = "value2"

        # Force _dirty_len to True and add pending removals
        d._dirty_len = True
        d._pending_removals = [ref1, ref2]

        # Call __len__ which should trigger _scrub_removals
        length = len(d)

        # Verify the result and that _scrub_removals was called
        assert length == len(d.data) - len(d._pending_removals)
        assert d._dirty_len is False  # _scrub_removals should set this to False

    def test_len_with_dirty_len_and_empty_pending_removals(self):
        """Test __len__ when _dirty_len is True but _pending_removals is empty."""
        d = WeakIdKeyDictionary()

        # Create an object that can be weakly referenced
        class TestObject:
            pass

        key = TestObject()

        # Manually add to data dict using proper WeakIdRef key
        ref_key = WeakIdRef(key, d._remove)
        d.data[ref_key] = "value"

        # Force _dirty_len to True but keep pending removals empty
        d._dirty_len = True
        d._pending_removals = []

        # Call __len__ - should not trigger _scrub_removals since pending_removals is empty
        length = len(d)

        # Verify the result
        assert length == len(d.data) - len(d._pending_removals)
        # _dirty_len should remain True since _scrub_removals wasn't called
        assert d._dirty_len is True

    def test_len_without_dirty_len(self):
        """Test __len__ when _dirty_len is False."""
        d = WeakIdKeyDictionary()

        # Create an object that can be weakly referenced
        class TestObject:
            pass

        key = TestObject()

        # Manually add to data dict using proper WeakIdRef key
        ref_key = WeakIdRef(key, d._remove)
        d.data[ref_key] = "value"

        # _dirty_len is False by default
        d._dirty_len = False
        d._pending_removals = [ref_key]  # This shouldn't matter since _dirty_len is False

        # Call __len__ - should not trigger _scrub_removals
        length = len(d)

        # Verify the result
        assert length == len(d.data) - len(d._pending_removals)
        assert d._dirty_len is False  # Should remain unchanged
