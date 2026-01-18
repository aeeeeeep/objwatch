# MIT License
# Copyright (c) 2025 aeeeeeep

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseSink(ABC):
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
