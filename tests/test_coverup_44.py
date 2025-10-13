# file: objwatch/event_handls.py:50-76
# asked: {"lines": [50, 51, 52, 56, 58, 59, 60, 61, 62, 65, 66, 67, 68, 70, 71, 73, 74, 75, 76], "branches": [[65, 66], [65, 70], [73, 0], [73, 74]]}
# gained: {"lines": [50, 51, 52, 56, 58, 59, 60, 61, 62, 65, 66, 67, 68, 70, 71, 73, 74, 75, 76], "branches": [[65, 66], [65, 70], [73, 0], [73, 74]]}

import pytest
import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch, MagicMock
from objwatch.event_handls import EventHandls
from objwatch.events import EventType


class TestEventHandlsHandleRun:
    """Test cases for EventHandls.handle_run method to achieve full coverage."""

    def test_handle_run_without_abc_wrapper_and_output_xml_false(self, monkeypatch):
        """Test handle_run without abc_wrapper and output_xml=False."""
        event_handls = EventHandls()
        event_handls.output_xml = False
        event_handls.current_node = [Mock()]

        func_info = {
            'qualified_name': 'test_function',
            'module': 'test_module',
            'symbol': 'test_symbol',
            'symbol_type': 'function',
        }

        log_calls = []

        def mock_log_debug(msg):
            log_calls.append(msg)

        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        event_handls.handle_run(lineno=42, func_info=func_info, abc_wrapper=None, call_depth=1, index_info="[0]")

        expected_log = "[0]   42 | run test_function"
        assert len(log_calls) == 1
        assert expected_log in log_calls[0]

    def test_handle_run_with_abc_wrapper_and_output_xml_false(self, monkeypatch):
        """Test handle_run with abc_wrapper and output_xml=False."""
        event_handls = EventHandls()
        event_handls.output_xml = False
        event_handls.current_node = [Mock()]

        func_info = {
            'qualified_name': 'test_function',
            'module': 'test_module',
            'symbol': 'test_symbol',
            'symbol_type': 'function',
            'frame': Mock(),
        }

        abc_wrapper = Mock()
        abc_wrapper.wrap_call.return_value = "wrapped_call"

        log_calls = []

        def mock_log_debug(msg):
            log_calls.append(msg)

        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        event_handls.handle_run(lineno=42, func_info=func_info, abc_wrapper=abc_wrapper, call_depth=2, index_info="[1]")

        abc_wrapper.wrap_call.assert_called_once_with('test_symbol', func_info['frame'])

        assert len(log_calls) == 1
        assert "[1]   42 | | run test_function <- wrapped_call" in log_calls[0]

    def test_handle_run_without_abc_wrapper_and_output_xml_true(self, monkeypatch):
        """Test handle_run without abc_wrapper and output_xml=True."""
        event_handls = EventHandls(output_xml="test.xml")
        parent_node = Mock()
        event_handls.current_node = [parent_node]

        func_info = {
            'qualified_name': 'test_function',
            'module': 'test_module',
            'symbol': 'test_symbol',
            'symbol_type': 'function',
        }

        log_calls = []

        def mock_log_debug(msg):
            log_calls.append(msg)

        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        event_handls.handle_run(lineno=42, func_info=func_info, abc_wrapper=None, call_depth=0, index_info="[2]")

        assert len(log_calls) == 1
        assert "[2]   42 run test_function" in log_calls[0]

        # Verify XML element creation
        assert parent_node.append.called
        function_element = parent_node.append.call_args[0][0]
        assert function_element.tag == 'Function'
        assert function_element.attrib['module'] == 'test_module'
        assert function_element.attrib['symbol'] == 'test_symbol'
        assert function_element.attrib['symbol_type'] == 'function'
        assert function_element.attrib['run_line'] == '42'
        assert 'call_msg' not in function_element.attrib

    def test_handle_run_with_abc_wrapper_and_output_xml_true(self, monkeypatch):
        """Test handle_run with abc_wrapper and output_xml=True."""
        event_handls = EventHandls(output_xml="test.xml")
        parent_node = Mock()
        event_handls.current_node = [parent_node]

        func_info = {
            'qualified_name': 'test_function',
            'module': 'test_module',
            'symbol': 'test_symbol',
            'symbol_type': 'method',
            'frame': Mock(),
        }

        abc_wrapper = Mock()
        abc_wrapper.wrap_call.return_value = "wrapped_method_call"

        log_calls = []

        def mock_log_debug(msg):
            log_calls.append(msg)

        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        event_handls.handle_run(
            lineno=100, func_info=func_info, abc_wrapper=abc_wrapper, call_depth=3, index_info="[3]"
        )

        abc_wrapper.wrap_call.assert_called_once_with('test_symbol', func_info['frame'])

        assert len(log_calls) == 1
        assert "[3]  100 | | | run test_function <- wrapped_method_call" in log_calls[0]

        # Verify XML element creation with call_msg
        assert parent_node.append.called
        function_element = parent_node.append.call_args[0][0]
        assert function_element.tag == 'Function'
        assert function_element.attrib['module'] == 'test_module'
        assert function_element.attrib['symbol'] == 'test_symbol'
        assert function_element.attrib['symbol_type'] == 'method'
        assert function_element.attrib['run_line'] == '100'
        assert function_element.attrib['call_msg'] == 'wrapped_method_call'

    def test_handle_run_with_none_symbol_type(self, monkeypatch):
        """Test handle_run with None symbol_type (should default to 'function')."""
        event_handls = EventHandls(output_xml="test.xml")
        parent_node = Mock()
        event_handls.current_node = [parent_node]

        func_info = {
            'qualified_name': 'test_function',
            'module': 'test_module',
            'symbol': 'test_symbol',
            'symbol_type': None,
        }

        log_calls = []

        def mock_log_debug(msg):
            log_calls.append(msg)

        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        event_handls.handle_run(lineno=42, func_info=func_info, abc_wrapper=None, call_depth=0, index_info="[4]")

        # Verify XML element creation with default symbol_type
        assert parent_node.append.called
        function_element = parent_node.append.call_args[0][0]
        assert function_element.attrib['symbol_type'] == 'function'
