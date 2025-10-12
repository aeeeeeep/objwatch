# file: objwatch/event_handls.py:155-194
# asked: {"lines": [155, 157, 158, 159, 160, 161, 162, 163, 164, 165, 179, 180, 181, 182, 184, 185, 186, 187, 188, 189, 190, 191, 194], "branches": [[184, 0], [184, 185]]}
# gained: {"lines": [155, 157, 158, 159, 160, 161, 162, 163, 164, 165, 179, 180, 181, 182, 184, 185, 186, 187, 188, 189, 190, 191, 194], "branches": [[184, 0], [184, 185]]}

import pytest
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
from objwatch.event_handls import EventHandls
from objwatch.events import EventType
from objwatch.utils.logger import log_debug


class TestEventHandlsHandleApd:
    """Test cases for EventHandls.handle_apd method to achieve full coverage."""

    def test_handle_apd_without_xml_output(self, monkeypatch):
        """Test handle_apd when output_xml is None (lines 179-182)."""
        # Setup
        event_handls = EventHandls(output_xml=None)
        mock_log_debug = MagicMock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Test parameters
        lineno = 42
        class_name = "TestClass"
        key = "test_list"
        value_type = list
        old_value_len = 3
        current_value_len = 5
        call_depth = 2
        index_info = "[0]"

        # Execute
        event_handls.handle_apd(
            lineno=lineno,
            class_name=class_name,
            key=key,
            value_type=value_type,
            old_value_len=old_value_len,
            current_value_len=current_value_len,
            call_depth=call_depth,
            index_info=index_info,
        )

        # Verify
        expected_msg = f"{class_name}.{key} ({value_type.__name__})(len){old_value_len} -> {current_value_len}"
        expected_prefix = f"{lineno:>5} " + "| " * call_depth
        mock_log_debug.assert_called_once()
        call_args = mock_log_debug.call_args[0][0]
        assert index_info in call_args
        assert expected_prefix in call_args
        assert EventType.APD.label in call_args
        assert expected_msg in call_args

    def test_handle_apd_with_xml_output(self, monkeypatch):
        """Test handle_apd when output_xml is set (lines 179-194)."""
        # Setup
        event_handls = EventHandls(output_xml="test.xml")
        mock_log_debug = MagicMock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Create a mock current_node with at least one element
        mock_parent = ET.Element('parent')
        event_handls.current_node = [mock_parent]

        # Test parameters
        lineno = 42
        class_name = "TestClass"
        key = "test_list"
        value_type = list
        old_value_len = 3
        current_value_len = 5
        call_depth = 2
        index_info = "[0]"

        # Execute
        event_handls.handle_apd(
            lineno=lineno,
            class_name=class_name,
            key=key,
            value_type=value_type,
            old_value_len=old_value_len,
            current_value_len=current_value_len,
            call_depth=call_depth,
            index_info=index_info,
        )

        # Verify debug logging
        mock_log_debug.assert_called_once()

        # Verify XML structure
        assert len(mock_parent) == 1
        apd_element = mock_parent[0]
        assert apd_element.tag == EventType.APD.label
        assert apd_element.attrib['name'] == f"{class_name}.{key}"
        assert apd_element.attrib['line'] == str(lineno)
        assert apd_element.attrib['old'] == f"({value_type.__name__})(len){old_value_len}"
        assert apd_element.attrib['new'] == f"({value_type.__name__})(len){current_value_len}"

    def test_handle_apd_with_none_lengths(self, monkeypatch):
        """Test handle_apd with None values for old_value_len and current_value_len."""
        # Setup
        event_handls = EventHandls(output_xml=None)
        mock_log_debug = MagicMock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Test parameters
        lineno = 42
        class_name = "TestClass"
        key = "test_list"
        value_type = list
        old_value_len = None
        current_value_len = None
        call_depth = 1
        index_info = ""

        # Execute
        event_handls.handle_apd(
            lineno=lineno,
            class_name=class_name,
            key=key,
            value_type=value_type,
            old_value_len=old_value_len,
            current_value_len=current_value_len,
            call_depth=call_depth,
            index_info=index_info,
        )

        # Verify
        mock_log_debug.assert_called_once()
        call_args = mock_log_debug.call_args[0][0]
        assert f"({value_type.__name__})(len){old_value_len} -> {current_value_len}" in call_args

    def test_handle_apd_with_zero_call_depth(self, monkeypatch):
        """Test handle_apd with call_depth=0."""
        # Setup
        event_handls = EventHandls(output_xml=None)
        mock_log_debug = MagicMock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Test parameters
        lineno = 42
        class_name = "TestClass"
        key = "test_list"
        value_type = list
        old_value_len = 0
        current_value_len = 1
        call_depth = 0
        index_info = "[1]"

        # Execute
        event_handls.handle_apd(
            lineno=lineno,
            class_name=class_name,
            key=key,
            value_type=value_type,
            old_value_len=old_value_len,
            current_value_len=current_value_len,
            call_depth=call_depth,
            index_info=index_info,
        )

        # Verify
        mock_log_debug.assert_called_once()
        call_args = mock_log_debug.call_args[0][0]
        assert f"{lineno:>5} " in call_args  # Should not have any pipes for depth 0
        assert "| " not in call_args
        assert index_info in call_args

    def test_handle_apd_with_different_types(self, monkeypatch):
        """Test handle_apd with different value types."""
        # Setup
        event_handls = EventHandls(output_xml=None)
        mock_log_debug = MagicMock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Test with different types
        test_cases = [(dict, "dict"), (set, "set"), (tuple, "tuple"), (str, "str")]

        for value_type, type_name in test_cases:
            mock_log_debug.reset_mock()

            # Test parameters
            lineno = 10
            class_name = "Container"
            key = "data"
            old_value_len = 1
            current_value_len = 2
            call_depth = 1
            index_info = ""

            # Execute
            event_handls.handle_apd(
                lineno=lineno,
                class_name=class_name,
                key=key,
                value_type=value_type,
                old_value_len=old_value_len,
                current_value_len=current_value_len,
                call_depth=call_depth,
                index_info=index_info,
            )

            # Verify
            mock_log_debug.assert_called_once()
            call_args = mock_log_debug.call_args[0][0]
            assert f"({type_name})(len){old_value_len} -> {current_value_len}" in call_args
