# MIT License
# Copyright (c) 2025 aeeeeeep

import signal
import atexit
import xml.etree.ElementTree as ET
from enum import Enum
from types import FunctionType

try:
    from types import NoneType
except ImportError:
    NoneType = type(None)

from typing import Any, Dict, Optional
from .utils.logger import log_error, log_debug, log_warn, log_info
from .events import EventType


# Define types that are directly loggable
log_element_types = (
    bool,
    int,
    float,
    str,
    NoneType,
    FunctionType,
    Enum,
)

# Define sequence types for logging
log_sequence_types = (list, set, dict, tuple)


class EventHandls:
    """
    Handles various events for ObjWatch, including function execution and variable updates.
    Optionally saves the events in an XML format.
    """

    def __init__(self, output_xml: Optional[str] = None) -> None:
        """
        Initialize the EventHandls with optional XML output configuration.

        Args:
            output_xml (Optional[str]): Path to the XML file for writing structured logs.
        """
        self.output_xml = output_xml
        if self.output_xml:
            self.is_xml_saved: bool = False
            self.stack_root: ET.Element = ET.Element('ObjWatch')
            self.current_node: list = [self.stack_root]
            # Register for normal exit handling
            atexit.register(self.save_xml)
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

    def handle_run(
        self, lineno: int, func_info: Dict[str, Any], abc_wrapper: Optional[Any], call_depth: int, rank_info: str
    ) -> None:
        """
        Handle the 'run' event indicating the start of a function or method execution.

        Args:
            lineno (int): The line number where the event is called.
            func_info (Dict[str, Any]): Information about the function being executed.
            abc_wrapper (Optional[Any]): Custom wrapper for additional processing.
            call_depth (int): Current depth of the call stack.
            rank_info (str): Information about the GPU rank, if applicable.
        """
        func_name = func_info['func_name']
        if func_info.get('is_method', False):
            class_name = func_info['class_name']
            logger_msg = f"{class_name}.{func_name}"
        else:
            logger_msg = f"{func_name}"
        attrib = {'name': logger_msg, 'run_line': str(lineno)}

        if abc_wrapper:
            call_msg = abc_wrapper.wrap_call(func_name, func_info['frame'])
            attrib['call_msg'] = call_msg
            logger_msg += ' <- ' + call_msg

        prefix = f"{lineno:>5} " + "| " * call_depth
        log_debug(f"{rank_info}{prefix}{EventType.RUN.label} {logger_msg}")

        if self.output_xml:
            function_element = ET.Element('Function', attrib=attrib)
            self.current_node[-1].append(function_element)
            self.current_node.append(function_element)

    def handle_end(
        self,
        lineno: int,
        func_info: Dict[str, Any],
        abc_wrapper: Optional[Any],
        call_depth: int,
        rank_info: str,
        result: Any,
    ) -> None:
        """
        Handle the 'end' event indicating the end of a function or method execution.

        Args:
            lineno (int): The line number where the event is called.
            func_info (Dict[str, Any]): Information about the function that has ended.
            abc_wrapper (Optional[Any]): Custom wrapper for additional processing.
            call_depth (int): Current depth of the call stack.
            rank_info (str): Information about the GPU rank, if applicable.
            result (Any): The result returned by the function.
        """
        func_name = func_info['func_name']
        if func_info.get('is_method', False):
            class_name = func_info['class_name']
            logger_msg = f"{class_name}.{func_name}"
        else:
            logger_msg = f"{func_name}"

        return_msg = ""
        if abc_wrapper:
            return_msg = abc_wrapper.wrap_return(func_name, result)
            logger_msg += ' -> ' + return_msg

        prefix = f"{lineno:>5} " + "| " * call_depth
        log_debug(f"{rank_info}{prefix}{EventType.END.label} {logger_msg}")

        if self.output_xml and len(self.current_node) > 1:
            self.current_node[-1].set('return_msg', return_msg)
            self.current_node[-1].set('end_line', str(lineno))
            self.current_node.pop()

    def handle_upd(
        self,
        lineno: int,
        class_name: str,
        key: str,
        old_value: Any,
        current_value: Any,
        call_depth: int,
        rank_info: str,
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
            rank_info (str): Information about the GPU rank, if applicable.
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
        prefix = f"{lineno:>5} " + "| " * call_depth
        log_debug(f"{rank_info}{prefix}{EventType.UPD.label} {logger_msg}")

        if self.output_xml:
            upd_element = ET.Element(
                EventType.UPD.label,
                attrib={
                    'name': f"{class_name}.{key}",
                    'line': str(lineno),
                    'old': f"{old_msg}",
                    'new': f"{current_msg}",
                },
            )
            self.current_node[-1].append(upd_element)

    def handle_apd(
        self,
        lineno: int,
        class_name: str,
        key: str,
        value_type: type,
        old_value_len: int,
        current_value_len: int,
        call_depth: int,
        rank_info: str,
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
            rank_info (str): Information about the GPU rank, if applicable.
        """
        diff_msg = f" ({value_type.__name__})(len){old_value_len} -> {current_value_len}"
        logger_msg = f"{class_name}.{key}{diff_msg}"
        prefix = f"{lineno:>5} " + "| " * call_depth
        log_debug(f"{rank_info}{prefix}{EventType.APD.label} {logger_msg}")

        if self.output_xml:
            apd_element = ET.Element(
                EventType.APD.label,
                attrib={
                    'name': f"{class_name}.{key}",
                    'line': str(lineno),
                    'old': f"({value_type.__name__})(len){old_value_len}",
                    'new': f"({value_type.__name__})(len){current_value_len}",
                },
            )
            self.current_node[-1].append(apd_element)

    def handle_pop(
        self,
        lineno: int,
        class_name: str,
        key: str,
        value_type: type,
        old_value_len: int,
        current_value_len: int,
        call_depth: int,
        rank_info: str,
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
            rank_info (str): Information about the GPU rank, if applicable.
        """
        diff_msg = f" ({value_type.__name__})(len){old_value_len} -> {current_value_len}"
        logger_msg = f"{class_name}.{key}{diff_msg}"
        prefix = f"{lineno:>5} " + "| " * call_depth
        log_debug(f"{rank_info}{prefix}{EventType.POP.label} {logger_msg}")

        if self.output_xml:
            pop_element = ET.Element(
                EventType.POP.label,
                attrib={
                    'name': f"{class_name}.{key}",
                    'line': str(lineno),
                    'old': f"({value_type.__name__})(len){old_value_len}",
                    'new': f"({value_type.__name__})(len){current_value_len}",
                },
            )
            self.current_node[-1].append(pop_element)

    def determine_change_type(self, old_value_len: int, current_value_len: int) -> EventType:
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

    @staticmethod
    def format_sequence(seq: Any, max_elements: int = 3, func: Optional[FunctionType] = None) -> str:
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
            if all(isinstance(x, log_element_types) for x in seq[:max_elements]):
                display = seq[:max_elements]
            elif func is not None:
                display = func(seq[:max_elements])
        elif isinstance(seq, (set, tuple)):
            seq_list = list(seq)[:max_elements]
            if all(isinstance(x, log_element_types) for x in seq_list):
                display = seq_list
            elif func is not None:
                display = func(seq_list)
        elif isinstance(seq, dict):
            seq_keys = list(seq.keys())[:max_elements]
            seq_values = list(seq.values())[:max_elements]
            if all(isinstance(x, log_element_types) for x in seq_keys) and all(
                isinstance(x, log_element_types) for x in seq_values
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
        if isinstance(value, log_element_types):
            return f"{value}"
        elif isinstance(value, log_sequence_types):
            return EventHandls.format_sequence(value)
        else:
            return f"(type){value.__class__.__name__}"

    def save_xml(self) -> None:
        """
        Save the accumulated events to an XML file upon program exit.
        """
        if self.output_xml and not self.is_xml_saved:
            log_info("Starting XML formatting.")
            tree = ET.ElementTree(self.stack_root)
            if hasattr(ET, 'indent'):
                ET.indent(tree)
            else:
                log_warn(
                    "Current Python version not support `xml.etree.ElementTree.indent`. XML formatting is skipped."
                )

            log_info(f"Starting to save XML to {self.output_xml}.")
            tree.write(self.output_xml, encoding='utf-8', xml_declaration=True)
            log_info(f"XML saved successfully to {self.output_xml}.")

            self.is_xml_saved = True

    def signal_handler(self, signum, frame):
        """
        Signal handler for abnormal program termination.
        Calls save_xml when a termination signal is received.

        Args:
            signum (int): The signal number.
            frame (frame): The current stack frame.
        """
        if not self.is_xml_saved:
            log_error(f"Received signal {signum}, saving XML before exiting.")
            self.save_xml()
            exit(1)  # Ensure the program exits after handling the signal
