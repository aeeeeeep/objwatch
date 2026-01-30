# MIT License
# Copyright (c) 2025 aeeeeeep

import unittest

from objwatch.events.models.event_type import EventType


class TestEventType(unittest.TestCase):
    def test_event_type_labels(self):
        """Test that all event types have correct labels."""
        self.assertEqual(EventType.RUN.label, 'run')
        self.assertEqual(EventType.END.label, 'end')
        self.assertEqual(EventType.UPD.label, 'upd')
        self.assertEqual(EventType.APD.label, 'apd')
        self.assertEqual(EventType.POP.label, 'pop')

    def test_event_type_str(self):
        """Test string representation of event types."""
        self.assertEqual(str(EventType.RUN), 'run')
        self.assertEqual(str(EventType.END), 'end')
        self.assertEqual(str(EventType.UPD), 'upd')

    def test_is_function_event(self):
        """Test function event type checking."""
        self.assertTrue(EventType.RUN.is_function_event)
        self.assertTrue(EventType.END.is_function_event)
        self.assertFalse(EventType.UPD.is_function_event)
        self.assertFalse(EventType.APD.is_function_event)
        self.assertFalse(EventType.POP.is_function_event)

    def test_is_variable_event(self):
        """Test variable event type checking."""
        self.assertTrue(EventType.UPD.is_variable_event)
        self.assertFalse(EventType.RUN.is_variable_event)
        self.assertFalse(EventType.END.is_variable_event)
        self.assertFalse(EventType.APD.is_variable_event)
        self.assertFalse(EventType.POP.is_variable_event)

    def test_is_collection_event(self):
        """Test collection event type checking."""
        self.assertTrue(EventType.APD.is_collection_event)
        self.assertTrue(EventType.POP.is_collection_event)
        self.assertFalse(EventType.RUN.is_collection_event)
        self.assertFalse(EventType.END.is_collection_event)
        self.assertFalse(EventType.UPD.is_collection_event)


if __name__ == '__main__':
    unittest.main()
