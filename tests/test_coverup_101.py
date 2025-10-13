# file: objwatch/utils/weak.py:146-147
# asked: {"lines": [146, 147], "branches": []}
# gained: {"lines": [146, 147], "branches": []}

import pytest
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionaryGet:
    def test_get_existing_key_returns_value(self):
        """Test that get() returns the correct value for an existing key."""

        # Use a class instance instead of object() to allow weak references
        class TestClass:
            pass

        obj = TestClass()
        d = WeakIdKeyDictionary()
        d[obj] = "test_value"

        result = d.get(obj)
        assert result == "test_value"

    def test_get_nonexistent_key_returns_default(self):
        """Test that get() returns the default value for a nonexistent key."""

        class TestClass:
            pass

        obj = TestClass()
        d = WeakIdKeyDictionary()

        result = d.get(obj, "default_value")
        assert result == "default_value"

    def test_get_nonexistent_key_returns_none_without_default(self):
        """Test that get() returns None for a nonexistent key when no default is provided."""

        class TestClass:
            pass

        obj = TestClass()
        d = WeakIdKeyDictionary()

        result = d.get(obj)
        assert result is None
