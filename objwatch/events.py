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

    # Represents the creation of a new variable.
    UPD = 3

    # Denotes the addition of elements to data structures like lists, tuple, sets, or dictionaries.
    APD = 4

    # Marks the removal of elements from data structures like lists, tuple, sets, or dictionaries.
    POP = 5

    def __init__(self, value):
        labels = {1: 'run', 2: 'end', 3: 'upd', 4: 'apd', 5: 'pop'}
        self.label = labels[value]
