# MIT License
# Copyright (c) 2025 aeeeeeep

import json
import signal
import atexit
from typing import Any, Dict, List

from ...runtime_info import runtime_info
from ...utils.logger import log_info, log_error
from ...utils.util import target_handler
from ..models.base_event import BaseEvent
from ..models.function_event import FunctionEvent
from ..models.variable_event import VariableEvent
from ..models.collection_event import CollectionEvent
from .abc_handler import ABCEventHandler


class JsonOutputHandler(ABCEventHandler):
    """
    Handler for outputting events to a JSON file.

    Maintains a hierarchical structure of events and saves them to
    a JSON file on program exit or when explicitly requested.

    The output format matches the legacy golden file structure:
    - FunctionEvent: type, module, symbol, symbol_type, run_line, qualified_name, events, call_msg, return_msg, end_line
    - VariableEvent: type, name, line, old, new, call_depth
    - CollectionEvent: type, name, line, old, new, call_depth
    """

    def __init__(self, **kwargs: Any):
        """
        Initialize the JSON output handler.

        Args:
            **kwargs: Optional keyword arguments including 'config' for ObjWatch configuration.
        """
        super().__init__(**kwargs)
        self.config = kwargs.get('config')
        self.output_json = self.config.output_json if self.config else None

        # State tracking
        self.is_json_saved: bool = False
        self.event_id: int = 1

        # JSON structure with runtime info, config and events stack
        self.stack_root: Dict[str, Any] = {
            'ObjWatch': {
                'runtime_info': runtime_info.get_info_dict(),
                'config': self.config.to_dict() if self.config else {},
                'events': [],
            }
        }
        self.current_node: List[Any] = [self.stack_root['ObjWatch']['events']]

        # Register exit handlers
        self._register_exit_handlers()

    def _register_exit_handlers(self) -> None:
        """Register handlers for normal and abnormal program exits."""
        # Register for normal exit handling
        atexit.register(self.save_json)

        # Register signal handlers for abnormal exits
        signal_types = [
            signal.SIGTERM,  # Termination signal (default)
            signal.SIGINT,  # Interrupt from keyboard (Ctrl + C)
            signal.SIGABRT,  # Abort signal from program
            signal.SIGHUP,  # Hangup signal
            signal.SIGQUIT,  # Quit signal
            signal.SIGUSR1,  # User-defined signal 1
            signal.SIGUSR2,  # User-defined signal 2
            signal.SIGALRM,  # Alarm signal
            signal.SIGSEGV,  # Segmentation fault
        ]

        for signal_type in signal_types:
            try:
                signal.signal(signal_type, self._signal_handler)
            except (ValueError, OSError):
                # Some signals may not be available on all platforms
                pass

    def _signal_handler(self, signum, frame) -> None:
        """
        Signal handler for abnormal program termination.

        Args:
            signum: The signal number
            frame: The current stack frame
        """
        if not self.is_json_saved:
            log_error(f"Received signal {signum}, saving JSON before exiting.")
            self.save_json()
            exit(1)

    def can_handle(self, event: BaseEvent) -> bool:
        """
        Check if this handler can process the given event.

        This handler can process all event types when output_json is configured.

        Args:
            event: The event to check

        Returns:
            bool: True if output_json is configured
        """
        return self.output_json is not None

    def handle(self, event: BaseEvent) -> None:
        """
        Process the event by adding it to the JSON structure.

        Args:
            event: The event to process
        """
        if not self.output_json:
            return

        try:
            # Handle function events with hierarchy
            if isinstance(event, FunctionEvent):
                self._handle_function_event(event)
            else:
                # For variable and collection events, convert and add to current node
                event_data = self._convert_event_to_json(event)
                event_data['id'] = self.event_id
                self.event_id += 1
                self.current_node[-1].append(event_data)
        except Exception as e:
            log_error(f"JsonOutputHandler failed to process event: {e}")
            # Try to process with minimal data to avoid losing the event
            try:
                minimal_event = self._create_minimal_event(event, e)
                self.current_node[-1].append(minimal_event)
            except Exception as inner_e:
                # Last resort: skip this event if even minimal event creation fails
                # This prevents the entire handler from crashing due to a single problematic event
                log_error(f"JsonOutputHandler failed to create minimal event: {inner_e}")
                pass

    def _create_minimal_event(self, event: BaseEvent, error: Exception) -> Dict[str, Any]:
        """
        Create a minimal event representation when serialization fails.

        Args:
            event: The event that failed to serialize
            error: The serialization error

        Returns:
            Dict[str, Any]: Minimal event data
        """
        data = {
            'id': self.event_id,
            'type': event.event_type.label.upper(),
            'line': event.lineno,
            'call_depth': event.call_depth,
            'error': f"Failed to serialize: {error}",
        }
        self.event_id += 1
        return data

    def _convert_event_to_json(self, event: BaseEvent) -> Dict[str, Any]:
        """
        Convert an event to JSON-compatible dictionary format matching legacy structure.

        Note: This method does NOT assign event ID. The caller is responsible
        for assigning the ID before adding to the JSON structure.

        Args:
            event: The event to convert

        Returns:
            Dict[str, Any]: JSON-compatible dictionary in legacy format
        """
        if isinstance(event, FunctionEvent):
            return self._convert_function_event(event)
        elif isinstance(event, VariableEvent):
            return self._convert_variable_event(event)
        elif isinstance(event, CollectionEvent):
            return self._convert_collection_event(event)
        else:
            # Fallback for unknown event types
            return {
                'type': event.event_type.label.upper(),
                'line': event.lineno,
                'call_depth': event.call_depth,
            }

    def _convert_function_event(self, event: FunctionEvent) -> Dict[str, Any]:
        """
        Convert FunctionEvent to legacy JSON format.

        Legacy format:
        {
            "id": 1,
            "type": "Function",
            "module": "tests.test_output_json",
            "symbol": "TestClass.outer_function",
            "symbol_type": "function",
            "run_line": 87,
            "qualified_name": "tests.test_output_json.TestClass.outer_function",
            "events": [],
            "call_msg": "'0':(type)TestClass",
            "return_msg": "",
            "end_line": 87
        }

        Args:
            event: The FunctionEvent to convert

        Returns:
            Dict[str, Any]: Legacy format dictionary (without id)
        """
        func_info = event.func_info

        data: Dict[str, Any] = {
            'type': 'Function',
            'module': func_info.get('module', ''),
            'symbol': func_info.get('symbol', ''),
            'symbol_type': func_info.get('symbol_type') or 'function',
            'run_line': event.lineno,
            'qualified_name': func_info.get('qualified_name', ''),
            'events': [],
        }

        # Only add call_msg if it's not empty
        if event.call_msg:
            data['call_msg'] = event.call_msg

        # For end events, add return_msg and end_line
        if not event.is_run_event:
            data['end_line'] = event.lineno
            if event.return_msg:
                data['return_msg'] = event.return_msg

        return data

    def _convert_variable_event(self, event: VariableEvent) -> Dict[str, Any]:
        """
        Convert VariableEvent to legacy JSON format.

        Legacy format:
        {
            "id": 2,
            "type": "upd",
            "name": "TestClass.a",
            "line": 35,
            "old": "None",
            "new": "10",
            "call_depth": 1
        }

        Args:
            event: The VariableEvent to convert

        Returns:
            Dict[str, Any]: Legacy format dictionary (without id)
        """
        # Use wrapper-provided messages if available, otherwise format from values
        old_str = event.old_msg if event.old_msg else self._format_value(event.old_value)
        current_str = event.current_msg if event.current_msg else self._format_value(event.current_value)

        return {
            'type': event.event_type.label.lower(),
            'name': f"{event.class_name}.{event.key}",
            'line': event.lineno,
            'old': old_str,
            'new': current_str,
            'call_depth': event.call_depth,
        }

    def _format_value(self, value: Any) -> str:
        """
        Format a value for JSON output.

        Args:
            value: The value to format

        Returns:
            str: Formatted value string
        """
        if value is None:
            return "None"
        if isinstance(value, (bool, int, float)):
            return str(value)
        if isinstance(value, str):
            return value
        if isinstance(value, (list, tuple)):
            return f"(list){list(value)}"
        if isinstance(value, dict):
            items = [f"({k!r}, {v!r})" for k, v in value.items()]
            return f"(dict)[{', '.join(items)}]"
        if isinstance(value, set):
            return f"(set){sorted(value)}"
        # For other types, show type name
        return f"(type){type(value).__name__}"

    def _convert_collection_event(self, event: CollectionEvent) -> Dict[str, Any]:
        """
        Convert CollectionEvent to legacy JSON format.

        Legacy format:
        {
            "id": 4,
            "type": "apd",
            "name": "TestClass.b",
            "line": 38,
            "old": {"type": "list", "len": 3},
            "new": {"type": "list", "len": 4},
            "call_depth": 1
        }

        Args:
            event: The CollectionEvent to convert

        Returns:
            Dict[str, Any]: Legacy format dictionary (without id)
        """
        value_type_name = event.value_type.__name__ if hasattr(event.value_type, '__name__') else str(event.value_type)

        return {
            'type': event.event_type.label.lower(),
            'name': f"{event.class_name}.{event.key}",
            'line': event.lineno,
            'old': {
                'type': value_type_name,
                'len': event.old_value_len,
            },
            'new': {
                'type': value_type_name,
                'len': event.current_value_len,
            },
            'call_depth': event.call_depth,
        }

    def _handle_function_event(self, event: FunctionEvent) -> None:
        """
        Handle function events with proper hierarchy.

        Args:
            event: The original function event
        """
        if event.is_run_event:
            # Convert and add function event to current node
            event_data = self._convert_function_event(event)
            event_data['id'] = self.event_id
            self.event_id += 1
            self.current_node[-1].append(event_data)
            # Push the function's events list to the stack
            self.current_node.append(event_data['events'])
        else:
            # End event: find corresponding run event and update it
            if len(self.current_node) > 1:
                parent_node = self.current_node[-2]
                symbol = event.get_symbol()

                # Find the corresponding function event
                for func_event in reversed(parent_node):
                    if (
                        func_event.get('type') == 'Function'
                        and func_event.get('symbol') == symbol
                        and 'end_line' not in func_event
                    ):
                        func_event['end_line'] = event.lineno
                        if event.return_msg:
                            func_event['return_msg'] = event.return_msg
                        break

                # Pop the function's events list from the stack
                self.current_node.pop()

    def save_json(self) -> None:
        """
        Save the accumulated events to a JSON file.

        Uses compact JSON format to reduce file size.
        """
        if not self.output_json or self.is_json_saved:
            return

        log_info(f"Starting to save JSON to {self.output_json}.")

        try:
            with open(self.output_json, 'w', encoding='utf-8') as f:
                json.dump(
                    self.stack_root, f, ensure_ascii=False, indent=None, separators=(',', ':'), default=target_handler
                )
            log_info(f"JSON saved successfully to {self.output_json}.")
            self.is_json_saved = True
        except Exception as e:
            log_error(f"Failed to save JSON to {self.output_json}: {e}")

    def stop(self) -> None:
        """
        Stop the handler and save any pending data.
        """
        self.save_json()
        # Unregister atexit handler to prevent double-saving
        try:
            atexit.unregister(self.save_json)
        except Exception:
            # Ignore errors when unregistering, as the handler might not be registered
            # This is a defensive programming approach to ensure cleanup doesn't fail
            pass
