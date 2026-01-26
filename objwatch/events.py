# MIT License
# Copyright (c) 2025 aeeeeeep

from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


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


@dataclass
class LogEvent:
    """
    Lightweight data structure for raw tracing events.
    Contains minimal data needed to reconstruct the final log message.
    """

    # Basic event information (all required, no defaults)
    timestamp: float
    event_type: str
    lineno: int
    call_depth: int

    # Optional context information with defaults
    level: str = "INFO"
    index_info: str = ""

    # Function information (for run/end events)
    func_info: Optional[Dict[str, Any]] = None

    # Update information (for upd events)
    class_name: Optional[str] = None
    key: Optional[str] = None
    old_value: Optional[Any] = None
    current_value: Optional[Any] = None

    # Collection change information (for apd/pop events)
    value_type: Optional[type] = None
    old_value_len: Optional[int] = None
    current_value_len: Optional[int] = None

    # Additional metadata
    process_id: Optional[str] = None
    output_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling non-serializable types."""
        return asdict(self)
