# file: objwatch/wrappers/abc_wrapper.py:36-48
# asked: {"lines": [36, 37, 48], "branches": []}
# gained: {"lines": [36, 37], "branches": []}

import pytest
from typing import Any
from objwatch.wrappers.abc_wrapper import ABCWrapper


class TestABCWrapper(ABCWrapper):
    """Concrete implementation for testing abstract methods."""

    def wrap_call(self, func_name: str, frame: Any) -> str:
        return f"call:{func_name}"

    def wrap_return(self, func_name: str, result: Any) -> str:
        return f"return:{func_name}:{result}"

    def wrap_upd(self, old_value: Any, current_value: Any) -> tuple:
        return f"old:{old_value}", f"new:{current_value}"


def test_abc_wrapper_cannot_be_instantiated_directly():
    """Test that ABCWrapper cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ABCWrapper()


def test_concrete_implementation_can_be_instantiated():
    """Test that concrete implementation can be instantiated."""
    wrapper = TestABCWrapper()
    assert wrapper is not None


def test_wrap_return_abstract_method():
    """Test that wrap_return is an abstract method requiring implementation."""
    assert hasattr(ABCWrapper, 'wrap_return')
    assert ABCWrapper.wrap_return.__isabstractmethod__


def test_concrete_wrap_return_implementation():
    """Test concrete implementation of wrap_return method."""
    wrapper = TestABCWrapper()
    result = wrapper.wrap_return("test_func", "test_result")
    assert result == "return:test_func:test_result"
    assert isinstance(result, str)


def test_wrap_return_with_none_result():
    """Test wrap_return with None result."""
    wrapper = TestABCWrapper()
    result = wrapper.wrap_return("none_func", None)
    assert result == "return:none_func:None"


def test_wrap_return_with_numeric_result():
    """Test wrap_return with numeric result."""
    wrapper = TestABCWrapper()
    result = wrapper.wrap_return("math_func", 42)
    assert result == "return:math_func:42"


def test_wrap_return_with_complex_result():
    """Test wrap_return with complex data structure."""
    wrapper = TestABCWrapper()
    complex_data = {"key": "value", "list": [1, 2, 3]}
    result = wrapper.wrap_return("complex_func", complex_data)
    assert "complex_func" in result
    assert isinstance(result, str)
