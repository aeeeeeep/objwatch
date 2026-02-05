# MIT License
# Copyright (c) 2025 aeeeeeep

"""
Unit tests for EventType enum.

Test Strategy:
- Given: Event type definitions
- When: Accessing or using event types
- Then: Should behave according to specification
"""

import pytest
from objwatch.events.models.event_type import EventType


class TestEventTypeBasics:
    """Tests for basic EventType functionality."""

    def test_given_event_types_when_accessing_then_values_correct(self):
        """
        Given EventType enum,
        When accessing event types,
        Then should have correct values.
        """
        assert EventType.RUN.value == 1
        assert EventType.END.value == 2
        assert EventType.UPD.value == 3
        assert EventType.APD.value == 4
        assert EventType.POP.value == 5

    def test_given_event_types_when_accessing_labels_then_correct(self):
        """
        Given EventType enum,
        When accessing labels,
        Then should have correct labels.
        """
        assert EventType.RUN.label == "run"
        assert EventType.END.label == "end"
        assert EventType.UPD.label == "upd"
        assert EventType.APD.label == "apd"
        assert EventType.POP.label == "pop"

    def test_given_event_types_when_converting_to_string_then_returns_label(self):
        """
        Given EventType enum,
        When converting to string,
        Then should return the label.
        """
        assert str(EventType.RUN) == "run"
        assert str(EventType.END) == "end"
        assert str(EventType.UPD) == "upd"


class TestEventTypeProperties:
    """Tests for EventType properties."""

    def test_given_run_event_when_checking_is_function_event_then_true(self):
        """
        Given RUN event type,
        When checking is_function_event,
        Then should return True.
        """
        assert EventType.RUN.is_function_event is True

    def test_given_end_event_when_checking_is_function_event_then_true(self):
        """
        Given END event type,
        When checking is_function_event,
        Then should return True.
        """
        assert EventType.END.is_function_event is True

    def test_given_upd_event_when_checking_is_function_event_then_false(self):
        """
        Given UPD event type,
        When checking is_function_event,
        Then should return False.
        """
        assert EventType.UPD.is_function_event is False

    def test_given_apd_event_when_checking_is_collection_event_then_true(self):
        """
        Given APD event type,
        When checking is_collection_event,
        Then should return True.
        """
        assert EventType.APD.is_collection_event is True

    def test_given_pop_event_when_checking_is_collection_event_then_true(self):
        """
        Given POP event type,
        When checking is_collection_event,
        Then should return True.
        """
        assert EventType.POP.is_collection_event is True

    def test_given_upd_event_when_checking_is_variable_event_then_true(self):
        """
        Given UPD event type,
        When checking is_variable_event,
        Then should return True.
        """
        assert EventType.UPD.is_variable_event is True

    def test_given_non_upd_event_when_checking_is_variable_event_then_false(self):
        """
        Given non-UPD event type,
        When checking is_variable_event,
        Then should return False.
        """
        assert EventType.RUN.is_variable_event is False
        assert EventType.APD.is_variable_event is False


class TestEventTypeComparison:
    """Tests for EventType comparison."""

    def test_given_same_event_types_when_comparing_then_equal(self):
        """
        Given the same event types,
        When comparing,
        Then should be equal.
        """
        assert EventType.RUN == EventType.RUN
        assert EventType.UPD == EventType.UPD

    def test_given_different_event_types_when_comparing_then_not_equal(self):
        """
        Given different event types,
        When comparing,
        Then should not be equal.
        """
        assert EventType.RUN != EventType.END
        assert EventType.UPD != EventType.APD
