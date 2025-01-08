# MIT License
# Copyright (c) 2025 aeeeeeep

import sys
import pkgutil
import importlib
from types import FunctionType, FrameType
from typing import Any, Dict, List, Optional, Set

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
    """
    Tracer class to monitor and trace function calls, returns, and variable updates
    within specified target modules. Supports multi-GPU environments with PyTorch.
    """

    def __init__(
        self,
        targets: List[str],
        exclude_targets: Optional[List[str]] = None,
        ranks: Optional[List[int]] = None,
        wrapper: Optional[FunctionWrapper] = None,
        output_xml: Optional[str] = None,
        with_locals: bool = False,
        with_module_path: bool = False,
    ) -> None:
        """
        Initialize the Tracer with configuration parameters.

        Args:
            targets (List[str]): Files or modules to monitor.
            exclude_targets (Optional[List[str]]): Files or modules to exclude from monitoring.
            ranks (Optional[List[int]]): GPU ranks to track when using torch.distributed.
            wrapper (Optional[FunctionWrapper]): Custom wrapper to extend tracing and logging functionality.
            output_xml (Optional[str]): Path to the XML file for writing structured logs.
            with_locals (bool): Enable tracing and logging of local variables within functions.
            with_module_path (bool): Prepend the module path to function names in logs.
        """
        self.with_locals: bool = with_locals
        if self.with_locals:
            self.tracked_locals: Dict[FrameType, Dict[str, Any]] = {}
            self.tracked_locals_lens: Dict[FrameType, Dict[str, int]] = {}
        self.with_module_path: bool = with_module_path

        # Process and determine the set of target files to monitor
        self.targets: Set[str] = self._process_targets(targets) - self._process_targets(exclude_targets)
        log_debug(f"Processed targets:\n{'>' * 10}\n" + "\n".join(self.targets) + f"\n{'<' * 10}")

        # Initialize tracking dictionaries for objects
        self.tracked_objects: WeakTensorKeyDictionary = WeakTensorKeyDictionary()
        self.tracked_objects_lens: WeakTensorKeyDictionary = WeakTensorKeyDictionary()

        # Initialize event handlers with optional XML output
        self.event_handlers: EventHandls = EventHandls(output_xml=output_xml)

        # Handle multi-GPU support if PyTorch is available
        self.torch_available: bool = torch_available
        if self.torch_available:
            self.current_rank: Optional[int] = None
            self.ranks: Set[int] = set(ranks if ranks is not None else [0])
        else:
            self.ranks: Set[int] = set()

        # Load the function wrapper if provided
        self.function_wrapper: Optional[FunctionWrapper] = self.load_wrapper(wrapper)
        self.call_depth: int = 0

    def _process_targets(self, targets: Optional[List[str]]) -> Set[str]:
        """
        Process the list of target modules or files to monitor.

        Args:
            targets (Optional[List[str]]): List of target modules or file paths.

        Returns:
            Set[str]: Set of processed file paths to monitor.
        """
        processed: Set[str] = set()
        if isinstance(targets, str):
            targets = [targets]
        elif targets is None:
            return processed
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
        return processed

    def load_wrapper(self, wrapper: Optional[FunctionWrapper]) -> Optional[FunctionWrapper]:
        """
        Load a custom function wrapper if provided.

        Args:
            wrapper (Optional[FunctionWrapper]): The custom wrapper to load.

        Returns:
            Optional[FunctionWrapper]: The initialized wrapper or None.
        """
        if wrapper and issubclass(wrapper, FunctionWrapper):
            log_warn(f"wrapper '{wrapper.__name__}' loaded")
            return wrapper()
        return None

    def _get_function_info(self, frame: FrameType, event: str) -> Dict[str, Any]:
        """
        Extract information about the currently executing function.

        Args:
            frame (FrameType): The current stack frame.
            event (str): The event type (e.g., 'call', 'return').

        Returns:
            Dict[str, Any]: Dictionary containing function information.
        """
        func_info: Dict[str, Any] = {}
        func_name: str = frame.f_code.co_name

        if self.with_module_path:
            module_name: str = frame.f_globals.get('__name__', '')
            if module_name:
                func_name = f"{module_name}.{func_name}"

        func_info['func_name'] = func_name
        func_info['frame'] = frame

        if 'self' in frame.f_locals:
            obj = frame.f_locals['self']
            class_name: str = obj.__class__.__name__
            func_info['is_method'] = False
            method = getattr(obj, func_name, None)
            if callable(method) and hasattr(method, '__code__') and method.__code__ == frame.f_code:
                func_info['is_method'] = True
                func_info['class_name'] = class_name

            if hasattr(obj, '__dict__'):
                attrs: Dict[str, Any] = {k: v for k, v in obj.__dict__.items() if not callable(v)}
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

    def trace_factory(self) -> FunctionType:  # noqa: C901
        """
        Create the tracing function to be used with sys.settrace.

        Returns:
            FunctionType: The trace function.
        """

        def trace_func(frame: FrameType, event: str, arg: Any) -> Optional[FunctionType]:
            if not frame.f_code.co_filename.endswith(tuple(self.targets)):
                return trace_func

            # Handle multi-GPU ranks if PyTorch is available
            rank_info = ""
            if self.torch_available:
                if self.current_rank is None and torch.distributed and torch.distributed.is_initialized():
                    self.current_rank = torch.distributed.get_rank()
                if self.current_rank in self.ranks:
                    rank_info: str = f"[Rank {self.current_rank}] "
                elif self.current_rank is not None and self.current_rank not in self.ranks:
                    return trace_func

            lineno = frame.f_lineno
            if event == "call":
                func_info = self._get_function_info(frame, event)
                self.event_handlers.handle_run(lineno, func_info, self.function_wrapper, self.call_depth, rank_info)
                self.call_depth += 1

                if self.with_locals:
                    local_vars: Dict[str, Any] = {
                        k: v for k, v in frame.f_locals.items() if k != 'self' and not callable(v)
                    }
                    self.tracked_locals[frame] = local_vars
                    self.tracked_locals_lens[frame] = {}
                    for var, value in local_vars.items():
                        if isinstance(value, log_sequence_types):
                            self.tracked_locals_lens[frame][var] = len(value)

                return trace_func

            elif event == "return":
                self.call_depth -= 1
                func_info = self._get_function_info(frame, event)
                self.event_handlers.handle_end(
                    lineno, func_info, self.function_wrapper, self.call_depth, rank_info, arg
                )

                if self.with_locals and frame in self.tracked_locals:
                    del self.tracked_locals[frame]
                    del self.tracked_locals_lens[frame]

                return trace_func

            elif event == "line":
                if 'self' in frame.f_locals:
                    obj = frame.f_locals['self']
                    class_name: str = obj.__class__.__name__

                    if obj in self.tracked_objects:
                        old_attrs: Dict[str, Any] = self.tracked_objects[obj]
                        old_attrs_lens: Dict[str, int] = self.tracked_objects_lens[obj]
                        current_attrs: Dict[str, Any] = {k: v for k, v in obj.__dict__.items() if not callable(v)}

                        for key, current_value in current_attrs.items():
                            old_value = old_attrs.get(key, None)
                            old_value_len = old_attrs_lens.get(key, None)
                            if old_value_len is not None:
                                current_value_len = len(current_value)
                                change_type: EventType = self.event_handlers.determine_change_type(
                                    old_value_len, current_value_len
                                )
                            else:
                                change_type = EventType.UPD

                            if id(old_value) == id(current_value):
                                if change_type == EventType.APD:
                                    self.event_handlers.handle_apd(
                                        lineno,
                                        class_name,
                                        key,
                                        type(current_value),
                                        old_value_len,
                                        current_value_len,
                                        self.call_depth,
                                        rank_info,
                                    )
                                elif change_type == EventType.POP:
                                    self.event_handlers.handle_pop(
                                        lineno,
                                        class_name,
                                        key,
                                        type(current_value),
                                        old_value_len,
                                        current_value_len,
                                        self.call_depth,
                                        rank_info,
                                    )
                            elif change_type == EventType.UPD:
                                self.event_handlers.handle_upd(
                                    lineno,
                                    class_name,
                                    key,
                                    old_value,
                                    current_value,
                                    self.call_depth,
                                    rank_info,
                                    self.function_wrapper,
                                )
                            old_attrs[key] = current_value
                            if isinstance(current_value, log_sequence_types):
                                self.tracked_objects_lens[obj][key] = len(current_value)

                if self.with_locals and frame in self.tracked_locals:
                    old_locals: Dict[str, Any] = self.tracked_locals[frame]
                    current_locals: Dict[str, Any] = {
                        k: v for k, v in frame.f_locals.items() if k != 'self' and not callable(v)
                    }
                    old_locals_lens: Dict[str, int] = self.tracked_locals_lens[frame]

                    added_vars: Set[str] = set(current_locals.keys()) - set(old_locals.keys())
                    for var in added_vars:
                        current_local: Any = current_locals[var]
                        self.event_handlers.handle_upd(
                            lineno,
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

                    common_vars: Set[str] = set(old_locals.keys()) & set(current_locals.keys())
                    for var in common_vars:
                        old_local: Any = old_locals[var]
                        old_local_len: Optional[int] = old_locals_lens.get(var, None)
                        current_local: Any = current_locals[var]
                        if old_local_len is not None and isinstance(current_local, log_sequence_types):
                            current_local_len: int = len(current_local)
                            change_type: EventType = self.event_handlers.determine_change_type(
                                old_local_len, current_local_len
                            )
                        else:
                            change_type = EventType.UPD

                        if id(old_local) == id(current_local):
                            if change_type == EventType.APD:
                                self.event_handlers.handle_apd(
                                    lineno,
                                    "_",
                                    var,
                                    type(current_local),
                                    old_local_len,
                                    current_local_len,
                                    self.call_depth,
                                    rank_info,
                                )
                            elif change_type == EventType.POP:
                                self.event_handlers.handle_pop(
                                    lineno,
                                    "_",
                                    var,
                                    type(current_local),
                                    old_local_len,
                                    current_local_len,
                                    self.call_depth,
                                    rank_info,
                                )
                        elif change_type == EventType.UPD:
                            self.event_handlers.handle_upd(
                                lineno,
                                "_",
                                var,
                                old_local,
                                current_local,
                                self.call_depth,
                                rank_info,
                                self.function_wrapper,
                            )
                        if isinstance(current_local, log_sequence_types):
                            self.tracked_locals_lens[frame][var] = len(current_local)

                    self.tracked_locals[frame] = current_locals

                return trace_func

            return trace_func

        return trace_func

    def start(self) -> None:
        """
        Start the tracing process by setting the trace function.
        """
        log_info("Starting tracing.")
        sys.settrace(self.trace_factory())
        if self.torch_available and torch.distributed and torch.distributed.is_initialized():
            torch.distributed.barrier()

    def stop(self) -> None:
        """
        Stop the tracing process by removing the trace function and saving XML logs.
        """
        log_info("Stopping tracing.")
        sys.settrace(None)
        self.event_handlers.save_xml()
