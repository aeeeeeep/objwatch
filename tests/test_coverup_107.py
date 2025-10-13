# file: objwatch/utils/weak.py:178-188
# asked: {"lines": [178, 188], "branches": []}
# gained: {"lines": [178, 188], "branches": []}

import pytest
from weakref import ref
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionaryKeyrefs:
    def test_keyrefs_empty(self):
        """Test keyrefs returns empty list when dictionary is empty."""
        weak_dict = WeakIdKeyDictionary()
        result = weak_dict.keyrefs()
        assert result == []
        assert isinstance(result, list)

    def test_keyrefs_with_items(self):
        """Test keyrefs returns list of weak references when dictionary has items."""

        # Use objects that can be weakly referenced
        class KeyObject:
            def __init__(self, name):
                self.name = name

        key1 = KeyObject("key1")
        key2 = KeyObject("key2")
        value1 = "value1"
        value2 = "value2"

        weak_dict = WeakIdKeyDictionary()
        weak_dict[key1] = value1
        weak_dict[key2] = value2

        result = weak_dict.keyrefs()
        assert isinstance(result, list)
        assert len(result) == 2

        # Verify the references are the same as stored in self.data
        assert result == list(weak_dict.data)

        # Verify the references are WeakIdRef instances
        for ref_obj in result:
            assert isinstance(ref_obj, WeakIdRef)

    def test_keyrefs_after_removal(self):
        """Test keyrefs returns updated list after item removal."""

        class KeyObject:
            def __init__(self, name):
                self.name = name

        key1 = KeyObject("key1")
        key2 = KeyObject("key2")
        value1 = "value1"
        value2 = "value2"

        weak_dict = WeakIdKeyDictionary()
        weak_dict[key1] = value1
        weak_dict[key2] = value2

        # Get initial keyrefs
        initial_refs = weak_dict.keyrefs()
        assert len(initial_refs) == 2

        # Remove one item
        del weak_dict[key1]

        # Get updated keyrefs
        updated_refs = weak_dict.keyrefs()
        assert len(updated_refs) == 1
        assert updated_refs == list(weak_dict.data)

    def test_keyrefs_during_iteration(self):
        """Test keyrefs works correctly during iteration."""

        class KeyObject:
            def __init__(self, name):
                self.name = name

        key1 = KeyObject("key1")
        key2 = KeyObject("key2")
        value1 = "value1"
        value2 = "value2"

        weak_dict = WeakIdKeyDictionary()
        weak_dict[key1] = value1
        weak_dict[key2] = value2

        # Use keyrefs during iteration over the dictionary
        for key_ref in weak_dict.keyrefs():
            # The references might not be live, so we need to check
            key = key_ref() if hasattr(key_ref, '__call__') else key_ref
            if key is not None:
                assert key in weak_dict
