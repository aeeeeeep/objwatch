import sys
import pkgutil
import importlib
from .wrappers import FunctionWrapper
from .events import EventType
from .event_handls import EventHandls, log_sequence_types
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
            self.tracked_locals_lens = {}
        self.with_module_path = with_module_path

        self.targets = self._process_targets(targets)
        self.tracked_objects = WeakTensorKeyDictionary()
        self.tracked_objects_lens = WeakTensorKeyDictionary()
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

            if hasattr(obj, '__dict__'):
                attrs = {k: v for k, v in obj.__dict__.items() if not callable(v)}
                if obj not in self.tracked_objects:
                    self.tracked_objects[obj] = attrs
                if obj not in self.tracked_objects_lens:
                    self.tracked_objects_lens[obj] = {}
                for k, v in attrs.items():
                    if isinstance(v, log_sequence_types):
                        self.tracked_objects_lens[obj][k] = len(v)
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
            if self.torch_available and self.current_rank in self.ranks:
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
                    self.tracked_locals_lens[frame] = {}
                    for var, value in local_vars.items():
                        if isinstance(value, log_sequence_types):
                            self.tracked_locals_lens[frame][var] = len(value)

                return trace_func

            elif event == "return":
                self.call_depth -= 1
                func_info = self._get_function_info(frame, event)
                self.event_handlers.handle_end(func_info, self.function_wrapper, self.call_depth, rank_info, arg)

                if self.with_locals and frame in self.tracked_locals:
                    del self.tracked_locals[frame]
                    del self.tracked_locals_lens[frame]

                return trace_func

            elif event == "line":
                if 'self' in frame.f_locals:
                    obj = frame.f_locals['self']
                    class_name = obj.__class__.__name__

                    if obj in self.tracked_objects:
                        old_attrs = self.tracked_objects[obj]
                        old_attrs_lens = self.tracked_objects_lens[obj]
                        current_attrs = {k: v for k, v in obj.__dict__.items() if not callable(v)}

                        for key, current_value in current_attrs.items():
                            old_value = old_attrs.get(key, None)
                            old_value_len = old_attrs_lens.get(key, None)
                            if old_value_len is not None:
                                current_value_len = len(current_value)
                                change_type = self.event_handlers.determine_change_type(
                                    old_value_len, current_value_len
                                )
                            else:
                                change_type = EventType.UPD

                            if id(old_value) == id(current_value) and change_type == EventType.APD:
                                self.event_handlers.handle_apd(
                                    class_name,
                                    key,
                                    type(current_value),
                                    old_value_len,
                                    current_value_len,
                                    self.call_depth,
                                    rank_info,
                                )
                            elif id(old_value) == id(current_value) and change_type == EventType.POP:
                                self.event_handlers.handle_pop(
                                    class_name,
                                    key,
                                    type(current_value),
                                    old_value_len,
                                    current_value_len,
                                    self.call_depth,
                                    rank_info,
                                )
                            elif id(old_value) != id(current_value) and change_type == EventType.UPD:
                                self.event_handlers.handle_upd(
                                    class_name, key, old_value, current_value, self.call_depth, rank_info, self.function_wrapper
                                )
                            old_attrs[key] = current_value
                            if isinstance(current_value, log_sequence_types):
                                self.tracked_objects_lens[obj][key] = len(current_value)

                if self.with_locals and frame in self.tracked_locals:
                    old_locals = self.tracked_locals[frame]
                    current_locals = {k: v for k, v in frame.f_locals.items() if k != 'self' and not callable(v)}
                    old_locals_lens = self.tracked_locals_lens[frame]

                    added_vars = set(current_locals.keys()) - set(old_locals.keys())
                    for var in added_vars:
                        current_local = current_locals[var]
                        self.event_handlers.handle_upd(
                            class_name="_",
                            key=var,
                            old_value=None,
                            current_value=current_local,
                            call_depth=self.call_depth,
                            rank_info=rank_info,
                            function_wrapper=self.function_wrapper,
                        )
                        if isinstance(current_local, log_sequence_types):
                            self.tracked_locals_lens[frame][var] = len(current_local)

                    common_vars = set(old_locals.keys()) & set(current_locals.keys())
                    for var in common_vars:
                        old_local = old_locals[var]
                        old_local_len = old_locals_lens.get(var, None)
                        current_local = current_locals[var]
                        if old_local_len is not None and isinstance(current_local, log_sequence_types):
                            current_local_len = len(current_local)
                            change_type = self.event_handlers.determine_change_type(old_local_len, current_local_len)
                        else:
                            change_type = EventType.UPD

                        if id(old_local) == id(current_local) and change_type == EventType.APD:
                            self.event_handlers.handle_apd(
                                "_",
                                var,
                                type(current_local),
                                old_local_len,
                                current_local_len,
                                self.call_depth,
                                rank_info,
                            )
                        elif id(old_local) == id(current_local) and change_type == EventType.POP:
                            self.event_handlers.handle_pop(
                                "_",
                                var,
                                type(current_local),
                                old_local_len,
                                current_local_len,
                                self.call_depth,
                                rank_info,
                            )
                        elif id(old_local) != id(current_local) and change_type == EventType.UPD:
                            self.event_handlers.handle_upd(
                                "_", var, old_local, current_local, self.call_depth, rank_info, self.function_wrapper
                            )
                        if isinstance(current_local, log_sequence_types):
                            self.tracked_locals_lens[frame][var] = len(current_local)

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
