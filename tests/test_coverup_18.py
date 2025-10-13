# file: objwatch/events.py:7-29
# asked: {"lines": [7, 8, 13, 16, 19, 22, 25, 27, 28, 29], "branches": []}
# gained: {"lines": [7, 8, 13, 16, 19, 22, 25, 27, 28, 29], "branches": []}

import pytest


def test_event_type_enum_members():
    """Test that all EventType enum members are properly defined and have correct labels."""
    from objwatch.events import EventType

    # Test RUN member
    assert EventType.RUN.value == 1
    assert EventType.RUN.label == 'run'

    # Test END member
    assert EventType.END.value == 2
    assert EventType.END.label == 'end'

    # Test UPD member
    assert EventType.UPD.value == 3
    assert EventType.UPD.label == 'upd'

    # Test APD member
    assert EventType.APD.value == 4
    assert EventType.APD.label == 'apd'

    # Test POP member
    assert EventType.POP.value == 5
    assert EventType.POP.label == 'pop'


def test_event_type_enum_iteration():
    """Test that EventType enum can be iterated and all members are accessible."""
    from objwatch.events import EventType

    expected_members = [(1, 'run'), (2, 'end'), (3, 'upd'), (4, 'apd'), (5, 'pop')]

    for event_type, (expected_value, expected_label) in zip(EventType, expected_members):
        assert event_type.value == expected_value
        assert event_type.label == expected_label


def test_event_type_enum_lookup():
    """Test that EventType enum members can be looked up by value."""
    from objwatch.events import EventType

    assert EventType(1) is EventType.RUN
    assert EventType(2) is EventType.END
    assert EventType(3) is EventType.UPD
    assert EventType(4) is EventType.APD
    assert EventType(5) is EventType.POP


def test_event_type_enum_comparison():
    """Test that EventType enum members can be compared."""
    from objwatch.events import EventType

    assert EventType.RUN == EventType.RUN
    assert EventType.END == EventType.END
    assert EventType.UPD == EventType.UPD
    assert EventType.APD == EventType.APD
    assert EventType.POP == EventType.POP

    assert EventType.RUN != EventType.END
    assert EventType.END != EventType.UPD
