# MIT License
# Copyright (c) 2025 aeeeeeep

from types import FunctionType
from typing import Any, Optional

from ...constants import Constants
from ..models.base_event import BaseEvent
from ..models.function_event import FunctionEvent
from ..models.variable_event import VariableEvent
from ..models.collection_event import CollectionEvent
from .abc_formatter import ABCEventFormatter


class LogEventFormatter(ABCEventFormatter):
    """
    Formatter for standard log output format.

    Converts events to the human-readable log format used by ObjWatch.
    """

    def __init__(self, max_sequence_elements: int = Constants.MAX_SEQUENCE_ELEMENTS):
        """
        Initialize the formatter.

        Args:
            max_sequence_elements: Maximum number of elements to display in sequences
        """
        self.max_sequence_elements = max_sequence_elements

    def can_format(self, event: BaseEvent) -> bool:
        """
        Check if this formatter can handle the given event.

        This formatter can handle all event types.

        Args:
            event: The event to check

        Returns:
            bool: Always True
        """
        return True

    def format(self, event: BaseEvent) -> str:
        """
        Format an event into a log string.

        Args:
            event: The event to format

        Returns:
            str: Formatted log string
        """
        prefix = self.format_prefix(event.lineno, event.call_depth)
        message = self._format_message_content(event)
        return f"{event.index_info}{prefix}{event.event_type.label} {message}"

    def _format_message_content(self, event: BaseEvent) -> str:
        """
        Format the message content based on event type.

        Args:
            event: The event to format

        Returns:
            str: Formatted message content
        """
        if isinstance(event, FunctionEvent):
            return event.format_message()
        elif isinstance(event, VariableEvent):
            return event.format_message()
        elif isinstance(event, CollectionEvent):
            return event.format_message()
        else:
            return f"Unknown event type: {event.event_type}"

    def format_value(self, value: Any, is_return: bool = False) -> str:
        """
        Format a value for display in logs.

        Args:
            value: The value to format
            is_return: Whether this is a return value

        Returns:
            str: Formatted value string
        """
        formatted: str
        if isinstance(value, Constants.LOG_ELEMENT_TYPES):
            formatted = f"{value}"
        elif isinstance(value, Constants.LOG_SEQUENCE_TYPES):
            seq_formatted = self.format_sequence(value)
            if seq_formatted is None:
                formatted = f"({type(value).__name__})[{len(value)} elements]"
            else:
                formatted = seq_formatted
        else:
            try:
                formatted = f"(type){value.__name__}"
            except Exception:
                formatted = f"(type){type(value).__name__}"

        if is_return and isinstance(value, Constants.LOG_SEQUENCE_TYPES):
            return f"[{formatted}]"
        return formatted

    def format_sequence(self, seq: Any, func: Optional[FunctionType] = None) -> Optional[str]:
        """
        Format a sequence to display a limited number of elements.

        Args:
            seq: The sequence to format
            func: Optional function to process elements

        Returns:
            Optional[str]: Formatted sequence string, or None if the sequence
                          cannot be formatted with the given function.
        """
        len_seq = len(seq)
        if len_seq == 0:
            return f'({type(seq).__name__})[]'

        display = self._get_display_elements(seq, func)

        if display is not None:
            if len_seq > self.max_sequence_elements:
                remaining = len_seq - self.max_sequence_elements
                display.append(f"... ({remaining} more elements)")
            return f'({type(seq).__name__})' + str(display)
        else:
            return None

    def _get_display_elements(self, seq: Any, func: Optional[FunctionType]) -> Optional[list]:
        """
        Get display elements for a sequence.

        Args:
            seq: The sequence to process
            func: Optional function to process elements

        Returns:
            Optional[list]: Display elements or None if cannot be formatted.
        """
        if isinstance(seq, list):
            return self._format_list(seq, func)
        elif isinstance(seq, (set, tuple)):
            return self._format_set_tuple(seq, func)
        elif isinstance(seq, dict):
            return self._format_dict(seq, func)
        return None

    def _format_list(self, seq: list, func: Optional[FunctionType]) -> Optional[list]:
        """
        Format a list for display.

        Args:
            seq: The list to format
            func: Optional function to process elements

        Returns:
            Optional[list]: Display elements or None if cannot be formatted.
        """
        if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq[: self.max_sequence_elements]):
            return seq[: self.max_sequence_elements]
        elif func is not None:
            return func(seq[: self.max_sequence_elements])
        return None

    def _format_set_tuple(self, seq: Any, func: Optional[FunctionType]) -> Optional[list]:
        """
        Format a set or tuple for display.

        Args:
            seq: The set or tuple to format
            func: Optional function to process elements

        Returns:
            Optional[list]: Display elements or None if cannot be formatted.
        """
        seq_list = list(seq)[: self.max_sequence_elements]
        if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_list):
            return seq_list
        elif func is not None:
            return func(seq_list)
        return None

    def _format_dict(self, seq: dict, func: Optional[FunctionType]) -> Optional[list]:
        """
        Format a dict for display.

        Args:
            seq: The dict to format
            func: Optional function to process elements

        Returns:
            Optional[list]: Display elements or None if cannot be formatted.
        """
        seq_keys = list(seq.keys())[: self.max_sequence_elements]
        seq_values = list(seq.values())[: self.max_sequence_elements]
        if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_keys) and all(
            isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_values
        ):
            return list(seq.items())[: self.max_sequence_elements]
        elif func is not None:
            display_values = func(seq_values)
            if display_values:
                display = []
                for k, v in zip(seq_keys, display_values):
                    display.append((k, v))
                return display
        return None
