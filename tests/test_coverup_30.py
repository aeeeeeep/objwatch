# file: objwatch/tracer.py:462-492
# asked: {"lines": [462, 472, 473, 475, 476, 477, 478, 480, 481, 483, 484, 485, 486, 487, 488, 489, 492], "branches": [[475, 476], [475, 480]]}
# gained: {"lines": [462, 472, 473, 475, 476, 477, 478, 480, 481, 483, 484, 485, 486, 487, 488, 489, 492], "branches": [[475, 476], [475, 480]]}

import pytest
import sys
from types import FrameType
from unittest.mock import Mock, patch
from objwatch.config import ObjWatchConfig


class TestTracerGetFunctionInfo:
    """Test cases for Tracer._get_function_info method."""

    def test_get_function_info_with_self_in_locals_method_traced(self, monkeypatch):
        """Test _get_function_info when 'self' is in locals and method should be traced."""
        from objwatch.tracer import Tracer

        # Create config with required target
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock frame with 'self' in locals
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': 'test_module'}
        mock_frame.f_locals = {'self': Mock(__class__=Mock(__name__='TestClass'))}
        mock_frame.f_code.co_name = 'test_method'

        # Mock _should_trace_method to return True
        monkeypatch.setattr(tracer, '_should_trace_method', lambda module, cls, method: True)

        result = tracer._get_function_info(mock_frame)

        assert result['module'] == 'test_module'
        assert result['symbol'] == 'TestClass.test_method'
        assert result['symbol_type'] == 'method'
        assert result['qualified_name'] == 'test_module.TestClass.test_method'
        assert result['frame'] is mock_frame

    def test_get_function_info_with_self_in_locals_method_not_traced(self, monkeypatch):
        """Test _get_function_info when 'self' is in locals but method should not be traced."""
        from objwatch.tracer import Tracer

        # Create config with required target
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock frame with 'self' in locals
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': 'test_module'}
        mock_frame.f_locals = {'self': Mock(__class__=Mock(__name__='TestClass'))}
        mock_frame.f_code.co_name = 'test_method'

        # Mock _should_trace_method to return False
        monkeypatch.setattr(tracer, '_should_trace_method', lambda module, cls, method: False)

        result = tracer._get_function_info(mock_frame)

        assert result['module'] == 'test_module'
        assert result['symbol'] == 'TestClass.test_method'
        assert result['symbol_type'] is None
        assert result['qualified_name'] == 'test_module.TestClass.test_method'
        assert result['frame'] is mock_frame

    def test_get_function_info_without_self_function_traced(self, monkeypatch):
        """Test _get_function_info when 'self' is not in locals and function should be traced."""
        from objwatch.tracer import Tracer

        # Create config with required target
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock frame without 'self' in locals
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': 'test_module'}
        mock_frame.f_locals = {}
        mock_frame.f_code.co_name = 'test_function'

        # Mock _should_trace_function to return True
        monkeypatch.setattr(tracer, '_should_trace_function', lambda module, func: True)

        result = tracer._get_function_info(mock_frame)

        assert result['module'] == 'test_module'
        assert result['symbol'] == 'test_function'
        assert result['symbol_type'] == 'function'
        assert result['qualified_name'] == 'test_module.test_function'
        assert result['frame'] is mock_frame

    def test_get_function_info_without_self_function_not_traced(self, monkeypatch):
        """Test _get_function_info when 'self' is not in locals and function should not be traced."""
        from objwatch.tracer import Tracer

        # Create config with required target
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock frame without 'self' in locals
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': 'test_module'}
        mock_frame.f_locals = {}
        mock_frame.f_code.co_name = 'test_function'

        # Mock _should_trace_function to return False
        monkeypatch.setattr(tracer, '_should_trace_function', lambda module, func: False)

        result = tracer._get_function_info(mock_frame)

        assert result['module'] == 'test_module'
        assert result['symbol'] == 'test_function'
        assert result['symbol_type'] is None
        assert result['qualified_name'] == 'test_module.test_function'
        assert result['frame'] is mock_frame

    def test_get_function_info_with_empty_module_name(self, monkeypatch):
        """Test _get_function_info when module name is empty."""
        from objwatch.tracer import Tracer

        # Create config with required target
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock frame with empty module name
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': ''}
        mock_frame.f_locals = {}
        mock_frame.f_code.co_name = 'test_function'

        # Mock _should_trace_function to return True
        monkeypatch.setattr(tracer, '_should_trace_function', lambda module, func: True)

        result = tracer._get_function_info(mock_frame)

        assert result['module'] == ''
        assert result['symbol'] == 'test_function'
        assert result['symbol_type'] == 'function'
        assert result['qualified_name'] == 'test_function'  # No module prefix when module is empty
        assert result['frame'] is mock_frame
