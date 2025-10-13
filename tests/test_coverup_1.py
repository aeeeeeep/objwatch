# file: objwatch/utils/weak.py:81-97
# asked: {"lines": [81, 86, 87, 88, 89, 90, 91, 92, 94, 95, 96, 97], "branches": [[88, 89]]}
# gained: {"lines": [81, 86, 87, 88, 89, 90, 91, 92, 94, 95, 96, 97], "branches": [[88, 89]]}

import pytest
from weakref import ref
from objwatch.utils.weak import WeakIdKeyDictionary


class TestWeakIdKeyDictionaryCommitRemovals:

    def test_commit_removals_empty_pending(self):
        """Test _commit_removals when _pending_removals is empty."""
        weak_dict = WeakIdKeyDictionary()
        # Initially empty, should return immediately
        weak_dict._commit_removals()
        assert len(weak_dict._pending_removals) == 0
        assert len(weak_dict.data) == 0

    def test_commit_removals_with_valid_keys(self):
        """Test _commit_removals with keys that exist in data."""
        obj1 = object()
        obj2 = object()
        weak_dict = WeakIdKeyDictionary()

        # Add objects to data
        weak_dict.data[obj1] = "value1"
        weak_dict.data[obj2] = "value2"

        # Add pending removals
        weak_dict._pending_removals = [obj1, obj2]

        # Commit removals
        weak_dict._commit_removals()

        # Verify removals were processed
        assert len(weak_dict._pending_removals) == 0
        assert len(weak_dict.data) == 0
        assert obj1 not in weak_dict.data
        assert obj2 not in weak_dict.data

    def test_commit_removals_with_missing_keys(self):
        """Test _commit_removals with keys that don't exist in data (KeyError case)."""
        obj1 = object()
        obj2 = object()
        weak_dict = WeakIdKeyDictionary()

        # Add only obj1 to data, but both to pending removals
        weak_dict.data[obj1] = "value1"
        weak_dict._pending_removals = [obj1, obj2]

        # Commit removals - should handle KeyError for obj2
        weak_dict._commit_removals()

        # Verify removals were processed
        assert len(weak_dict._pending_removals) == 0
        assert len(weak_dict.data) == 0
        assert obj1 not in weak_dict.data
        assert obj2 not in weak_dict.data

    def test_commit_removals_mixed_scenario(self):
        """Test _commit_removals with mix of existing and non-existing keys."""
        obj1 = object()
        obj2 = object()
        obj3 = object()
        weak_dict = WeakIdKeyDictionary()

        # Add some objects to data
        weak_dict.data[obj1] = "value1"
        weak_dict.data[obj3] = "value3"

        # Add pending removals including non-existent key
        weak_dict._pending_removals = [obj1, obj2, obj3]

        # Commit removals
        weak_dict._commit_removals()

        # Verify all removals processed
        assert len(weak_dict._pending_removals) == 0
        assert len(weak_dict.data) == 0
        assert obj1 not in weak_dict.data
        assert obj2 not in weak_dict.data
        assert obj3 not in weak_dict.data
