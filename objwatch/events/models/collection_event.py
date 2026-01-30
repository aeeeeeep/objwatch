# MIT License
# Copyright (c) 2025 aeeeeeep

from dataclasses import dataclass
from typing import Dict, Any

from .event_type import EventType
from .base_event import BaseEvent


@dataclass(frozen=True)
class CollectionEvent(BaseEvent):
    """Event for collection change (apd/pop)."""

    class_name: str
    key: str
    value_type: type
    old_value_len: int
    current_value_len: int

    def __post_init__(self):
        if self.event_type not in (EventType.APD, EventType.POP):
            raise ValueError(f"CollectionEvent only supports APD or POP event types, got {self.event_type}")

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'timestamp': self.timestamp,
            'event_type': self.event_type.label,
            'lineno': self.lineno,
            'call_depth': self.call_depth,
            'index_info': self.index_info,
            'process_id': self.process_id,
            'class_name': self.class_name,
            'key': self.key,
            'value_type': self.value_type.__name__ if hasattr(self.value_type, '__name__') else str(self.value_type),
            'old_value_len': self.old_value_len,
            'current_value_len': self.current_value_len,
        }
        return data

    def format_message(self) -> str:
        value_type_name = self.value_type.__name__ if hasattr(self.value_type, '__name__') else str(self.value_type)
        diff_msg = f" ({value_type_name})(len){self.old_value_len} -> {self.current_value_len}"
        return f"{self.class_name}.{self.key}{diff_msg}"

    def get_qualified_name(self) -> str:
        return f"{self.class_name}.{self.key}"

    @property
    def is_append(self) -> bool:
        return self.event_type == EventType.APD

    @property
    def is_pop(self) -> bool:
        return self.event_type == EventType.POP

    @property
    def change_count(self) -> int:
        return self.current_value_len - self.old_value_len

    @property
    def is_empty_before(self) -> bool:
        return self.old_value_len == 0

    @property
    def is_empty_after(self) -> bool:
        return self.current_value_len == 0
