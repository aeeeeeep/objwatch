# file: objwatch/wrappers/abc_wrapper.py:133-144
# asked: {"lines": [133, 143, 144], "branches": []}
# gained: {"lines": [133, 143, 144], "branches": []}

import pytest
from unittest.mock import Mock, MagicMock
from objwatch.wrappers.abc_wrapper import ABCWrapper
from objwatch.constants import Constants
from objwatch.event_handls import EventHandls
from types import FunctionType
from enum import Enum


class TestABCWrapper:
    """Test class for ABCWrapper's _format_return method."""

    class ConcreteWrapper(ABCWrapper):
        """Concrete implementation for testing abstract methods."""

        def wrap_call(self, func_name, frame):
            return f"call_{func_name}"

        def wrap_return(self, func_name, result):
            return f"return_{func_name}"

        def wrap_upd(self, old_value, current_value):
            return f"upd_old", f"upd_current"

    def test_format_return_with_basic_types(self):
        """Test _format_return with basic types (bool, int, float, str, None)."""
        wrapper = self.ConcreteWrapper()

        # Test with boolean
        result = wrapper._format_return(True)
        assert result == "True"

        # Test with integer
        result = wrapper._format_return(42)
        assert result == "42"

        # Test with float
        result = wrapper._format_return(3.14)
        assert result == "3.14"

        # Test with string
        result = wrapper._format_return("hello")
        assert result == "hello"

        # Test with None
        result = wrapper._format_return(None)
        assert result == "None"

    def test_format_return_with_function_type(self):
        """Test _format_return with FunctionType."""
        wrapper = self.ConcreteWrapper()

        def test_func():
            pass

        result = wrapper._format_return(test_func)
        # FunctionType is in LOG_ELEMENT_TYPES, so it should return the string representation
        assert "test_func" in result

    def test_format_return_with_enum_type(self):
        """Test _format_return with Enum type."""
        wrapper = self.ConcreteWrapper()

        class TestEnum(Enum):
            VALUE1 = 1
            VALUE2 = 2

        result = wrapper._format_return(TestEnum.VALUE1)
        assert "VALUE1" in result

    def test_format_return_with_list_sequence(self, monkeypatch):
        """Test _format_return with list sequence."""
        wrapper = self.ConcreteWrapper()

        # Mock format_sequence to return a formatted string
        mock_format_sequence = Mock(return_value="(list)[1, 2, 3]")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        test_list = [1, 2, 3]
        result = wrapper._format_return(test_list)

        mock_format_sequence.assert_called_once_with(test_list, func=wrapper.format_sequence_func)
        assert result == "[(list)[1, 2, 3]]"

    def test_format_return_with_empty_list_sequence(self, monkeypatch):
        """Test _format_return with empty list sequence."""
        wrapper = self.ConcreteWrapper()

        # Mock format_sequence to return empty list format
        mock_format_sequence = Mock(return_value="(list)[]")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        test_list = []
        result = wrapper._format_return(test_list)

        mock_format_sequence.assert_called_once_with(test_list, func=wrapper.format_sequence_func)
        assert result == "[(list)[]]"

    def test_format_return_with_set_sequence(self, monkeypatch):
        """Test _format_return with set sequence."""
        wrapper = self.ConcreteWrapper()

        # Mock format_sequence to return a formatted string
        mock_format_sequence = Mock(return_value="(set)[1, 2, 3]")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        test_set = {1, 2, 3}
        result = wrapper._format_return(test_set)

        mock_format_sequence.assert_called_once_with(test_set, func=wrapper.format_sequence_func)
        assert result == "[(set)[1, 2, 3]]"

    def test_format_return_with_tuple_sequence(self, monkeypatch):
        """Test _format_return with tuple sequence."""
        wrapper = self.ConcreteWrapper()

        # Mock format_sequence to return a formatted string
        mock_format_sequence = Mock(return_value="(tuple)[1, 2, 3]")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        test_tuple = (1, 2, 3)
        result = wrapper._format_return(test_tuple)

        mock_format_sequence.assert_called_once_with(test_tuple, func=wrapper.format_sequence_func)
        assert result == "[(tuple)[1, 2, 3]]"

    def test_format_return_with_dict_sequence(self, monkeypatch):
        """Test _format_return with dict sequence."""
        wrapper = self.ConcreteWrapper()

        # Mock format_sequence to return a formatted string
        mock_format_sequence = Mock(return_value="(dict)[('a', 1), ('b', 2)]")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        test_dict = {'a': 1, 'b': 2}
        result = wrapper._format_return(test_dict)

        mock_format_sequence.assert_called_once_with(test_dict, func=wrapper.format_sequence_func)
        assert result == "[(dict)[('a', 1), ('b', 2)]]"

    def test_format_return_with_sequence_format_sequence_func(self, monkeypatch):
        """Test _format_return with sequence when format_sequence_func is set."""
        wrapper = self.ConcreteWrapper()
        wrapper.format_sequence_func = lambda x: [str(i * 2) for i in x]

        # Mock format_sequence to use the custom function
        def mock_format_sequence(seq, max_elements=None, func=None):
            if func:
                return f"(list){func(seq)}"
            return f"(list){seq}"

        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        test_list = [1, 2, 3]
        result = wrapper._format_return(test_list)

        assert result == "[(list)['2', '4', '6']]"

    def test_format_return_with_sequence_empty_format_result(self, monkeypatch):
        """Test _format_return with sequence when format_sequence returns empty string."""
        wrapper = self.ConcreteWrapper()

        # Mock format_sequence to return empty string
        mock_format_sequence = Mock(return_value="")
        monkeypatch.setattr(EventHandls, "format_sequence", mock_format_sequence)

        test_list = [1, 2, 3]
        result = wrapper._format_return(test_list)

        mock_format_sequence.assert_called_once_with(test_list, func=wrapper.format_sequence_func)
        # When format_sequence returns empty string, it should fall back to (type)list
        assert result == "[(type)list]"

    def test_format_return_with_custom_object(self):
        """Test _format_return with custom object that has __name__ attribute."""
        wrapper = self.ConcreteWrapper()

        class CustomClass:
            __name__ = "CustomClass"

        custom_obj = CustomClass()
        result = wrapper._format_return(custom_obj)
        assert result == "(type)CustomClass"

    def test_format_return_with_object_no_name(self):
        """Test _format_return with object that doesn't have __name__ attribute."""
        wrapper = self.ConcreteWrapper()

        class CustomClass:
            pass

        custom_obj = CustomClass()
        result = wrapper._format_return(custom_obj)
        assert result == "(type)CustomClass"
