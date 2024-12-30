from types import NoneType, FunctionType
from typing import Any, Dict
from .utils.logger import log_debug


log_types = (
    bool,
    int,
    float,
    NoneType,
    FunctionType,
)


class EventHandls:
    @staticmethod
    def handle_run(func_info: Dict[str, Any], function_wrapper: Any, call_depth: int, rank_info: str):
        """
        Handles the 'run' event indicating the start of a function or method execution.
        """
        func_name = func_info['func_name']
        if func_info.get('is_method', False):
            class_name = func_info['class_name']
            logger_msg = f"run {class_name}.{func_name}"
        else:
            logger_msg = f"run {func_name}"

        if function_wrapper:
            call_msg = function_wrapper.wrap_call(func_name, func_info['frame'])
            logger_msg += call_msg

        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}{logger_msg}")

    @staticmethod
    def handle_end(func_info: Dict[str, Any], function_wrapper: Any, call_depth: int, rank_info: str, result: Any):
        """
        Handles the 'end' event indicating the end of a function or method execution.
        """
        func_name = func_info['func_name']
        if func_info.get('is_method', False):
            class_name = func_info['class_name']
            logger_msg = f"end {class_name}.{func_name}"
        else:
            logger_msg = f"end {func_name}"

        if function_wrapper:
            return_msg = function_wrapper.wrap_return(func_name, result)
            logger_msg += return_msg

        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}{logger_msg}")

    @staticmethod
    def handle_upd(class_name: str, key: str, old_value: Any, current_value: Any, call_depth: int, rank_info: str):
        """
        Handles the 'upd' event representing the creation of a new variable.
        """
        if isinstance(old_value, log_types):
            old_msg = old_value
        else:
            old_msg = getattr(old_value, '__class__')
        if isinstance(current_value, log_types):
            current_msg = current_value
        else:
            current_msg = getattr(current_value, '__class__')
        diff_msg = f" {old_msg} -> {current_msg}"
        logger_msg = f"upd {class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}{logger_msg}")

    @staticmethod
    def handle_apd(class_name: str, key: str, old_value: Any, current_value: Any, call_depth: int, rank_info: str):
        """
        Handles the 'apd' event denoting the addition of elements to data structures.
        """
        diff_msg = f" {len(old_value)} -> {len(current_value)}"
        logger_msg = f"apd {class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}{logger_msg}")

    @staticmethod
    def handle_pop(class_name: str, key: str, old_value: Any, current_value: Any, call_depth: int, rank_info: str):
        """
        Handles the 'pop' event marking the removal of elements from data structures.
        """
        diff_msg = f" {len(old_value)} -> {len(current_value)}"
        logger_msg = f"pop {class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        log_debug(f"{rank_info}{prefix}{logger_msg}")

    @staticmethod
    def determine_change_type(old_value: Any, current_value: Any) -> str:
        """
        Determines the type of change between old and current values.
        """
        if isinstance(old_value, (list, set, dict)) and isinstance(current_value, type(old_value)):
            diff = len(current_value) - len(old_value)
            if diff > 0:
                return "apd"
            elif diff < 0:
                return "pop"
        return "upd"
