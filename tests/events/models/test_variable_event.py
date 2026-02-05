# MIT License
# Copyright (c) 2025 aeeeeeep

import unittest

from objwatch.events.models.event_type import EventType
from objwatch.events.models.variable_event import VariableEvent


class TestVariableEvent(unittest.TestCase):
    def test_variable_update_event(self):
        """Test creating a variable update event."""
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

        self.assertEqual(event.event_type, EventType.UPD)
        self.assertEqual(event.class_name, 'TestClass')
        self.assertEqual(event.key, 'value')
        self.assertEqual(event.old_value, 10)
        self.assertEqual(event.current_value, 20)
        self.assertFalse(event.is_new_variable)

    def test_new_variable_event(self):
        """Test creating a new variable event (old_value is None)."""
        event = VariableEvent(
            timestamp=1234567890.0,
            event_type=EventType.UPD,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='TestClass',
            key='new_var',
            old_value=None,
            current_value='initial_value',
        )

        self.assertTrue(event.is_new_variable)
        self.assertEqual(event.old_value, None)
        self.assertEqual(event.current_value, 'initial_value')

    def test_invalid_event_type(self):
        """Test that invalid event types raise ValueError."""
        with self.assertRaises(ValueError):
            VariableEvent(
                timestamp=1234567890.0,
                event_type=EventType.RUN,
                lineno=42,
                call_depth=1,
                index_info="",
                process_id=None,
                class_name='TestClass',
                key='value',
            )

    def test_format_message(self):
        """Test formatting variable update message."""
        event = VariableEvent(
            timestamp=1234567890.0,
            event_type=EventType.UPD,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='TestClass',
            key='count',
            old_value=5,
            current_value=10,
        )

        message = event.format_message()
        self.assertIn('TestClass.count', message)
        self.assertIn('5', message)
        self.assertIn('10', message)
        self.assertIn('->', message)

    def test_global_variable(self):
        """Test global variable event."""
        event = VariableEvent(
            timestamp=1234567890.0,
            event_type=EventType.UPD,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='@',
            key='GLOBAL_VAR',
            old_value=None,
            current_value=100,
        )

        self.assertTrue(event.is_global_variable)
        self.assertFalse(event.is_local_variable)

    def test_local_variable(self):
        """Test local variable event."""
        event = VariableEvent(
            timestamp=1234567890.0,
            event_type=EventType.UPD,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='_',
            key='local_var',
            old_value=None,
            current_value='value',
        )

        self.assertTrue(event.is_local_variable)
        self.assertFalse(event.is_global_variable)

    def test_to_dict(self):
        """Test converting event to dictionary."""
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

        data = event.to_dict()
        self.assertEqual(data['event_type'], 'upd')
        self.assertEqual(data['class_name'], 'TestClass')
        self.assertEqual(data['key'], 'value')
        self.assertEqual(data['old_value'], 10)
        self.assertEqual(data['current_value'], 20)


if __name__ == '__main__':
    unittest.main()
