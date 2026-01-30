# MIT License
# Copyright (c) 2025 aeeeeeep

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseSink(ABC):
    """
    Abstract base class for all sinks.

    Sinks are responsible for outputting tracing events to various destinations
    such as files, stdout, or network endpoints.
    """

    def __init__(self, output_path: Optional[str] = None, **kwargs) -> None:
        """
        Initialize the sink.

        Args:
            output_path: Optional file path for output.
            **kwargs: Additional keyword arguments for subclass initialization.
        """
        self.output_path = output_path

    @abstractmethod
    def emit(self, event: Dict[str, Any]) -> None:
        """Process a tracing event.
        Args:
            event: A dictionary containing trace data (timestamp, type, payload).
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Cleanup resources."""
        pass
