# MIT License
# Copyright (c) 2025 aeeeeeep

from abc import ABC, abstractmethod
from typing import Any

from ..models.base_event import BaseEvent


class ABCEventHandler(ABC):
    """
    Abstract base class for event handlers.

    Handlers are responsible for processing events and performing
    actions such as logging, JSON output, or custom processing.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the event handler.

        Args:
            **kwargs: Optional keyword arguments for subclass initialization.
        """
        pass

    @abstractmethod
    def can_handle(self, event: BaseEvent) -> bool:
        """
        Check if this handler can process the given event.

        Args:
            event: The event to check

        Returns:
            bool: True if this handler can process the event
        """
        pass

    @abstractmethod
    def handle(self, event: BaseEvent) -> None:
        """
        Process the event.

        Args:
            event: The event to process
        """
        pass

    def start(self) -> None:
        """
        Called when the handler is started.
        Override to perform initialization.
        """
        pass

    def stop(self) -> None:
        """
        Called when the handler is stopped.
        Override to perform cleanup.
        """
        pass
