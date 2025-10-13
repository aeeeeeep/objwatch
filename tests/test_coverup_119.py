# file: objwatch/tracer.py:560-602
# asked: {"lines": [560, 568, 569, 571, 572, 573, 575, 576, 577, 578, 579, 581, 582, 583, 585, 586, 587, 588, 590, 591, 592, 593, 594, 595, 596, 597, 600, 601, 602], "branches": [[568, 569], [568, 571], [575, 0], [575, 576], [581, 0], [581, 582], [582, 583], [582, 585], [601, 581], [601, 602]]}
# gained: {"lines": [560, 568, 569, 571, 572, 573, 575, 576, 577, 578, 579, 581, 582, 583, 585, 586, 587, 588, 590, 591, 592, 593, 594, 595, 596, 597, 600, 601, 602], "branches": [[568, 569], [568, 571], [575, 0], [575, 576], [581, 0], [581, 582], [582, 583], [582, 585], [601, 581], [601, 602]]}

import pytest
from unittest.mock import Mock, MagicMock, patch
import types
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig
from objwatch.constants import Constants


class TestObject:
    def __init__(self):
        self.regular_attr = "initial"
        self.list_attr = [1, 2, 3]
        self.dict_attr = {"a": 1, "b": 2}
        self.tuple_attr = (1, 2, 3)
        self.set_attr = {1, 2, 3}


class TestTrackObjectChange:

    def test_track_object_change_no_self_in_locals(self, monkeypatch):
        """Test that method returns early when 'self' not in frame.f_locals"""
        config = ObjWatchConfig(targets=["test_file.py"])
        tracer = Tracer(config)
        mock_frame = Mock()
        mock_frame.f_locals = {}

        tracer._track_object_change(mock_frame, 100)

        # No assertions needed - just verifying no exceptions and early return

    def test_track_object_change_object_not_tracked(self, monkeypatch):
        """Test that method returns early when object is not in tracked_objects"""
        config = ObjWatchConfig(targets=["test_file.py"])
        tracer = Tracer(config)
        tracer.tracked_objects = {}
        tracer.tracked_objects_lens = {}

        test_obj = TestObject()
        mock_frame = Mock()
        mock_frame.f_locals = {'self': test_obj}
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': '__main__'}

        tracer._track_object_change(mock_frame, 100)

        # No assertions needed - just verifying no exceptions and early return

    def test_track_object_change_with_sequence_types(self, monkeypatch):
        """Test tracking changes with sequence types (list, dict, tuple, set)"""
        config = ObjWatchConfig(targets=["test_file.py"])
        tracer = Tracer(config)

        # Setup tracked object
        test_obj = TestObject()
        tracer.tracked_objects = {
            test_obj: {'list_attr': [1, 2], 'dict_attr': {'a': 1}, 'tuple_attr': (1, 2), 'set_attr': {1, 2}}
        }
        tracer.tracked_objects_lens = {test_obj: {'list_attr': 2, 'dict_attr': 1, 'tuple_attr': 2, 'set_attr': 2}}

        # Mock dependencies
        mock_frame = Mock()
        mock_frame.f_locals = {'self': test_obj}
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': '__main__'}

        # Mock _filename_endswith to return True (trace all attrs)
        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: True)
        monkeypatch.setattr(tracer, '_should_trace_attribute', lambda m, c, a: True)

        # Mock _handle_change_type to verify it's called correctly
        mock_handle_change = Mock()
        monkeypatch.setattr(tracer, '_handle_change_type', mock_handle_change)

        tracer._track_object_change(mock_frame, 100)

        # Verify _handle_change_type was called for each attribute (including regular_attr)
        assert mock_handle_change.call_count == 5

        # Verify tracked objects were updated
        assert tracer.tracked_objects[test_obj]['regular_attr'] == 'initial'
        assert tracer.tracked_objects[test_obj]['list_attr'] == [1, 2, 3]
        assert tracer.tracked_objects[test_obj]['dict_attr'] == {"a": 1, "b": 2}
        assert tracer.tracked_objects[test_obj]['tuple_attr'] == (1, 2, 3)
        assert tracer.tracked_objects[test_obj]['set_attr'] == {1, 2, 3}

        # Verify tracked objects lens were updated for sequence types
        assert tracer.tracked_objects_lens[test_obj]['list_attr'] == 3
        assert tracer.tracked_objects_lens[test_obj]['dict_attr'] == 2
        assert tracer.tracked_objects_lens[test_obj]['tuple_attr'] == 3
        assert tracer.tracked_objects_lens[test_obj]['set_attr'] == 3
        # regular_attr should not have lens entry
        assert 'regular_attr' not in tracer.tracked_objects_lens[test_obj]

    def test_track_object_change_with_filtered_attributes(self, monkeypatch):
        """Test that attributes are filtered based on _should_trace_attribute"""
        config = ObjWatchConfig(targets=["test_file.py"])
        tracer = Tracer(config)

        test_obj = TestObject()
        tracer.tracked_objects = {test_obj: {'regular_attr': 'old', 'list_attr': [1, 2]}}
        tracer.tracked_objects_lens = {test_obj: {'list_attr': 2}}

        mock_frame = Mock()
        mock_frame.f_locals = {'self': test_obj}
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': '__main__'}

        # Mock _filename_endswith to return False (use attribute filtering)
        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: False)

        # Mock _should_trace_attribute to only allow 'list_attr'
        def mock_should_trace(module, class_name, attr_name):
            return attr_name == 'list_attr'

        monkeypatch.setattr(tracer, '_should_trace_attribute', mock_should_trace)

        mock_handle_change = Mock()
        monkeypatch.setattr(tracer, '_handle_change_type', mock_handle_change)

        tracer._track_object_change(mock_frame, 100)

        # Verify only list_attr was processed (not regular_attr)
        assert mock_handle_change.call_count == 1
        call_args = mock_handle_change.call_args[0]
        assert call_args[2] == 'list_attr'  # key should be 'list_attr'

        # Verify tracked objects were updated only for list_attr
        assert tracer.tracked_objects[test_obj]['list_attr'] == [1, 2, 3]
        # regular_attr should remain unchanged since it wasn't processed
        assert tracer.tracked_objects[test_obj]['regular_attr'] == 'old'

    def test_track_object_change_non_sequence_attributes(self, monkeypatch):
        """Test tracking changes with non-sequence attributes"""
        config = ObjWatchConfig(targets=["test_file.py"])
        tracer = Tracer(config)

        # Create a test object with only non-sequence attributes
        class TestObjectNonSequence:
            def __init__(self):
                self.regular_attr = "initial"
                self.number_attr = 42
                self.string_attr = "hello"

        test_obj = TestObjectNonSequence()
        tracer.tracked_objects = {
            test_obj: {'regular_attr': 'old_value', 'number_attr': 100, 'string_attr': 'old_string'}
        }
        tracer.tracked_objects_lens = {test_obj: {}}

        mock_frame = Mock()
        mock_frame.f_locals = {'self': test_obj}
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': '__main__'}

        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: True)
        monkeypatch.setattr(tracer, '_should_trace_attribute', lambda m, c, a: True)

        mock_handle_change = Mock()
        monkeypatch.setattr(tracer, '_handle_change_type', mock_handle_change)

        tracer._track_object_change(mock_frame, 100)

        # Verify _handle_change_type was called for each non-sequence attribute
        assert mock_handle_change.call_count == 3

        # Find the call for regular_attr specifically
        regular_attr_call = None
        for call in mock_handle_change.call_args_list:
            if call[0][2] == 'regular_attr':
                regular_attr_call = call
                break

        assert regular_attr_call is not None
        call_args = regular_attr_call[0]
        assert call_args[2] == 'regular_attr'  # key
        assert call_args[3] == 'old_value'  # old_value
        assert call_args[4] == 'initial'  # current_value
        assert call_args[5] is None  # old_value_len (None for non-sequence)
        assert call_args[6] is None  # current_value_len (None for non-sequence)

        # Verify tracked objects were updated
        assert tracer.tracked_objects[test_obj]['regular_attr'] == 'initial'
        assert tracer.tracked_objects[test_obj]['number_attr'] == 42
        assert tracer.tracked_objects[test_obj]['string_attr'] == 'hello'
        # No lens update for non-sequence types
        assert 'regular_attr' not in tracer.tracked_objects_lens[test_obj]
        assert 'number_attr' not in tracer.tracked_objects_lens[test_obj]
        assert 'string_attr' not in tracer.tracked_objects_lens[test_obj]

    def test_track_object_change_with_callable_filtering(self, monkeypatch):
        """Test that callable attributes are filtered out in current_attrs"""
        config = ObjWatchConfig(targets=["test_file.py"])
        tracer = Tracer(config)

        class TestObjWithCallable:
            def __init__(self):
                self.data = "value"
                self.method = lambda x: x + 1

        test_obj = TestObjWithCallable()
        tracer.tracked_objects = {test_obj: {'data': 'old_value'}}
        tracer.tracked_objects_lens = {test_obj: {}}

        mock_frame = Mock()
        mock_frame.f_locals = {'self': test_obj}
        mock_frame.f_code.co_filename = "test_file.py"
        mock_frame.f_globals = {'__name__': '__main__'}

        monkeypatch.setattr(tracer, '_filename_endswith', lambda x: True)
        monkeypatch.setattr(tracer, '_should_trace_attribute', lambda m, c, a: True)

        mock_handle_change = Mock()
        monkeypatch.setattr(tracer, '_handle_change_type', mock_handle_change)

        tracer._track_object_change(mock_frame, 100)

        # Verify only non-callable attribute was processed
        assert mock_handle_change.call_count == 1
        call_args = mock_handle_change.call_args[0]
        assert call_args[2] == 'data'
        assert 'method' not in test_obj.__dict__ or callable(test_obj.__dict__['method'])
