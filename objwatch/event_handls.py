from types import NoneType, FunctionType
from typing import Any, Dict
import xml.etree.ElementTree as ET
from .utils.logger import log_debug


log_element_types = (
    bool,
    int,
    float,
    str,
    NoneType,
    FunctionType,
)
log_sequence_types = (list, set, dict)


class EventHandls:
    def __init__(self, output_xml: str = None):
        self.output_xml = output_xml
        if self.output_xml:
            self.stack_root = ET.Element('ObjWatch')
            self.current_node = [self.stack_root]

    def handle_run(self, func_info: Dict[str, Any], function_wrapper: Any, call_depth: int, rank_info: str):
        """
        Handles the 'run' event indicating the start of a function or method execution.
        """
        func_name = func_info['func_name']
        if func_info.get('is_method', False):
            class_name = func_info['class_name']
            logger_msg = f"{class_name}.{func_name}"
        else:
            logger_msg = f"{func_name}"

        if function_wrapper:
            call_msg = function_wrapper.wrap_call(func_name, func_info['frame'])
            logger_msg += call_msg

        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}run {logger_msg}")

        if self.output_xml:
            function_element = ET.Element('Function', attrib={'name': logger_msg})
            self.current_node[-1].append(function_element)
            self.current_node.append(function_element)

    def handle_end(
        self, func_info: Dict[str, Any], function_wrapper: Any, call_depth: int, rank_info: str, result: Any
    ):
        """
        Handles the 'end' event indicating the end of a function or method execution.
        """
        func_name = func_info['func_name']
        if func_info.get('is_method', False):
            class_name = func_info['class_name']
            logger_msg = f"{class_name}.{func_name}"
        else:
            logger_msg = f"{func_name}"

        if function_wrapper:
            return_msg = function_wrapper.wrap_return(func_name, result)
            logger_msg += return_msg

        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}end {logger_msg}")

        if self.output_xml and len(self.current_node) > 1:
            self.current_node.pop()

    def handle_upd(
        self, class_name: str, key: str, old_value: Any, current_value: Any, call_depth: int, rank_info: str
    ):
        """
        Handles the 'upd' event representing the creation of a new variable or updating an existing one.
        """
        if isinstance(old_value, log_element_types):
            old_msg = old_value
        elif isinstance(old_value, log_sequence_types):
            old_msg = EventHandls.format_sequence(old_value)
        else:
            old_msg = old_value.__class__.__name__

        if isinstance(current_value, log_element_types):
            current_msg = current_value
        elif isinstance(current_value, log_sequence_types):
            current_msg = EventHandls.format_sequence(current_value)
        else:
            current_msg = current_value.__class__.__name__

        diff_msg = f" {old_msg} -> {current_msg}"
        logger_msg = f"{class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}upd {logger_msg}")

        if self.output_xml:
            upd_element = ET.Element('upd', attrib={'name': logger_msg})
            self.current_node[-1].append(upd_element)

    def handle_apd(
        self, class_name: str, key: str, old_value: Any, current_value: Any, call_depth: int, rank_info: str
    ):
        """
        Handles the 'apd' event denoting the addition of elements to data structures.
        """
        diff_msg = f" {len(old_value)} -> {len(current_value)}"
        logger_msg = f"{class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}apd {logger_msg}")

        if self.output_xml:
            apd_element = ET.Element('apd', attrib={'name': logger_msg})
            self.current_node[-1].append(apd_element)

    def handle_pop(
        self, class_name: str, key: str, old_value: Any, current_value: Any, call_depth: int, rank_info: str
    ):
        """
        Handles the 'pop' event marking the removal of elements from data structures.
        """
        diff_msg = f" {len(old_value)} -> {len(current_value)}"
        logger_msg = f"{class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}pop {logger_msg}")

        if self.output_xml:
            pop_element = ET.Element('pop', attrib={'name': logger_msg})
            self.current_node[-1].append(pop_element)

    def determine_change_type(self, old_value: Any, current_value: Any) -> str:
        """
        Determines the type of change between old and current values.
        """
        if isinstance(old_value, log_sequence_types) and isinstance(current_value, type(old_value)):
            diff = len(current_value) - len(old_value)
            if diff > 0:
                return "apd"
            elif diff < 0:
                return "pop"
        return "upd"

    @staticmethod
    def format_sequence(seq: Any, max_elements: int = 3, func: FunctionType = None) -> str:
        """
        Formats a sequence to display at most max_elements elements. Extra elements are represented by '...'.
        """
        len_seq = len(seq)
        if len_seq == 0:
            return f'({type(seq).__name__})[]'
        display = None
        if isinstance(seq, list):
            if all(isinstance(x, log_element_types) for x in seq[:max_elements]):
                display = seq[:max_elements]
            elif func is not None:
                display = func(seq[:max_elements])
        elif isinstance(seq, set):
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

    def save_xml(self):
        if self.output_xml:
            tree = ET.ElementTree(self.stack_root)
            tree.write(self.output_xml, encoding='utf-8', xml_declaration=True)
