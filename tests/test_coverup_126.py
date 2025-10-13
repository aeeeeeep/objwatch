# file: objwatch/event_handls.py:255-305
# asked: {"lines": [255, 256, 257, 258, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 291, 292, 293, 294, 295, 296, 297, 299, 300, 301, 302, 303, 305], "branches": [[271, 272], [271, 273], [274, 275], [274, 279], [275, 276], [275, 277], [277, 278], [277, 299], [279, 280], [279, 285], [281, 282], [281, 283], [283, 284], [283, 299], [285, 286], [285, 299], [288, 291], [288, 292], [292, 293], [292, 299], [294, 295], [294, 299], [296, 297], [296, 299], [299, 300], [299, 305], [300, 301], [300, 303]]}
# gained: {"lines": [255, 256, 257, 258, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 291, 292, 293, 294, 295, 296, 297, 299, 300, 301, 302, 303, 305], "branches": [[271, 272], [271, 273], [274, 275], [274, 279], [275, 276], [275, 277], [277, 278], [277, 299], [279, 280], [279, 285], [281, 282], [281, 283], [283, 284], [283, 299], [285, 286], [288, 291], [288, 292], [292, 293], [292, 299], [294, 295], [294, 299], [296, 297], [296, 299], [299, 300], [299, 305], [300, 301]]}

import pytest
from types import FunctionType
from typing import Any, Optional
from objwatch.event_handls import EventHandls
from objwatch.constants import Constants
from enum import Enum


class TestEnum(Enum):
    VALUE1 = 1
    VALUE2 = 2


def test_format_sequence_empty_list():
    """Test formatting an empty list."""
    result = EventHandls.format_sequence([])
    assert result == "(list)[]"


def test_format_sequence_empty_tuple():
    """Test formatting an empty tuple."""
    result = EventHandls.format_sequence(())
    assert result == "(tuple)[]"


def test_format_sequence_empty_set():
    """Test formatting an empty set."""
    result = EventHandls.format_sequence(set())
    assert result == "(set)[]"


def test_format_sequence_empty_dict():
    """Test formatting an empty dict."""
    result = EventHandls.format_sequence({})
    assert result == "(dict)[]"


def test_format_sequence_list_with_log_element_types():
    """Test formatting a list with LOG_ELEMENT_TYPES."""
    seq = [1, 2, 3, 4, 5]
    result = EventHandls.format_sequence(seq, max_elements=3)
    assert result == "(list)[1, 2, 3, '... (2 more elements)']"


def test_format_sequence_tuple_with_log_element_types():
    """Test formatting a tuple with LOG_ELEMENT_TYPES."""
    seq = (1, 2, 3, 4, 5)
    result = EventHandls.format_sequence(seq, max_elements=3)
    assert result == "(tuple)[1, 2, 3, '... (2 more elements)']"


def test_format_sequence_set_with_log_element_types():
    """Test formatting a set with LOG_ELEMENT_TYPES."""
    seq = {1, 2, 3, 4, 5}
    result = EventHandls.format_sequence(seq, max_elements=3)
    assert "(set)" in result
    assert "'... (2 more elements)'" in result


def test_format_sequence_dict_with_log_element_types():
    """Test formatting a dict with LOG_ELEMENT_TYPES."""
    seq = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e'}
    result = EventHandls.format_sequence(seq, max_elements=3)
    assert result == "(dict)[(1, 'a'), (2, 'b'), (3, 'c'), '... (2 more elements)']"


def test_format_sequence_list_with_func_non_log_element_types():
    """Test formatting a list with non-LOG_ELEMENT_TYPES and custom function."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    def custom_func(elements):
        return [str(x) + "_processed" for x in elements]

    seq = [CustomClass(), CustomClass(), CustomClass(), CustomClass(), CustomClass()]
    result = EventHandls.format_sequence(seq, max_elements=3, func=custom_func)
    expected = "(list)['CustomClass()_processed', 'CustomClass()_processed', 'CustomClass()_processed', '... (2 more elements)']"
    assert result == expected


def test_format_sequence_tuple_with_func_non_log_element_types():
    """Test formatting a tuple with non-LOG_ELEMENT_TYPES and custom function."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    def custom_func(elements):
        return [str(x) + "_processed" for x in elements]

    seq = (CustomClass(), CustomClass(), CustomClass(), CustomClass(), CustomClass())
    result = EventHandls.format_sequence(seq, max_elements=3, func=custom_func)
    expected = "(tuple)['CustomClass()_processed', 'CustomClass()_processed', 'CustomClass()_processed', '... (2 more elements)']"
    assert result == expected


def test_format_sequence_set_with_func_non_log_element_types():
    """Test formatting a set with non-LOG_ELEMENT_TYPES and custom function."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    def custom_func(elements):
        return [str(x) + "_processed" for x in elements]

    seq = {CustomClass(), CustomClass(), CustomClass(), CustomClass(), CustomClass()}
    result = EventHandls.format_sequence(seq, max_elements=3, func=custom_func)
    assert "(set)" in result
    assert "_processed" in result
    assert "'... (2 more elements)'" in result


def test_format_sequence_dict_with_func_non_log_element_types():
    """Test formatting a dict with non-LOG_ELEMENT_TYPES and custom function."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    def custom_func(elements):
        return [str(x) + "_processed" for x in elements]

    seq = {
        CustomClass(): CustomClass(),
        CustomClass(): CustomClass(),
        CustomClass(): CustomClass(),
        CustomClass(): CustomClass(),
    }
    result = EventHandls.format_sequence(seq, max_elements=3, func=custom_func)
    assert "(dict)" in result
    assert "_processed" in result
    assert "'... (1 more elements)'" in result


def test_format_sequence_dict_with_func_falsy_values():
    """Test formatting a dict with a custom function that returns falsy values."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    def custom_func(elements):
        return []

    seq = {CustomClass(): 'a', CustomClass(): 'b', CustomClass(): 'c'}
    result = EventHandls.format_sequence(seq, max_elements=3, func=custom_func)
    assert result == "(dict)[3 elements]"


def test_format_sequence_list_non_log_element_types():
    """Test formatting a list with non-LOG_ELEMENT_TYPES."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    seq = [CustomClass(), CustomClass(), CustomClass()]
    result = EventHandls.format_sequence(seq, max_elements=2)
    assert result == "(list)[3 elements]"


def test_format_sequence_tuple_non_log_element_types():
    """Test formatting a tuple with non-LOG_ELEMENT_TYPES."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    seq = (CustomClass(), CustomClass(), CustomClass())
    result = EventHandls.format_sequence(seq, max_elements=2)
    assert result == "(tuple)[3 elements]"


def test_format_sequence_set_non_log_element_types():
    """Test formatting a set with non-LOG_ELEMENT_TYPES."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    seq = {CustomClass(), CustomClass(), CustomClass()}
    result = EventHandls.format_sequence(seq, max_elements=2)
    assert result == "(set)[3 elements]"


def test_format_sequence_dict_non_log_element_types():
    """Test formatting a dict with non-LOG_ELEMENT_TYPES."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    seq = {CustomClass(): CustomClass(), CustomClass(): CustomClass()}
    result = EventHandls.format_sequence(seq, max_elements=2)
    assert result == "(dict)[2 elements]"


def test_format_sequence_dict_non_log_element_types_with_func_falsy():
    """Test formatting a dict with non-LOG_ELEMENT_TYPES and custom function that returns falsy."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    def custom_func(elements):
        return []

    seq = {CustomClass(): CustomClass(), CustomClass(): CustomClass()}
    result = EventHandls.format_sequence(seq, max_elements=2, func=custom_func)
    assert result == "(dict)[2 elements]"


def test_format_sequence_with_enum_types():
    """Test formatting sequences with Enum types (which are LOG_ELEMENT_TYPES)."""
    seq = [TestEnum.VALUE1, TestEnum.VALUE2, TestEnum.VALUE1]
    result = EventHandls.format_sequence(seq, max_elements=2)
    expected = "(list)[<TestEnum.VALUE1: 1>, <TestEnum.VALUE2: 2>, '... (1 more elements)']"
    assert result == expected


def test_format_sequence_with_function_types():
    """Test formatting sequences with FunctionType (which are LOG_ELEMENT_TYPES)."""

    def test_func():
        pass

    seq = [test_func, len, str]
    result = EventHandls.format_sequence(seq, max_elements=2)
    assert result == "(list)[3 elements]"


def test_format_sequence_dict_mixed_log_element_types():
    """Test formatting a dict with mixed LOG_ELEMENT_TYPES and non-LOG_ELEMENT_TYPES."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    seq = {1: 'a', 2: CustomClass(), 3: 'c'}
    result = EventHandls.format_sequence(seq, max_elements=3)
    assert result == "(dict)[3 elements]"


def test_format_sequence_dict_with_func_non_log_element_types_keys_and_values():
    """Test formatting a dict with non-LOG_ELEMENT_TYPES keys and values, no custom function."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    seq = {CustomClass(): CustomClass(), CustomClass(): CustomClass(), CustomClass(): CustomClass()}
    result = EventHandls.format_sequence(seq, max_elements=3)
    assert result == "(dict)[3 elements]"


def test_format_sequence_dict_with_func_none_values():
    """Test formatting a dict with a custom function that returns None."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    def custom_func(elements):
        return None

    seq = {CustomClass(): 'a', CustomClass(): 'b', CustomClass(): 'c'}
    result = EventHandls.format_sequence(seq, max_elements=3, func=custom_func)
    assert result == "(dict)[3 elements]"


def test_format_sequence_dict_with_func_false_values():
    """Test formatting a dict with a custom function that returns False."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    def custom_func(elements):
        return False

    seq = {CustomClass(): 'a', CustomClass(): 'b', CustomClass(): 'c'}
    result = EventHandls.format_sequence(seq, max_elements=3, func=custom_func)
    assert result == "(dict)[3 elements]"


def test_format_sequence_dict_with_func_zero_values():
    """Test formatting a dict with a custom function that returns 0."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    def custom_func(elements):
        return 0

    seq = {CustomClass(): 'a', CustomClass(): 'b', CustomClass(): 'c'}
    result = EventHandls.format_sequence(seq, max_elements=3, func=custom_func)
    assert result == "(dict)[3 elements]"


def test_format_sequence_dict_with_func_empty_string_values():
    """Test formatting a dict with a custom function that returns empty string."""

    class CustomClass:
        def __repr__(self):
            return "CustomClass()"

    def custom_func(elements):
        return ""

    seq = {CustomClass(): 'a', CustomClass(): 'b', CustomClass(): 'c'}
    result = EventHandls.format_sequence(seq, max_elements=3, func=custom_func)
    assert result == "(dict)[3 elements]"
