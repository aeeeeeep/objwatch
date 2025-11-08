# MIT License
# Copyright (c) 2025 aeeeeeep

import sys
import json
import signal
import atexit
from functools import lru_cache
from types import FunctionType
from typing import Any, Optional, Dict, List

from .config import ObjWatchConfig
from .constants import Constants
from .events import EventType
from .utils.util import target_handler
from .utils.logger import log_error, log_debug, log_info
from .runtime_info import runtime_info


class EventHandls:
    """
    Handles various events for ObjWatch, including function execution and variable updates.
    Optionally saves the events in a JSON format.
    """

    def __init__(self, config: ObjWatchConfig) -> None:
        """
        Initialize the EventHandls with optional JSON output.

        Args:
            config (ObjWatchConfig): The configuration object to include in the JSON output.
        """
        self.config = config
        self.output_json = self.config.output_json
        if self.output_json:
            self.is_json_saved: bool = False
            # JSON structure with runtime info, config and events stack
            self.stack_root: Dict[str, Any] = {
                'ObjWatch': {
                    'runtime_info': runtime_info.get_info_dict(),
                    'config': config.to_dict(),
                    'events': [],
                }
            }
            self.current_node: List[Any] = [self.stack_root['ObjWatch']['events']]
            # Register for normal exit handling
            atexit.register(self.save_json)
            # Register signal handlers for abnormal exits
            signal_types = [
                signal.SIGTERM,  # Termination signal (default)
                signal.SIGINT,  # Interrupt from keyboard (Ctrl + C)
                signal.SIGABRT,  # Abort signal from program (e.g., abort() call)
                signal.SIGHUP,  # Hangup signal (usually for daemon processes)
                signal.SIGQUIT,  # Quit signal (generates core dump)
                signal.SIGUSR1,  # User-defined signal 1
                signal.SIGUSR2,  # User-defined signal 2
                signal.SIGALRM,  # Alarm signal (usually for timers)
                signal.SIGSEGV,  # Segmentation fault (access violation)
            ]
            for signal_type in signal_types:
                signal.signal(signal_type, self.signal_handler)

    @staticmethod
    @lru_cache(maxsize=sys.maxsize)
    def _generate_prefix(lineno: int, call_depth: int) -> str:
        """
        Generate a formatted prefix for logging with caching.

        Args:
            lineno (int): The line number where the event occurred.
            call_depth (int): Current depth of the call stack.

        Returns:
            str: The formatted prefix string.
        """
        return f"{lineno:>5} " + "| " * call_depth

    def _log_event(self, lineno: int, event_type: EventType, message: str, call_depth: int, index_info: str) -> None:
        """
        Log an event with consistent formatting.

        Args:
            lineno (int): The line number where the event occurred.
            event_type (EventType): The type of event.
            message (str): The message to log.
            call_depth (int): Current depth of the call stack.
            index_info (str): Information about the index to track in a multi-process environment.
        """
        prefix = self._generate_prefix(lineno, call_depth)
        log_debug(f"{index_info}{prefix}{event_type.label} {message}")

    def _add_json_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a JSON event object with the given data and add it to the current node.

        Args:
            event_type (str): Type of the event to create.
            data (dict): Dictionary of data to include in the event.

        Returns:
            dict: The created event dictionary.
        """
        event = {'type': event_type, **data}
        self.current_node[-1].append(event)
        return event

    def _handle_collection_change(
        self,
        lineno: int,
        class_name: str,
        key: str,
        value_type: type,
        old_value_len: Optional[int],
        current_value_len: Optional[int],
        call_depth: int,
        index_info: str,
        event_type: EventType,
    ) -> None:
        """
        Handle collection change events (APD or POP) with a common implementation.

        Args:
            lineno (int): The line number where the event is called.
            class_name (str): Name of the class containing the data structure.
            key (str): Name of the data structure.
            value_type (type): Type of the elements.
            old_value_len (int): Previous length of the data structure.
            current_value_len (int): New length of the data structure.
            call_depth (int): Current depth of the call stack.
            index_info (str): Information about the index to track in a multi-process environment.
            event_type (EventType): The type of event (APD or POP).
        """
        diff_msg = f" ({value_type.__name__})(len){old_value_len} -> {current_value_len}"
        logger_msg = f"{class_name}.{key}{diff_msg}"

        self._log_event(lineno, event_type, logger_msg, call_depth, index_info)

        if self.output_json:
            self._add_json_event(
                event_type.label,
                {
                    'name': f"{class_name}.{key}",
                    'line': lineno,
                    'old': {'type': value_type.__name__, 'len': old_value_len},
                    'new': {'type': value_type.__name__, 'len': current_value_len},
                    'call_depth': call_depth,
                },
            )

    def handle_run(
        self, lineno: int, func_info: dict, abc_wrapper: Optional[Any], call_depth: int, index_info: str
    ) -> None:
        """
        Handle the 'run' event indicating the start of a function or method execution.
        """
        logger_msg = func_info['qualified_name']

        func_data = {
            'module': func_info['module'],
            'symbol': func_info['symbol'],
            'symbol_type': func_info['symbol_type'] or 'function',
            'run_line': lineno,
            'qualified_name': func_info['qualified_name'],
            'events': [],
        }

        if abc_wrapper:
            call_msg = abc_wrapper.wrap_call(func_info['symbol'], func_info.get('frame'))
            func_data['call_msg'] = call_msg
            logger_msg += ' <- ' + call_msg

        self._log_event(lineno, EventType.RUN, logger_msg, call_depth, index_info)

        if self.output_json:
            function_event = self._add_json_event('Function', func_data)
            # Push the function's events list to the stack to maintain hierarchy
            self.current_node.append(function_event['events'])

    def handle_end(
        self,
        lineno: int,
        func_info: dict,
        abc_wrapper: Optional[Any],
        call_depth: int,
        index_info: str,
        result: Any,
    ) -> None:
        """
        Handle the 'end' event indicating the end of a function or method execution.
        """
        logger_msg = func_info['qualified_name']
        return_msg = ""

        if abc_wrapper:
            return_msg = abc_wrapper.wrap_return(func_info['symbol'], result)
            logger_msg += ' -> ' + return_msg

        self._log_event(lineno, EventType.END, logger_msg, call_depth, index_info)

        if self.output_json and len(self.current_node) > 1:
            # Find the corresponding function event in the parent node
            parent_node = self.current_node[-2]
            # Assuming the last event in the parent node is the current function
            for event in reversed(parent_node):
                if event.get('type') == 'Function' and event.get('symbol') == func_info['symbol']:
                    event['return_msg'] = return_msg
                    event['end_line'] = lineno
                    break
            # Pop the function's events list from the stack
            self.current_node.pop()

    def handle_upd(
        self,
        lineno: int,
        class_name: str,
        key: str,
        old_value: Any,
        current_value: Any,
        call_depth: int,
        index_info: str,
        abc_wrapper: Optional[Any] = None,
    ) -> None:
        """
        Handle the 'upd' event representing the creation or updating of a variable.

        Args:
            lineno (int): The line number where the event is called.
            class_name (str): Name of the class containing the variable.
            key (str): Variable name.
            old_value (Any): Previous value of the variable.
            current_value (Any): New value of the variable.
            call_depth (int): Current depth of the call stack.
            index_info (str): Information about the index to track in a multi-process environment.
            abc_wrapper (Optional[Any]): Custom wrapper for additional processing.
        """
        if abc_wrapper:
            upd_msg = abc_wrapper.wrap_upd(old_value, current_value)
            if upd_msg is not None:
                old_msg, current_msg = upd_msg
        else:
            old_msg = self._format_value(old_value)
            current_msg = self._format_value(current_value)

        diff_msg = f" {old_msg} -> {current_msg}"
        logger_msg = f"{class_name}.{key}{diff_msg}"

        self._log_event(lineno, EventType.UPD, logger_msg, call_depth, index_info)

        if self.output_json:
            self._add_json_event(
                EventType.UPD.label,
                {
                    'name': f"{class_name}.{key}",
                    'line': lineno,
                    'old': old_msg,
                    'new': current_msg,
                    'call_depth': call_depth,
                },
            )

    def handle_apd(
        self,
        lineno: int,
        class_name: str,
        key: str,
        value_type: type,
        old_value_len: Optional[int],
        current_value_len: Optional[int],
        call_depth: int,
        index_info: str,
    ) -> None:
        """
        Handle the 'apd' event denoting the addition of elements to data structures.

        Args:
            lineno (int): The line number where the event is called.
            class_name (str): Name of the class containing the data structure.
            key (str): Name of the data structure.
            value_type (type): Type of the elements being added.
            old_value_len (int): Previous length of the data structure.
            current_value_len (int): New length of the data structure.
            call_depth (int): Current depth of the call stack.
            index_info (str): Information about the index to track in a multi-process environment.
        """
        self._handle_collection_change(
            lineno, class_name, key, value_type, old_value_len, current_value_len, call_depth, index_info, EventType.APD
        )

    def handle_pop(
        self,
        lineno: int,
        class_name: str,
        key: str,
        value_type: type,
        old_value_len: Optional[int],
        current_value_len: Optional[int],
        call_depth: int,
        index_info: str,
    ) -> None:
        """
        Handle the 'pop' event marking the removal of elements from data structures.

        Args:
            lineno (int): The line number where the event is called.
            class_name (str): Name of the class containing the data structure.
            key (str): Name of the data structure.
            value_type (type): Type of the elements being removed.
            old_value_len (int): Previous length of the data structure.
            current_value_len (int): New length of the data structure.
            call_depth (int): Current depth of the call stack.
            index_info (str): Information about the index to track in a multi-process environment.
        """
        self._handle_collection_change(
            lineno, class_name, key, value_type, old_value_len, current_value_len, call_depth, index_info, EventType.POP
        )

    def determine_change_type(self, old_value_len: int, current_value_len: int) -> Optional[EventType]:
        """
        Determine the type of change based on the difference in lengths.

        Args:
            old_value_len (int): Previous length of the data structure.
            current_value_len (int): New length of the data structure.

        Returns:
            EventType: The determined event type (APD or POP).
        """
        diff = current_value_len - old_value_len
        if diff > 0:
            return EventType.APD
        elif diff < 0:
            return EventType.POP
        return None

    @staticmethod
    def format_sequence(
        seq: Any, max_elements: int = Constants.MAX_SEQUENCE_ELEMENTS, func: Optional[FunctionType] = None
    ) -> str:
        """
        Format a sequence to display a limited number of elements.

        Args:
            seq (Any): The sequence to format.
            max_elements (int): Maximum number of elements to display.
            func (Optional[FunctionType]): Optional function to process elements.

        Returns:
            str: The formatted sequence string.
        """
        len_seq = len(seq)
        if len_seq == 0:
            return f'({type(seq).__name__})[]'
        display: Optional[list] = None
        if isinstance(seq, list):
            if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq[:max_elements]):
                display = seq[:max_elements]
            elif func is not None:
                display = func(seq[:max_elements])
        elif isinstance(seq, (set, tuple)):
            seq_list = list(seq)[:max_elements]
            if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_list):
                display = seq_list
            elif func is not None:
                display = func(seq_list)
        elif isinstance(seq, dict):
            seq_keys = list(seq.keys())[:max_elements]
            seq_values = list(seq.values())[:max_elements]
            if all(isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_keys) and all(
                isinstance(x, Constants.LOG_ELEMENT_TYPES) for x in seq_values
            ):
                display = list(seq.items())[:max_elements]
            elif func is not None:
                display_values = func(seq_values)
                if display_values:
                    display = []
                    for k, v in zip(seq_keys, display_values):
                        display.append((k, v))

        if display is not None:
            if len_seq > max_elements:
                remaining = len_seq - max_elements
                display.append(f"... ({remaining} more elements)")
            return f'({type(seq).__name__})' + str(display)
        else:
            return f"({type(seq).__name__})[{len(seq)} elements]"

    @staticmethod
    def _format_value(value: Any) -> str:
        """
        Format individual values for the 'upd' event when no wrapper is provided.

        Args:
            value (Any): The value to format.

        Returns:
            str: The formatted value string.
        """
        if isinstance(value, Constants.LOG_ELEMENT_TYPES):
            return f"{value}"
        elif isinstance(value, Constants.LOG_SEQUENCE_TYPES):
            return EventHandls.format_sequence(value)
        else:
            try:
                return f"(type){value.__name__}"
            except Exception:
                return f"(type){type(value).__name__}"

    def save_json(self) -> None:
        """
        Save the accumulated events to a JSON file upon program exit with optimized size.
        """
        if self.output_json and not self.is_json_saved:
            log_info(f"Starting to save JSON to {self.output_json}.")
            # Use compact JSON format to reduce file size
            with open(self.output_json, 'w', encoding='utf-8') as f:
                json.dump(
                    self.stack_root, f, ensure_ascii=False, indent=None, separators=(',', ':'), default=target_handler
                )
            log_info(f"JSON saved successfully to {self.output_json}.")

            self.is_json_saved = True

    def signal_handler(self, signum, frame):
        """
        Signal handler for abnormal program termination.
        Calls save_json when a termination signal is received.

        Args:
            signum (int): The signal number.
            frame (frame): The current stack frame.
        """
        if not self.is_json_saved:
            log_error(f"Received signal {signum}, saving JSON before exiting.")
            self.save_json()
            exit(1)  # Ensure the program exits after handling the signal
