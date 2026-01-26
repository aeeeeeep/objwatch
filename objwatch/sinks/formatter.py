# MIT License
# Copyright (c) 2025 aeeeeeep

from typing import Any, Optional
from types import FunctionType

from ..constants import Constants
from ..events import LogEvent


class Formatter:
    """
    Formats LogEvent objects into the final log string format.
    Acts as a rendering engine on the consumer side, converting raw event data
    into the human-readable format expected by users.
    """

    @staticmethod
    def _generate_prefix(lineno: int, call_depth: int) -> str:
        """
        Generate a formatted prefix for logging with caching.

        Args:
            lineno (int): The line number where the event occurred.
            call_depth (int): Current depth of the call stack.

        Returns:
            str: The formatted prefix string.
        """
        return f"{lineno:>5} " + "  " * call_depth

    @staticmethod
    def format_sequence(
        seq: Any, max_elements: int = Constants.MAX_SEQUENCE_ELEMENTS, func: Optional[FunctionType] = None
    ) -> str:
        """
        Format a sequence to display a limited number of elements.

        Args:
            seq (Any): The sequence to format.
            max_elements (int): Maximum number of elements to display.
            func (Optional[FunctionType]): Optional function to process elements.

        Returns:
            str: The formatted sequence string.
        """
        len_seq = len(seq)
        if len_seq == 0:
            return f'({type(seq).__name__})[]'
        display: Optional[list] = None
        if isinstance(seq, list):
            if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq[:max_elements]):
                display = seq[:max_elements]
            elif func is not None:
                display = func(seq[:max_elements])
        elif isinstance(seq, (set, tuple)):
            seq_list = list(seq)[:max_elements]
            if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_list):
                display = seq_list
            elif func is not None:
                display = func(seq_list)
        elif isinstance(seq, dict):
            seq_keys = list(seq.keys())[:max_elements]
            seq_values = list(seq.values())[:max_elements]
            if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_keys) and all(
                isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_values
            ):
                display = list(seq.items())[:max_elements]
            elif func is not None:
                display_values = func(seq_values)
                if display_values:
                    display = []
                    for k, v in zip(seq_keys, display_values):
                        display.append((k, v))

        if display is not None:
            if len_seq > max_elements:
                remaining = len_seq - max_elements
                display.append(f"... ({remaining} more elements)")
            return f'({type(seq).__name__})' + str(display)
        else:
            return f"({type(seq).__name__})[{len(seq)} elements]"

    @staticmethod
    def _format_value(value: Any) -> str:
        """
        Format individual values for the 'upd' event.

        Args:
            value (Any): The value to format.

        Returns:
            str: The formatted value string.
        """
        if isinstance(value, Constants.LOG_ELEMENT_TYPES):
            return f"{value}"
        elif isinstance(value, Constants.LOG_SEQUENCE_TYPES):
            return Formatter.format_sequence(value)
        else:
            try:
                return f"(type){value.__name__}"
            except Exception:
                return f"(type){type(value).__name__}"

    @staticmethod
    def format(event: LogEvent) -> str:
        """
        Format a LogEvent into the final log string.

        Args:
            event (LogEvent): The event to format.

        Returns:
            str: The formatted log string.
        """
        prefix = Formatter._generate_prefix(event.lineno, event.call_depth)

        if event.event_type == 'run':
            # Handle run events
            func_name = event.func_info['qualified_name']
            logger_msg = func_name

        elif event.event_type == 'end':
            # Handle end events
            func_name = event.func_info['qualified_name']
            logger_msg = func_name

        elif event.event_type == 'upd':
            # Handle update events
            old_msg = Formatter._format_value(event.old_value)
            current_msg = Formatter._format_value(event.current_value)
            diff_msg = f" {old_msg} -> {current_msg}"
            logger_msg = f"{event.class_name}.{event.key}{diff_msg}"

        elif event.event_type in ('apd', 'pop'):
            # Handle collection change events
            # value_type might be a string if it was serialized, so handle both cases
            value_type_name = (
                event.value_type.__name__ if hasattr(event.value_type, '__name__') else str(event.value_type)
            )
            diff_msg = f" ({value_type_name})(len){event.old_value_len} -> {event.current_value_len}"
            logger_msg = f"{event.class_name}.{event.key}{diff_msg}"

        else:
            # Handle unknown event types
            logger_msg = f"Unknown event type: {event.event_type}"

        return f"{event.index_info}{prefix}{event.event_type} {logger_msg}\n"
