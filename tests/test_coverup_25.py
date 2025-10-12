# file: objwatch/event_handls.py:78-104
# asked: {"lines": [78, 80, 81, 82, 83, 84, 85, 86, 90, 91, 93, 94, 95, 97, 98, 100, 101, 102, 103, 104], "branches": [[93, 94], [93, 97], [100, 0], [100, 101]]}
# gained: {"lines": [78, 80, 81, 82, 83, 84, 85, 86, 90, 91, 93, 94, 95, 97, 98, 100, 101, 102, 103, 104], "branches": [[93, 94], [93, 97], [100, 0], [100, 101]]}

import pytest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET
from objwatch.event_handls import EventHandls
from objwatch.events import EventType


class TestEventHandlsHandleEnd:

    def test_handle_end_with_abc_wrapper_and_xml_output(self, monkeypatch):
        """Test handle_end with abc_wrapper and XML output enabled."""
        # Setup
        event_handls = EventHandls(output_xml="test.xml")
        # Create real XML elements instead of mocks
        root = ET.Element('root')
        child = ET.SubElement(root, 'child')
        event_handls.current_node = [root, child]

        func_info = {'qualified_name': 'test_function', 'symbol': 'test_symbol', 'symbol_type': 'method'}

        abc_wrapper = Mock()
        abc_wrapper.wrap_return.return_value = "wrapped_result"

        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Execute
        event_handls.handle_end(
            lineno=100,
            func_info=func_info,
            abc_wrapper=abc_wrapper,
            call_depth=2,
            index_info="[1] ",
            result="original_result",
        )

        # Assertions
        abc_wrapper.wrap_return.assert_called_once_with('test_symbol', 'original_result')
        mock_log_debug.assert_called_once()
        call_args = mock_log_debug.call_args[0][0]
        assert "100" in call_args
        assert "| | " in call_args
        assert "[1]" in call_args
        assert "end" in call_args
        assert "test_function -> wrapped_result" in call_args

        # Check XML attributes on the child element (which should have been popped)
        # The child element should have the attributes set before being popped
        assert child.get('return_msg') == "wrapped_result"
        assert child.get('end_line') == "100"
        assert child.get('symbol_type') == "method"

        # Check that current_node was popped (should only contain root now)
        assert len(event_handls.current_node) == 1
        assert event_handls.current_node[0] is root

    def test_handle_end_without_abc_wrapper_and_xml_output(self, monkeypatch):
        """Test handle_end without abc_wrapper but with XML output enabled."""
        # Setup
        event_handls = EventHandls(output_xml="test.xml")
        root = ET.Element('root')
        child = ET.SubElement(root, 'child')
        event_handls.current_node = [root, child]

        func_info = {'qualified_name': 'test_function', 'symbol': 'test_symbol', 'symbol_type': 'function'}

        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Execute
        event_handls.handle_end(
            lineno=50, func_info=func_info, abc_wrapper=None, call_depth=1, index_info="[2] ", result="some_result"
        )

        # Assertions
        mock_log_debug.assert_called_once()
        call_args = mock_log_debug.call_args[0][0]
        assert "50" in call_args
        assert "| " in call_args
        assert "[2]" in call_args
        assert "end" in call_args
        assert "test_function" in call_args
        assert "->" not in call_args  # No return message without abc_wrapper

        # Check XML attributes
        assert child.get('return_msg') == ""
        assert child.get('end_line') == "50"
        assert child.get('symbol_type') == "function"

        # Check that current_node was popped
        assert len(event_handls.current_node) == 1
        assert event_handls.current_node[0] is root

    def test_handle_end_without_xml_output(self, monkeypatch):
        """Test handle_end without XML output enabled."""
        # Setup
        event_handls = EventHandls(output_xml=None)

        func_info = {'qualified_name': 'test_function', 'symbol': 'test_symbol', 'symbol_type': 'function'}

        abc_wrapper = Mock()
        abc_wrapper.wrap_return.return_value = "wrapped_result"

        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Execute
        event_handls.handle_end(
            lineno=75,
            func_info=func_info,
            abc_wrapper=abc_wrapper,
            call_depth=0,
            index_info="",
            result="original_result",
        )

        # Assertions
        abc_wrapper.wrap_return.assert_called_once_with('test_symbol', 'original_result')
        mock_log_debug.assert_called_once()
        call_args = mock_log_debug.call_args[0][0]
        assert "75" in call_args
        assert "|" not in call_args  # No call depth bars at depth 0
        assert "end" in call_args
        assert "test_function -> wrapped_result" in call_args

        # Verify no XML operations were attempted
        assert not hasattr(event_handls, 'current_node') or len(event_handls.current_node) <= 1

    def test_handle_end_with_single_node_in_xml_stack(self, monkeypatch):
        """Test handle_end when current_node has only one element (no pop)."""
        # Setup
        event_handls = EventHandls(output_xml="test.xml")
        root = ET.Element('root')
        event_handls.current_node = [root]  # Only one element

        func_info = {'qualified_name': 'test_function', 'symbol': 'test_symbol', 'symbol_type': 'function'}

        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Execute
        event_handls.handle_end(
            lineno=25, func_info=func_info, abc_wrapper=None, call_depth=3, index_info="[0] ", result="result"
        )

        # Assertions
        mock_log_debug.assert_called_once()

        # Verify no attributes were set on root (since len(current_node) <= 1)
        assert root.attrib == {}

        # Verify current_node still has only root
        assert len(event_handls.current_node) == 1
        assert event_handls.current_node[0] is root
