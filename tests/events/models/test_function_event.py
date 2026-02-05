# MIT License
# Copyright (c) 2025 aeeeeeep

import unittest
from types import FrameType

from objwatch.events.models.event_type import EventType
from objwatch.events.models.function_event import FunctionEvent


class TestFunctionEvent(unittest.TestCase):
    def setUp(self):
        self.func_info = {
            'module': 'test_module',
            'symbol': 'TestClass.test_method',
            'symbol_type': 'method',
            'qualified_name': 'test_module.TestClass.test_method',
            'frame': None,
        }

    def test_run_event_creation(self):
        """Test creating a function run event."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
            call_msg="'0':10, '1':20",
        )

        self.assertEqual(event.event_type, EventType.RUN)
        self.assertEqual(event.lineno, 42)
        self.assertEqual(event.call_depth, 1)
        self.assertEqual(event.get_qualified_name(), 'test_module.TestClass.test_method')
        self.assertEqual(event.get_symbol(), 'TestClass.test_method')
        self.assertEqual(event.get_module(), 'test_module')
        self.assertTrue(event.is_run_event)
        self.assertFalse(event.is_end_event)
        self.assertTrue(event.has_wrapper_message)

    def test_end_event_creation(self):
        """Test creating a function end event."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.END,
            lineno=50,
            call_depth=0,
            index_info="",
            process_id=None,
            func_info=self.func_info,
            result="test_result",
            return_msg="test_result",
        )

        self.assertEqual(event.event_type, EventType.END)
        self.assertEqual(event.lineno, 50)
        self.assertEqual(event.call_depth, 0)
        self.assertTrue(event.is_end_event)
        self.assertFalse(event.is_run_event)
        self.assertTrue(event.has_wrapper_message)

    def test_invalid_event_type(self):
        """Test that invalid event types raise ValueError."""
        with self.assertRaises(ValueError):
            FunctionEvent(
                timestamp=1234567890.0,
                event_type=EventType.UPD,
                lineno=42,
                call_depth=1,
                index_info="",
                process_id=None,
                func_info=self.func_info,
            )

    def test_format_message_run(self):
        """Test formatting run event message."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
            call_msg="'0':10",
        )

        message = event.format_message()
        self.assertIn('test_module.TestClass.test_method', message)
        self.assertIn("<-", message)
        self.assertIn("'0':10", message)

    def test_format_message_end(self):
        """Test formatting end event message."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.END,
            lineno=50,
            call_depth=0,
            index_info="",
            process_id=None,
            func_info=self.func_info,
            return_msg="result",
        )

        message = event.format_message()
        self.assertIn('test_module.TestClass.test_method', message)
        self.assertIn("->", message)
        self.assertIn("result", message)

    def test_to_dict(self):
        """Test converting event to dictionary."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
            call_msg="test",
        )

        data = event.to_dict()
        self.assertEqual(data['event_type'], 'run')
        self.assertEqual(data['lineno'], 42)
        self.assertEqual(data['call_depth'], 1)
        self.assertEqual(data['call_msg'], 'test')
        # Frame should be removed
        self.assertNotIn('frame', data.get('func_info', {}))


if __name__ == '__main__':
    unittest.main()
