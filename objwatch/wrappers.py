from abc import ABC, abstractmethod
from .event_handls import log_element_types, log_sequence_types, EventHandls


class FunctionWrapper(ABC):
    @abstractmethod
    def wrap_call(self, func_name, frame):
        pass

    @abstractmethod
    def wrap_return(self, func_name, result):
        pass

    @abstractmethod
    def wrap_upd(self, old_value, current_value):
        pass

    def _extract_args_kwargs(self, frame):
        args = []
        kwargs = {}
        code = frame.f_code
        arg_names = code.co_varnames[: code.co_argcount]
        for name in arg_names:
            if name in frame.f_locals:
                args.append(frame.f_locals[name])

        if code.co_flags & 0x08:  # CO_VARKEYWORDS
            kwargs = {k: v for k, v in frame.f_locals.items() if k not in arg_names and not k.startswith('_')}
        return args, kwargs

    def _format_args_kwargs(self, args, kwargs):
        formatted_args = [f"'{i}':{self._format_value(arg)}" for i, arg in enumerate(args)]
        formatted_kwargs = [f"'{k}':{self._format_value(v)}" for k, v in kwargs.items()]
        call_msg = ', '.join(filter(None, formatted_args + formatted_kwargs))
        return call_msg

    def _format_value(self, value, is_return=False):
        pass

    def _format_return(self, result):
        return_msg = self._format_value(result, is_return=True)
        return return_msg


class BaseLogger(FunctionWrapper):
    def wrap_call(self, func_name, frame):
        args, kwargs = self._extract_args_kwargs(frame)
        call_msg = self._format_args_kwargs(args, kwargs)
        return call_msg

    def wrap_return(self, func_name, result):
        return_msg = self._format_return(result)
        return return_msg

    def wrap_upd(self, old_value, current_value):
        old_msg = self._format_value(old_value)
        current_msg = self._format_value(current_value)
        return old_msg, current_msg

    def _format_value(self, value, is_return=False):
        if isinstance(value, log_element_types):
            formatted = f"{value}"
        elif isinstance(value, log_sequence_types):
            formatted_sequence = EventHandls.format_sequence(value)
            if formatted_sequence:
                formatted = f"{formatted_sequence}"
            else:
                formatted = f"(type){value.__class__.__name__}"
        else:
            formatted = f"(type){value.__class__.__name__}"

        if is_return:
            if isinstance(value, log_sequence_types) and formatted:
                return f"[{formatted}]"
            return f"{formatted}"
        return formatted


try:
    import torch
except ImportError:
    torch = None


class TensorShapeLogger(FunctionWrapper):
    @staticmethod
    def _process_tensor_item(seq):
        if all(isinstance(x, torch.Tensor) for x in seq):
            return [x.shape for x in seq]
        else:
            return None

    def wrap_call(self, func_name, frame):
        args, kwargs = self._extract_args_kwargs(frame)
        call_msg = self._format_args_kwargs(args, kwargs)
        return call_msg

    def wrap_return(self, func_name, result):
        return_msg = self._format_return(result)
        return return_msg

    def wrap_upd(self, old_value, current_value):
        old_msg = self._format_value(old_value)
        current_msg = self._format_value(current_value)
        return old_msg, current_msg

    def _format_value(self, value, is_return=False):
        if isinstance(value, torch.Tensor):
            formatted = f"{value.shape}"
        elif isinstance(value, log_element_types):
            formatted = f"{value}"
        elif isinstance(value, log_sequence_types):
            formatted_sequence = EventHandls.format_sequence(value, func=TensorShapeLogger._process_tensor_item)
            if formatted_sequence:
                formatted = f"{formatted_sequence}"
            else:
                formatted = f"(type){value.__class__.__name__}"
        else:
            formatted = f"(type){value.__class__.__name__}"

        if is_return:
            if isinstance(value, torch.Tensor):
                return f"{value.shape}"
            elif isinstance(value, log_sequence_types) and formatted:
                return f"[{formatted}]"
            return f"{formatted}"
        return formatted
