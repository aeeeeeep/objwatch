# MIT License
# Copyright (c) 2025 aeeeeeep

import unittest

from objwatch.events.models.event_type import EventType
from objwatch.events.models.collection_event import CollectionEvent


class TestCollectionEvent(unittest.TestCase):
    def test_append_event(self):
        """Test creating a collection append event."""
        event = CollectionEvent(
            timestamp=1234567890.0,
            event_type=EventType.APD,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='TestClass',
            key='items',
            value_type=int,
            old_value_len=3,
            current_value_len=5,
        )

        self.assertEqual(event.event_type, EventType.APD)
        self.assertEqual(event.class_name, 'TestClass')
        self.assertEqual(event.key, 'items')
        self.assertEqual(event.old_value_len, 3)
        self.assertEqual(event.current_value_len, 5)
        self.assertTrue(event.is_append)
        self.assertFalse(event.is_pop)
        self.assertEqual(event.change_count, 2)

    def test_pop_event(self):
        """Test creating a collection pop event."""
        event = CollectionEvent(
            timestamp=1234567890.0,
            event_type=EventType.POP,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='TestClass',
            key='items',
            value_type=str,
            old_value_len=5,
            current_value_len=3,
        )

        self.assertEqual(event.event_type, EventType.POP)
        self.assertTrue(event.is_pop)
        self.assertFalse(event.is_append)
        self.assertEqual(event.change_count, -2)

    def test_invalid_event_type(self):
        """Test that invalid event types raise ValueError."""
        with self.assertRaises(ValueError):
            CollectionEvent(
                timestamp=1234567890.0,
                event_type=EventType.UPD,
                lineno=42,
                call_depth=1,
                index_info="",
                process_id=None,
                class_name='TestClass',
                key='items',
                value_type=int,
                old_value_len=0,
                current_value_len=1,
            )

    def test_format_message(self):
        """Test formatting collection change message."""
        event = CollectionEvent(
            timestamp=1234567890.0,
            event_type=EventType.APD,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='TestClass',
            key='items',
            value_type=int,
            old_value_len=3,
            current_value_len=5,
        )

        message = event.format_message()
        self.assertIn('TestClass.items', message)
        self.assertIn('int', message)
        self.assertIn('3', message)
        self.assertIn('5', message)
        self.assertIn('->', message)

    def test_empty_states(self):
        """Test empty collection states."""
        empty_to_items = CollectionEvent(
            timestamp=1234567890.0,
            event_type=EventType.APD,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='TestClass',
            key='items',
            value_type=int,
            old_value_len=0,
            current_value_len=3,
        )

        self.assertTrue(empty_to_items.is_empty_before)
        self.assertFalse(empty_to_items.is_empty_after)

        items_to_empty = CollectionEvent(
            timestamp=1234567890.0,
            event_type=EventType.POP,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='TestClass',
            key='items',
            value_type=int,
            old_value_len=3,
            current_value_len=0,
        )

        self.assertFalse(items_to_empty.is_empty_before)
        self.assertTrue(items_to_empty.is_empty_after)

    def test_to_dict(self):
        """Test converting event to dictionary."""
        event = CollectionEvent(
            timestamp=1234567890.0,
            event_type=EventType.APD,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            class_name='TestClass',
            key='items',
            value_type=int,
            old_value_len=3,
            current_value_len=5,
        )

        data = event.to_dict()
        self.assertEqual(data['event_type'], 'apd')
        self.assertEqual(data['class_name'], 'TestClass')
        self.assertEqual(data['key'], 'items')
        self.assertEqual(data['value_type'], 'int')  # Type is converted to string
        self.assertEqual(data['old_value_len'], 3)
        self.assertEqual(data['current_value_len'], 5)


if __name__ == '__main__':
    unittest.main()
