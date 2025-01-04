import atexit
import xml.etree.ElementTree as ET
from types import NoneType, FunctionType
from typing import Any, Dict
from .utils.logger import log_debug
from .events import EventType

log_element_types = (
    bool,
    int,
    float,
    str,
    NoneType,
    FunctionType,
)
log_sequence_types = (list, set, dict, tuple)


class EventHandls:
    def __init__(self, output_xml: str = None):
        self.output_xml = output_xml
        if self.output_xml:
            self.is_xml_saved = False
            self.stack_root = ET.Element('ObjWatch')
            self.current_node = [self.stack_root]
            atexit.register(self.save_xml)

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
        attrib = {'name': logger_msg}

        if function_wrapper:
            call_msg = function_wrapper.wrap_call(func_name, func_info['frame'])
            attrib['call_msg'] = call_msg
            logger_msg += ' <- ' + call_msg

        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}{EventType.RUN.value} {logger_msg}")

        if self.output_xml:
            function_element = ET.Element('Function', attrib=attrib)
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

        return_msg = ""
        if function_wrapper:
            return_msg = function_wrapper.wrap_return(func_name, result)
            logger_msg += ' -> ' + return_msg

        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}{EventType.END.value} {logger_msg}")

        if self.output_xml and len(self.current_node) > 1:
            self.current_node[-1].set('return_msg', return_msg)
            self.current_node.pop()

    def handle_upd(
        self,
        class_name: str,
        key: str,
        old_value: Any,
        current_value: Any,
        call_depth: int,
        rank_info: str,
        function_wrapper: FunctionType = None,
    ):
        """
        Handles the 'upd' event representing the creation of a new variable or updating an existing one.
        """
        if function_wrapper:
            old_msg, current_msg = function_wrapper.wrap_upd(old_value, current_value)
        else:
            old_msg = self._format_value(old_value)
            current_msg = self._format_value(current_value)

        diff_msg = f" {old_msg} -> {current_msg}"
        logger_msg = f"{class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}{EventType.UPD.value} {logger_msg}")

        if self.output_xml:
            upd_element = ET.Element(
                EventType.UPD.value,
                attrib={'name': f"{class_name}.{key}", 'old': f"{old_msg}", 'new': f"{current_msg}"},
            )
            self.current_node[-1].append(upd_element)

    def handle_apd(
        self,
        class_name: str,
        key: str,
        value_type: type,
        old_value_len: int,
        current_value_len: int,
        call_depth: int,
        rank_info: str,
    ):
        """
        Handles the 'apd' event denoting the addition of elements to data structures.
        """
        diff_msg = f" ({value_type.__name__})(len){old_value_len} -> {current_value_len}"
        logger_msg = f"{class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}{EventType.APD.value} {logger_msg}")

        if self.output_xml:
            apd_element = ET.Element(
                EventType.APD.value,
                attrib={
                    'name': f"{class_name}.{key}",
                    'old': f"({value_type.__name__})(len){old_value_len}",
                    'new': f"({value_type.__name__})(len){current_value_len}",
                },
            )
            self.current_node[-1].append(apd_element)

    def handle_pop(
        self,
        class_name: str,
        key: str,
        value_type: type,
        old_value_len: int,
        current_value_len: int,
        call_depth: int,
        rank_info: str,
    ):
        """
        Handles the 'pop' event marking the removal of elements from data structures.
        """
        diff_msg = f" ({value_type.__name__})(len){old_value_len} -> {current_value_len}"
        logger_msg = f"{class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}{EventType.POP.value} {logger_msg}")

        if self.output_xml:
            pop_element = ET.Element(
                EventType.POP.value,
                attrib={
                    'name': f"{class_name}.{key}",
                    'old': f"({value_type.__name__})(len){old_value_len}",
                    'new': f"({value_type.__name__})(len){current_value_len}",
                },
            )
            self.current_node[-1].append(pop_element)

    def determine_change_type(self, old_value_len: int, current_value_len: int) -> EventType:
        """
        Determines the type of change between old and current values.
        """
        diff = current_value_len - old_value_len
        if diff > 0:
            return EventType.APD
        elif diff < 0:
            return EventType.POP

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
        Helper method to format individual values for the 'upd' event when no wrapper is provided.
        """
        if isinstance(value, log_element_types):
            return f"{value}"
        elif isinstance(value, log_sequence_types):
            return EventHandls.format_sequence(value)
        else:
            return f"(type){value.__class__.__name__}"

    def save_xml(self):
        if self.output_xml and not self.is_xml_saved:
            tree = ET.ElementTree(self.stack_root)
            ET.indent(tree)
            tree.write(self.output_xml, encoding='utf-8', xml_declaration=True)
            self.is_xml_saved = True
