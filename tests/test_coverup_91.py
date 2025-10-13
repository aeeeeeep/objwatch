# file: objwatch/utils/weak.py:198-200
# asked: {"lines": [198, 199, 200], "branches": []}
# gained: {"lines": [198, 199, 200], "branches": []}

import pytest
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionaryPop:

    def test_pop_existing_key(self):
        """Test pop with an existing key."""
        d = WeakIdKeyDictionary()

        # Use a class instance that can be weakly referenced
        class TestKey:
            def __init__(self, value):
                self.value = value

        key = TestKey("test_key")
        value = "test_value"
        d[key] = value

        # Test pop with existing key
        result = d.pop(key)
        assert result == value
        assert key not in d
        assert d._dirty_len is True

    def test_pop_nonexistent_key_with_default(self):
        """Test pop with a non-existent key and default value."""
        d = WeakIdKeyDictionary()

        # Use a class instance that can be weakly referenced
        class TestKey:
            def __init__(self, value):
                self.value = value

        key = TestKey("test_key")

        # Test pop with non-existent key and default
        default_value = "default"
        result = d.pop(key, default_value)
        assert result == default_value
        assert d._dirty_len is True

    def test_pop_nonexistent_key_without_default(self):
        """Test pop with a non-existent key without default raises KeyError."""
        d = WeakIdKeyDictionary()

        # Use a class instance that can be weakly referenced
        class TestKey:
            def __init__(self, value):
                self.value = value

        key = TestKey("test_key")

        # Test pop with non-existent key without default
        with pytest.raises(KeyError):
            d.pop(key)
        assert d._dirty_len is True

    def test_pop_with_multiple_args(self):
        """Test pop with multiple arguments (edge case)."""
        d = WeakIdKeyDictionary()

        # Use a class instance that can be weakly referenced
        class TestKey:
            def __init__(self, value):
                self.value = value

        key = TestKey("test_key")

        # Test pop with multiple default arguments (should use first one)
        # The dict.pop method only accepts up to 2 arguments (key and default)
        # so we need to test with just one default argument
        result = d.pop(key, "default1")
        assert result == "default1"
        assert d._dirty_len is True
