# MIT License
# Copyright (c) 2025 aeeeeeep

from types import FrameType


def target_handler(o):
    """
    Custom JSON encoder handler for objects that are not JSON serializable by default.

    Args:
        o: The object to serialize

    Returns:
        A JSON-serializable representation of the object
    """
    # Handle frame objects (not serializable)
    if isinstance(o, FrameType):
        return "<frame>"

    # Handle sets (convert to list)
    if isinstance(o, set):
        return list(o)

    # Handle objects with __dict__
    if hasattr(o, '__dict__'):
        try:
            return o.__dict__
        except Exception:
            return str(o)

    # Fallback to string representation
    return str(o)
