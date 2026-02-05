# MIT License
# Copyright (c) 2025 aeeeeeep

import unittest
from unittest.mock import patch, MagicMock

from objwatch.events.models.event_type import EventType
from objwatch.events.models.function_event import FunctionEvent
from objwatch.events.models.variable_event import VariableEvent
from objwatch.events.handlers.logging_handler import LoggingEventHandler


class TestLoggingEventHandler(unittest.TestCase):
    def setUp(self):
        self.handler = LoggingEventHandler()
        self.func_info = {
            'module': 'test_module',
            'symbol': 'test_func',
            'symbol_type': 'function',
            'qualified_name': 'test_module.test_func',
            'frame': None,
        }

    def test_can_handle(self):
        """Test that handler can process all event types."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )
        self.assertTrue(self.handler.can_handle(event))

    @patch('objwatch.events.handlers.logging_handler.log_debug')
    def test_handle_function_event(self, mock_log_debug):
        """Test handling function event."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )

        self.handler.handle(event)
        mock_log_debug.assert_called_once()
        call_args = mock_log_debug.call_args
        self.assertIn('run', call_args[0][0])

    @patch('objwatch.events.handlers.logging_handler.log_debug')
    def test_handle_variable_event(self, mock_log_debug):
        """Test handling variable event."""
        event = VariableEvent(
            timestamp=1234567890.0,
            event_type=EventType.UPD,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='TestClass',
            key='value',
            old_value=10,
            current_value=20,
        )

        self.handler.handle(event)
        mock_log_debug.assert_called_once()
        call_args = mock_log_debug.call_args
        self.assertIn('upd', call_args[0][0])

    @patch('objwatch.events.handlers.logging_handler.log_debug')
    def test_event_passed_for_deferred_serialization(self, mock_log_debug):
        """Test that event is passed directly for deferred serialization."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )

        self.handler.handle(event)
        call_args = mock_log_debug.call_args
        self.assertIn('extra', call_args[1])
        self.assertIn('event', call_args[1]['extra'])

        # Verify the original event is passed directly
        passed_event = call_args[1]['extra']['event']
        self.assertEqual(passed_event, event)

        # Verify to_dict() works correctly when called (deferred serialization)
        event_dict = passed_event.to_dict()
        self.assertEqual(event_dict['event_type'], 'run')
        self.assertEqual(event_dict['lineno'], 42)
        self.assertEqual(event_dict['call_depth'], 1)

    @patch('objwatch.events.handlers.logging_handler.log_debug')
    def test_event_properties(self, mock_log_debug):
        """Test that event properties are accessible."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )

        self.handler.handle(event)
        call_args = mock_log_debug.call_args
        passed_event = call_args[1]['extra']['event']

        # Test properties
        self.assertEqual(passed_event.event_type, EventType.RUN)
        self.assertEqual(passed_event.lineno, 42)
        self.assertEqual(passed_event.call_depth, 1)
        self.assertEqual(passed_event.index_info, "")
        self.assertIsNone(passed_event.process_id)
        self.assertEqual(passed_event.timestamp, 1234567890.0)
        self.assertTrue(passed_event.is_run_event)
        self.assertFalse(passed_event.is_end_event)


if __name__ == '__main__':
    unittest.main()
