# file: objwatch/tracer.py:304-323
# asked: {"lines": [304, 305, 317, 318, 320, 321, 323], "branches": [[318, 320], [318, 323]]}
# gained: {"lines": [304, 305, 317, 318, 320, 321, 323], "branches": [[318, 320], [318, 323]]}

import pytest
from unittest.mock import Mock
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerShouldTraceAttribute:
    """Test cases for Tracer._should_trace_attribute method."""

    def test_should_trace_attribute_track_all_true_not_excluded(self, monkeypatch):
        """Test when track_all is True and attribute is not in excluded attributes."""
        # Setup
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock the internal data structures
        tracer.class_info = {'test_module': {'TestClass': {'track_all': True}}}
        tracer.exclude_attribute_index = {'test_module': {'TestClass': {'excluded_attr'}}}
        tracer.attribute_index = {}

        # Clear the cache to ensure fresh test
        tracer._should_trace_attribute.cache_clear()

        # Test: attribute not in excluded list
        result = tracer._should_trace_attribute('test_module', 'TestClass', 'some_attr')

        # Assert
        assert result is True

    def test_should_trace_attribute_track_all_true_excluded(self, monkeypatch):
        """Test when track_all is True and attribute is in excluded attributes."""
        # Setup
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock the internal data structures
        tracer.class_info = {'test_module': {'TestClass': {'track_all': True}}}
        tracer.exclude_attribute_index = {'test_module': {'TestClass': {'excluded_attr'}}}
        tracer.attribute_index = {}

        # Clear the cache to ensure fresh test
        tracer._should_trace_attribute.cache_clear()

        # Test: attribute in excluded list
        result = tracer._should_trace_attribute('test_module', 'TestClass', 'excluded_attr')

        # Assert
        assert result is False

    def test_should_trace_attribute_track_all_false_in_attributes(self, monkeypatch):
        """Test when track_all is False and attribute is in attribute index."""
        # Setup
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock the internal data structures
        tracer.class_info = {'test_module': {'TestClass': {'track_all': False}}}
        tracer.exclude_attribute_index = {}
        tracer.attribute_index = {'test_module': {'TestClass': {'target_attr'}}}

        # Clear the cache to ensure fresh test
        tracer._should_trace_attribute.cache_clear()

        # Test: attribute in attribute index
        result = tracer._should_trace_attribute('test_module', 'TestClass', 'target_attr')

        # Assert
        assert result is True

    def test_should_trace_attribute_track_all_false_not_in_attributes(self, monkeypatch):
        """Test when track_all is False and attribute is not in attribute index."""
        # Setup
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock the internal data structures
        tracer.class_info = {'test_module': {'TestClass': {'track_all': False}}}
        tracer.exclude_attribute_index = {}
        tracer.attribute_index = {'test_module': {'TestClass': {'other_attr'}}}

        # Clear the cache to ensure fresh test
        tracer._should_trace_attribute.cache_clear()

        # Test: attribute not in attribute index
        result = tracer._should_trace_attribute('test_module', 'TestClass', 'non_target_attr')

        # Assert
        assert result is False

    def test_should_trace_attribute_module_not_in_class_info(self, monkeypatch):
        """Test when module is not present in class_info."""
        # Setup
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock the internal data structures
        tracer.class_info = {}
        tracer.exclude_attribute_index = {}
        tracer.attribute_index = {}

        # Clear the cache to ensure fresh test
        tracer._should_trace_attribute.cache_clear()

        # Test: module not in class_info
        result = tracer._should_trace_attribute('unknown_module', 'TestClass', 'some_attr')

        # Assert
        assert result is False

    def test_should_trace_attribute_class_not_in_class_info(self, monkeypatch):
        """Test when class is not present in class_info for the module."""
        # Setup
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock the internal data structures
        tracer.class_info = {'test_module': {'OtherClass': {'track_all': True}}}
        tracer.exclude_attribute_index = {}
        tracer.attribute_index = {}

        # Clear the cache to ensure fresh test
        tracer._should_trace_attribute.cache_clear()

        # Test: class not in class_info for module
        result = tracer._should_trace_attribute('test_module', 'UnknownClass', 'some_attr')

        # Assert
        assert result is False

    def test_should_trace_attribute_track_all_true_empty_excluded(self, monkeypatch):
        """Test when track_all is True and excluded attributes is empty."""
        # Setup
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock the internal data structures
        tracer.class_info = {'test_module': {'TestClass': {'track_all': True}}}
        tracer.exclude_attribute_index = {'test_module': {'TestClass': set()}}
        tracer.attribute_index = {}

        # Clear the cache to ensure fresh test
        tracer._should_trace_attribute.cache_clear()

        # Test: empty excluded attributes
        result = tracer._should_trace_attribute('test_module', 'TestClass', 'any_attr')

        # Assert
        assert result is True

    def test_should_trace_attribute_track_all_true_module_not_in_excluded(self, monkeypatch):
        """Test when track_all is True and module not in exclude_attribute_index."""
        # Setup
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock the internal data structures
        tracer.class_info = {'test_module': {'TestClass': {'track_all': True}}}
        tracer.exclude_attribute_index = {}
        tracer.attribute_index = {}

        # Clear the cache to ensure fresh test
        tracer._should_trace_attribute.cache_clear()

        # Test: module not in exclude_attribute_index
        result = tracer._should_trace_attribute('test_module', 'TestClass', 'any_attr')

        # Assert
        assert result is True

    def test_should_trace_attribute_track_all_true_class_not_in_excluded(self, monkeypatch):
        """Test when track_all is True and class not in exclude_attribute_index for module."""
        # Setup
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Mock the internal data structures
        tracer.class_info = {'test_module': {'TestClass': {'track_all': True}}}
        tracer.exclude_attribute_index = {'test_module': {'OtherClass': {'excluded_attr'}}}
        tracer.attribute_index = {}

        # Clear the cache to ensure fresh test
        tracer._should_trace_attribute.cache_clear()

        # Test: class not in exclude_attribute_index for module
        result = tracer._should_trace_attribute('test_module', 'TestClass', 'any_attr')

        # Assert
        assert result is True
