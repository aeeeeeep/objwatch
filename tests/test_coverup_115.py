# file: objwatch/tracer.py:374-421
# asked: {"lines": [374, 384, 385, 387, 390, 391, 394, 395, 396, 399, 400, 403, 404, 407, 408, 409, 410, 411, 413, 415, 417, 418, 419, 421], "branches": [[384, 385], [384, 387], [390, 391], [390, 394], [394, 395], [394, 417], [403, 404], [403, 407], [407, 408], [407, 415], [418, 419], [418, 421]]}
# gained: {"lines": [374, 384, 385, 387, 390, 391, 394, 395, 396, 399, 400, 403, 404, 407, 408, 409, 410, 411, 413, 417, 418, 419, 421], "branches": [[384, 385], [384, 387], [390, 391], [390, 394], [394, 395], [394, 417], [403, 404], [403, 407], [407, 408], [418, 419], [418, 421]]}

import pytest
import sys
from types import FrameType
from unittest.mock import Mock, patch
from objwatch.config import ObjWatchConfig


class TestTracerShouldTraceFrame:
    """Test cases for Tracer._should_trace_frame method to achieve full coverage."""

    def test_filename_endswith_returns_true(self, monkeypatch):
        """Test when _filename_endswith returns True (line 384-385)."""
        from objwatch.tracer import Tracer

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': 'test_module'}

        # Mock _filename_endswith to return True
        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: True)
        monkeypatch.setattr(tracer, '_should_trace_module', lambda x: False)

        result = tracer._should_trace_frame(mock_frame)
        assert result is True

    def test_module_not_traced_returns_false(self, monkeypatch):
        """Test when module is not traced (line 390-391)."""
        from objwatch.tracer import Tracer

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': 'test_module'}

        # Mock _filename_endswith to return False, _should_trace_module to return False
        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: False)
        monkeypatch.setattr(tracer, '_should_trace_module', lambda x: False)

        result = tracer._should_trace_frame(mock_frame)
        assert result is False

    def test_class_method_traced_returns_true(self, monkeypatch):
        """Test when class and method are both traced (line 394-404)."""
        from objwatch.tracer import Tracer

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': 'test_module'}

        # Create a simple object with __class__ attribute
        class TestClass:
            pass

        test_obj = TestClass()
        mock_frame.f_locals = {'self': test_obj}
        mock_frame.f_code.co_name = "test_method"

        # Mock dependencies
        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: False)
        monkeypatch.setattr(tracer, '_should_trace_module', lambda x: True)
        monkeypatch.setattr(tracer, '_should_trace_class', lambda x, y: True)
        monkeypatch.setattr(tracer, '_should_trace_method', lambda x, y, z: True)

        result = tracer._should_trace_frame(mock_frame)
        assert result is True

    def test_class_traced_attributes_traced_returns_true(self, monkeypatch):
        """Test when class is traced and attributes are traced (line 407-413)."""
        from objwatch.tracer import Tracer

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': 'test_module'}

        # Create a simple object with __class__ and __dict__ attributes
        class TestClass:
            def __init__(self):
                self.attr1 = 'value1'
                self.attr2 = 'value2'

        test_obj = TestClass()
        mock_frame.f_locals = {'self': test_obj}
        mock_frame.f_code.co_name = "test_method"

        # Mock dependencies
        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: False)
        monkeypatch.setattr(tracer, '_should_trace_module', lambda x: True)
        monkeypatch.setattr(tracer, '_should_trace_class', lambda x, y: True)
        monkeypatch.setattr(tracer, '_should_trace_method', lambda x, y, z: False)
        monkeypatch.setattr(tracer, '_should_trace_attribute', lambda x, y, z: True)

        result = tracer._should_trace_frame(mock_frame)
        assert result is True

    def test_class_traced_no_attributes_traced_returns_false(self, monkeypatch):
        """Test when class is traced but no attributes are traced (line 407-415)."""
        from objwatch.tracer import Tracer

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': 'test_module'}

        # Create a simple object with __class__ and __dict__ attributes
        class TestClass:
            def __init__(self):
                self.attr1 = 'value1'
                self.attr2 = 'value2'

        test_obj = TestClass()
        mock_frame.f_locals = {'self': test_obj}
        mock_frame.f_code.co_name = "test_method"

        # Mock dependencies
        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: False)
        monkeypatch.setattr(tracer, '_should_trace_module', lambda x: True)
        monkeypatch.setattr(tracer, '_should_trace_class', lambda x, y: True)
        monkeypatch.setattr(tracer, '_should_trace_method', lambda x, y, z: False)
        monkeypatch.setattr(tracer, '_should_trace_attribute', lambda x, y, z: False)

        result = tracer._should_trace_frame(mock_frame)
        assert result is False

    def test_function_traced_returns_true(self, monkeypatch):
        """Test when function is traced (line 417-419)."""
        from objwatch.tracer import Tracer

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': 'test_module'}
        mock_frame.f_locals = {}  # No 'self' for function case
        mock_frame.f_code.co_name = "test_function"

        # Mock dependencies
        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: False)
        monkeypatch.setattr(tracer, '_should_trace_module', lambda x: True)
        monkeypatch.setattr(tracer, '_should_trace_function', lambda x, y: True)

        result = tracer._should_trace_frame(mock_frame)
        assert result is True

    def test_check_global_changes_returns_true(self, monkeypatch):
        """Test when _check_global_changes returns True (line 421)."""
        from objwatch.tracer import Tracer

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': 'test_module'}
        mock_frame.f_locals = {}  # No 'self' for function case
        mock_frame.f_code.co_name = "test_function"

        # Mock dependencies
        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: False)
        monkeypatch.setattr(tracer, '_should_trace_module', lambda x: True)
        monkeypatch.setattr(tracer, '_should_trace_function', lambda x, y: False)
        monkeypatch.setattr(tracer, '_check_global_changes', lambda x: True)

        result = tracer._should_trace_frame(mock_frame)
        assert result is True

    def test_check_global_changes_returns_false(self, monkeypatch):
        """Test when _check_global_changes returns False (line 421)."""
        from objwatch.tracer import Tracer

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': 'test_module'}
        mock_frame.f_locals = {}  # No 'self' for function case
        mock_frame.f_code.co_name = "test_function"

        # Mock dependencies
        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: False)
        monkeypatch.setattr(tracer, '_should_trace_module', lambda x: True)
        monkeypatch.setattr(tracer, '_should_trace_function', lambda x, y: False)
        monkeypatch.setattr(tracer, '_check_global_changes', lambda x: False)

        result = tracer._should_trace_frame(mock_frame)
        assert result is False
