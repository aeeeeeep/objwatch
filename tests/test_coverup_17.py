# file: objwatch/event_handls.py:196-235
# asked: {"lines": [196, 198, 199, 200, 201, 202, 203, 204, 205, 206, 220, 221, 222, 223, 225, 226, 227, 228, 229, 230, 231, 232, 235], "branches": [[225, 0], [225, 226]]}
# gained: {"lines": [196, 198, 199, 200, 201, 202, 203, 204, 205, 206, 220, 221, 222, 223, 225, 226, 227, 228, 229, 230, 231, 232, 235], "branches": [[225, 0], [225, 226]]}

import pytest
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
from objwatch.event_handls import EventHandls
from objwatch.events import EventType


class TestEventHandlsHandlePop:
    """Test cases for EventHandls.handle_pop method."""

    def test_handle_pop_without_xml_output(self, monkeypatch):
        """Test handle_pop when output_xml is None (lines 220-223)."""
        # Setup
        event_handls = EventHandls(output_xml=None)
        mock_log_debug = MagicMock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Execute
        event_handls.handle_pop(
            lineno=42,
            class_name="TestClass",
            key="test_list",
            value_type=list,
            old_value_len=5,
            current_value_len=4,
            call_depth=2,
            index_info="[0]",
        )

        # Verify
        expected_msg = "[0]   42 | | pop TestClass.test_list (list)(len)5 -> 4"
        mock_log_debug.assert_called_once_with(expected_msg)

    def test_handle_pop_with_xml_output(self, monkeypatch):
        """Test handle_pop when output_xml is set (lines 220-235)."""
        # Setup
        event_handls = EventHandls(output_xml="test.xml")
        mock_log_debug = MagicMock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Create a mock current_node with at least one element
        mock_element = ET.Element('root')
        event_handls.current_node = [mock_element]

        # Execute
        event_handls.handle_pop(
            lineno=42,
            class_name="TestClass",
            key="test_list",
            value_type=list,
            old_value_len=5,
            current_value_len=4,
            call_depth=2,
            index_info="[0]",
        )

        # Verify debug logging
        expected_msg = "[0]   42 | | pop TestClass.test_list (list)(len)5 -> 4"
        mock_log_debug.assert_called_once_with(expected_msg)

        # Verify XML element creation
        assert len(mock_element) == 1
        pop_element = mock_element[0]
        assert pop_element.tag == "pop"
        assert pop_element.attrib['name'] == "TestClass.test_list"
        assert pop_element.attrib['line'] == "42"
        assert pop_element.attrib['old'] == "(list)(len)5"
        assert pop_element.attrib['new'] == "(list)(len)4"

    def test_handle_pop_with_none_lengths(self, monkeypatch):
        """Test handle_pop with None values for old_value_len and current_value_len."""
        # Setup
        event_handls = EventHandls(output_xml=None)
        mock_log_debug = MagicMock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Execute
        event_handls.handle_pop(
            lineno=42,
            class_name="TestClass",
            key="test_list",
            value_type=list,
            old_value_len=None,
            current_value_len=None,
            call_depth=1,
            index_info="",
        )

        # Verify
        expected_msg = "   42 | pop TestClass.test_list (list)(len)None -> None"
        mock_log_debug.assert_called_once_with(expected_msg)

    def test_handle_pop_with_zero_call_depth(self, monkeypatch):
        """Test handle_pop with call_depth=0."""
        # Setup
        event_handls = EventHandls(output_xml=None)
        mock_log_debug = MagicMock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Execute
        event_handls.handle_pop(
            lineno=42,
            class_name="TestClass",
            key="test_list",
            value_type=list,
            old_value_len=3,
            current_value_len=2,
            call_depth=0,
            index_info="[1]",
        )

        # Verify
        expected_msg = "[1]   42 pop TestClass.test_list (list)(len)3 -> 2"
        mock_log_debug.assert_called_once_with(expected_msg)

    def test_handle_pop_with_different_value_types(self, monkeypatch):
        """Test handle_pop with different value types."""
        # Setup
        event_handls = EventHandls(output_xml=None)
        mock_log_debug = MagicMock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Test with dict type
        event_handls.handle_pop(
            lineno=42,
            class_name="TestClass",
            key="test_dict",
            value_type=dict,
            old_value_len=10,
            current_value_len=9,
            call_depth=1,
            index_info="",
        )

        # Verify
        expected_msg = "   42 | pop TestClass.test_dict (dict)(len)10 -> 9"
        mock_log_debug.assert_called_once_with(expected_msg)
