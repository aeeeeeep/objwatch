# MIT License
# Copyright (c) 2025 aeeeeeep

from dataclasses import dataclass
from typing import Dict, Any

from .event_type import EventType
from .base_event import BaseEvent


@dataclass(frozen=True)
class FunctionEvent(BaseEvent):
    """Event for function execution (run/end)."""

    func_info: Dict[str, Any]
    result: Any = None
    call_msg: str = ""
    return_msg: str = ""

    def __post_init__(self):
        if self.event_type not in (EventType.RUN, EventType.END):
            raise ValueError(f"FunctionEvent only supports RUN or END event types, got {self.event_type}")

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'timestamp': self.timestamp,
            'event_type': self.event_type.label,
            'lineno': self.lineno,
            'call_depth': self.call_depth,
            'index_info': self.index_info,
            'process_id': self.process_id,
            'func_info': self._serialize_func_info(self.func_info),
            'result': self._serialize_value(self.result) if self.result is not None else None,
            'call_msg': self.call_msg,
            'return_msg': self.return_msg,
        }
        return data

    def _serialize_func_info(self, func_info: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for key, value in func_info.items():
            if key == 'frame':
                continue
            result[key] = value
        return result

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
        qualified_name = self.get_qualified_name()
        if self.is_run_event:
            if self.call_msg:
                return f"{qualified_name} <- {self.call_msg}"
            return f"{qualified_name} <- "
        else:
            if self.return_msg:
                return f"{qualified_name} -> {self.return_msg}"
            return qualified_name

    def get_qualified_name(self) -> str:
        return self.func_info.get('qualified_name', '')

    def get_symbol(self) -> str:
        return self.func_info.get('symbol', '')

    def get_module(self) -> str:
        return self.func_info.get('module', '')

    def get_symbol_type(self) -> str:
        return self.func_info.get('symbol_type', 'function')

    @property
    def has_wrapper_message(self) -> bool:
        if self.is_run_event:
            return bool(self.call_msg)
        return bool(self.return_msg)
