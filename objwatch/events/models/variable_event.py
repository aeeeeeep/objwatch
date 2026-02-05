# MIT License
# Copyright (c) 2025 aeeeeeep

from dataclasses import dataclass
from typing import Dict, Any

from .event_type import EventType
from .base_event import BaseEvent


@dataclass(frozen=True)
class VariableEvent(BaseEvent):
    """Event for variable update."""

    class_name: str
    key: str
    old_value: Any = None
    current_value: Any = None
    old_msg: str = ""
    current_msg: str = ""

    def __post_init__(self):
        if self.event_type != EventType.UPD:
            raise ValueError(f"VariableEvent only supports UPD event type, got {self.event_type}")

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
            'old_value': self._serialize_value(self.old_value),
            'current_value': self._serialize_value(self.current_value),
            'old_msg': self.old_msg,
            'current_msg': self.current_msg,
        }
        return data

    def _serialize_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value]
        if isinstance(value, dict):
            return {str(k): self._serialize_value(v) for k, v in value.items()}
        return f"(type){type(value).__name__}"

    def format_message(self) -> str:
        old_str = self.old_msg if self.old_msg else self._format_value(self.old_value)
        current_str = self.current_msg if self.current_msg else self._format_value(self.current_value)
        return f"{self.class_name}.{self.key} {old_str} -> {current_str}"

    def _format_value(self, value: Any) -> str:
        if value is None:
            return "None"
        if isinstance(value, (bool, int, float, str)):
            return str(value)
        if isinstance(value, (list, tuple, set, dict)):
            type_name = type(value).__name__
            return f"({type_name})[{len(value)} elements]"
        try:
            return f"(type){value.__name__}"
        except AttributeError:
            return f"(type){type(value).__name__}"

    def get_qualified_name(self) -> str:
        return f"{self.class_name}.{self.key}"

    @property
    def is_new_variable(self) -> bool:
        return self.old_value is None

    @property
    def is_global_variable(self) -> bool:
        return self.class_name == "@"

    @property
    def is_local_variable(self) -> bool:
        return self.class_name == "_"
