# MIT License
# Copyright (c) 2025 aeeeeeep

from abc import ABC, abstractmethod

from objwatch.events.models.base_event import BaseEvent


class ABCEventFormatter(ABC):
    """
    Abstract base class for event formatters.

    Formatters are responsible for converting event objects into
    specific output formats (log strings, JSON, etc.).
    """

    @abstractmethod
    def format(self, event: BaseEvent) -> str:
        """
        Format an event into a string representation.

        Args:
            event: The event to format

        Returns:
            str: Formatted string representation of the event
        """
        pass

    @abstractmethod
    def can_format(self, event: BaseEvent) -> bool:
        """
        Check if this formatter can handle the given event.

        Args:
            event: The event to check

        Returns:
            bool: True if this formatter can format the event
        """
        pass

    def format_prefix(self, lineno: int, call_depth: int) -> str:
        """
        Generate the standard prefix for log messages.

        Args:
            lineno: Line number where the event occurred
            call_depth: Current call stack depth

        Returns:
            str: Formatted prefix like "   42   " (with indentation)
        """
        return f"{lineno:>5} " + "  " * call_depth
