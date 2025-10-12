# file: objwatch/tracer.py:283-302
# asked: {"lines": [283, 284, 296, 297, 299, 300, 302], "branches": [[297, 299], [297, 302]]}
# gained: {"lines": [283, 284, 296, 297, 299, 300, 302], "branches": [[297, 299], [297, 302]]}

import pytest
from unittest.mock import Mock, MagicMock
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerShouldTraceMethod:
    """Test cases for Tracer._should_trace_method method to achieve full coverage."""

    def test_should_trace_method_track_all_true_method_not_excluded(self, monkeypatch):
        """Test when track_all is True and method is not in excluded methods."""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = {}
        mock_config.exclude_targets = {}
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        tracer = Tracer(mock_config)

        # Set up the required attributes
        tracer.class_info = {'test_module': {'TestClass': {'track_all': True}}}
        tracer.exclude_method_index = {'test_module': {'TestClass': {'excluded_method'}}}
        tracer.method_index = {}

        # Test: method not in excluded methods
        result = tracer._should_trace_method('test_module', 'TestClass', 'some_method')
        assert result is True

        # Verify cache is working by calling again
        result2 = tracer._should_trace_method('test_module', 'TestClass', 'some_method')
        assert result2 is True

    def test_should_trace_method_track_all_true_method_excluded(self, monkeypatch):
        """Test when track_all is True and method is in excluded methods."""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = {}
        mock_config.exclude_targets = {}
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        tracer = Tracer(mock_config)

        # Set up the required attributes
        tracer.class_info = {'test_module': {'TestClass': {'track_all': True}}}
        tracer.exclude_method_index = {'test_module': {'TestClass': {'excluded_method'}}}
        tracer.method_index = {}

        # Test: method is in excluded methods
        result = tracer._should_trace_method('test_module', 'TestClass', 'excluded_method')
        assert result is False

    def test_should_trace_method_track_all_false_method_in_index(self, monkeypatch):
        """Test when track_all is False and method is in method_index."""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = {}
        mock_config.exclude_targets = {}
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        tracer = Tracer(mock_config)

        # Set up the required attributes
        tracer.class_info = {'test_module': {'TestClass': {'track_all': False}}}
        tracer.exclude_method_index = {}
        tracer.method_index = {'test_module': {'TestClass': {'target_method'}}}

        # Test: method is in method_index
        result = tracer._should_trace_method('test_module', 'TestClass', 'target_method')
        assert result is True

    def test_should_trace_method_track_all_false_method_not_in_index(self, monkeypatch):
        """Test when track_all is False and method is not in method_index."""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = {}
        mock_config.exclude_targets = {}
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        tracer = Tracer(mock_config)

        # Set up the required attributes
        tracer.class_info = {'test_module': {'TestClass': {'track_all': False}}}
        tracer.exclude_method_index = {}
        tracer.method_index = {'test_module': {'TestClass': {'other_method'}}}

        # Test: method is not in method_index
        result = tracer._should_trace_method('test_module', 'TestClass', 'some_method')
        assert result is False

    def test_should_trace_method_module_not_in_class_info(self, monkeypatch):
        """Test when module is not present in class_info."""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = {}
        mock_config.exclude_targets = {}
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        tracer = Tracer(mock_config)

        # Set up the required attributes
        tracer.class_info = {}
        tracer.exclude_method_index = {}
        tracer.method_index = {}

        # Test: module not in class_info
        result = tracer._should_trace_method('unknown_module', 'TestClass', 'some_method')
        assert result is False

    def test_should_trace_method_class_not_in_class_info(self, monkeypatch):
        """Test when class is not present in class_info for the module."""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = {}
        mock_config.exclude_targets = {}
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        tracer = Tracer(mock_config)

        # Set up the required attributes
        tracer.class_info = {'test_module': {'OtherClass': {'track_all': True}}}
        tracer.exclude_method_index = {}
        tracer.method_index = {}

        # Test: class not in class_info for the module
        result = tracer._should_trace_method('test_module', 'UnknownClass', 'some_method')
        assert result is False

    def test_should_trace_method_track_all_true_empty_exclude_method_index(self, monkeypatch):
        """Test when track_all is True and exclude_method_index is empty for the module/class."""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = {}
        mock_config.exclude_targets = {}
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        tracer = Tracer(mock_config)

        # Set up the required attributes
        tracer.class_info = {'test_module': {'TestClass': {'track_all': True}}}
        tracer.exclude_method_index = {}
        tracer.method_index = {}

        # Test: track_all True with empty exclude_method_index
        result = tracer._should_trace_method('test_module', 'TestClass', 'some_method')
        assert result is True

    def test_should_trace_method_track_all_true_module_not_in_exclude_method_index(self, monkeypatch):
        """Test when track_all is True and module is not in exclude_method_index."""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = {}
        mock_config.exclude_targets = {}
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        tracer = Tracer(mock_config)

        # Set up the required attributes
        tracer.class_info = {'test_module': {'TestClass': {'track_all': True}}}
        tracer.exclude_method_index = {'other_module': {'TestClass': {'excluded_method'}}}
        tracer.method_index = {}

        # Test: track_all True with module not in exclude_method_index
        result = tracer._should_trace_method('test_module', 'TestClass', 'some_method')
        assert result is True

    def test_should_trace_method_track_all_true_class_not_in_exclude_method_index(self, monkeypatch):
        """Test when track_all is True and class is not in exclude_method_index for the module."""
        # Create a mock config
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.with_locals = False
        mock_config.with_globals = False
        mock_config.targets = {}
        mock_config.exclude_targets = {}
        mock_config.output_xml = False
        mock_config.framework = None
        mock_config.wrapper = None
        mock_config.indexes = None

        tracer = Tracer(mock_config)

        # Set up the required attributes
        tracer.class_info = {'test_module': {'TestClass': {'track_all': True}}}
        tracer.exclude_method_index = {'test_module': {'OtherClass': {'excluded_method'}}}
        tracer.method_index = {}

        # Test: track_all True with class not in exclude_method_index for the module
        result = tracer._should_trace_method('test_module', 'TestClass', 'some_method')
        assert result is True
