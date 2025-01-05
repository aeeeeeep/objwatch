# MIT License
# Copyright (c) 2025 aeeeeeep

from enum import Enum


class EventType(Enum):
    """
    Enumeration of event types used by ObjWatch to categorize tracing events.
    """

    # Indicates the start of a function or class method execution.
    RUN = 'run'

    # Signifies the end of a function or class method execution.
    END = 'end'

    # Represents the creation of a new variable.
    UPD = 'upd'

    # Denotes the addition of elements to data structures like lists, sets, or dictionaries.
    APD = 'apd'

    # Marks the removal of elements from data structures like lists, sets, or dictionaries.
    POP = 'pop'
