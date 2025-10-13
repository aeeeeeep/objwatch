# file: objwatch/tracer.py:423-440
# asked: {"lines": [423, 432, 434, 435, 437, 438, 440], "branches": [[434, 435], [434, 437], [437, 438], [437, 440]]}
# gained: {"lines": [423, 432, 434, 435, 437, 438, 440], "branches": [[434, 435], [434, 437], [437, 438], [437, 440]]}

import pytest
from types import FrameType
from unittest.mock import Mock, MagicMock
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerGlobalChanges:
    """Test cases for Tracer._check_global_changes method"""

    def test_check_global_changes_no_global_index_with_globals_true(self, monkeypatch):
        """Test when global_index is empty and with_globals is True"""
        config = ObjWatchConfig(targets=['test_module'], with_globals=True)
        tracer = Tracer(config)
        tracer.global_index = {}
        tracer.builtin_fields = {'__builtins__', '__name__', 'self'}

        # Create a mock frame with globals containing non-builtin variables
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': 'test_module', 'custom_var': 'value', '__builtins__': {}}

        result = tracer._check_global_changes(mock_frame)
        assert result is True

    def test_check_global_changes_no_global_index_with_globals_true_only_builtins(self, monkeypatch):
        """Test when global_index is empty and with_globals is True but only builtin variables exist"""
        config = ObjWatchConfig(targets=['test_module'], with_globals=True)
        tracer = Tracer(config)
        tracer.global_index = {}
        tracer.builtin_fields = {'__builtins__', '__name__', 'self'}

        # Create a mock frame with only builtin globals
        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': 'test_module', '__builtins__': {}, 'self': None}

        result = tracer._check_global_changes(mock_frame)
        assert result is False

    def test_check_global_changes_with_globals_false(self, monkeypatch):
        """Test when with_globals is False"""
        config = ObjWatchConfig(targets=['test_module'], with_globals=False)
        tracer = Tracer(config)
        tracer.global_index = {'test_module': True}

        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': 'test_module'}

        result = tracer._check_global_changes(mock_frame)
        assert result is False

    def test_check_global_changes_with_globals_true_module_in_global_index(self, monkeypatch):
        """Test when with_globals is True and module exists in global_index"""
        config = ObjWatchConfig(targets=['test_module'], with_globals=True)
        tracer = Tracer(config)
        tracer.global_index = {'test_module': True}

        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': 'test_module'}

        result = tracer._check_global_changes(mock_frame)
        assert result is True

    def test_check_global_changes_with_globals_true_module_not_in_global_index(self, monkeypatch):
        """Test when with_globals is True but module not in global_index"""
        config = ObjWatchConfig(targets=['test_module'], with_globals=True)
        tracer = Tracer(config)
        tracer.global_index = {'other_module': True}

        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': 'test_module'}

        result = tracer._check_global_changes(mock_frame)
        assert result is False

    def test_check_global_changes_empty_module_name(self, monkeypatch):
        """Test when module name is empty"""
        config = ObjWatchConfig(targets=['test_module'], with_globals=True)
        tracer = Tracer(config)
        tracer.global_index = {'test_module': True}

        mock_frame = Mock(spec=FrameType)
        mock_frame.f_globals = {'__name__': ''}

        result = tracer._check_global_changes(mock_frame)
        assert result is False
