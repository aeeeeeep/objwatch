# file: objwatch/utils/weak.py:99-102
# asked: {"lines": [99, 100, 101, 102], "branches": []}
# gained: {"lines": [99, 100, 101, 102], "branches": []}

import pytest
from objwatch.utils.weak import WeakIdKeyDictionary


class TestWeakIdKeyDictionaryScrubRemovals:

    def test_scrub_removals_with_keys_in_data(self):
        """Test _scrub_removals when pending removals contain keys that are still in data"""
        d = WeakIdKeyDictionary()

        # Directly manipulate the internal data structure to avoid WeakIdRef creation issues
        # Create some arbitrary keys that can be used in pending removals
        key1 = "test_key_1"
        key2 = "test_key_2"
        key3 = "test_key_3"

        # Add keys directly to data dictionary
        d.data[key1] = "value1"
        d.data[key2] = "value2"
        d.data[key3] = "value3"

        # Set up pending removals with keys that are in data
        d._pending_removals = [key1, key2, key3]
        d._dirty_len = True

        # Call _scrub_removals
        d._scrub_removals()

        # Verify all keys are still in pending removals since they're in data
        assert d._pending_removals == [key1, key2, key3]
        assert d._dirty_len is False

    def test_scrub_removals_with_keys_not_in_data(self):
        """Test _scrub_removals when pending removals contain keys that are not in data"""
        d = WeakIdKeyDictionary()

        # Create keys
        key_in_data = "test_key_in_data"
        key_not_in_data1 = "test_key_not_in_data1"
        key_not_in_data2 = "test_key_not_in_data2"

        # Add only one key to the data dictionary
        d.data[key_in_data] = "value1"

        # Set up pending removals with keys that are not all in data
        d._pending_removals = [key_in_data, key_not_in_data1, key_not_in_data2]
        d._dirty_len = True

        # Call _scrub_removals
        d._scrub_removals()

        # Verify only the key that was in data remains in pending removals
        assert d._pending_removals == [key_in_data]
        assert d._dirty_len is False

    def test_scrub_removals_empty_pending_removals(self):
        """Test _scrub_removals when pending removals is empty"""
        d = WeakIdKeyDictionary()

        # Add a key to the data dictionary
        key = "test_key"
        d.data[key] = "value1"

        # Set up empty pending removals
        d._pending_removals = []
        d._dirty_len = True

        # Call _scrub_removals
        d._scrub_removals()

        # Verify pending removals remains empty
        assert d._pending_removals == []
        assert d._dirty_len is False

    def test_scrub_removals_no_keys_in_data(self):
        """Test _scrub_removals when pending removals contain no keys that are in data"""
        d = WeakIdKeyDictionary()

        # Don't add any keys to the data dictionary
        # Set up pending removals with keys that are not in data
        key1 = "test_key1"
        key2 = "test_key2"
        d._pending_removals = [key1, key2]
        d._dirty_len = True

        # Call _scrub_removals
        d._scrub_removals()

        # Verify pending removals becomes empty
        assert d._pending_removals == []
        assert d._dirty_len is False
