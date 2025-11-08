# MIT License
# Copyright (c) 2025 aeeeeeep

import platform
import importlib.metadata
from typing import Optional
from datetime import datetime

__version__ = importlib.metadata.version("objwatch")


class RuntimeInfo:
    """Runtime information class for ObjWatch.

    This class stores and provides access to runtime information such as:
    - Version of ObjWatch
    - Start time of execution
    - System version information
    - Python version

    Uses singleton pattern to ensure consistent runtime information across the application.
    """

    _instance: Optional['RuntimeInfo'] = None

    def __new__(cls) -> 'RuntimeInfo':
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(RuntimeInfo, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize runtime information."""
        # Store version information
        self._version = __version__
        # Store start time of execution
        self._start_time = datetime.now()
        # Get system information
        self._system_info = platform.platform()
        # Get Python version
        self._python_version = platform.python_version()

    @property
    def version(self) -> str:
        """Get the version of ObjWatch."""
        return self._version

    @property
    def start_time(self) -> str:
        """Get the start time of execution in UTC."""
        return self._start_time.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def system_info(self) -> str:
        """Get system version information."""
        return self._system_info

    @property
    def python_version(self) -> str:
        """Get Python version."""
        return self._python_version

    def get_info_dict(self) -> dict:
        """Get all runtime information as a dictionary."""
        return {
            'version': self.version,
            'start_time': self.start_time,
            'system_info': self.system_info,
            'python_version': self.python_version,
        }

    def update(self) -> None:
        """Update runtime information with current values.

        Refreshes the runtime information to reflect the current state.
        It's useful to call this at the start of the tracing process
        to ensure the timing information is accurate.
        """
        self._start_time = datetime.now()


# Create a global instance for easy access
runtime_info = RuntimeInfo()
