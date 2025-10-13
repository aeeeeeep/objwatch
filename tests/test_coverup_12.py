# file: objwatch/utils/weak.py:135-144
# asked: {"lines": [135, 136, 138, 139, 140, 141, 142, 143, 144], "branches": [[140, 141], [140, 144], [142, 140], [142, 143]]}
# gained: {"lines": [135, 136, 138, 139, 140, 141, 142, 143, 144], "branches": [[140, 141], [140, 144], [142, 143]]}

import pytest
from objwatch.utils.weak import WeakIdKeyDictionary
from copy import deepcopy


class TestWeakIdKeyDictionaryDeepCopy:

    def test_deepcopy_with_valid_weakrefs(self):
        """Test deepcopy when all weak references are still valid."""

        # Use objects that can have weak references (custom classes)
        class TestObj:
            def __init__(self, value):
                self.value = value

            def __repr__(self):
                return f"TestObj({self.value})"

        obj1 = TestObj(1)
        obj2 = TestObj(2)
        original_dict = WeakIdKeyDictionary()
        original_dict[obj1] = [10, 20, 30]
        original_dict[obj2] = {"x": 100, "y": 200}

        # Perform deepcopy
        copied_dict = deepcopy(original_dict)

        # Verify the copy is a new instance
        assert copied_dict is not original_dict
        assert isinstance(copied_dict, WeakIdKeyDictionary)

        # Verify contents are deeply copied
        assert obj1 in copied_dict
        assert obj2 in copied_dict
        assert copied_dict[obj1] == [10, 20, 30]
        assert copied_dict[obj2] == {"x": 100, "y": 200}

        # Verify deep copy by modifying original objects
        original_dict[obj1].append(40)
        original_dict[obj2]["z"] = 300

        # Copied values should remain unchanged
        assert copied_dict[obj1] == [10, 20, 30]
        assert copied_dict[obj2] == {"x": 100, "y": 200}

        # Clean up
        del obj1, obj2, original_dict, copied_dict

    def test_deepcopy_with_expired_weakrefs(self):
        """Test deepcopy when some weak references have expired."""

        class TestObj:
            def __init__(self, value):
                self.value = value

        obj1 = TestObj(1)
        original_dict = WeakIdKeyDictionary()
        original_dict[obj1] = [10, 20, 30]

        # Create a weak reference that will expire
        def create_expired_ref():
            temp_obj = TestObj(2)
            original_dict[temp_obj] = [40, 50, 60]
            # temp_obj goes out of scope here, so its weakref should expire

        create_expired_ref()

        # Perform deepcopy - should skip expired references
        copied_dict = deepcopy(original_dict)

        # Verify only the valid reference is copied
        assert obj1 in copied_dict
        assert copied_dict[obj1] == [10, 20, 30]

        # The dictionary should only contain the valid reference
        assert len(copied_dict) == 1

        # Clean up
        del obj1, original_dict, copied_dict

    def test_deepcopy_empty_dict(self):
        """Test deepcopy of an empty WeakIdKeyDictionary."""
        original_dict = WeakIdKeyDictionary()

        # Perform deepcopy
        copied_dict = deepcopy(original_dict)

        # Verify the copy is a new instance
        assert copied_dict is not original_dict
        assert isinstance(copied_dict, WeakIdKeyDictionary)

        # Verify it's empty
        assert len(copied_dict) == 0

        # Clean up
        del original_dict, copied_dict

    def test_deepcopy_with_nested_objects(self):
        """Test deepcopy with nested objects that require memo handling."""

        class TestObj:
            def __init__(self, value):
                self.value = value

        obj1 = TestObj(1)
        obj2 = {"nested": obj1}
        original_dict = WeakIdKeyDictionary()
        original_dict[obj1] = obj2  # Circular reference

        # Perform deepcopy
        copied_dict = deepcopy(original_dict)

        # Verify the copy
        assert obj1 in copied_dict
        copied_obj2 = copied_dict[obj1]
        assert copied_obj2 is not obj2
        assert copied_obj2["nested"] is not obj1

        # Verify the nested structure is preserved
        assert copied_obj2["nested"].value == 1

        # Clean up
        del obj1, obj2, original_dict, copied_dict
