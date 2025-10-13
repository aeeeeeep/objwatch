# file: objwatch/event_handls.py:328-346
# asked: {"lines": [328, 332, 333, 334, 335, 336, 338, 339, 342, 343, 344, 346], "branches": [[332, 0], [332, 333], [335, 336], [335, 338]]}
# gained: {"lines": [328, 332, 333, 334, 335, 336, 338, 339, 342, 343, 344, 346], "branches": [[332, 0], [332, 333], [335, 336], [335, 338]]}

import pytest
import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch, MagicMock
import sys


class TestEventHandlsSaveXML:
    """Test cases for EventHandls.save_xml method to achieve full coverage."""

    def test_save_xml_without_et_indent_success(self, monkeypatch):
        """Test save_xml when ET.indent is not available and output_xml is set."""
        from objwatch.event_handls import EventHandls

        # Mock the logger functions to capture calls
        mock_log_info = Mock()
        mock_log_warn = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_info', mock_log_info)
        monkeypatch.setattr('objwatch.event_handls.log_warn', mock_log_warn)

        # Create instance with output_xml
        event_handls = EventHandls(output_xml="/tmp/test_output.xml")
        event_handls.is_xml_saved = False
        event_handls.stack_root = ET.Element('ObjWatch')

        # Remove ET.indent to simulate older Python versions
        monkeypatch.delattr(ET, 'indent', raising=False)

        # Mock tree.write to avoid actual file I/O
        with patch('xml.etree.ElementTree.ElementTree') as MockElementTree:
            mock_tree_instance = Mock()
            MockElementTree.return_value = mock_tree_instance
            mock_tree_instance.write = Mock()

            event_handls.save_xml()

        # Verify XML was saved
        assert event_handls.is_xml_saved is True

        # Verify warning was logged about missing ET.indent
        mock_log_warn.assert_called_once()
        warning_msg = mock_log_warn.call_args[0][0]
        assert "Current Python version not support `xml.etree.ElementTree.indent`" in warning_msg

    def test_save_xml_no_output_xml(self, monkeypatch):
        """Test save_xml when output_xml is None (should do nothing)."""
        from objwatch.event_handls import EventHandls

        # Mock the logger functions
        mock_log_info = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_info', mock_log_info)

        # Create instance without output_xml
        event_handls = EventHandls(output_xml=None)

        # Mock the XML creation to verify it's not called
        with patch('xml.etree.ElementTree.ElementTree') as mock_et:
            event_handls.save_xml()

            # Verify no XML operations were performed
            mock_et.assert_not_called()
            mock_log_info.assert_not_called()

    def test_save_xml_already_saved(self, monkeypatch):
        """Test save_xml when is_xml_saved is already True (should do nothing)."""
        from objwatch.event_handls import EventHandls

        # Mock the logger functions
        mock_log_info = Mock()
        monkeypatch.setattr('objwatch.event_handls.log_info', mock_log_info)

        # Create instance with output_xml but already saved
        event_handls = EventHandls(output_xml="/tmp/test_output.xml")
        event_handls.is_xml_saved = True

        # Mock the XML creation to verify it's not called
        with patch('xml.etree.ElementTree.ElementTree') as mock_et:
            event_handls.save_xml()

            # Verify no XML operations were performed
            mock_et.assert_not_called()
            mock_log_info.assert_not_called()
