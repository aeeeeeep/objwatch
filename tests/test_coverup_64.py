# file: objwatch/tracer.py:494-558
# asked: {"lines": [494, 496, 497, 498, 499, 500, 501, 502, 503, 516, 517, 518, 519, 520, 523, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557], "branches": [[516, 517], [516, 523], [525, 526], [525, 548], [526, 527], [526, 537], [537, 0], [537, 538], [548, 0], [548, 549]]}
# gained: {"lines": [494, 496, 497, 498, 499, 500, 501, 502, 503, 516, 517, 518, 519, 523, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557], "branches": [[516, 517], [516, 523], [525, 526], [525, 548], [526, 527], [526, 537], [537, 0], [537, 538], [548, 549]]}

import pytest
from unittest.mock import Mock, MagicMock, patch
from objwatch.tracer import Tracer
from objwatch.events import EventType
from objwatch.config import ObjWatchConfig


class TestTracerHandleChangeType:
    """Test cases for Tracer._handle_change_type method to achieve full coverage."""

    def test_handle_change_type_with_lengths_apd_same_id(self, monkeypatch):
        """Test _handle_change_type with lengths, APD change type, and same object IDs."""
        config = ObjWatchConfig(targets=["__main__"])
        tracer = Tracer(config)

        # Mock event handlers
        mock_handlers = Mock()
        mock_handlers.determine_change_type.return_value = EventType.APD
        tracer.event_handlers = mock_handlers

        # Mock call_depth and index_info
        tracer.call_depth = 1
        tracer.index_info = "test_index"

        # Create same object (same ID) but modify it to simulate append
        test_list = [1, 2]
        old_value = test_list
        test_list.append(3)  # Now test_list is [1, 2, 3] but same object ID

        # Call the method with same object IDs and lengths that result in APD
        tracer._handle_change_type(
            lineno=10,
            class_name="TestClass",
            key="test_key",
            old_value=old_value,
            current_value=test_list,  # Same object ID but different content
            old_value_len=2,
            current_value_len=3,
        )

        # Verify APD handler was called
        mock_handlers.handle_apd.assert_called_once_with(10, "TestClass", "test_key", list, 2, 3, 1, "test_index")

    def test_handle_change_type_with_lengths_pop_same_id(self, monkeypatch):
        """Test _handle_change_type with lengths, POP change type, and same object IDs."""
        config = ObjWatchConfig(targets=["__main__"])
        tracer = Tracer(config)

        # Mock event handlers
        mock_handlers = Mock()
        mock_handlers.determine_change_type.return_value = EventType.POP
        tracer.event_handlers = mock_handlers

        # Mock call_depth and index_info
        tracer.call_depth = 1
        tracer.index_info = "test_index"

        # Create same object (same ID) but modify it to simulate pop
        test_list = [1, 2, 3]
        old_value = test_list
        test_list.pop()  # Now test_list is [1, 2] but same object ID

        # Call the method with same object IDs and lengths that result in POP
        tracer._handle_change_type(
            lineno=20,
            class_name="TestClass",
            key="test_key",
            old_value=old_value,
            current_value=test_list,  # Same object ID but different content
            old_value_len=3,
            current_value_len=2,
        )

        # Verify POP handler was called
        mock_handlers.handle_pop.assert_called_once_with(20, "TestClass", "test_key", list, 3, 2, 1, "test_index")

    def test_handle_change_type_with_lengths_upd_different_id(self, monkeypatch):
        """Test _handle_change_type with lengths, UPD change type, and different object IDs."""
        config = ObjWatchConfig(targets=["__main__"])
        tracer = Tracer(config)

        # Mock event handlers
        mock_handlers = Mock()
        mock_handlers.determine_change_type.return_value = EventType.UPD
        tracer.event_handlers = mock_handlers

        # Mock call_depth, index_info, and abc_wrapper
        tracer.call_depth = 1
        tracer.index_info = "test_index"
        tracer.abc_wrapper = Mock()

        # Create different objects (different IDs)
        old_val = [1, 2]
        current_val = [3, 4]

        # Call the method with different object IDs and UPD change type
        tracer._handle_change_type(
            lineno=30,
            class_name="TestClass",
            key="test_key",
            old_value=old_val,
            current_value=current_val,
            old_value_len=2,
            current_value_len=2,
        )

        # Verify UPD handler was called
        mock_handlers.handle_upd.assert_called_once_with(
            30, "TestClass", "test_key", old_val, current_val, 1, "test_index", tracer.abc_wrapper
        )

    def test_handle_change_type_without_lengths_upd_different_id(self, monkeypatch):
        """Test _handle_change_type without lengths, UPD change type, and different object IDs."""
        config = ObjWatchConfig(targets=["__main__"])
        tracer = Tracer(config)

        # Mock event handlers
        mock_handlers = Mock()
        tracer.event_handlers = mock_handlers

        # Mock call_depth, index_info, and abc_wrapper
        tracer.call_depth = 1
        tracer.index_info = "test_index"
        tracer.abc_wrapper = Mock()

        # Create different objects (different IDs)
        old_val = {"a": 1}
        current_val = {"b": 2}

        # Call the method with different object IDs and no lengths (should default to UPD)
        tracer._handle_change_type(
            lineno=40,
            class_name="TestClass",
            key="test_key",
            old_value=old_val,
            current_value=current_val,
            old_value_len=None,
            current_value_len=None,
        )

        # Verify UPD handler was called
        mock_handlers.handle_upd.assert_called_once_with(
            40, "TestClass", "test_key", old_val, current_val, 1, "test_index", tracer.abc_wrapper
        )

    def test_handle_change_type_with_lengths_none_change_same_id(self, monkeypatch):
        """Test _handle_change_type with lengths, None change type, and same object IDs."""
        config = ObjWatchConfig(targets=["__main__"])
        tracer = Tracer(config)

        # Mock event handlers
        mock_handlers = Mock()
        mock_handlers.determine_change_type.return_value = None
        tracer.event_handlers = mock_handlers

        # Mock call_depth and index_info
        tracer.call_depth = 1
        tracer.index_info = "test_index"

        # Create same object (same ID) with no length change
        test_list = [1, 2]
        old_value = test_list

        # Call the method with same object IDs and lengths that result in None change type
        tracer._handle_change_type(
            lineno=50,
            class_name="TestClass",
            key="test_key",
            old_value=old_value,
            current_value=test_list,  # Same object, same length
            old_value_len=2,
            current_value_len=2,
        )

        # Verify no handlers were called (None change type with same IDs)
        mock_handlers.handle_apd.assert_not_called()
        mock_handlers.handle_pop.assert_not_called()
        mock_handlers.handle_upd.assert_not_called()

    def test_handle_change_type_with_lengths_upd_same_id(self, monkeypatch):
        """Test _handle_change_type with lengths, UPD change type, and same object IDs."""
        config = ObjWatchConfig(targets=["__main__"])
        tracer = Tracer(config)

        # Mock event handlers
        mock_handlers = Mock()
        mock_handlers.determine_change_type.return_value = EventType.UPD
        tracer.event_handlers = mock_handlers

        # Mock call_depth and index_info
        tracer.call_depth = 1
        tracer.index_info = "test_index"

        # Create same object (same ID)
        test_list = [1, 2]
        old_value = test_list

        # Call the method with same object IDs and UPD change type
        tracer._handle_change_type(
            lineno=60,
            class_name="TestClass",
            key="test_key",
            old_value=old_value,
            current_value=test_list,  # Same object
            old_value_len=2,
            current_value_len=2,
        )

        # Verify no handlers were called (UPD change type with same IDs)
        mock_handlers.handle_apd.assert_not_called()
        mock_handlers.handle_pop.assert_not_called()
        mock_handlers.handle_upd.assert_not_called()

    def test_handle_change_type_without_lengths_same_id(self, monkeypatch):
        """Test _handle_change_type without lengths and same object IDs."""
        config = ObjWatchConfig(targets=["__main__"])
        tracer = Tracer(config)

        # Mock event handlers
        mock_handlers = Mock()
        tracer.event_handlers = mock_handlers

        # Mock call_depth and index_info
        tracer.call_depth = 1
        tracer.index_info = "test_index"

        # Create same object (same ID)
        test_dict = {"a": 1}
        old_value = test_dict

        # Call the method with same object IDs and no lengths
        tracer._handle_change_type(
            lineno=70,
            class_name="TestClass",
            key="test_key",
            old_value=old_value,
            current_value=test_dict,  # Same object
            old_value_len=None,
            current_value_len=None,
        )

        # Verify no handlers were called (no lengths with same IDs)
        mock_handlers.handle_apd.assert_not_called()
        mock_handlers.handle_pop.assert_not_called()
        mock_handlers.handle_upd.assert_not_called()
