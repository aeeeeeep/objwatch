# MIT License
# Copyright (c) 2025 aeeeeeep

import sys
import pkgutil
import importlib
from functools import lru_cache
from types import FunctionType, FrameType, ModuleType
from typing import Optional, Union, Any, Dict, List, Set

from .wrappers import ABCWrapper
from .events import EventType
from .event_handls import EventHandls, log_sequence_types
from .utils.logger import log_error, log_debug, log_warn, log_info
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
        targets: List[Union[str, ModuleType]],
        exclude_targets: Optional[List[str]] = None,
        ranks: Optional[List[int]] = None,
        wrapper: Optional[ABCWrapper] = None,
        output_xml: Optional[str] = None,
        with_locals: bool = False,
        with_globals: bool = False,
        with_module_path: bool = False,
    ) -> None:
        """
        Initialize the Tracer with configuration parameters.

        Args:
            targets (List[str]): Files or modules to monitor.
            exclude_targets (Optional[List[str]]): Files or modules to exclude from monitoring.
            ranks (Optional[List[int]]): GPU ranks to track when using torch.distributed.
            wrapper (Optional[ABCWrapper]): Custom wrapper to extend tracing and logging functionality.
            output_xml (Optional[str]): Path to the XML file for writing structured logs.
            with_locals (bool): Enable tracing and logging of local variables within functions.
            with_globals (bool): Enable tracing and logging of global variables across function calls.
            with_module_path (bool): Prepend the module path to function names in logs.
        """
        self.with_locals: bool = with_locals
        if self.with_locals:
            self.tracked_locals: Dict[FrameType, Dict[str, Any]] = {}
            self.tracked_locals_lens: Dict[FrameType, Dict[str, int]] = {}

        self.with_globals: bool = with_globals
        if self.with_globals:
            self.tracked_globals: Dict[FrameType, Dict[str, Any]] = {}
            self.tracked_globals_lens: Dict[FrameType, Dict[str, int]] = {}
            # List of Python built-in fields to exclude from tracking
            self.builtin_fields = set(dir(__builtins__)) | {
                'self',
                '__builtins__',
                '__name__',
                '__package__',
                '__loader__',
                '__spec__',
                '__file__',
                '__cached__',
            }

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
        self.rank_info: str = ""
        if self.torch_available:
            self.current_rank = None
            self.ranks: Set[int] = set(ranks if ranks is not None else [0])
        else:
            self.ranks: Set[int] = set()

        # Load the function wrapper if provided
        self.abc_wrapper: ABCWrapper = self.load_wrapper(wrapper)
        self.call_depth: int = 0

    def _process_targets(self, targets: Optional[List[Union[str, ModuleType]]]) -> Set[str]:
        """
        Process the list of target modules or files to monitor.

        Args:
            targets (Optional[List[Union[str, ModuleType]]): List of target modules or file paths.

        Returns:
            Set[str]: Set of processed file paths to monitor.
        """
        processed: Set[str] = set()
        if isinstance(targets, str):
            targets = [targets]
        elif targets is None:
            return processed
        for target in targets:
            if isinstance(target, str):
                if target.endswith('.py'):
                    processed.add(target)
                    continue
                target_name = target
            elif isinstance(target, ModuleType):
                target_name = target.__name__
            else:
                log_warn(f"Unsupported target type: {type(target)}. Only 'str' or 'ModuleType' are supported.")
                continue

            spec = importlib.util.find_spec(target_name)
            if spec and spec.origin:
                processed.add(spec.origin)

                # Check if the module has submodules
                if hasattr(spec, 'submodule_search_locations'):
                    for importer, modname, ispkg in pkgutil.walk_packages(
                        spec.submodule_search_locations, prefix=target_name + '.'
                    ):
                        # For each submodule, use find_spec to check its path
                        try:
                            sub_spec = importlib.util.find_spec(modname)
                            if sub_spec and sub_spec.origin:
                                processed.add(sub_spec.origin)
                        except Exception as e:
                            log_error(f"Submodule {modname} could not be imported. Error: {e}")
            else:
                log_warn(f"Module {target_name} could not be found or has no file associated.")

        return processed

    def load_wrapper(self, wrapper: Optional[ABCWrapper]) -> Optional[ABCWrapper]:
        """
        Load a custom function wrapper if provided.

        Args:
            wrapper (Optional[ABCWrapper]): The custom wrapper to load.

        Returns:
            Optional[ABCWrapper]: The initialized wrapper or None.
        """
        if wrapper and issubclass(wrapper, ABCWrapper):
            log_warn(f"wrapper '{wrapper.__name__}' loaded")
            return wrapper()
        return None

    def _get_function_info(self, frame: FrameType) -> Dict[str, Any]:
        """
        Extract information about the currently executing function.

        Args:
            frame (FrameType): The current stack frame.

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
            try:
                method = getattr(obj, func_name, None)
            except Exception as e:
                log_error(f"Error occurred while getattr '{func_name}' from class '{class_name}': {e}")
                method = None
            if callable(method) and hasattr(method, '__code__') and method.__code__ == frame.f_code:
                func_info['is_method'] = True
                func_info['class_name'] = class_name

            if hasattr(obj, '__dict__') and hasattr(obj.__class__, '__weakref__'):
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

    @lru_cache(maxsize=sys.maxsize)
    def _filename_not_endswith(self, filename: str) -> bool:
        """
        Check if the filename does not end with any of the target extensions.

        Args:
            filename (str): The filename to check.

        Returns:
            bool: True if the filename does not end with the target extensions, False otherwise.
        """
        return not filename.endswith(tuple(self.targets))

    def _handle_change_type(
        self,
        lineno: int,
        class_name: str,
        key: str,
        old_value: Optional[Any],
        current_value: Any,
        old_value_len: Optional[int],
        current_value_len: Optional[int],
    ) -> None:
        """
        Helper function to handle the change type for both object attributes and local variables.

        Args:
            lineno (int): Line number where the change occurred.
            class_name (str): Class name if the change relates to an object attribute.
            key (str): The key (variable or attribute) being tracked.
            old_value (Optional[Any]): The old value of the variable or attribute.
            current_value (Any): The current value of the variable or attribute.
            old_value_len (Optional[int]): The length of the old value (if applicable).
            current_value_len (Optional[int]): The length of the current value (if applicable).
        """
        if old_value_len is not None and current_value_len is not None:
            change_type: EventType = (
                self.event_handlers.determine_change_type(old_value_len, current_value_len)
                if old_value_len is not None
                else EventType.UPD
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
                    self.rank_info,
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
                    self.rank_info,
                )
        elif change_type == EventType.UPD:
            self.event_handlers.handle_upd(
                lineno,
                class_name,
                key,
                old_value,
                current_value,
                self.call_depth,
                self.rank_info,
                self.abc_wrapper,
            )

    def _track_object_change(self, frame: FrameType, lineno: int):
        """
        Handle changes in object attributes and track updates.

        Args:
            frame (FrameType): The current stack frame.
            lineno (int): The line number where the change occurred.
        """

        obj = frame.f_locals['self']
        class_name = obj.__class__.__name__

        if obj in self.tracked_objects:
            old_attrs = self.tracked_objects[obj]
            old_attrs_lens = self.tracked_objects_lens[obj]
            current_attrs = {k: v for k, v in obj.__dict__.items() if not callable(v)}

            for key, current_value in current_attrs.items():
                old_value = old_attrs.get(key, None)
                old_value_len = old_attrs_lens.get(key, None)
                is_current_seq = isinstance(current_value, log_sequence_types)
                current_value_len = len(current_value) if old_value_len is not None and is_current_seq else None

                self._handle_change_type(
                    lineno,
                    class_name,
                    key,
                    old_value,
                    current_value,
                    old_value_len,
                    current_value_len,
                )

                old_attrs[key] = current_value
                if is_current_seq:
                    self.tracked_objects_lens[obj][key] = len(current_value)

    def _track_locals_change(self, frame: FrameType, lineno: int):
        """
        Handle changes in local variables and track updates.

        Args:
            frame (FrameType): The current stack frame.
            lineno (int): The line number where the change occurred.
        """

        if frame not in self.tracked_locals:
            return

        old_locals = self.tracked_locals[frame]
        current_locals = {k: v for k, v in frame.f_locals.items() if k != 'self' and not callable(v)}
        old_locals_lens = self.tracked_locals_lens[frame]

        added_vars = set(current_locals.keys()) - set(old_locals.keys())
        for var in added_vars:
            current_local = current_locals[var]

            self.event_handlers.handle_upd(
                lineno,
                class_name="_",
                key=var,
                old_value=None,
                current_value=current_local,
                call_depth=self.call_depth,
                rank_info=self.rank_info,
                abc_wrapper=self.abc_wrapper,
            )

            if isinstance(current_local, log_sequence_types):
                self.tracked_locals_lens[frame][var] = len(current_local)

        common_vars = set(old_locals.keys()) & set(current_locals.keys())
        for var in common_vars:
            old_local = old_locals[var]
            old_local_len = old_locals_lens.get(var, None)
            current_local = current_locals[var]
            is_current_seq = isinstance(current_local, log_sequence_types)
            current_local_len = len(current_local) if old_local_len is not None and is_current_seq else None

            self._handle_change_type(lineno, "_", var, old_local, current_local, old_local_len, current_local_len)

            if is_current_seq:
                self.tracked_locals_lens[frame][var] = len(current_local)

        self.tracked_locals[frame] = current_locals

    def _track_globals_change(self, frame: FrameType, lineno: int):
        """
        Handle changes in global variables and track updates.

        Args:
            frame (FrameType): The current stack frame.
            lineno (int): The line number where the change occurred.
        """

        global_vars = frame.f_globals
        for key, current_value in global_vars.items():
            if key in self.builtin_fields:
                continue

            old_value = self.tracked_globals.get(key, None)
            old_value_len = self.tracked_globals_lens.get(key, None)
            is_current_seq = isinstance(current_value, log_sequence_types)
            current_value_len = len(current_value) if old_value_len is not None and is_current_seq else None

            self._handle_change_type(lineno, "@", key, old_value, current_value, old_value_len, current_value_len)

            self.tracked_globals[key] = current_value
            if is_current_seq:
                self.tracked_globals_lens[key] = len(current_value)

    def trace_factory(self) -> FunctionType:  # noqa: C901
        """
        Create the tracing function to be used with sys.settrace.

        Returns:
            FunctionType: The trace function.
        """

        def trace_func(frame: FrameType, event: str, arg: Any) -> Optional[FunctionType]:
            """
            This function is the actual trace function used by sys.settrace. It is called
            for every event (e.g., call, return, line) during code execution.

            Args:
                frame (FrameType): The current stack frame.
                event (str): The type of event ('call', 'return', or 'line').
                arg (Any): The argument for the event (e.g., return value for 'return').

            Returns:
                Optional[FunctionType]: Returns the trace function itself to continue tracing.
            """

            # Skip frames that do not match the filename condition
            if self._filename_not_endswith(frame.f_code.co_filename):
                return trace_func

            # Handle multi-GPU ranks if PyTorch is available
            if self.torch_available:
                if self.current_rank is None:
                    if torch.distributed and torch.distributed.is_initialized():
                        self.current_rank = torch.distributed.get_rank()
                        self.rank_info = f"[Rank {self.current_rank}] "
                elif self.current_rank not in self.ranks:
                    return trace_func

            lineno = frame.f_lineno
            if event == "call":
                # Handle function call event
                func_info = self._get_function_info(frame)
                self.event_handlers.handle_run(lineno, func_info, self.abc_wrapper, self.call_depth, self.rank_info)
                self.call_depth += 1

                # Track local variables if needed
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
                # Handle function return event
                self.call_depth -= 1
                func_info = self._get_function_info(frame)
                self.event_handlers.handle_end(
                    lineno, func_info, self.abc_wrapper, self.call_depth, self.rank_info, arg
                )

                # Clean up local tracking after function return
                if self.with_locals and frame in self.tracked_locals:
                    del self.tracked_locals[frame]
                    del self.tracked_locals_lens[frame]

                return trace_func

            elif event == "line":
                # Handle line event (track changes at each line of code)
                if 'self' in frame.f_locals:
                    self._track_object_change(frame, lineno)

                if self.with_locals:
                    self._track_locals_change(frame, lineno)

                if self.with_globals:
                    self._track_globals_change(frame, lineno)

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
