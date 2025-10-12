# file: objwatch/wrappers/abc_wrapper.py:102-131
# asked: {"lines": [102, 113, 114, 115, 116, 117, 118, 120, 122, 123, 124, 125, 127, 128, 129, 130, 131], "branches": [[113, 114], [113, 115], [115, 116], [115, 122], [117, 118], [117, 120], [127, 128], [127, 131], [128, 129], [128, 130]]}
# gained: {"lines": [102, 113, 114, 115, 116, 117, 118, 120, 122, 123, 124, 125, 127, 128, 129, 130, 131], "branches": [[113, 114], [113, 115], [115, 116], [115, 122], [117, 118], [117, 120], [127, 128], [127, 131], [128, 129], [128, 130]]}

import pytest
from typing import Any
from unittest.mock import Mock
from objwatch.wrappers.abc_wrapper import ABCWrapper
from objwatch.constants import Constants
from objwatch.event_handls import EventHandls
from enum import Enum
from types import FunctionType, FrameType


class TestEnum(Enum):
    VALUE1 = 1
    VALUE2 = 2


class ConcreteTestWrapper(ABCWrapper):
    def wrap_call(self, func_name: str, frame: FrameType) -> str:
        return f"call:{func_name}"

    def wrap_return(self, func_name: str, result: Any) -> str:
        return f"return:{func_name}:{result}"

    def wrap_upd(self, old_value: Any, current_value: Any) -> tuple:
        return f"old:{old_value}", f"new:{current_value}"


class TestABCWrapperFormatValue:

    def test_format_value_log_element_types(self):
        wrapper = ConcreteTestWrapper()

        # Test bool
        result = wrapper._format_value(True)
        assert result == "True"

        # Test int
        result = wrapper._format_value(42)
        assert result == "42"

        # Test float
        result = wrapper._format_value(3.14)
        assert result == "3.14"

        # Test str
        result = wrapper._format_value("hello")
        assert result == "hello"

        # Test None
        result = wrapper._format_value(None)
        assert result == "None"

        # Test FunctionType
        def test_func():
            pass

        result = wrapper._format_value(test_func)
        assert result == f"{test_func}"

        # Test Enum
        result = wrapper._format_value(TestEnum.VALUE1)
        assert result == f"{TestEnum.VALUE1}"

    def test_format_value_log_sequence_types_with_formatted_sequence(self, monkeypatch):
        wrapper = ConcreteTestWrapper()

        # Mock format_sequence to return a non-empty string
        mock_format_sequence = Mock(return_value="[1, 2, 3]")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        # Test list
        result = wrapper._format_value([1, 2, 3])
        assert result == "[1, 2, 3]"
        mock_format_sequence.assert_called_once_with([1, 2, 3], func=None)

    def test_format_value_log_sequence_types_with_empty_formatted_sequence(self, monkeypatch):
        wrapper = ConcreteTestWrapper()

        # Mock format_sequence to return empty string
        mock_format_sequence = Mock(return_value="")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        # Test tuple
        result = wrapper._format_value((1, 2, 3))
        assert result == "(type)tuple"
        mock_format_sequence.assert_called_once_with((1, 2, 3), func=None)

    def test_format_value_other_types_with_name_attribute(self):
        wrapper = ConcreteTestWrapper()

        class TestClass:
            __name__ = "TestClass"

        result = wrapper._format_value(TestClass)
        assert result == "(type)TestClass"

    def test_format_value_other_types_without_name_attribute(self):
        wrapper = ConcreteTestWrapper()

        # Create an object that doesn't have __name__ attribute
        # Use a simple object instance instead of a class
        test_obj = object()

        result = wrapper._format_value(test_obj)
        assert result == "(type)object"

    def test_format_value_is_return_true_with_sequence_and_formatted(self, monkeypatch):
        wrapper = ConcreteTestWrapper()

        # Mock format_sequence to return a non-empty string
        mock_format_sequence = Mock(return_value="[1, 2, 3]")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        # Test with is_return=True for sequence type
        result = wrapper._format_value([1, 2, 3], is_return=True)
        assert result == "[[1, 2, 3]]"
        mock_format_sequence.assert_called_once_with([1, 2, 3], func=None)

    def test_format_value_is_return_true_with_sequence_and_empty_formatted(self, monkeypatch):
        wrapper = ConcreteTestWrapper()

        # Mock format_sequence to return empty string
        mock_format_sequence = Mock(return_value="")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        # Test with is_return=True for sequence type with empty formatted result
        result = wrapper._format_value([1, 2, 3], is_return=True)
        assert result == "[(type)list]"
        mock_format_sequence.assert_called_once_with([1, 2, 3], func=None)

    def test_format_value_is_return_true_with_non_sequence(self):
        wrapper = ConcreteTestWrapper()

        # Test with is_return=True for non-sequence type
        result = wrapper._format_value(42, is_return=True)
        assert result == "42"

    def test_format_value_is_return_false_with_sequence_and_formatted(self, monkeypatch):
        wrapper = ConcreteTestWrapper()

        # Mock format_sequence to return a non-empty string
        mock_format_sequence = Mock(return_value="[1, 2, 3]")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        # Test with is_return=False for sequence type (default)
        result = wrapper._format_value([1, 2, 3], is_return=False)
        assert result == "[1, 2, 3]"
        mock_format_sequence.assert_called_once_with([1, 2, 3], func=None)

    def test_format_value_with_custom_format_sequence_func(self, monkeypatch):
        wrapper = ConcreteTestWrapper()

        def custom_format_func(seq):
            return ["custom"] * len(seq)

        wrapper.format_sequence_func = custom_format_func

        # Mock format_sequence to verify it uses the custom function
        mock_format_sequence = Mock(return_value="['custom', 'custom', 'custom']")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        result = wrapper._format_value([1, 2, 3])
        assert result == "['custom', 'custom', 'custom']"
        mock_format_sequence.assert_called_once_with([1, 2, 3], func=custom_format_func)
