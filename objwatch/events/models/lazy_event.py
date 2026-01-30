# MIT License
# Copyright (c) 2025 aeeeeeep

from dataclasses import dataclass
from typing import Dict, Any, Optional
import time

from .base_event import BaseEvent
from .event_type import EventType


@dataclass(frozen=True)
class LazyEventRef:
    """Lightweight event reference for lazy serialization."""

    event: BaseEvent
    created_at: float

    def __init__(self, event: BaseEvent, created_at: Optional[float] = None):
        object.__setattr__(self, 'event', event)
        object.__setattr__(self, 'created_at', created_at if created_at is not None else time.time())

    def to_dict(self) -> Dict[str, Any]:
        """Perform full serialization on consumer side."""
        return self.event.to_dict()

    def format_message(self) -> str:
        """Get formatted message from wrapped event."""
        return self.event.format_message()

    def get_qualified_name(self) -> str:
        """Get qualified name from wrapped event."""
        return self.event.get_qualified_name()

    @property
    def event_type(self) -> EventType:
        return self.event.event_type

    @property
    def lineno(self) -> int:
        return self.event.lineno

    @property
    def call_depth(self) -> int:
        return self.event.call_depth

    @property
    def index_info(self) -> str:
        return self.event.index_info

    @property
    def process_id(self) -> Optional[str]:
        return self.event.process_id

    @property
    def timestamp(self) -> float:
        return self.event.timestamp

    @property
    def is_run_event(self) -> bool:
        return self.event.is_run_event

    @property
    def is_end_event(self) -> bool:
        return self.event.is_end_event

    @property
    def is_upd_event(self) -> bool:
        return self.event.is_upd_event

    @property
    def is_apd_event(self) -> bool:
        return self.event.is_apd_event

    @property
    def is_pop_event(self) -> bool:
        return self.event.is_pop_event
