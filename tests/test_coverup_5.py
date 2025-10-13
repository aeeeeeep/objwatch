# file: objwatch/event_handls.py:307-326
# asked: {"lines": [307, 308, 318, 319, 320, 321, 323, 324, 325, 326], "branches": [[318, 319], [318, 320], [320, 321], [320, 323]]}
# gained: {"lines": [307, 308, 318, 319, 320, 321, 323, 324, 325, 326], "branches": [[318, 319], [318, 320], [320, 321], [320, 323]]}

import pytest
from objwatch.event_handls import EventHandls
from objwatch.constants import Constants
from enum import Enum
from types import FunctionType


class TestEnum(Enum):
    VALUE1 = 1
    VALUE2 = 2


def dummy_function():
    pass


class CustomClass:
    def __init__(self, name):
        self.name = name


class TestEventHandlsFormatValue:

    def test_format_value_log_element_types(self):
        """Test _format_value with LOG_ELEMENT_TYPES"""
        # Test bool
        assert EventHandls._format_value(True) == "True"
        assert EventHandls._format_value(False) == "False"

        # Test int
        assert EventHandls._format_value(42) == "42"

        # Test float
        assert EventHandls._format_value(3.14) == "3.14"

        # Test str
        assert EventHandls._format_value("hello") == "hello"

        # Test None
        assert EventHandls._format_value(None) == "None"

        # Test FunctionType
        assert EventHandls._format_value(dummy_function) == f"{dummy_function}"

        # Test Enum
        assert EventHandls._format_value(TestEnum.VALUE1) == f"{TestEnum.VALUE1}"

    def test_format_value_log_sequence_types(self):
        """Test _format_value with LOG_SEQUENCE_TYPES"""
        # Test list
        test_list = [1, 2, 3]
        result = EventHandls._format_value(test_list)
        assert result == EventHandls.format_sequence(test_list)

        # Test set
        test_set = {1, 2, 3}
        result = EventHandls._format_value(test_set)
        assert result == EventHandls.format_sequence(test_set)

        # Test dict
        test_dict = {"a": 1, "b": 2}
        result = EventHandls._format_value(test_dict)
        assert result == EventHandls.format_sequence(test_dict)

        # Test tuple
        test_tuple = (1, 2, 3)
        result = EventHandls._format_value(test_tuple)
        assert result == EventHandls.format_sequence(test_tuple)

    def test_format_value_with_name_attribute(self):
        """Test _format_value with objects that have __name__ attribute"""
        # Test class with __name__
        result = EventHandls._format_value(CustomClass)
        assert result == "(type)CustomClass"

        # Test function with __name__
        def test_func():
            pass

        result = EventHandls._format_value(test_func)
        assert result == f"{test_func}"  # FunctionType is LOG_ELEMENT_TYPE

    def test_format_value_without_name_attribute(self):
        """Test _format_value with objects that don't have __name__ attribute"""
        # Test class instance without __name__
        obj = CustomClass("test")
        result = EventHandls._format_value(obj)
        assert result == "(type)CustomClass"

        # Test list instance without __name__
        obj = [1, 2, 3]
        result = EventHandls._format_value(obj)
        assert result == EventHandls.format_sequence(obj)  # list is LOG_SEQUENCE_TYPE

    def test_format_value_edge_cases(self):
        """Test _format_value with edge cases"""

        # Test object that raises exception when accessing __name__
        class NoNameClass:
            @property
            def __name__(self):
                raise AttributeError("No __name__")

        obj = NoNameClass()
        result = EventHandls._format_value(obj)
        assert result == "(type)NoNameClass"

        # Test with complex object that doesn't fit other categories
        class ComplexObject:
            def __repr__(self):
                return "ComplexObject()"

        obj = ComplexObject()
        result = EventHandls._format_value(obj)
        assert result == "(type)ComplexObject"
