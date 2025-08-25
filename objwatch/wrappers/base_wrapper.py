# MIT License
# Copyright (c) 2025 aeeeeeep

from types import FrameType
from typing import Any, Tuple

from .abc_wrapper import ABCWrapper


class BaseWrapper(ABCWrapper):
    """
    BaseWrapper implements the ABCWrapper abstract methods to provide basic logging functionality.
    """

    def wrap_call(self, func_name: str, frame: FrameType) -> str:
        """
        Format the function call information.

        Args:
            func_name (str): Name of the function being called.
            frame (FrameType): The current stack frame.

        Returns:
            str: Formatted call message.
        """
        args, kwargs = self._extract_args_kwargs(frame)
        call_msg = self._format_args_kwargs(args, kwargs)
        return call_msg

    def wrap_return(self, func_name: str, result: Any) -> str:
        """
        Format the function return information.

        Args:
            func_name (str): Name of the function returning.
            result (Any): The result returned by the function.

        Returns:
            str: Formatted return message.
        """
        return_msg = self._format_return(result)
        return return_msg

    def wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]:
        """
        Format the update information of a variable.

        Args:
            old_value (Any): The old value of the variable.
            current_value (Any): The new value of the variable.

        Returns:
            Tuple[str, str]: Formatted old and new values.
        """
        old_msg = self._format_value(old_value)
        current_msg = self._format_value(current_value)
        return old_msg, current_msg
