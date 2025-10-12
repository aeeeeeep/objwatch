# file: objwatch/wrappers/abc_wrapper.py:50-62
# asked: {"lines": [50, 51, 62], "branches": []}
# gained: {"lines": [50, 51], "branches": []}

import pytest
from typing import Any, Tuple
from abc import ABC, abstractmethod
from objwatch.wrappers.abc_wrapper import ABCWrapper


class ConcreteWrapper(ABCWrapper):
    """Concrete implementation for testing abstract methods."""

    def wrap_call(self, func_name: str, frame: Any) -> str:
        return f"call:{func_name}"

    def wrap_return(self, func_name: str, result: Any) -> str:
        return f"return:{func_name}:{result}"

    def wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]:
        return (f"old:{old_value}", f"new:{current_value}")


class FailingWrapper(ABCWrapper):
    """Wrapper that fails to implement abstract methods for testing instantiation."""

    def wrap_call(self, func_name: str, frame: Any) -> str:
        return f"call:{func_name}"

    def wrap_return(self, func_name: str, result: Any) -> str:
        return f"return:{func_name}:{result}"


def test_abc_wrapper_cannot_be_instantiated():
    """Test that ABCWrapper cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ABCWrapper()


def test_concrete_wrapper_implements_all_abstract_methods():
    """Test that concrete wrapper properly implements all abstract methods."""
    wrapper = ConcreteWrapper()

    # Test wrap_upd method specifically
    old_val, new_val = wrapper.wrap_upd("old_value", "new_value")
    assert old_val == "old:old_value"
    assert new_val == "new:new_value"

    # Test other abstract methods
    assert wrapper.wrap_call("test_func", None) == "call:test_func"
    assert wrapper.wrap_return("test_func", "result") == "return:test_func:result"


def test_incomplete_wrapper_fails_instantiation():
    """Test that wrapper missing wrap_upd method cannot be instantiated."""
    with pytest.raises(TypeError):
        FailingWrapper()


def test_wrap_upd_with_different_data_types():
    """Test wrap_upd method with various data types."""
    wrapper = ConcreteWrapper()

    # Test with integers
    old_int, new_int = wrapper.wrap_upd(1, 2)
    assert old_int == "old:1"
    assert new_int == "new:2"

    # Test with strings
    old_str, new_str = wrapper.wrap_upd("hello", "world")
    assert old_str == "old:hello"
    assert new_str == "new:world"

    # Test with None values
    old_none, new_none = wrapper.wrap_upd(None, "something")
    assert old_none == "old:None"
    assert new_none == "new:something"

    # Test with lists
    old_list, new_list = wrapper.wrap_upd([1, 2], [3, 4])
    assert old_list == "old:[1, 2]"
    assert new_list == "new:[3, 4]"


def test_wrap_upd_edge_cases():
    """Test wrap_upd method with edge cases."""
    wrapper = ConcreteWrapper()

    # Test with empty strings
    old_empty, new_empty = wrapper.wrap_upd("", "not_empty")
    assert old_empty == "old:"
    assert new_empty == "new:not_empty"

    # Test with boolean values
    old_bool, new_bool = wrapper.wrap_upd(True, False)
    assert old_bool == "old:True"
    assert new_bool == "new:False"

    # Test with zero values
    old_zero, new_zero = wrapper.wrap_upd(0, 1)
    assert old_zero == "old:0"
    assert new_zero == "new:1"
