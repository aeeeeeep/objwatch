# MIT License
# Copyright (c) 2025 aeeeeeep

from abc import ABC, abstractmethod
from types import FrameType
from typing import Any, Dict, List, Tuple


class ABCWrapper(ABC):
    """
    Abstract base class for function wrappers to extend tracing and logging functionality.
    """

    @abstractmethod
    def wrap_call(self, func_name: str, frame: FrameType) -> str:
        """
        Process and format the function call information.

        Args:
            func_name (str): Name of the function being called.
            frame (FrameType): The current stack frame.

        Returns:
            str: Formatted call message.
        """
        pass

    @abstractmethod
    def wrap_return(self, func_name: str, result: Any) -> str:
        """
        Process and format the function return information.

        Args:
            func_name (str): Name of the function returning.
            result (Any): The result returned by the function.

        Returns:
            str: Formatted return message.
        """
        pass

    def wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]:
        """
        Process and format the update information of a variable.

        Args:
            old_value (Any): The old value of the variable.
            current_value (Any): The new value of the variable.

        Returns:
            Tuple[str, str]: Formatted old and new values.
        """
        pass

    def _extract_args_kwargs(self, frame: FrameType) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Extract positional and keyword arguments from the current frame.

        Args:
            frame (FrameType): The current stack frame.

        Returns:
            Tuple[List[Any], Dict[str, Any]]: Lists of positional and keyword arguments.
        """
        args: List[Any] = []
        kwargs: Dict[str, Any] = {}
        code = frame.f_code
        arg_names = code.co_varnames[: code.co_argcount]
        for name in arg_names:
            if name in frame.f_locals:
                args.append(frame.f_locals[name])

        if code.co_flags & 0x08:  # CO_VARKEYWORDS
            kwargs = {k: v for k, v in frame.f_locals.items() if k not in arg_names and not k.startswith('_')}
        return args, kwargs

    def _format_args_kwargs(self, args: List[Any], kwargs: Dict[str, Any]) -> str:
        """
        Format positional and keyword arguments into a string.

        Args:
            args (List[Any]): List of positional arguments.
            kwargs (Dict[str, Any]): Dictionary of keyword arguments.

        Returns:
            str: Formatted arguments string.
        """
        formatted_args = [f"'{i}':{self._format_value(arg)}" for i, arg in enumerate(args)]
        formatted_kwargs = [f"'{k}':{self._format_value(v)}" for k, v in kwargs.items()]
        call_msg = ', '.join(filter(None, formatted_args + formatted_kwargs))
        return call_msg

    def _format_value(self, value: Any, is_return: bool = False) -> str:
        """
        Format a value into a string. To be implemented by subclasses.

        Args:
            value (Any): The value to format.
            is_return (bool): Flag indicating if the value is a return value.

        Returns:
            str: Formatted value string.
        """
        pass

    def _format_return(self, result: Any) -> str:
        """
        Format the return value of a function.

        Args:
            result (Any): The result returned by the function.

        Returns:
            str: Formatted return message.
        """
        return_msg = self._format_value(result, is_return=True)
        return return_msg
