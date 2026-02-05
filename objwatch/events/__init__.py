# MIT License
# Copyright (c) 2025 aeeeeeep

"""
ObjWatch Events Module

Provides a modular event handling system with clear separation of concerns:
- models: Event data structures
- formatters: Event formatting logic
- handlers: Event processing and output
- dispatcher: Event routing and distribution
"""

from .models.event_type import EventType
from .models.base_event import BaseEvent
from .models.function_event import FunctionEvent
from .models.variable_event import VariableEvent
from .models.collection_event import CollectionEvent
from .dispatcher import EventDispatcher

__all__ = [
    'EventType',
    'BaseEvent',
    'FunctionEvent',
    'VariableEvent',
    'CollectionEvent',
    'EventDispatcher',
]
