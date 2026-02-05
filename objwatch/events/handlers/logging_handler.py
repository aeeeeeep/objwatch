# MIT License
# Copyright (c) 2025 aeeeeeep

from ...utils.logger import log_debug
from ..models.base_event import BaseEvent
from .abc_handler import ABCEventHandler


class LoggingEventHandler(ABCEventHandler):
    """Handler for logging events with deferred serialization."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._formatter = None

    @property
    def formatter(self):
        if self._formatter is None:
            from ..formatters.log_formatter import LogEventFormatter

            self._formatter = LogEventFormatter()
        return self._formatter

    def can_handle(self, event: BaseEvent) -> bool:
        """Check if this handler can process the given event."""
        return True

    def handle(self, event: BaseEvent) -> None:
        """Process event by passing it directly for deferred serialization."""
        formatted_msg = self.formatter.format(event)
        log_debug(formatted_msg, extra={'event': event})
