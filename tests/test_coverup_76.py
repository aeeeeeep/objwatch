# file: objwatch/tracer.py:654-689
# asked: {"lines": [654, 663, 664, 666, 667, 669, 670, 671, 672, 674, 675, 676, 678, 679, 680, 681, 683, 684, 687, 688, 689], "branches": [[666, 667], [666, 669], [669, 670], [669, 671], [671, 672], [671, 674], [674, 0], [674, 675], [675, 676], [675, 678], [688, 674], [688, 689]]}
# gained: {"lines": [654, 663, 664, 666, 667, 669, 670, 671, 672, 674, 675, 676, 678, 679, 680, 681, 683, 684, 687, 688, 689], "branches": [[666, 667], [666, 669], [669, 670], [669, 671], [671, 672], [671, 674], [674, 0], [674, 675], [675, 676], [675, 678], [688, 674], [688, 689]]}

import pytest
from types import FrameType
from unittest.mock import Mock, MagicMock, patch
import sys
from objwatch.config import ObjWatchConfig


class TestTracerTrackGlobalsChange:
    """Test cases for Tracer._track_globals_change method to achieve full coverage."""

    def test_track_globals_change_with_globals_disabled(self, monkeypatch):
        """Test that method returns early when with_globals is False."""
        from objwatch.tracer import Tracer

        # Create a minimal config with with_globals=False
        config = Mock(spec=ObjWatchConfig)
        config.with_globals = False
        config.with_locals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.wrapper = None
        config.indexes = None

        tracer = Tracer(config)

        frame = Mock(spec=FrameType)
        frame.f_globals = {'__name__': 'test_module'}

        # Should return early without processing
        tracer._track_globals_change(frame, 123)

        # Verify no changes were made to tracked collections
        # Since with_globals=False, these attributes shouldn't exist
        assert not hasattr(tracer, 'tracked_globals')
        assert not hasattr(tracer, 'tracked_globals_lens')

    def test_track_globals_change_new_module_initialization(self, monkeypatch):
        """Test initialization of new module in tracked collections."""
        from objwatch.tracer import Tracer

        # Create config with with_globals=True
        config = Mock(spec=ObjWatchConfig)
        config.with_globals = True
        config.with_locals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.wrapper = None
        config.indexes = None

        tracer = Tracer(config)

        # Mock _should_trace_global to return True for specific globals
        def mock_should_trace_global(module, global_name):
            return global_name in ['tracked_var', 'seq_var']

        tracer._should_trace_global = mock_should_trace_global

        frame = Mock(spec=FrameType)
        frame.f_globals = {
            '__name__': 'new_module',
            'tracked_var': 42,
            'seq_var': [1, 2, 3],
            'ignored_var': 'should_not_track',
        }

        tracer._track_globals_change(frame, 456)

        # Verify module was initialized in both collections
        assert 'new_module' in tracer.tracked_globals
        assert 'new_module' in tracer.tracked_globals_lens
        # Verify tracked variables were stored
        assert tracer.tracked_globals['new_module']['tracked_var'] == 42
        assert tracer.tracked_globals['new_module']['seq_var'] == [1, 2, 3]
        # Verify sequence length was tracked
        assert tracer.tracked_globals_lens['new_module']['seq_var'] == 3
        # Verify ignored variable was not tracked
        assert 'ignored_var' not in tracer.tracked_globals['new_module']

    def test_track_globals_change_sequence_types_tracking(self, monkeypatch):
        """Test tracking of sequence types (list, set, dict, tuple) with length."""
        from objwatch.tracer import Tracer
        from objwatch.constants import Constants

        # Create config with with_globals=True
        config = Mock(spec=ObjWatchConfig)
        config.with_globals = True
        config.with_locals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.wrapper = None
        config.indexes = None

        tracer = Tracer(config)
        tracer.tracked_globals = {'existing_module': {}}
        tracer.tracked_globals_lens = {'existing_module': {}}

        # Mock _should_trace_global to return True for all
        tracer._should_trace_global = Mock(return_value=True)

        # Mock _handle_change_type to verify it's called correctly
        mock_handle_change = Mock()
        tracer._handle_change_type = mock_handle_change

        frame = Mock(spec=FrameType)
        frame.f_globals = {
            '__name__': 'existing_module',
            'list_var': [1, 2],
            'set_var': {1, 2, 3},
            'dict_var': {'a': 1, 'b': 2},
            'tuple_var': (4, 5, 6, 7),
            'int_var': 100,
        }

        tracer._track_globals_change(frame, 789)

        # Verify all variables were tracked
        assert tracer.tracked_globals['existing_module']['list_var'] == [1, 2]
        assert tracer.tracked_globals['existing_module']['set_var'] == {1, 2, 3}
        assert tracer.tracked_globals['existing_module']['dict_var'] == {'a': 1, 'b': 2}
        assert tracer.tracked_globals['existing_module']['tuple_var'] == (4, 5, 6, 7)
        assert tracer.tracked_globals['existing_module']['int_var'] == 100

        # Verify sequence lengths were tracked for sequence types
        assert tracer.tracked_globals_lens['existing_module']['list_var'] == 2
        assert tracer.tracked_globals_lens['existing_module']['set_var'] == 3
        assert tracer.tracked_globals_lens['existing_module']['dict_var'] == 2
        assert tracer.tracked_globals_lens['existing_module']['tuple_var'] == 4
        # Non-sequence types should not have length tracked
        assert 'int_var' not in tracer.tracked_globals_lens['existing_module']

        # Verify _handle_change_type was called for each variable
        # There are 5 variables, but __name__ is also processed, making 6 calls
        assert mock_handle_change.call_count == 6

    def test_track_globals_change_with_existing_values(self, monkeypatch):
        """Test tracking when there are existing values in tracked collections."""
        from objwatch.tracer import Tracer

        # Create config with with_globals=True
        config = Mock(spec=ObjWatchConfig)
        config.with_globals = True
        config.with_locals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.wrapper = None
        config.indexes = None

        tracer = Tracer(config)
        tracer.tracked_globals = {'test_module': {'existing_var': 'old_value', 'seq_var': [1, 2]}}
        tracer.tracked_globals_lens = {'test_module': {'seq_var': 2}}

        # Mock _should_trace_global to return True for all
        tracer._should_trace_global = Mock(return_value=True)

        # Mock _handle_change_type to capture calls
        mock_handle_change = Mock()
        tracer._handle_change_type = mock_handle_change

        frame = Mock(spec=FrameType)
        frame.f_globals = {
            '__name__': 'test_module',
            'existing_var': 'new_value',
            'seq_var': [1, 2, 3, 4],  # Length changed from 2 to 4
            'new_var': 'fresh_value',
        }

        tracer._track_globals_change(frame, 999)

        # Verify values were updated
        assert tracer.tracked_globals['test_module']['existing_var'] == 'new_value'
        assert tracer.tracked_globals['test_module']['seq_var'] == [1, 2, 3, 4]
        assert tracer.tracked_globals['test_module']['new_var'] == 'fresh_value'

        # Verify sequence length was updated
        assert tracer.tracked_globals_lens['test_module']['seq_var'] == 4

        # Verify _handle_change_type was called for each variable with correct parameters
        # 3 variables + __name__ = 4 calls
        assert mock_handle_change.call_count == 4

    def test_track_globals_change_filtering_by_should_trace(self, monkeypatch):
        """Test that _should_trace_global filtering works correctly."""
        from objwatch.tracer import Tracer

        # Create config with with_globals=True
        config = Mock(spec=ObjWatchConfig)
        config.with_globals = True
        config.with_locals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.wrapper = None
        config.indexes = None

        tracer = Tracer(config)

        # Create a mock that returns True only for specific variables
        should_trace_calls = []

        def mock_should_trace_global(module, global_name):
            should_trace_calls.append((module, global_name))
            return global_name in ['tracked1', 'tracked2']

        tracer._should_trace_global = mock_should_trace_global

        frame = Mock(spec=FrameType)
        frame.f_globals = {
            '__name__': 'filter_module',
            'tracked1': 'value1',
            'tracked2': [1, 2],
            'ignored1': 'skip1',
            'ignored2': {'a': 1},
        }

        tracer._track_globals_change(frame, 111)

        # Verify only tracked variables were processed
        assert set(tracer.tracked_globals['filter_module'].keys()) == {'tracked1', 'tracked2'}
        assert set(tracer.tracked_globals_lens['filter_module'].keys()) == {'tracked2'}  # Only sequence type

        # Verify _should_trace_global was called for each global including __name__
        expected_calls = [
            ('filter_module', '__name__'),
            ('filter_module', 'tracked1'),
            ('filter_module', 'tracked2'),
            ('filter_module', 'ignored1'),
            ('filter_module', 'ignored2'),
        ]
        assert set(should_trace_calls) == set(expected_calls)
