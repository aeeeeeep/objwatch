# MIT License
# Copyright (c) 2025 aeeeeeep

from enum import Enum
from types import FunctionType

try:
    from types import NoneType  # type: ignore
except ImportError:
    NoneType = type(None)  # type: ignore


class Constants:
    """
    Constants class for managing magic values and configuration parameters in ObjWatch project.
    """

    # Target processing related constants
    MAX_TARGETS_DISPLAY = 8  # Maximum number of targets to display before truncation

    # Sequence formatting related constants
    MAX_SEQUENCE_ELEMENTS = 3  # Maximum number of elements to display when formatting sequences

    # Logging related constants
    LOG_INDENT_LEVEL = 2  # Default indentation level for JSON serialization

    # Log element types
    # Define types that are directly loggable
    LOG_ELEMENT_TYPES = (
        bool,
        int,
        float,
        str,
        NoneType,
        FunctionType,
        Enum,
    )

    # Log sequence types
    # Define sequence types for logging
    LOG_SEQUENCE_TYPES = (list, set, dict, tuple)

    # Handle globals symbol in log message
    HANDLE_GLOBALS_SYMBOL = "@"

    # Handle locals symbol in log message
    HANDLE_LOCALS_SYMBOL = "_"
