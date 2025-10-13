# file: objwatch/tracer.py:604-652
# asked: {"lines": [604, 612, 613, 615, 616, 617, 619, 620, 621, 623, 624, 625, 626, 627, 628, 629, 630, 631, 634, 635, 637, 638, 639, 640, 641, 642, 643, 645, 646, 649, 650, 652], "branches": [[612, 613], [612, 615], [620, 621], [620, 637], [634, 620], [634, 635], [638, 639], [638, 652], [649, 638], [649, 650]]}
# gained: {"lines": [604, 612, 613, 615, 616, 617, 619, 620, 621, 623, 624, 625, 626, 627, 628, 629, 630, 631, 634, 635, 637, 638, 639, 640, 641, 642, 643, 645, 646, 649, 650, 652], "branches": [[612, 613], [612, 615], [620, 621], [620, 637], [634, 620], [634, 635], [638, 639], [638, 652], [649, 638], [649, 650]]}

import pytest
from types import FrameType
from unittest.mock import Mock, MagicMock, patch
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig
from objwatch.constants import Constants


class TestTracerTrackLocalsChange:
    """Test cases for Tracer._track_locals_change method to achieve full coverage."""

    def test_track_locals_change_with_locals_disabled(self, monkeypatch):
        """Test that method returns early when with_locals is False."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=False)
        tracer = Tracer(config)
        frame = Mock(spec=FrameType)
        lineno = 10

        # Mock event_handlers to ensure it's not called
        mock_event_handlers = Mock()
        tracer.event_handlers = mock_event_handlers

        tracer._track_locals_change(frame, lineno)

        # Verify no interactions with event_handlers
        mock_event_handlers.handle_upd.assert_not_called()

    def test_track_locals_change_frame_not_tracked(self, monkeypatch):
        """Test that method returns early when frame is not in tracked_locals."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=True)
        tracer = Tracer(config)
        frame = Mock(spec=FrameType)
        lineno = 10

        # Ensure frame is not in tracked_locals
        tracer.tracked_locals = {}

        # Mock event_handlers to ensure it's not called
        mock_event_handlers = Mock()
        tracer.event_handlers = mock_event_handlers

        tracer._track_locals_change(frame, lineno)

        # Verify no interactions with event_handlers
        mock_event_handlers.handle_upd.assert_not_called()

    def test_track_locals_change_added_vars(self, monkeypatch):
        """Test handling of newly added local variables."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=True)
        tracer = Tracer(config)
        frame = Mock(spec=FrameType)
        lineno = 10

        # Set up tracked_locals with existing variables
        tracer.tracked_locals = {frame: {'existing_var': 'old_value'}}
        tracer.tracked_locals_lens = {frame: {}}

        # Set up current frame locals with new variable
        frame.f_locals = {
            'existing_var': 'old_value',
            'new_var': 'new_value',
            'self': 'self_value',
            'callable_func': lambda x: x,
        }

        # Mock event_handlers
        mock_event_handlers = Mock()
        tracer.event_handlers = mock_event_handlers
        tracer.call_depth = 1
        tracer.index_info = 'test_index'
        tracer.abc_wrapper = None

        tracer._track_locals_change(frame, lineno)

        # Verify handle_upd was called for the new variable
        mock_event_handlers.handle_upd.assert_called_once_with(
            lineno,
            class_name=Constants.HANDLE_LOCALS_SYMBOL,
            key='new_var',
            old_value=None,
            current_value='new_value',
            call_depth=1,
            index_info='test_index',
            abc_wrapper=None,
        )

        # Verify tracked_locals was updated
        assert tracer.tracked_locals[frame] == {'existing_var': 'old_value', 'new_var': 'new_value'}

    def test_track_locals_change_added_sequence_var(self, monkeypatch):
        """Test handling of newly added sequence local variable."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=True)
        tracer = Tracer(config)
        frame = Mock(spec=FrameType)
        lineno = 10

        # Set up tracked_locals with existing variables
        tracer.tracked_locals = {frame: {'existing_var': 'old_value'}}
        tracer.tracked_locals_lens = {frame: {}}

        # Set up current frame locals with new sequence variable
        new_list = [1, 2, 3]
        frame.f_locals = {'existing_var': 'old_value', 'new_list': new_list, 'self': 'self_value'}

        # Mock event_handlers
        mock_event_handlers = Mock()
        tracer.event_handlers = mock_event_handlers
        tracer.call_depth = 1
        tracer.index_info = 'test_index'
        tracer.abc_wrapper = None

        tracer._track_locals_change(frame, lineno)

        # Verify handle_upd was called for the new sequence variable
        mock_event_handlers.handle_upd.assert_called_once_with(
            lineno,
            class_name=Constants.HANDLE_LOCALS_SYMBOL,
            key='new_list',
            old_value=None,
            current_value=new_list,
            call_depth=1,
            index_info='test_index',
            abc_wrapper=None,
        )

        # Verify tracked_locals_lens was updated for sequence
        assert tracer.tracked_locals_lens[frame]['new_list'] == len(new_list)
        assert tracer.tracked_locals[frame] == {'existing_var': 'old_value', 'new_list': new_list}

    def test_track_locals_change_common_vars(self, monkeypatch):
        """Test handling of common local variables that exist in both old and current."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=True)
        tracer = Tracer(config)
        frame = Mock(spec=FrameType)
        lineno = 10

        # Set up tracked_locals with existing variables
        old_value = 'old_value'
        tracer.tracked_locals = {frame: {'common_var': old_value}}
        tracer.tracked_locals_lens = {frame: {}}

        # Set up current frame locals with updated variable
        current_value = 'new_value'
        frame.f_locals = {'common_var': current_value, 'self': 'self_value'}

        # Mock _handle_change_type
        mock_handle_change = Mock()
        tracer._handle_change_type = mock_handle_change
        tracer.call_depth = 1
        tracer.index_info = 'test_index'
        tracer.abc_wrapper = None

        tracer._track_locals_change(frame, lineno)

        # Verify _handle_change_type was called for the common variable
        mock_handle_change.assert_called_once_with(
            lineno,
            Constants.HANDLE_LOCALS_SYMBOL,
            'common_var',
            old_value,
            current_value,
            None,  # old_local_len
            None,  # current_local_len
        )

        # Verify tracked_locals was updated
        assert tracer.tracked_locals[frame] == {'common_var': current_value}

    def test_track_locals_change_common_sequence_vars(self, monkeypatch):
        """Test handling of common sequence local variables with length tracking."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=True)
        tracer = Tracer(config)
        frame = Mock(spec=FrameType)
        lineno = 10

        # Set up tracked_locals with existing sequence variable
        old_list = [1, 2]
        tracer.tracked_locals = {frame: {'list_var': old_list}}
        tracer.tracked_locals_lens = {frame: {'list_var': len(old_list)}}

        # Set up current frame locals with updated sequence variable
        current_list = [1, 2, 3, 4]
        frame.f_locals = {'list_var': current_list, 'self': 'self_value'}

        # Mock _handle_change_type
        mock_handle_change = Mock()
        tracer._handle_change_type = mock_handle_change
        tracer.call_depth = 1
        tracer.index_info = 'test_index'
        tracer.abc_wrapper = None

        tracer._track_locals_change(frame, lineno)

        # Verify _handle_change_type was called for the sequence variable with lengths
        mock_handle_change.assert_called_once_with(
            lineno,
            Constants.HANDLE_LOCALS_SYMBOL,
            'list_var',
            old_list,
            current_list,
            len(old_list),  # old_local_len
            len(current_list),  # current_local_len
        )

        # Verify tracked_locals_lens was updated
        assert tracer.tracked_locals_lens[frame]['list_var'] == len(current_list)
        assert tracer.tracked_locals[frame] == {'list_var': current_list}

    def test_track_locals_change_mixed_vars(self, monkeypatch):
        """Test handling of mixed added and common variables."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=True)
        tracer = Tracer(config)
        frame = Mock(spec=FrameType)
        lineno = 10

        # Set up tracked_locals with existing variables
        tracer.tracked_locals = {frame: {'common_var': 'old_value'}}
        tracer.tracked_locals_lens = {frame: {}}

        # Set up current frame locals with mixed variables
        frame.f_locals = {
            'common_var': 'updated_value',
            'new_var': 'new_value',
            'new_list': [1, 2, 3],
            'self': 'self_value',
            'callable_func': lambda x: x,
        }

        # Mock event handlers
        mock_event_handlers = Mock()
        tracer.event_handlers = mock_event_handlers
        mock_handle_change = Mock()
        tracer._handle_change_type = mock_handle_change
        tracer.call_depth = 1
        tracer.index_info = 'test_index'
        tracer.abc_wrapper = None

        tracer._track_locals_change(frame, lineno)

        # Verify handle_upd was called for both new variables
        assert mock_event_handlers.handle_upd.call_count == 2

        # Verify _handle_change_type was called for common variable
        mock_handle_change.assert_called_once_with(
            lineno, Constants.HANDLE_LOCALS_SYMBOL, 'common_var', 'old_value', 'updated_value', None, None
        )

        # Verify tracked_locals_lens was updated for sequence
        assert tracer.tracked_locals_lens[frame]['new_list'] == 3

        # Verify final tracked_locals state
        expected_locals = {'common_var': 'updated_value', 'new_var': 'new_value', 'new_list': [1, 2, 3]}
        assert tracer.tracked_locals[frame] == expected_locals
