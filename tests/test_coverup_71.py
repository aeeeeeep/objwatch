# file: objwatch/wrappers/abc_wrapper.py:22-34
# asked: {"lines": [22, 23, 34], "branches": []}
# gained: {"lines": [22, 23], "branches": []}

import pytest
from types import FrameType
from typing import Any, Tuple
from unittest.mock import Mock
from objwatch.wrappers.abc_wrapper import ABCWrapper


class TestABCWrapper(ABCWrapper):
    """Concrete implementation for testing the abstract base class."""

    def wrap_call(self, func_name: str, frame: FrameType) -> str:
        """Test implementation of wrap_call."""
        return f"Call: {func_name}"

    def wrap_return(self, func_name: str, result: Any) -> str:
        """Test implementation of wrap_return."""
        return f"Return: {func_name} -> {result}"

    def wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]:
        """Test implementation of wrap_upd."""
        return f"Old: {old_value}", f"New: {current_value}"


def test_abc_wrapper_abstract_methods():
    """Test that ABCWrapper cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ABCWrapper()


def test_concrete_wrapper_wrap_call():
    """Test the wrap_call method implementation."""
    wrapper = TestABCWrapper()
    mock_frame = Mock(spec=FrameType)

    result = wrapper.wrap_call("test_function", mock_frame)

    assert result == "Call: test_function"
    assert isinstance(result, str)


def test_wrap_call_with_different_function_names():
    """Test wrap_call with various function names."""
    wrapper = TestABCWrapper()
    mock_frame = Mock(spec=FrameType)

    # Test with simple function name
    result1 = wrapper.wrap_call("func1", mock_frame)
    assert result1 == "Call: func1"

    # Test with method name
    result2 = wrapper.wrap_call("ClassName.method", mock_frame)
    assert result2 == "Call: ClassName.method"

    # Test with special characters
    result3 = wrapper.wrap_call("__init__", mock_frame)
    assert result3 == "Call: __init__"


def test_wrap_call_frame_parameter():
    """Test that wrap_call properly receives and uses the frame parameter."""
    wrapper = TestABCWrapper()

    # Create a more realistic mock frame
    mock_frame = Mock(spec=FrameType)
    mock_frame.f_code.co_name = "test_function"
    mock_frame.f_lineno = 42

    result = wrapper.wrap_call("test_function", mock_frame)

    # Verify the method was called with the correct parameters
    assert result == "Call: test_function"
    # The frame parameter is passed but not used in this test implementation
    # This test ensures the method signature is correct and the frame is accepted
