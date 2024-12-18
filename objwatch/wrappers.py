from abc import ABC, abstractmethod


class FunctionWrapper(ABC):
    @abstractmethod
    def wrap_call(self, func_name, frame):
        pass

    @abstractmethod
    def wrap_return(self, func_name, result):
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
        call_msg = ' <- '
        formatted_args = [self._format_value(i, arg) for i, arg in enumerate(args)]
        formatted_kwargs = [self._format_value(k, v) for k, v in kwargs.items()]
        call_msg += ', '.join(filter(None, formatted_args + formatted_kwargs))
        return call_msg

    def _format_value(self, key, value):
        pass

    def _format_return(self, result):
        return_msg = ' -> ' + self._format_value('result', result, is_return=True)
        return return_msg


class BaseLogger(FunctionWrapper):
    def wrap_call(self, func_name, frame):
        args, kwargs = self._extract_args_kwargs(frame)
        call_msg = self._format_args_kwargs(args, kwargs)
        return call_msg

    def wrap_return(self, func_name, result):
        return_msg = self._format_return(result)
        return return_msg

    def _format_value(self, key, value, is_return=False):
        if isinstance(value, (bool, int, float)):
            formatted = f"'{key}':{value}"
        elif isinstance(value, list):
            formatted = self._format_list(key, value)
        else:
            formatted = ''

        if is_return:
            if isinstance(value, list):
                return f"[{formatted}]"
            return f"{formatted}"
        return formatted

    def _format_list(self, key, lst):
        if len(lst) == 0:
            return f"'{key}':[]"
        elif isinstance(lst[0], (bool, int, float)):
            numel = len(lst)
            display_elm = lst[:3] if numel > 3 else lst
            elm_values = ', '.join([f"value_{j}:{element}" for j, element in enumerate(display_elm)])
            if numel > 3:
                elm_values += f"...({numel - 3} more elements)"
            return f"'{key}':[{elm_values}]"
        return ''


try:
    import torch
except ImportError:
    torch = None


class TensorShapeLogger(FunctionWrapper):
    def wrap_call(self, func_name, frame):
        args, kwargs = self._extract_args_kwargs(frame)
        call_msg = self._format_args_kwargs(args, kwargs)
        return call_msg

    def wrap_return(self, func_name, result):
        return_msg = self._format_return(result)
        return return_msg

    def _format_value(self, key, value, is_return=False):
        if isinstance(value, torch.Tensor):
            formatted = f"'{key}':{value.shape}"
        elif isinstance(value, (bool, int, float)):
            formatted = f"'{key}':{value}"
        elif isinstance(value, list):
            formatted = self._format_list(key, value)
        else:
            formatted = ''

        if is_return:
            if isinstance(value, torch.Tensor):
                return f"{value.shape}"
            elif isinstance(value, list):
                return f"[{formatted}]"
            return f"{formatted}"
        return formatted

    def _format_list(self, key, lst):
        if len(lst) == 0:
            return f"'{key}':[]"
        elif isinstance(lst[0], torch.Tensor):
            num_tensors = len(lst)
            display_tensors = lst[:3] if num_tensors > 3 else lst
            tensor_shapes = ', '.join([f"tensor_{j}:{tensor.shape}" for j, tensor in enumerate(display_tensors)])
            if num_tensors > 3:
                tensor_shapes += f"...({num_tensors - 3} more tensors)"
            return f"'{key}':[{tensor_shapes}]"
        elif isinstance(lst[0], (bool, int, float)):
            # 复用 BaseLogger 的列表格式化
            base_logger = BaseLogger()
            return base_logger._format_list(key, lst)
        return ''
