# file: objwatch/utils/weak.py:149-154
# asked: {"lines": [149, 150, 151, 152, 153, 154], "branches": []}
# gained: {"lines": [149, 150, 151, 154], "branches": []}

import pytest
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionaryContains:

    def test_contains_with_valid_key(self, monkeypatch):
        """Test __contains__ with a valid key that can be converted to WeakIdRef"""

        # Create a mock ref_type that returns a consistent reference
        class MockRef:
            def __init__(self, key):
                self.key = key

            def __hash__(self):
                return id(self.key)

            def __eq__(self, other):
                return isinstance(other, MockRef) and self.key == other.key

        def mock_ref_type(key, callback=None):
            return MockRef(key)

        d = WeakIdKeyDictionary()
        monkeypatch.setattr(d, 'ref_type', mock_ref_type)

        # Add a key to the data directly to simulate the dictionary state
        key = object()
        mock_ref = mock_ref_type(key)
        d.data[mock_ref] = "value"

        # This should execute lines 149-151 and 154
        # The key should be found because mock_ref_type(key) returns the same MockRef instance
        assert key in d

    def test_contains_with_invalid_key_type(self):
        """Test __contains__ with a key that raises TypeError when creating WeakIdRef"""
        d = WeakIdKeyDictionary()

        # Create a key that would cause TypeError when passed to ref_type
        # For example, using a type that cannot be weakly referenced
        class UnhashableType:
            __hash__ = None

        key = UnhashableType()

        # This should execute lines 149-153 (TypeError path)
        assert key not in d

    def test_contains_with_nonexistent_valid_key(self, monkeypatch):
        """Test __contains__ with a valid key that is not in the dictionary"""

        # Create a mock ref_type that returns a consistent reference
        class MockRef:
            def __init__(self, key):
                self.key = key

            def __hash__(self):
                return id(self.key)

            def __eq__(self, other):
                return isinstance(other, MockRef) and self.key == other.key

        def mock_ref_type(key, callback=None):
            return MockRef(key)

        d = WeakIdKeyDictionary()
        monkeypatch.setattr(d, 'ref_type', mock_ref_type)

        key = object()

        # This should execute lines 149-151 and 154 (wr not in self.data)
        assert key not in d
