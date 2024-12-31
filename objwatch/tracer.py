import sys
import pkgutil
import importlib
from .wrappers import FunctionWrapper
from .event_handls import EventHandls
from .utils.logger import log_info, log_debug, log_warn
from .utils.weak import WeakTensorKeyDictionary

try:
    import torch

    torch_available = True
except ImportError:
    torch_available = False


class Tracer:
    def __init__(self, targets, ranks=None, wrapper=None, output_xml=None, with_locals=False, with_module_path=False):
        self.with_locals = with_locals
        if self.with_locals:
            self.tracked_locals = {}
        self.with_module_path = with_module_path

        self.targets = self._process_targets(targets)
        self.tracked_objects = WeakTensorKeyDictionary()
        self.event_handlers = EventHandls(output_xml=output_xml)
        self.torch_available = torch_available
        if self.torch_available:
            self.current_rank = None
            if ranks is None:
                self.ranks = [0]
            else:
                self.ranks = ranks
        else:
            self.ranks = []

        self.function_wrapper = self.load_wrapper(wrapper)
        self.call_depth = 0

    def _process_targets(self, targets):
        processed = set()
        if isinstance(targets, str):
            targets = [targets]
        for target in targets:
            if target.endswith('.py'):
                processed.add(target)
            else:
                try:
                    module = importlib.import_module(target)
                    if hasattr(module, '__file__') and module.__file__:
                        processed.add(module.__file__)
                        if hasattr(module, '__path__'):
                            for importer, modname, ispkg in pkgutil.walk_packages(
                                module.__path__, module.__name__ + '.'
                            ):
                                try:
                                    submodule = importlib.import_module(modname)
                                    if hasattr(submodule, '__file__') and submodule.__file__:
                                        processed.add(submodule.__file__)
                                except ImportError:
                                    log_warn(f"Submodule {modname} could not be imported.")
                    else:
                        log_warn(f"Module {target} does not have a __file__ attribute.")
                except ImportError:
                    log_warn(f"Module {target} could not be imported.")

        log_debug(f"Processed targets:")
        log_debug(">" * 10)
        for target in processed:
            log_debug(target)
        log_debug("<" * 10)

        return processed

    def load_wrapper(self, wrapper):
        if wrapper and issubclass(wrapper, FunctionWrapper):
            log_warn(f"wrapper '{wrapper.__name__}' loaded")
            return wrapper()

    def _get_function_info(self, frame, event):
        func_info = {}
        func_name = frame.f_code.co_name

        if self.with_module_path:
            module_name = frame.f_globals.get('__name__', '')
            if module_name:
                func_name = f"{module_name}.{func_name}"

        func_info['func_name'] = func_name
        func_info['frame'] = frame

        if 'self' in frame.f_locals:
            obj = frame.f_locals['self']
            class_name = obj.__class__.__name__
            func_info['is_method'] = False
            method = getattr(obj, func_name, None)
            if callable(method) and hasattr(method, '__code__') and method.__code__ == frame.f_code:
                func_info['is_method'] = True
                func_info['class_name'] = class_name

            if obj not in self.tracked_objects and hasattr(obj, '__dict__'):
                attrs = {k: v for k, v in obj.__dict__.items() if not callable(v)}
                self.tracked_objects[obj] = attrs
        else:
            func_info['is_method'] = False

        return func_info

    def trace_func_factory(self):
        def trace_func(frame, event, arg):
            if (
                self.torch_available
                and self.current_rank is None
                and torch.distributed
                and torch.distributed.is_initialized()
            ):
                self.current_rank = torch.distributed.get_rank()
            elif self.torch_available and self.current_rank in self.ranks:
                rank_info = f"[Rank {self.current_rank}] "
            elif self.torch_available and self.current_rank is not None and self.current_rank not in self.ranks:
                return trace_func
            else:
                rank_info = ""

            filename = frame.f_code.co_filename
            if not filename.endswith(tuple(self.targets)):
                return trace_func

            if event == "call":
                func_info = self._get_function_info(frame, event)
                self.event_handlers.handle_run(func_info, self.function_wrapper, self.call_depth, rank_info)
                self.call_depth += 1

                if self.with_locals:
                    local_vars = {k: v for k, v in frame.f_locals.items() if k != 'self' and not callable(v)}
                    self.tracked_locals[frame] = local_vars

                return trace_func

            elif event == "return":
                self.call_depth -= 1
                func_info = self._get_function_info(frame, event)
                self.event_handlers.handle_end(func_info, self.function_wrapper, self.call_depth, rank_info, arg)

                if self.with_locals and frame in self.tracked_locals:
                    del self.tracked_locals[frame]

                return trace_func

            elif event == "line":
                if 'self' in frame.f_locals:
                    obj = frame.f_locals['self']
                    class_name = obj.__class__.__name__

                    if obj in self.tracked_objects:
                        old_attrs = self.tracked_objects[obj]
                        current_attrs = {k: v for k, v in obj.__dict__.items() if not callable(v)}

                        for key, current_value in current_attrs.items():
                            old_value = old_attrs.get(key, None)
                            change_type = self.event_handlers.determine_change_type(old_value, current_value)
                            if id(old_value) == id(current_value):
                                if change_type != "upd":
                                    if change_type == "apd":
                                        self.event_handlers.handle_apd(
                                            class_name, key, old_value, current_value, self.call_depth, rank_info
                                        )
                                    elif change_type == "pop":
                                        self.event_handlers.handle_pop(
                                            class_name, key, old_value, current_value, self.call_depth, rank_info
                                        )
                            else:
                                if change_type == "upd":
                                    self.event_handlers.handle_upd(
                                        class_name, key, old_value, current_value, self.call_depth, rank_info
                                    )
                                old_attrs[key] = current_value

                if self.with_locals and frame in self.tracked_locals:
                    old_locals = self.tracked_locals[frame]
                    current_locals = {k: v for k, v in frame.f_locals.items() if k != 'self' and not callable(v)}

                    added_vars = set(current_locals.keys()) - set(old_locals.keys())
                    for var in added_vars:
                        self.event_handlers.handle_upd(
                            class_name="_",
                            key=var,
                            old_value=None,
                            current_value=current_locals[var],
                            call_depth=self.call_depth,
                            rank_info=rank_info,
                        )

                    common_vars = set(old_locals.keys()) & set(current_locals.keys())
                    for var in common_vars:
                        old_value = old_locals[var]
                        current_value = current_locals[var]
                        change_type = self.event_handlers.determine_change_type(old_value, current_value)
                        if id(old_value) == id(current_value):
                            if change_type != "upd":
                                if change_type == "apd":
                                    self.event_handlers.handle_apd(
                                        "_", var, old_value, current_value, self.call_depth, rank_info
                                    )
                                elif change_type == "pop":
                                    self.event_handlers.handle_pop(
                                        "_", var, old_value, current_value, self.call_depth, rank_info
                                    )
                        else:
                            if change_type == "upd":
                                self.event_handlers.handle_upd(
                                    "_", var, old_value, current_value, self.call_depth, rank_info
                                )

                    self.tracked_locals[frame] = current_locals

                return trace_func

            return trace_func

        return trace_func

    def start(self):
        log_info("Starting tracing.")
        sys.settrace(self.trace_func_factory())
        if self.torch_available and torch.distributed and torch.distributed.is_initialized():
            torch.distributed.barrier()

    def stop(self):
        log_info("Stopping tracing.")
        sys.settrace(None)
        self.event_handlers.save_xml()
