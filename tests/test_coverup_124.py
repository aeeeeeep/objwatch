# file: objwatch/event_handls.py:106-153
# asked: {"lines": [106, 108, 109, 110, 111, 112, 113, 114, 115, 116, 130, 131, 132, 133, 135, 136, 138, 139, 140, 141, 143, 144, 145, 146, 147, 148, 149, 150, 153], "branches": [[130, 131], [130, 135], [132, 133], [132, 138], [143, 0], [143, 144]]}
# gained: {"lines": [106, 108, 109, 110, 111, 112, 113, 114, 115, 116, 130, 131, 132, 133, 135, 136, 138, 139, 140, 141, 143, 144, 145, 146, 147, 148, 149, 150, 153], "branches": [[130, 131], [130, 135], [132, 133], [143, 0], [143, 144]]}

import pytest
import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch
from objwatch.event_handls import EventHandls
from objwatch.events import EventType
from objwatch.utils.logger import log_debug


class TestEventHandlsHandleUpd:
    """Test cases for EventHandls.handle_upd method to achieve full coverage."""

    def test_handle_upd_with_abc_wrapper_returns_values(self, monkeypatch):
        """Test handle_upd when abc_wrapper is provided and wrap_upd returns values."""
        # Setup
        event_handls = EventHandls()
        mock_abc_wrapper = Mock()
        mock_abc_wrapper.wrap_upd.return_value = ("wrapped_old", "wrapped_new")

        # Mock log_debug to capture the call
        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Call method
        event_handls.handle_upd(
            lineno=15,
            class_name="AnotherClass",
            key="another_var",
            old_value="old_val",
            current_value="new_val",
            call_depth=1,
            index_info="[1]",
            abc_wrapper=mock_abc_wrapper,
        )

        # Verify abc_wrapper.wrap_upd was called
        mock_abc_wrapper.wrap_upd.assert_called_once_with("old_val", "new_val")

        # Verify log_debug was called with wrapped values
        assert mock_log_debug.called
        call_args = mock_log_debug.call_args[0][0]
        assert "AnotherClass.another_var" in call_args
        assert "wrapped_old -> wrapped_new" in call_args
        assert "15" in call_args
        assert "| " in call_args
        assert "[1]" in call_args
        assert EventType.UPD.label in call_args

    def test_handle_upd_without_abc_wrapper(self, monkeypatch):
        """Test handle_upd when no abc_wrapper is provided."""
        # Setup
        event_handls = EventHandls()

        # Mock _format_value to return predictable values
        monkeypatch.setattr(event_handls, '_format_value', lambda x: f"formatted_{x}")

        # Mock log_debug to capture the call
        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Call method
        event_handls.handle_upd(
            lineno=20,
            class_name="NoWrapperClass",
            key="no_wrapper_var",
            old_value="old_value",
            current_value="current_value",
            call_depth=0,
            index_info="",
            abc_wrapper=None,
        )

        # Verify log_debug was called with formatted values
        assert mock_log_debug.called
        call_args = mock_log_debug.call_args[0][0]
        assert "NoWrapperClass.no_wrapper_var" in call_args
        assert "formatted_old_value -> formatted_current_value" in call_args
        assert "20" in call_args
        assert "| " not in call_args  # call_depth=0 should not show any pipes
        assert EventType.UPD.label in call_args

    def test_handle_upd_with_output_xml_enabled(self, monkeypatch):
        """Test handle_upd when output_xml is True and XML element is created."""
        # Setup
        event_handls = EventHandls(output_xml="test.xml")

        # Mock _format_value
        monkeypatch.setattr(event_handls, '_format_value', lambda x: f"xml_formatted_{x}")

        # Mock log_debug to avoid side effects
        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Store initial number of children
        initial_children_count = len(event_handls.current_node[-1])

        # Call method
        event_handls.handle_upd(
            lineno=25,
            class_name="XmlClass",
            key="xml_var",
            old_value="xml_old",
            current_value="xml_new",
            call_depth=3,
            index_info="[2]",
            abc_wrapper=None,
        )

        # Verify XML element was appended to current_node by checking children count
        assert len(event_handls.current_node[-1]) == initial_children_count + 1

        # Verify the last child is the UPD element
        last_child = event_handls.current_node[-1][-1]
        assert last_child.tag == EventType.UPD.label
        assert last_child.attrib['name'] == "XmlClass.xml_var"
        assert last_child.attrib['line'] == "25"
        assert last_child.attrib['old'] == "xml_formatted_xml_old"
        assert last_child.attrib['new'] == "xml_formatted_xml_new"

    def test_handle_upd_with_output_xml_disabled(self, monkeypatch):
        """Test handle_upd when output_xml is False and no XML element is created."""
        # Setup
        event_handls = EventHandls()

        # Mock _format_value
        monkeypatch.setattr(event_handls, '_format_value', lambda x: f"formatted_{x}")

        # Mock log_debug
        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Call method
        event_handls.handle_upd(
            lineno=30,
            class_name="NoXmlClass",
            key="no_xml_var",
            old_value="old",
            current_value="new",
            call_depth=1,
            index_info="",
            abc_wrapper=None,
        )

        # Verify no XML element was created (current_node should not exist)
        assert not hasattr(event_handls, 'current_node') or event_handls.current_node is None

    def test_handle_upd_with_abc_wrapper_returns_values_and_output_xml(self, monkeypatch):
        """Test handle_upd when abc_wrapper returns values and output_xml is enabled."""
        # Setup
        event_handls = EventHandls(output_xml="test.xml")
        mock_abc_wrapper = Mock()
        mock_abc_wrapper.wrap_upd.return_value = ("wrapped_old", "wrapped_new")

        # Mock log_debug to avoid side effects
        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Store initial number of children
        initial_children_count = len(event_handls.current_node[-1])

        # Call method
        event_handls.handle_upd(
            lineno=40,
            class_name="XmlWrapperClass",
            key="xml_wrapper_var",
            old_value="old_val",
            current_value="new_val",
            call_depth=2,
            index_info="[4]",
            abc_wrapper=mock_abc_wrapper,
        )

        # Verify abc_wrapper.wrap_upd was called
        mock_abc_wrapper.wrap_upd.assert_called_once_with("old_val", "new_val")

        # Verify XML element was appended to current_node by checking children count
        assert len(event_handls.current_node[-1]) == initial_children_count + 1

        # Verify the last child is the UPD element with wrapped values
        last_child = event_handls.current_node[-1][-1]
        assert last_child.tag == EventType.UPD.label
        assert last_child.attrib['name'] == "XmlWrapperClass.xml_wrapper_var"
        assert last_child.attrib['line'] == "40"
        assert last_child.attrib['old'] == "wrapped_old"
        assert last_child.attrib['new'] == "wrapped_new"

    def test_handle_upd_with_call_depth_zero(self, monkeypatch):
        """Test handle_upd with call_depth=0 to verify pipe formatting."""
        # Setup
        event_handls = EventHandls()

        # Mock _format_value to return predictable values
        monkeypatch.setattr(event_handls, '_format_value', lambda x: f"formatted_{x}")

        # Mock log_debug to capture the call
        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Call method with call_depth=0
        event_handls.handle_upd(
            lineno=45,
            class_name="ZeroDepthClass",
            key="zero_depth_var",
            old_value="old",
            current_value="new",
            call_depth=0,
            index_info="",
            abc_wrapper=None,
        )

        # Verify log_debug was called
        assert mock_log_debug.called
        call_args = mock_log_debug.call_args[0][0]
        assert "ZeroDepthClass.zero_depth_var" in call_args
        assert "formatted_old -> formatted_new" in call_args
        assert "45" in call_args
        # With call_depth=0, there should be no pipes after the line number
        assert "45     " in call_args or "45 " in call_args
        assert "| " not in call_args.split("45")[1].split(EventType.UPD.label)[0]

    def test_handle_upd_with_call_depth_three(self, monkeypatch):
        """Test handle_upd with call_depth=3 to verify pipe formatting."""
        # Setup
        event_handls = EventHandls()

        # Mock _format_value to return predictable values
        monkeypatch.setattr(event_handls, '_format_value', lambda x: f"formatted_{x}")

        # Mock log_debug to capture the call
        mock_log_debug = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_debug', mock_log_debug)

        # Call method with call_depth=3
        event_handls.handle_upd(
            lineno=50,
            class_name="ThreeDepthClass",
            key="three_depth_var",
            old_value="old",
            current_value="new",
            call_depth=3,
            index_info="[5]",
            abc_wrapper=None,
        )

        # Verify log_debug was called
        assert mock_log_debug.called
        call_args = mock_log_debug.call_args[0][0]
        assert "ThreeDepthClass.three_depth_var" in call_args
        assert "formatted_old -> formatted_new" in call_args
        assert "50" in call_args
        assert "| | | " in call_args  # call_depth=3 should show three pipes
        assert "[5]" in call_args
        assert EventType.UPD.label in call_args
