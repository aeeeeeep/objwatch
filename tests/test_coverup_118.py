# file: objwatch/wrappers/abc_wrapper.py:64-84
# asked: {"lines": [64, 74, 75, 76, 77, 78, 79, 80, 82, 83, 84], "branches": [[78, 79], [78, 82], [79, 78], [79, 80], [82, 83], [82, 84]]}
# gained: {"lines": [64, 74, 75, 76, 77, 78, 79, 80, 82, 83, 84], "branches": [[78, 79], [78, 82], [79, 78], [79, 80], [82, 83], [82, 84]]}

import pytest
import sys
from types import FrameType, CodeType
from typing import Any, List, Tuple
from objwatch.wrappers.abc_wrapper import ABCWrapper


class TestABCWrapper(ABCWrapper):
    """Concrete implementation for testing abstract methods"""

    def wrap_call(self, func_name: str, frame: FrameType) -> str:
        return f"call:{func_name}"

    def wrap_return(self, func_name: str, result: Any) -> str:
        return f"return:{func_name}:{result}"

    def wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]:
        return f"old:{old_value}", f"new:{current_value}"


class MockFrame:
    """Mock frame object for testing"""

    def __init__(self, arg_names: List[str], local_vars: dict, has_varkw: bool = False):
        self.f_locals = local_vars.copy()
        self.f_code = MockCode(arg_names, has_varkw)


class MockCode:
    """Mock code object for testing"""

    def __init__(self, arg_names: List[str], has_varkw: bool = False):
        self.co_varnames = tuple(arg_names)
        self.co_argcount = len(arg_names)
        self.co_flags = 0x08 if has_varkw else 0


def test_extract_args_kwargs_basic():
    """Test basic argument extraction without varargs/varkw"""
    wrapper = TestABCWrapper()

    # Create frame with basic arguments
    arg_names = ['a', 'b', 'c']
    local_vars = {'a': 1, 'b': 2, 'c': 3}
    frame = MockFrame(arg_names, local_vars)

    args, kwargs = wrapper._extract_args_kwargs(frame)

    assert args == [1, 2, 3]
    assert kwargs == {}


def test_extract_args_kwargs_with_varkw():
    """Test argument extraction with variable keyword arguments (CO_VARKEYWORDS)"""
    wrapper = TestABCWrapper()

    # Create frame with varkw flag and extra keyword arguments
    arg_names = ['a', 'b']
    local_vars = {'a': 1, 'b': 2, 'extra1': 'value1', 'extra2': 'value2'}
    frame = MockFrame(arg_names, local_vars, has_varkw=True)

    args, kwargs = wrapper._extract_args_kwargs(frame)

    assert args == [1, 2]
    assert kwargs == {'extra1': 'value1', 'extra2': 'value2'}


def test_extract_args_kwargs_with_varkw_ignores_private():
    """Test that varkw extraction ignores private variables (starting with _)"""
    wrapper = TestABCWrapper()

    # Create frame with varkw flag and mixed public/private variables
    arg_names = ['a', 'b']
    local_vars = {'a': 1, 'b': 2, 'public': 'value1', '_private': 'value2', '__dunder': 'value3'}
    frame = MockFrame(arg_names, local_vars, has_varkw=True)

    args, kwargs = wrapper._extract_args_kwargs(frame)

    assert args == [1, 2]
    assert kwargs == {'public': 'value1'}  # _private and __dunder should be excluded


def test_extract_args_kwargs_missing_locals():
    """Test when some arguments are not in frame.f_locals"""
    wrapper = TestABCWrapper()

    # Create frame where some arguments are missing from locals
    arg_names = ['a', 'b', 'c', 'd']
    local_vars = {'a': 1, 'c': 3}  # b and d are missing
    frame = MockFrame(arg_names, local_vars)

    args, kwargs = wrapper._extract_args_kwargs(frame)

    assert args == [1, 3]  # Only a and c should be included
    assert kwargs == {}


def test_extract_args_kwargs_no_varkw_flag():
    """Test that kwargs are empty when CO_VARKEYWORDS flag is not set"""
    wrapper = TestABCWrapper()

    # Create frame with extra variables but no varkw flag
    arg_names = ['a', 'b']
    local_vars = {'a': 1, 'b': 2, 'extra': 'value'}
    frame = MockFrame(arg_names, local_vars, has_varkw=False)

    args, kwargs = wrapper._extract_args_kwargs(frame)

    assert args == [1, 2]
    assert kwargs == {}  # Should be empty without varkw flag


def test_extract_args_kwargs_empty_args():
    """Test with empty argument list"""
    wrapper = TestABCWrapper()

    # Create frame with no arguments
    arg_names = []
    local_vars = {'other_var': 'value'}
    frame = MockFrame(arg_names, local_vars, has_varkw=True)

    args, kwargs = wrapper._extract_args_kwargs(frame)

    assert args == []
    assert kwargs == {'other_var': 'value'}  # All locals become kwargs with varkw flag


def test_extract_args_kwargs_mixed_case():
    """Test with mixed case variable names"""
    wrapper = TestABCWrapper()

    # Create frame with mixed case names
    arg_names = ['myVar', 'another_var']
    local_vars = {'myVar': 1, 'another_var': 2, 'ExtraVar': 'value1', '_privateVar': 'value2'}
    frame = MockFrame(arg_names, local_vars, has_varkw=True)

    args, kwargs = wrapper._extract_args_kwargs(frame)

    assert args == [1, 2]
    assert kwargs == {'ExtraVar': 'value1'}  # _privateVar should be excluded
