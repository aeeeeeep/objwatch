# MIT License
# Copyright (c) 2025 aeeeeeep

import unittest

from objwatch.events.models.event_type import EventType
from objwatch.events.models.function_event import FunctionEvent
from objwatch.events.models.variable_event import VariableEvent
from objwatch.events.models.collection_event import CollectionEvent
from objwatch.events.formatters.log_formatter import LogEventFormatter


class TestLogEventFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = LogEventFormatter()
        self.func_info = {
            'module': 'test_module',
            'symbol': 'test_func',
            'symbol_type': 'function',
            'qualified_name': 'test_module.test_func',
            'frame': None,
        }

    def test_can_format(self):
        """Test that formatter can handle all event types."""
        run_event = FunctionEvent(
            timestamp=1234567890.0,
            event_type=EventType.RUN,
            lineno=42,
            call_depth=1,
            index_info="",
            process_id=None,
            func_info=self.func_info,
        )
        self.assertTrue(self.formatter.can_format(run_event))

    def test_format_function_run(self):
        """Test formatting function run event."""
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

        formatted = self.formatter.format(event)
        self.assertIn('run', formatted)
        self.assertIn('test_module.test_func', formatted)
        self.assertIn('42', formatted)

    def test_format_function_end(self):
        """Test formatting function end event."""
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

        formatted = self.formatter.format(event)
        self.assertIn('end', formatted)
        self.assertIn('test_module.test_func', formatted)

    def test_format_variable_update(self):
        """Test formatting variable update event."""
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

        formatted = self.formatter.format(event)
        self.assertIn('upd', formatted)
        self.assertIn('TestClass.value', formatted)
        self.assertIn('10', formatted)
        self.assertIn('20', formatted)

    def test_format_collection_append(self):
        """Test formatting collection append event."""
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

        formatted = self.formatter.format(event)
        self.assertIn('apd', formatted)
        self.assertIn('TestClass.items', formatted)
        self.assertIn('3', formatted)
        self.assertIn('5', formatted)

    def test_format_collection_pop(self):
        """Test formatting collection pop event."""
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

        formatted = self.formatter.format(event)
        self.assertIn('pop', formatted)

    def test_format_prefix(self):
        """Test prefix formatting."""
        prefix = self.formatter.format_prefix(42, 2)
        self.assertIn('42', prefix)
        self.assertIn('    ', prefix)  # 2 levels of indentation

    def test_format_value(self):
        """Test value formatting."""
        self.assertEqual(self.formatter.format_value(42), '42')
        self.assertEqual(self.formatter.format_value('hello'), 'hello')
        self.assertEqual(self.formatter.format_value([1, 2, 3]), '(list)[1, 2, 3]')

    def test_format_sequence(self):
        """Test sequence formatting."""
        seq = [1, 2, 3, 4, 5]
        formatted = self.formatter.format_sequence(seq)
        self.assertIn('list', formatted)


if __name__ == '__main__':
    unittest.main()
