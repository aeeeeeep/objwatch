# MIT License
# Copyright (c) 2025 aeeeeeep

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

from .event_type import EventType


@dataclass(frozen=True)
class BaseEvent(ABC):
    """
    Abstract base class for all ObjWatch events.

    Provides common attributes and interface for all event types.
    Events are immutable (frozen dataclass) to ensure data integrity.
    """

    # Core event attributes (all required, no defaults)
    timestamp: float
    event_type: EventType
    lineno: int
    call_depth: int
    index_info: str
    process_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary containing all event data.
        """
        data = asdict(self)
        # Convert EventType enum to its label string
        data['event_type'] = self.event_type.label
        return data

    @abstractmethod
    def format_message(self) -> str:
        """
        Format the event-specific message content.

        Returns:
            str: The formatted message string for this event.
        """
        pass

    def get_qualified_name(self) -> str:
        """
        Get the qualified name for this event (if applicable).

        Returns:
            str: Qualified name or empty string.
        """
        return ""

    @property
    def is_run_event(self) -> bool:
        """Check if this is a function run event."""
        return self.event_type == EventType.RUN

    @property
    def is_end_event(self) -> bool:
        """Check if this is a function end event."""
        return self.event_type == EventType.END

    @property
    def is_upd_event(self) -> bool:
        """Check if this is a variable update event."""
        return self.event_type == EventType.UPD

    @property
    def is_apd_event(self) -> bool:
        """Check if this is a collection append event."""
        return self.event_type == EventType.APD

    @property
    def is_pop_event(self) -> bool:
        """Check if this is a collection pop event."""
        return self.event_type == EventType.POP
