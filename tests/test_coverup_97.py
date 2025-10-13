# file: objwatch/tracer.py:268-281
# asked: {"lines": [268, 269, 279, 280], "branches": []}
# gained: {"lines": [268, 269, 279, 280], "branches": []}

import pytest
from unittest.mock import Mock, MagicMock
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerShouldTraceClass:
    """Test cases for Tracer._should_trace_class method."""

    def test_should_trace_class_when_class_in_target_and_not_excluded(self, monkeypatch):
        """Test that class is traced when in target index and not in exclude index."""
        # Create a proper mock config with all required attributes
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.targets = []
        mock_config.exclude_targets = None
        mock_config.framework = None
        mock_config.indexes = None
        mock_config.output = None
        mock_config.output_xml = None
        mock_config.level = 10  # logging.DEBUG
        mock_config.simple = False
        mock_config.wrapper = None
        mock_config.with_locals = False
        mock_config.with_globals = False

        # Create tracer instance
        tracer = Tracer(mock_config)

        # Manually set the class_index and exclude_class_index to test the specific method
        tracer.class_index = {'test_module': {'TestClass'}}
        tracer.exclude_class_index = {'test_module': set()}

        # Clear the cache to ensure fresh test
        tracer._should_trace_class.cache_clear()

        # Test the method
        result = tracer._should_trace_class('test_module', 'TestClass')

        # Assert the result
        assert result is True

    def test_should_not_trace_class_when_class_not_in_target(self, monkeypatch):
        """Test that class is not traced when not in target index."""
        # Create a proper mock config with all required attributes
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.targets = []
        mock_config.exclude_targets = None
        mock_config.framework = None
        mock_config.indexes = None
        mock_config.output = None
        mock_config.output_xml = None
        mock_config.level = 10  # logging.DEBUG
        mock_config.simple = False
        mock_config.wrapper = None
        mock_config.with_locals = False
        mock_config.with_globals = False

        # Create tracer instance
        tracer = Tracer(mock_config)

        # Manually set the class_index and exclude_class_index to test the specific method
        tracer.class_index = {'test_module': {'OtherClass'}}
        tracer.exclude_class_index = {'test_module': set()}

        # Clear the cache to ensure fresh test
        tracer._should_trace_class.cache_clear()

        # Test the method
        result = tracer._should_trace_class('test_module', 'TestClass')

        # Assert the result
        assert result is False

    def test_should_not_trace_class_when_class_in_target_but_excluded(self, monkeypatch):
        """Test that class is not traced when in target index but also in exclude index."""
        # Create a proper mock config with all required attributes
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.targets = []
        mock_config.exclude_targets = None
        mock_config.framework = None
        mock_config.indexes = None
        mock_config.output = None
        mock_config.output_xml = None
        mock_config.level = 10  # logging.DEBUG
        mock_config.simple = False
        mock_config.wrapper = None
        mock_config.with_locals = False
        mock_config.with_globals = False

        # Create tracer instance
        tracer = Tracer(mock_config)

        # Manually set the class_index and exclude_class_index to test the specific method
        tracer.class_index = {'test_module': {'TestClass'}}
        tracer.exclude_class_index = {'test_module': {'TestClass'}}

        # Clear the cache to ensure fresh test
        tracer._should_trace_class.cache_clear()

        # Test the method
        result = tracer._should_trace_class('test_module', 'TestClass')

        # Assert the result
        assert result is False

    def test_should_not_trace_class_when_module_not_in_target(self, monkeypatch):
        """Test that class is not traced when module is not in target index."""
        # Create a proper mock config with all required attributes
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.targets = []
        mock_config.exclude_targets = None
        mock_config.framework = None
        mock_config.indexes = None
        mock_config.output = None
        mock_config.output_xml = None
        mock_config.level = 10  # logging.DEBUG
        mock_config.simple = False
        mock_config.wrapper = None
        mock_config.with_locals = False
        mock_config.with_globals = False

        # Create tracer instance
        tracer = Tracer(mock_config)

        # Manually set the class_index and exclude_class_index to test the specific method
        tracer.class_index = {'other_module': {'TestClass'}}
        tracer.exclude_class_index = {}

        # Clear the cache to ensure fresh test
        tracer._should_trace_class.cache_clear()

        # Test the method
        result = tracer._should_trace_class('test_module', 'TestClass')

        # Assert the result
        assert result is False

    def test_should_trace_class_when_module_in_target_but_class_not_in_exclude(self, monkeypatch):
        """Test that class is traced when module has empty exclude set for that class."""
        # Create a proper mock config with all required attributes
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.targets = []
        mock_config.exclude_targets = None
        mock_config.framework = None
        mock_config.indexes = None
        mock_config.output = None
        mock_config.output_xml = None
        mock_config.level = 10  # logging.DEBUG
        mock_config.simple = False
        mock_config.wrapper = None
        mock_config.with_locals = False
        mock_config.with_globals = False

        # Create tracer instance
        tracer = Tracer(mock_config)

        # Manually set the class_index and exclude_class_index to test the specific method
        tracer.class_index = {'test_module': {'TestClass'}}
        tracer.exclude_class_index = {'test_module': {'OtherClass'}}

        # Clear the cache to ensure fresh test
        tracer._should_trace_class.cache_clear()

        # Test the method
        result = tracer._should_trace_class('test_module', 'TestClass')

        # Assert the result
        assert result is True

    def test_should_not_trace_class_when_module_not_in_target_but_in_exclude(self, monkeypatch):
        """Test that class is not traced when module not in target but in exclude."""
        # Create a proper mock config with all required attributes
        mock_config = Mock(spec=ObjWatchConfig)
        mock_config.targets = []
        mock_config.exclude_targets = None
        mock_config.framework = None
        mock_config.indexes = None
        mock_config.output = None
        mock_config.output_xml = None
        mock_config.level = 10  # logging.DEBUG
        mock_config.simple = False
        mock_config.wrapper = None
        mock_config.with_locals = False
        mock_config.with_globals = False

        # Create tracer instance
        tracer = Tracer(mock_config)

        # Manually set the class_index and exclude_class_index to test the specific method
        tracer.class_index = {}
        tracer.exclude_class_index = {'test_module': {'TestClass'}}

        # Clear the cache to ensure fresh test
        tracer._should_trace_class.cache_clear()

        # Test the method
        result = tracer._should_trace_class('test_module', 'TestClass')

        # Assert the result
        assert result is False
