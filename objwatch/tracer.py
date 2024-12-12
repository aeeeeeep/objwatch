import sys
import importlib
from weakref import WeakKeyDictionary
from .logger import get_logger

try:
    import torch

    torch_available = True
except ImportError:
    torch_available = False

logger = get_logger()


class Tracer:
    def __init__(self, targets, ranks=None):
        self.targets = self._process_targets(targets)
        self.tracked_objects = WeakKeyDictionary()
        self.torch_available = torch_available
        if self.torch_available:
            self.current_rank = None
            if ranks is None:
                self.ranks = [0]
            else:
                self.ranks = ranks
        else:
            self.ranks = []

    def _process_targets(self, targets):
        processed = set()
        for target in targets:
            if target.endswith('.py'):
                processed.add(target)
            else:
                try:
                    module = importlib.import_module(target)
                    if hasattr(module, '__file__') and module.__file__:
                        processed.add(module.__file__)
                    else:
                        logger.warning(f"Module {target} does not have a __file__ attribute.")
                except ImportError:
                    logger.warning(f"Module {target} could not be imported.")
        logger.debug(f"Processed targets: {processed}")
        return processed

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
                func_name = frame.f_code.co_name
                if 'self' in frame.f_locals:
                    obj = frame.f_locals['self']
                    class_name = obj.__class__.__name__

                    is_method = False
                    method = getattr(obj, func_name, None)
                    if callable(method) and hasattr(method, '__code__') and method.__code__ == frame.f_code:
                        is_method = True

                    if is_method:
                        logger.debug(f"{rank_info}run {class_name}.{func_name}")
                    else:
                        logger.debug(f"{rank_info}run {func_name}")

                    if obj not in self.tracked_objects:
                        attrs = {k: v for k, v in obj.__dict__.items() if not callable(v)}
                        self.tracked_objects[obj] = attrs
                else:
                    logger.debug(f"{rank_info}run {func_name}")

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
                            if old_value != current_value:
                                logger.debug(f"{rank_info}upd {class_name}.{key}")
                                old_attrs[key] = current_value
            return trace_func

        return trace_func

    def start(self):
        logger.info("Starting tracing.")
        sys.settrace(self.trace_func_factory())
        if torch.distributed and torch.distributed.is_initialized():
            torch.distributed.barrier()

    def stop(self):
        logger.info("Stopping tracing.")
        sys.settrace(None)
