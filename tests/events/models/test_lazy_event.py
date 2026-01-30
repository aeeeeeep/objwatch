# MIT License
# Copyright (c) 2025 aeeeeeep

import unittest
import time

from objwatch.events.models.event_type import EventType
from objwatch.events.models.function_event import FunctionEvent
from objwatch.events.models.variable_event import VariableEvent
from objwatch.events.models.collection_event import CollectionEvent
from objwatch.events.models.lazy_event import LazyEventRef


class TestLazyEventRef(unittest.TestCase):
    """Test cases for LazyEventRef lazy serialization."""

    def setUp(self):
        self.func_info = {
            'module': 'test_module',
            'symbol': 'TestClass.test_method',
            'symbol_type': 'method',
            'qualified_name': 'test_module.TestClass.test_method',
            'frame': None,
        }

    def test_lazy_event_creation(self):
        """Test creating a LazyEventRef."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )

        lazy_event = LazyEventRef(event=event, created_at=1234567890.0)

        self.assertEqual(lazy_event.event, event)
        self.assertEqual(lazy_event.created_at, 1234567890.0)

    def test_lazy_event_auto_timestamp(self):
        """Test that LazyEventRef auto-generates timestamp if not provided."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )

        before = time.time()
        lazy_event = LazyEventRef(event=event)
        after = time.time()

        self.assertTrue(before <= lazy_event.created_at <= after)

    def test_lazy_event_to_dict_deferred_serialization(self):
        """Test that to_dict() performs deferred serialization."""
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

        lazy_event = LazyEventRef(event=event)

        # Serialization happens here (on consumer side)
        event_dict = lazy_event.to_dict()

        self.assertEqual(event_dict['event_type'], 'run')
        self.assertEqual(event_dict['lineno'], 42)
        self.assertEqual(event_dict['call_depth'], 1)
        self.assertEqual(event_dict['call_msg'], "'0':10, '1':20")
        self.assertIn('func_info', event_dict)
        self.assertEqual(event_dict['func_info']['module'], 'test_module')

    def test_lazy_event_format_message(self):
        """Test that format_message() proxies to wrapped event."""
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

        lazy_event = LazyEventRef(event=event)

        message = lazy_event.format_message()
        self.assertIn('test_module.TestClass.test_method', message)
        self.assertIn("<-", message)
        self.assertIn("'0':10", message)

    def test_lazy_event_get_qualified_name(self):
        """Test that get_qualified_name() proxies to wrapped event."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )

        lazy_event = LazyEventRef(event=event)

        qualified_name = lazy_event.get_qualified_name()
        self.assertEqual(qualified_name, 'test_module.TestClass.test_method')

    def test_lazy_event_properties(self):
        """Test that all properties proxy to wrapped event."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="test_index",
            process_id="pid_123",
            func_info=self.func_info,
        )

        lazy_event = LazyEventRef(event=event)

        self.assertEqual(lazy_event.event_type, EventType.RUN)
        self.assertEqual(lazy_event.lineno, 42)
        self.assertEqual(lazy_event.call_depth, 1)
        self.assertEqual(lazy_event.index_info, "test_index")
        self.assertEqual(lazy_event.process_id, "pid_123")
        self.assertEqual(lazy_event.timestamp, 1234567890.0)
        self.assertTrue(lazy_event.is_run_event)
        self.assertFalse(lazy_event.is_end_event)
        self.assertFalse(lazy_event.is_upd_event)
        self.assertFalse(lazy_event.is_apd_event)
        self.assertFalse(lazy_event.is_pop_event)

    def test_lazy_event_with_variable_event(self):
        """Test LazyEventRef with VariableEvent."""
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

        lazy_event = LazyEventRef(event=event)

        # Test properties
        self.assertEqual(lazy_event.event_type, EventType.UPD)
        self.assertTrue(lazy_event.is_upd_event)

        # Test deferred serialization
        event_dict = lazy_event.to_dict()
        self.assertEqual(event_dict['event_type'], 'upd')
        self.assertEqual(event_dict['class_name'], 'TestClass')
        self.assertEqual(event_dict['key'], 'value')
        self.assertEqual(event_dict['old_value'], 10)
        self.assertEqual(event_dict['current_value'], 20)

    def test_lazy_event_with_collection_event(self):
        """Test LazyEventRef with CollectionEvent."""
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
            old_value_len=5,
            current_value_len=6,
        )

        lazy_event = LazyEventRef(event=event)

        # Test properties
        self.assertEqual(lazy_event.event_type, EventType.APD)
        self.assertTrue(lazy_event.is_apd_event)
        self.assertFalse(lazy_event.is_pop_event)

        # Test deferred serialization
        event_dict = lazy_event.to_dict()
        self.assertEqual(event_dict['event_type'], 'apd')
        self.assertEqual(event_dict['class_name'], 'TestClass')
        self.assertEqual(event_dict['key'], 'items')
        self.assertEqual(event_dict['value_type'], 'int')
        self.assertEqual(event_dict['old_value_len'], 5)
        self.assertEqual(event_dict['current_value_len'], 6)

    def test_lazy_event_immutable(self):
        """Test that LazyEventRef is immutable (frozen dataclass)."""
        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )

        lazy_event = LazyEventRef(event=event)

        # Attempting to modify should raise an error
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            lazy_event.event = None


class FrozenInstanceError(Exception):
    """Exception raised when trying to modify a frozen dataclass instance."""

    pass


if __name__ == '__main__':
    unittest.main()
