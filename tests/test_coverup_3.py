# file: objwatch/constants.py:13-47
# asked: {"lines": [13, 14, 19, 22, 25, 29, 30, 31, 32, 33, 34, 35, 36, 41, 44, 47], "branches": []}
# gained: {"lines": [13, 14, 19, 22, 25, 29, 30, 31, 32, 33, 34, 35, 36, 41, 44, 47], "branches": []}

import pytest
from objwatch.constants import Constants
from enum import Enum
from types import FunctionType

try:
    from types import NoneType
except ImportError:
    NoneType = type(None)


class TestEnum(Enum):
    TEST_VALUE = 1


def test_constants_class_attributes():
    """Test that all Constants class attributes are accessible and have expected values."""
    assert Constants.MAX_TARGETS_DISPLAY == 8
    assert Constants.MAX_SEQUENCE_ELEMENTS == 3
    assert Constants.LOG_INDENT_LEVEL == 2
    assert Constants.HANDLE_GLOBALS_SYMBOL == "@"
    assert Constants.HANDLE_LOCALS_SYMBOL == "_"


def test_log_element_types():
    """Test that LOG_ELEMENT_TYPES contains all expected types."""
    expected_types = (bool, int, float, str, NoneType, FunctionType, Enum)
    assert Constants.LOG_ELEMENT_TYPES == expected_types

    # Test that each type in LOG_ELEMENT_TYPES is indeed a type
    for element_type in Constants.LOG_ELEMENT_TYPES:
        assert isinstance(element_type, type)


def test_log_sequence_types():
    """Test that LOG_SEQUENCE_TYPES contains all expected sequence types."""
    expected_types = (list, set, dict, tuple)
    assert Constants.LOG_SEQUENCE_TYPES == expected_types

    # Test that each type in LOG_SEQUENCE_TYPES is indeed a type
    for sequence_type in Constants.LOG_SEQUENCE_TYPES:
        assert isinstance(sequence_type, type)


def test_constants_class_docstring():
    """Test that Constants class has the expected docstring."""
    expected_docstring = "Constants class for managing magic values and configuration parameters in ObjWatch project."
    assert Constants.__doc__.strip() == expected_docstring
