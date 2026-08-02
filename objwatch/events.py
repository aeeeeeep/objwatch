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

    # Indicates an exception has occurred.
    EXCEPTION = 6

    # Indicates a C function is about to be called.
    C_CALL = 7

    # Indicates a C function has returned.
    C_RETURN = 8

    # Indicates a C function has raised an exception.
    C_EXCEPTION = 9

    def __init__(self, value):
        labels = {1: 'run', 2: 'end', 3: 'upd', 4: 'apd', 5: 'pop', 6: 'exception', 7: 'c_call', 8: 'c_return', 9: 'c_exception'}
        self.label = labels[value]
