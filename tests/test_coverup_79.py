# file: objwatch/utils/weak.py:118-119
# asked: {"lines": [118, 119], "branches": []}
# gained: {"lines": [118, 119], "branches": []}

import pytest
from objwatch.utils.weak import WeakIdKeyDictionary


class TestWeakIdKeyDictionary:
    def test_repr(self):
        """Test that __repr__ method returns expected format"""
        weak_dict = WeakIdKeyDictionary()
        repr_str = repr(weak_dict)
        assert repr_str.startswith("<WeakIdKeyDictionary at 0x")
        assert repr_str.endswith(">")
        assert "WeakIdKeyDictionary" in repr_str
