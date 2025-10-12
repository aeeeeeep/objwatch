# file: objwatch/utils/weak.py:202-203
# asked: {"lines": [202, 203], "branches": []}
# gained: {"lines": [202, 203], "branches": []}

import pytest
from objwatch.utils.weak import WeakIdKeyDictionary, WeakIdRef


class TestWeakIdKeyDictionarySetdefault:

    def test_setdefault_existing_key(self):
        """Test setdefault when key already exists - returns existing value"""
        d = WeakIdKeyDictionary()

        # Use a class instance that supports weak references
        class TestClass:
            def __init__(self, value):
                self.value = value

        key = TestClass("test")
        d[key] = "existing_value"

        result = d.setdefault(key, "default_value")

        assert result == "existing_value"
        assert d[key] == "existing_value"

    def test_setdefault_new_key_with_default(self):
        """Test setdefault when key doesn't exist with default value"""
        d = WeakIdKeyDictionary()

        # Use a class instance that supports weak references
        class TestClass:
            pass

        key = TestClass()

        result = d.setdefault(key, "default_value")

        assert result == "default_value"
        assert d[key] == "default_value"

    def test_setdefault_new_key_no_default(self):
        """Test setdefault when key doesn't exist without default value"""
        d = WeakIdKeyDictionary()

        # Use a class instance that supports weak references
        class TestClass:
            pass

        key = TestClass()

        result = d.setdefault(key)

        assert result is None
        assert key in d
        assert d[key] is None

    def test_setdefault_new_key_none_default(self):
        """Test setdefault when key doesn't exist with explicit None default"""
        d = WeakIdKeyDictionary()

        # Use a class instance that supports weak references
        class TestClass:
            pass

        key = TestClass()

        result = d.setdefault(key, None)

        assert result is None
        assert d[key] is None

    def test_setdefault_with_custom_ref_type(self):
        """Test setdefault with custom ref_type"""

        class CustomRef(WeakIdRef):
            pass

        d = WeakIdKeyDictionary(ref_type=CustomRef)

        # Use a class instance that supports weak references
        class TestClass:
            pass

        key = TestClass()

        result = d.setdefault(key, "custom_value")

        assert result == "custom_value"
        assert d[key] == "custom_value"

        # Verify the key is stored using CustomRef
        for ref_key in d.data.keys():
            assert isinstance(ref_key, CustomRef)
