# file: objwatch/event_handls.py:237-253
# asked: {"lines": [237, 248, 249, 250, 251, 252, 253], "branches": [[249, 250], [249, 251], [251, 252], [251, 253]]}
# gained: {"lines": [237, 248, 249, 250, 251, 252, 253], "branches": [[249, 250], [249, 251], [251, 252], [251, 253]]}

import pytest
from objwatch.event_handls import EventHandls
from objwatch.events import EventType


class TestEventHandlsDetermineChangeType:
    """Test cases for EventHandls.determine_change_type method."""

    def test_determine_change_type_apd(self):
        """Test APD event type when current length is greater than old length."""
        handler = EventHandls()
        result = handler.determine_change_type(3, 5)
        assert result == EventType.APD

    def test_determine_change_type_pop(self):
        """Test POP event type when current length is less than old length."""
        handler = EventHandls()
        result = handler.determine_change_type(5, 3)
        assert result == EventType.POP

    def test_determine_change_type_no_change(self):
        """Test None return when current length equals old length."""
        handler = EventHandls()
        result = handler.determine_change_type(4, 4)
        assert result is None

    def test_determine_change_type_zero_to_positive(self):
        """Test APD event type when moving from zero to positive length."""
        handler = EventHandls()
        result = handler.determine_change_type(0, 3)
        assert result == EventType.APD

    def test_determine_change_type_positive_to_zero(self):
        """Test POP event type when moving from positive to zero length."""
        handler = EventHandls()
        result = handler.determine_change_type(3, 0)
        assert result == EventType.POP

    def test_determine_change_type_negative_diff(self):
        """Test POP event type with negative difference."""
        handler = EventHandls()
        result = handler.determine_change_type(10, 2)
        assert result == EventType.POP

    def test_determine_change_type_positive_diff(self):
        """Test APD event type with positive difference."""
        handler = EventHandls()
        result = handler.determine_change_type(2, 10)
        assert result == EventType.APD
