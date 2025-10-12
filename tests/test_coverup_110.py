# file: objwatch/tracer.py:325-338
# asked: {"lines": [325, 326, 336, 337], "branches": []}
# gained: {"lines": [325, 326, 336, 337], "branches": []}

import pytest
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerShouldTraceFunction:
    """Test cases for Tracer._should_trace_function method."""

    def test_should_trace_function_included_and_not_excluded(self, monkeypatch):
        """Test that function is traced when included in targets and not in exclude targets."""

        # Mock the Targets class to avoid module loading issues
        def mock_get_filename_targets(self):
            return set()

        def mock_get_targets(self):
            return {'test_module': {'functions': ['test_func']}}

        def mock_get_exclude_targets(self):
            return {}

        monkeypatch.setattr('objwatch.targets.Targets.get_filename_targets', mock_get_filename_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_targets', mock_get_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_exclude_targets', mock_get_exclude_targets)

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Clear cache to ensure fresh test
        tracer._should_trace_function.cache_clear()

        result = tracer._should_trace_function('test_module', 'test_func')
        assert result is True

    def test_should_trace_function_included_but_excluded(self, monkeypatch):
        """Test that function is not traced when included in targets but also in exclude targets."""

        def mock_get_filename_targets(self):
            return set()

        def mock_get_targets(self):
            return {'test_module': {'functions': ['test_func']}}

        def mock_get_exclude_targets(self):
            return {'test_module': {'functions': ['test_func']}}

        monkeypatch.setattr('objwatch.targets.Targets.get_filename_targets', mock_get_filename_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_targets', mock_get_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_exclude_targets', mock_get_exclude_targets)

        config = ObjWatchConfig(targets=['test_module'], exclude_targets=['test_module'])
        tracer = Tracer(config)

        # Clear cache to ensure fresh test
        tracer._should_trace_function.cache_clear()

        result = tracer._should_trace_function('test_module', 'test_func')
        assert result is False

    def test_should_trace_function_not_included(self, monkeypatch):
        """Test that function is not traced when not included in targets."""

        def mock_get_filename_targets(self):
            return set()

        def mock_get_targets(self):
            return {'test_module': {'functions': ['other_func']}}

        def mock_get_exclude_targets(self):
            return {}

        monkeypatch.setattr('objwatch.targets.Targets.get_filename_targets', mock_get_filename_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_targets', mock_get_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_exclude_targets', mock_get_exclude_targets)

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Clear cache to ensure fresh test
        tracer._should_trace_function.cache_clear()

        result = tracer._should_trace_function('test_module', 'test_func')
        assert result is False

    def test_should_trace_function_module_not_in_targets(self, monkeypatch):
        """Test that function is not traced when module is not in targets."""

        def mock_get_filename_targets(self):
            return set()

        def mock_get_targets(self):
            return {'other_module': {'functions': ['test_func']}}

        def mock_get_exclude_targets(self):
            return {}

        monkeypatch.setattr('objwatch.targets.Targets.get_filename_targets', mock_get_filename_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_targets', mock_get_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_exclude_targets', mock_get_exclude_targets)

        config = ObjWatchConfig(targets=['other_module'])
        tracer = Tracer(config)

        # Clear cache to ensure fresh test
        tracer._should_trace_function.cache_clear()

        result = tracer._should_trace_function('test_module', 'test_func')
        assert result is False

    def test_should_trace_function_with_exclude_only(self, monkeypatch):
        """Test that function is not traced when only in exclude targets."""

        def mock_get_filename_targets(self):
            return set()

        def mock_get_targets(self):
            return {'test_module': {'functions': []}}  # Empty functions list

        def mock_get_exclude_targets(self):
            return {'test_module': {'functions': ['test_func']}}

        monkeypatch.setattr('objwatch.targets.Targets.get_filename_targets', mock_get_filename_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_targets', mock_get_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_exclude_targets', mock_get_exclude_targets)

        config = ObjWatchConfig(targets=['test_module'], exclude_targets=['test_module'])
        tracer = Tracer(config)

        # Clear cache to ensure fresh test
        tracer._should_trace_function.cache_clear()

        result = tracer._should_trace_function('test_module', 'test_func')
        assert result is False

    def test_should_trace_function_multiple_functions(self, monkeypatch):
        """Test tracing with multiple functions in same module."""

        def mock_get_filename_targets(self):
            return set()

        def mock_get_targets(self):
            return {'test_module': {'functions': ['func1', 'func2', 'func3']}}

        def mock_get_exclude_targets(self):
            return {'test_module': {'functions': ['func2']}}

        monkeypatch.setattr('objwatch.targets.Targets.get_filename_targets', mock_get_filename_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_targets', mock_get_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_exclude_targets', mock_get_exclude_targets)

        config = ObjWatchConfig(targets=['test_module'], exclude_targets=['test_module'])
        tracer = Tracer(config)

        # Clear cache to ensure fresh test
        tracer._should_trace_function.cache_clear()

        # func1 should be traced (included, not excluded)
        assert tracer._should_trace_function('test_module', 'func1') is True

        # func2 should not be traced (included but excluded)
        assert tracer._should_trace_function('test_module', 'func2') is False

        # func3 should be traced (included, not excluded)
        assert tracer._should_trace_function('test_module', 'func3') is True

        # func4 should not be traced (not included)
        assert tracer._should_trace_function('test_module', 'func4') is False

    def test_should_trace_function_empty_functions_list(self, monkeypatch):
        """Test that function is not traced when functions list is empty."""

        def mock_get_filename_targets(self):
            return set()

        def mock_get_targets(self):
            return {'test_module': {'functions': []}}  # Empty functions list

        def mock_get_exclude_targets(self):
            return {}

        monkeypatch.setattr('objwatch.targets.Targets.get_filename_targets', mock_get_filename_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_targets', mock_get_targets)
        monkeypatch.setattr('objwatch.targets.Targets.get_exclude_targets', mock_get_exclude_targets)

        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Clear cache to ensure fresh test
        tracer._should_trace_function.cache_clear()

        result = tracer._should_trace_function('test_module', 'test_func')
        assert result is False
