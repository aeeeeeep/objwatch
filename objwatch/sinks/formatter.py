# MIT License
# Copyright (c) 2025 aeeeeeep

from typing import Any, Optional, Dict
from types import FunctionType

from ..constants import Constants


class Formatter:
    """
    Formats event dictionaries into the final log string format.
    Acts as a rendering engine on the consumer side, converting raw event data
    into the human-readable format expected by users.

    This formatter works with dictionary data (typically from ZeroMQ or other
    sinks) rather than event objects.
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

        display = Formatter._get_display_elements(seq, max_elements, func)

        if display is not None:
            if len_seq > max_elements:
                remaining = len_seq - max_elements
                display.append(f"... ({remaining} more elements)")
            return f'({type(seq).__name__})' + str(display)
        else:
            return f"({type(seq).__name__})[{len(seq)} elements]"

    @staticmethod
    def _get_display_elements(seq: Any, max_elements: int, func: Optional[FunctionType]) -> Optional[list]:
        """
        Get display elements for a sequence.

        Args:
            seq (Any): The sequence to process.
            max_elements (int): Maximum number of elements to display.
            func (Optional[FunctionType]): Optional function to process elements.

        Returns:
            Optional[list]: Display elements or None if cannot be formatted.
        """
        if isinstance(seq, list):
            return Formatter._format_list(seq, max_elements, func)
        elif isinstance(seq, (set, tuple)):
            return Formatter._format_set_tuple(seq, max_elements, func)
        elif isinstance(seq, dict):
            return Formatter._format_dict(seq, max_elements, func)
        return None

    @staticmethod
    def _format_list(seq: list, max_elements: int, func: Optional[FunctionType]) -> Optional[list]:
        """
        Format a list for display.

        Args:
            seq (list): The list to format.
            max_elements (int): Maximum number of elements to display.
            func (Optional[FunctionType]): Optional function to process elements.

        Returns:
            Optional[list]: Display elements or None if cannot be formatted.
        """
        if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq[:max_elements]):
            return seq[:max_elements]
        elif func is not None:
            return func(seq[:max_elements])
        return None

    @staticmethod
    def _format_set_tuple(seq: Any, max_elements: int, func: Optional[FunctionType]) -> Optional[list]:
        """
        Format a set or tuple for display.

        Args:
            seq (Any): The set or tuple to format.
            max_elements (int): Maximum number of elements to display.
            func (Optional[FunctionType]): Optional function to process elements.

        Returns:
            Optional[list]: Display elements or None if cannot be formatted.
        """
        seq_list = list(seq)[:max_elements]
        if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_list):
            return seq_list
        elif func is not None:
            return func(seq_list)
        return None

    @staticmethod
    def _format_dict(seq: dict, max_elements: int, func: Optional[FunctionType]) -> Optional[list]:
        """
        Format a dict for display.

        Args:
            seq (dict): The dict to format.
            max_elements (int): Maximum number of elements to display.
            func (Optional[FunctionType]): Optional function to process elements.

        Returns:
            Optional[list]: Display elements or None if cannot be formatted.
        """
        seq_keys = list(seq.keys())[:max_elements]
        seq_values = list(seq.values())[:max_elements]
        if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_keys) and all(
            isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_values
        ):
            return list(seq.items())[:max_elements]
        elif func is not None:
            display_values = func(seq_values)
            if display_values:
                display = []
                for k, v in zip(seq_keys, display_values):
                    display.append((k, v))
                return display
        return None

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
    def format(event: Dict[str, Any]) -> str:
        """
        Format an event dictionary into the final log string.

        Args:
            event (Dict[str, Any]): The event dictionary to format.
                Expected keys:
                - event_type: str ('run', 'end', 'upd', 'apd', 'pop')
                - lineno: int
                - call_depth: int
                - index_info: str
                - func_info: dict (for run/end events)
                - class_name: str (for upd/apd/pop events)
                - key: str (for upd/apd/pop events)
                - old_value: Any (for upd events)
                - current_value: Any (for upd events)
                - value_type: type (for apd/pop events)
                - old_value_len: int (for apd/pop events)
                - current_value_len: int (for apd/pop events)

        Returns:
            str: The formatted log string.
        """
        lineno = event.get('lineno', 0)
        call_depth = event.get('call_depth', 0)
        event_type = event.get('event_type', 'unknown')
        index_info = event.get('index_info', '')

        prefix = Formatter._generate_prefix(lineno, call_depth)

        if event_type == 'run':
            # Handle run events
            func_info = event.get('func_info', {})
            func_name = func_info.get('qualified_name', 'unknown')
            logger_msg = func_name

        elif event_type == 'end':
            # Handle end events
            func_info = event.get('func_info', {})
            func_name = func_info.get('qualified_name', 'unknown')
            logger_msg = func_name

        elif event_type == 'upd':
            # Handle update events
            old_value = event.get('old_value')
            current_value = event.get('current_value')
            old_msg = Formatter._format_value(old_value)
            current_msg = Formatter._format_value(current_value)
            diff_msg = f" {old_msg} -> {current_msg}"
            class_name = event.get('class_name', '')
            key = event.get('key', '')
            logger_msg = f"{class_name}.{key}{diff_msg}"

        elif event_type in ('apd', 'pop'):
            # Handle collection change events
            value_type = event.get('value_type')
            value_type_name = (
                value_type.__name__ if value_type is not None and hasattr(value_type, '__name__') else str(value_type)
            )
            old_value_len = event.get('old_value_len', 0)
            current_value_len = event.get('current_value_len', 0)
            diff_msg = f" ({value_type_name})(len){old_value_len} -> {current_value_len}"
            class_name = event.get('class_name', '')
            key = event.get('key', '')
            logger_msg = f"{class_name}.{key}{diff_msg}"

        else:
            # Handle unknown event types
            logger_msg = f"Unknown event type: {event_type}"

        return f"{index_info}{prefix}{event_type} {logger_msg}\n"
