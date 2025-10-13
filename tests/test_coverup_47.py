# file: objwatch/tracer.py:691-771
# asked: {"lines": [691, 699, 714, 715, 717, 719, 720, 721, 722, 724, 726, 727, 729, 730, 731, 732, 735, 736, 737, 738, 739, 740, 741, 743, 745, 747, 748, 749, 750, 751, 755, 756, 757, 759, 761, 763, 764, 765, 767, 769, 771], "branches": [[714, 715], [714, 717], [717, 719], [717, 722], [719, 720], [719, 726], [722, 724], [722, 726], [727, 729], [727, 745], [735, 736], [735, 743], [739, 740], [739, 743], [740, 739], [740, 741], [745, 747], [745, 761], [755, 756], [755, 759], [761, 763], [761, 769]]}
# gained: {"lines": [691, 699, 714, 715, 717, 719, 720, 721, 722, 724, 726, 727, 729, 730, 731, 732, 735, 736, 737, 738, 739, 740, 741, 743, 745, 747, 748, 749, 750, 751, 755, 756, 757, 759, 761, 763, 764, 765, 767, 769, 771], "branches": [[714, 715], [714, 717], [717, 719], [717, 722], [719, 720], [719, 726], [722, 724], [727, 729], [727, 745], [735, 736], [735, 743], [739, 740], [739, 743], [740, 739], [740, 741], [745, 747], [745, 761], [755, 756], [761, 763], [761, 769]]}

import pytest
import sys
from types import FrameType
from unittest.mock import Mock, MagicMock, patch
import objwatch.tracer
from objwatch.constants import Constants


class TestTracerTraceFactory:
    """Test cases for Tracer.trace_factory method to achieve full coverage."""

    def test_trace_factory_should_not_trace_frame(self, monkeypatch):
        """Test that trace_func returns early when _should_trace_frame returns False."""
        from objwatch.tracer import Tracer
        from objwatch.config import ObjWatchConfig

        config = Mock(spec=ObjWatchConfig)
        config.with_locals = False
        config.with_globals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.indexes = [0]
        config.wrapper = None

        tracer = Tracer(config)
        tracer._should_trace_frame = Mock(return_value=False)
        tracer.current_index = None

        trace_func = tracer.trace_factory()

        mock_frame = Mock(spec=FrameType)
        mock_frame.f_lineno = 10

        # Should return trace_func immediately without further processing
        result = trace_func(mock_frame, "call", None)
        assert result is trace_func

        tracer._should_trace_frame.assert_called_once_with(mock_frame)

    def test_trace_factory_current_index_not_in_indexes(self, monkeypatch):
        """Test that trace_func returns early when current_index is not in indexes."""
        from objwatch.tracer import Tracer
        from objwatch.config import ObjWatchConfig

        config = Mock(spec=ObjWatchConfig)
        config.with_locals = False
        config.with_globals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.indexes = [2, 3]
        config.wrapper = None

        tracer = Tracer(config)
        tracer._should_trace_frame = Mock(return_value=True)
        tracer.current_index = 1
        tracer.indexes = {2, 3}  # current_index 1 not in indexes

        trace_func = tracer.trace_factory()

        mock_frame = Mock(spec=FrameType)
        mock_frame.f_lineno = 10

        # Should return trace_func immediately without further processing
        result = trace_func(mock_frame, "call", None)
        assert result is trace_func

        tracer._should_trace_frame.assert_called_once_with(mock_frame)

    def test_trace_factory_call_event_with_locals(self, monkeypatch):
        """Test call event handling with locals tracking enabled."""
        from objwatch.tracer import Tracer
        from objwatch.config import ObjWatchConfig

        config = Mock(spec=ObjWatchConfig)
        config.with_locals = True
        config.with_globals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.indexes = [0, 1]
        config.wrapper = None

        tracer = Tracer(config)
        tracer._should_trace_frame = Mock(return_value=True)
        tracer.current_index = None
        tracer.indexes = {0, 1}
        tracer.mp_handlers = Mock()
        tracer.mp_handlers.is_initialized.return_value = False
        tracer._get_function_info = Mock(return_value={"func": "info"})
        tracer._update_objects_lens = Mock()
        tracer.event_handlers = Mock()
        tracer.abc_wrapper = Mock()
        tracer.call_depth = 0
        tracer.index_info = ""

        trace_func = tracer.trace_factory()

        mock_frame = Mock(spec=FrameType)
        mock_frame.f_lineno = 10
        mock_frame.f_locals = {"x": [1, 2, 3], "y": "hello", "self": Mock(), "func": lambda x: x}
        mock_frame.f_code.co_filename = "test.py"

        result = trace_func(mock_frame, "call", None)

        assert result is trace_func
        tracer._get_function_info.assert_called_once_with(mock_frame)
        tracer._update_objects_lens.assert_called_once_with(mock_frame)
        tracer.event_handlers.handle_run.assert_called_once_with(10, {"func": "info"}, tracer.abc_wrapper, 0, "")
        assert tracer.call_depth == 1
        assert mock_frame in tracer.tracked_locals
        assert "x" in tracer.tracked_locals[mock_frame]
        assert "y" in tracer.tracked_locals[mock_frame]
        assert "self" not in tracer.tracked_locals[mock_frame]
        assert "func" not in tracer.tracked_locals[mock_frame]
        assert mock_frame in tracer.tracked_locals_lens
        assert tracer.tracked_locals_lens[mock_frame]["x"] == 3

    def test_trace_factory_return_event_with_locals(self, monkeypatch):
        """Test return event handling with locals tracking enabled."""
        from objwatch.tracer import Tracer
        from objwatch.config import ObjWatchConfig

        config = Mock(spec=ObjWatchConfig)
        config.with_locals = True
        config.with_globals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.indexes = [0, 1]
        config.wrapper = None

        tracer = Tracer(config)
        tracer._should_trace_frame = Mock(return_value=True)
        tracer.current_index = None
        tracer.indexes = {0, 1}
        tracer.mp_handlers = Mock()
        tracer.mp_handlers.is_initialized.return_value = False
        tracer._get_function_info = Mock(return_value={"func": "info"})
        tracer._update_objects_lens = Mock()
        tracer.event_handlers = Mock()
        tracer.abc_wrapper = Mock()
        tracer.call_depth = 2
        tracer.index_info = ""

        # Add frame to tracked_locals to test cleanup
        mock_frame = Mock(spec=FrameType)
        tracer.tracked_locals[mock_frame] = {"x": 1}
        tracer.tracked_locals_lens[mock_frame] = {"x": 1}

        trace_func = tracer.trace_factory()

        mock_frame.f_lineno = 20

        result = trace_func(mock_frame, "return", "return_value")

        assert result is trace_func
        assert tracer.call_depth == 1
        tracer._get_function_info.assert_called_once_with(mock_frame)
        tracer._update_objects_lens.assert_called_once_with(mock_frame)
        tracer.event_handlers.handle_end.assert_called_once_with(
            20, {"func": "info"}, tracer.abc_wrapper, 1, "", "return_value"
        )
        assert mock_frame not in tracer.tracked_locals
        assert mock_frame not in tracer.tracked_locals_lens

    def test_trace_factory_line_event(self, monkeypatch):
        """Test line event handling."""
        from objwatch.tracer import Tracer
        from objwatch.config import ObjWatchConfig

        config = Mock(spec=ObjWatchConfig)
        config.with_locals = False
        config.with_globals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.indexes = [0, 1]
        config.wrapper = None

        tracer = Tracer(config)
        tracer._should_trace_frame = Mock(return_value=True)
        tracer.current_index = None
        tracer.indexes = {0, 1}
        tracer.mp_handlers = Mock()
        tracer.mp_handlers.is_initialized.return_value = False
        tracer._track_object_change = Mock()
        tracer._track_locals_change = Mock()
        tracer._track_globals_change = Mock()

        trace_func = tracer.trace_factory()

        mock_frame = Mock(spec=FrameType)
        mock_frame.f_lineno = 30

        result = trace_func(mock_frame, "line", None)

        assert result is trace_func
        tracer._track_object_change.assert_called_once_with(mock_frame, 30)
        tracer._track_locals_change.assert_called_once_with(mock_frame, 30)
        tracer._track_globals_change.assert_called_once_with(mock_frame, 30)

    def test_trace_factory_mp_initialized(self, monkeypatch):
        """Test multi-process framework initialization."""
        from objwatch.tracer import Tracer
        from objwatch.config import ObjWatchConfig

        config = Mock(spec=ObjWatchConfig)
        config.with_locals = False
        config.with_globals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.indexes = [0, 1]
        config.wrapper = None

        tracer = Tracer(config)
        tracer._should_trace_frame = Mock(return_value=True)
        tracer.current_index = None
        tracer.indexes = {0, 1}
        tracer.mp_handlers = Mock()
        tracer.mp_handlers.is_initialized.return_value = True
        tracer.mp_handlers.get_index.return_value = 0
        tracer._get_function_info = Mock(return_value={"func": "info"})
        tracer._update_objects_lens = Mock()
        tracer.event_handlers = Mock()
        tracer.abc_wrapper = Mock()
        tracer.call_depth = 0
        tracer.index_info = ""

        trace_func = tracer.trace_factory()

        mock_frame = Mock(spec=FrameType)
        mock_frame.f_lineno = 10
        mock_frame.f_locals = {}

        result = trace_func(mock_frame, "call", None)

        assert result is trace_func
        assert tracer.current_index == 0
        assert tracer.index_info == "[#0] "
        tracer.mp_handlers.is_initialized.assert_called_once()
        tracer.mp_handlers.get_index.assert_called_once()

    def test_trace_factory_unknown_event(self, monkeypatch):
        """Test handling of unknown event types."""
        from objwatch.tracer import Tracer
        from objwatch.config import ObjWatchConfig

        config = Mock(spec=ObjWatchConfig)
        config.with_locals = False
        config.with_globals = False
        config.targets = []
        config.exclude_targets = []
        config.output_xml = False
        config.framework = None
        config.indexes = [0, 1]
        config.wrapper = None

        tracer = Tracer(config)
        tracer._should_trace_frame = Mock(return_value=True)
        tracer.current_index = None
        tracer.indexes = {0, 1}
        tracer.mp_handlers = Mock()
        tracer.mp_handlers.is_initialized.return_value = False

        trace_func = tracer.trace_factory()

        mock_frame = Mock(spec=FrameType)
        mock_frame.f_lineno = 40

        # Test with unknown event type
        result = trace_func(mock_frame, "unknown_event", None)

        assert result is trace_func
