# MIT License
# Copyright (c) 2025 aeeeeeep

import unittest
from unittest.mock import MagicMock, patch

from objwatch.events.dispatcher import EventDispatcher
from objwatch.events.models.event_type import EventType
from objwatch.events.models.function_event import FunctionEvent
from objwatch.events.handlers.abc_handler import ABCEventHandler


class MockHandler(ABCEventHandler):
    """Mock handler for testing."""

    def __init__(self, can_handle_result=True):
        self.can_handle_result = can_handle_result
        self.handled_events = []
        self.started = False
        self.stopped = False

    def can_handle(self, event):
        return self.can_handle_result

    def handle(self, event):
        self.handled_events.append(event)

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


class TestEventDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = EventDispatcher()
        self.func_info = {
            'module': 'test_module',
            'symbol': 'test_func',
            'symbol_type': 'function',
            'qualified_name': 'test_module.test_func',
            'frame': None,
        }

    def test_register_handler(self):
        """Test registering a handler."""
        handler = MockHandler()
        self.dispatcher.register_handler(handler)

        self.assertEqual(self.dispatcher.handler_count, 1)
        self.assertTrue(handler.started)

    def test_unregister_handler(self):
        """Test unregistering a handler."""
        handler = MockHandler()
        self.dispatcher.register_handler(handler)
        self.dispatcher.unregister_handler(handler)

        self.assertEqual(self.dispatcher.handler_count, 0)
        self.assertTrue(handler.stopped)

    def test_dispatch_event(self):
        """Test dispatching an event to handlers."""
        handler1 = MockHandler(can_handle_result=True)
        handler2 = MockHandler(can_handle_result=False)

        self.dispatcher.register_handler(handler1)
        self.dispatcher.register_handler(handler2)

        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )

        self.dispatcher.dispatch(event)

        self.assertEqual(len(handler1.handled_events), 1)
        self.assertEqual(len(handler2.handled_events), 0)

    def test_dispatch_multiple_handlers(self):
        """Test dispatching to multiple handlers that can handle the event."""
        handler1 = MockHandler(can_handle_result=True)
        handler2 = MockHandler(can_handle_result=True)

        self.dispatcher.register_handler(handler1)
        self.dispatcher.register_handler(handler2)

        event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )

        self.dispatcher.dispatch(event)

        self.assertEqual(len(handler1.handled_events), 1)
        self.assertEqual(len(handler2.handled_events), 1)

    def test_clear_handlers(self):
        """Test clearing all handlers."""
        handler = MockHandler()
        self.dispatcher.register_handler(handler)
        self.dispatcher.clear_handlers()

        self.assertEqual(self.dispatcher.handler_count, 0)
        self.assertTrue(handler.stopped)

    def test_handlers_property(self):
        """Test handlers property returns a copy."""
        handler = MockHandler()
        self.dispatcher.register_handler(handler)

        handlers = self.dispatcher.handlers
        handlers.clear()  # Should not affect the dispatcher

        self.assertEqual(self.dispatcher.handler_count, 1)

    def test_stop(self):
        """Test stopping the dispatcher."""
        handler = MockHandler()
        self.dispatcher.register_handler(handler)
        self.dispatcher.stop()

        self.assertTrue(handler.stopped)


if __name__ == '__main__':
    unittest.main()
