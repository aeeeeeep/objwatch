# MIT License
# Copyright (c) 2025 aeeeeeep

from enum import Enum


class EventType(Enum):
    """
    Enumeration of event types used by ObjWatch to categorize tracing events.
    """

    # Indicates the start of a function or class method execution.
    RUN = 1

    # Signifies the end of a function or class method execution.
    END = 2

    # Represents the creation of a new variable or updating of an existing variable.
    UPD = 3

    # Denotes the addition of elements to data structures like lists, tuple, sets, or dictionaries.
    APD = 4

    # Marks the removal of elements from data structures like lists, tuple, sets, or dictionaries.
    POP = 5

    def __init__(self, value):
        labels = {1: 'run', 2: 'end', 3: 'upd', 4: 'apd', 5: 'pop'}
        self.label = labels[value]

    def __str__(self):
        return self.label

    @property
    def is_function_event(self) -> bool:
        """Check if this event type is related to function execution."""
        return self in (EventType.RUN, EventType.END)

    @property
    def is_variable_event(self) -> bool:
        """Check if this event type is related to variable changes."""
        return self == EventType.UPD

    @property
    def is_collection_event(self) -> bool:
        """Check if this event type is related to collection changes."""
        return self in (EventType.APD, EventType.POP)
