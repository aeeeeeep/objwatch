from typing import Any, Dict
from .utils.logger import get_logger

logger = get_logger()


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
        logger.debug(f"{rank_info}{prefix}{logger_msg}")

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
        logger.debug(f"{rank_info}{prefix}{logger_msg}")

    @staticmethod
    def handle_upd(class_name: str, key: str, diff_msg: str, call_depth: int, rank_info: str):
        """
        Handles the 'upd' event representing the creation of a new variable.
        """
        logger_msg = f"upd {class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        logger.debug(f"{rank_info}{prefix}{logger_msg}")

    @staticmethod
    def handle_apd(class_name: str, key: str, diff_msg: str, call_depth: int, rank_info: str):
        """
        Handles the 'apd' event denoting the addition of elements to data structures.
        """
        logger_msg = f"apd {class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        logger.debug(f"{rank_info}{prefix}{logger_msg}")

    @staticmethod
    def handle_pop(class_name: str, key: str, diff_msg: str, call_depth: int, rank_info: str):
        """
        Handles the 'pop' event marking the removal of elements from data structures.
        """
        logger_msg = f"pop {class_name}.{key}{diff_msg}"
        prefix = "| " * call_depth
        logger.debug(f"{rank_info}{prefix}{logger_msg}")

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
