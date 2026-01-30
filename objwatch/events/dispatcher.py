# MIT License
# Copyright (c) 2025 aeeeeeep

from typing import List, Optional

from .models.base_event import BaseEvent
from .handlers.abc_handler import ABCEventHandler
from .handlers.logging_handler import LoggingEventHandler
from .handlers.json_output_handler import JsonOutputHandler
from ..config import ObjWatchConfig


class EventDispatcher:
    """
    Central dispatcher for routing events to registered handlers.

    The dispatcher maintains a list of event handlers and routes
    incoming events to all handlers that can process them.

    This class follows the Observer pattern, allowing multiple
    handlers to process the same event.
    """

    def __init__(self, config: Optional[ObjWatchConfig] = None):
        """
        Initialize the event dispatcher.

        Args:
            config: Optional configuration for auto-configuring handlers
        """
        self._handlers: List[ABCEventHandler] = []
        self._config = config

        # Auto-configure default handlers if config is provided
        if config:
            self._setup_default_handlers(config)

    def _setup_default_handlers(self, config: ObjWatchConfig) -> None:
        """
        Set up default handlers based on configuration.

        Args:
            config: The configuration to use
        """
        # Always add logging handler
        self.register_handler(LoggingEventHandler())

        # Add JSON output handler if output_json is configured
        if config.output_json:
            self.register_handler(JsonOutputHandler(config=config))

    def register_handler(self, handler: ABCEventHandler) -> None:
        """
        Register an event handler.

        Args:
            handler: The handler to register
        """
        if handler not in self._handlers:
            self._handlers.append(handler)
            handler.start()

    def unregister_handler(self, handler: ABCEventHandler) -> None:
        """
        Unregister an event handler.

        Args:
            handler: The handler to unregister
        """
        if handler in self._handlers:
            handler.stop()
            self._handlers.remove(handler)

    def dispatch(self, event: BaseEvent) -> None:
        """
        Dispatch an event to all registered handlers that can handle it.

        Args:
            event: The event to dispatch
        """
        for handler in self._handlers:
            try:
                if handler.can_handle(event):
                    handler.handle(event)
            except Exception as e:
                # Log error but continue processing with other handlers
                # Import here to avoid circular imports
                from ..utils.logger import log_error

                log_error(f"Handler {type(handler).__name__} failed to process event: {e}")

    def start(self) -> None:
        """
        Start all registered handlers.
        """
        for handler in self._handlers:
            handler.start()

    def stop(self) -> None:
        """
        Stop all registered handlers and perform cleanup.
        """
        for handler in self._handlers:
            try:
                handler.stop()
            except Exception as e:
                from ..utils.logger import log_error

                log_error(f"Error stopping handler {type(handler).__name__}: {e}")

    def clear_handlers(self) -> None:
        """
        Clear all registered handlers.
        """
        self.stop()
        self._handlers.clear()

    @property
    def handlers(self) -> List[ABCEventHandler]:
        """
        Get the list of registered handlers.

        Returns:
            List[ABCEventHandler]: Copy of the handlers list
        """
        return self._handlers.copy()

    @property
    def handler_count(self) -> int:
        """
        Get the number of registered handlers.

        Returns:
            int: Number of handlers
        """
        return len(self._handlers)
