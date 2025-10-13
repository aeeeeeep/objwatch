# file: objwatch/wrappers/tensor_shape_wrapper.py:41-54
# asked: {"lines": [41, 52, 53, 54], "branches": []}
# gained: {"lines": [41, 52, 53, 54], "branches": []}

import pytest
from types import FrameType
from unittest.mock import Mock, MagicMock
from objwatch.wrappers.tensor_shape_wrapper import TensorShapeWrapper


class TestTensorShapeWrapperWrapCall:
    """Test cases for TensorShapeWrapper.wrap_call method."""

    def test_wrap_call_with_positional_args(self, monkeypatch):
        """Test wrap_call with positional arguments only."""
        wrapper = TensorShapeWrapper()

        # Mock frame with positional arguments
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code = Mock()
        mock_frame.f_code.co_varnames = ('arg1', 'arg2')
        mock_frame.f_code.co_argcount = 2
        mock_frame.f_locals = {'arg1': 'value1', 'arg2': 'value2'}

        # Mock the _extract_args_kwargs method to return specific args
        monkeypatch.setattr(wrapper, '_extract_args_kwargs', lambda frame: (['value1', 'value2'], {}))

        # Mock the _format_args_kwargs method to return a formatted string
        monkeypatch.setattr(wrapper, '_format_args_kwargs', lambda args, kwargs: "'0':'value1', '1':'value2'")

        result = wrapper.wrap_call('test_func', mock_frame)

        assert result == "'0':'value1', '1':'value2'"

    def test_wrap_call_with_keyword_args(self, monkeypatch):
        """Test wrap_call with keyword arguments only."""
        wrapper = TensorShapeWrapper()

        # Mock frame with keyword arguments
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code = Mock()
        mock_frame.f_code.co_varnames = ()
        mock_frame.f_code.co_argcount = 0
        mock_frame.f_locals = {'key1': 'val1', 'key2': 'val2'}

        # Mock the _extract_args_kwargs method to return specific kwargs
        monkeypatch.setattr(wrapper, '_extract_args_kwargs', lambda frame: ([], {'key1': 'val1', 'key2': 'val2'}))

        # Mock the _format_args_kwargs method to return a formatted string
        monkeypatch.setattr(wrapper, '_format_args_kwargs', lambda args, kwargs: "'key1':'val1', 'key2':'val2'")

        result = wrapper.wrap_call('test_func', mock_frame)

        assert result == "'key1':'val1', 'key2':'val2'"

    def test_wrap_call_with_mixed_args(self, monkeypatch):
        """Test wrap_call with both positional and keyword arguments."""
        wrapper = TensorShapeWrapper()

        # Mock frame with mixed arguments
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code = Mock()
        mock_frame.f_code.co_varnames = ('arg1',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'arg1': 'pos_val', 'kwarg1': 'kw_val'}

        # Mock the _extract_args_kwargs method to return mixed args
        monkeypatch.setattr(wrapper, '_extract_args_kwargs', lambda frame: (['pos_val'], {'kwarg1': 'kw_val'}))

        # Mock the _format_args_kwargs method to return a formatted string
        monkeypatch.setattr(wrapper, '_format_args_kwargs', lambda args, kwargs: "'0':'pos_val', 'kwarg1':'kw_val'")

        result = wrapper.wrap_call('test_func', mock_frame)

        assert result == "'0':'pos_val', 'kwarg1':'kw_val'"

    def test_wrap_call_with_no_args(self, monkeypatch):
        """Test wrap_call with no arguments."""
        wrapper = TensorShapeWrapper()

        # Mock frame with no arguments
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code = Mock()
        mock_frame.f_code.co_varnames = ()
        mock_frame.f_code.co_argcount = 0
        mock_frame.f_locals = {}

        # Mock the _extract_args_kwargs method to return empty args
        monkeypatch.setattr(wrapper, '_extract_args_kwargs', lambda frame: ([], {}))

        # Mock the _format_args_kwargs method to return empty string
        monkeypatch.setattr(wrapper, '_format_args_kwargs', lambda args, kwargs: '')

        result = wrapper.wrap_call('test_func', mock_frame)

        assert result == ''
