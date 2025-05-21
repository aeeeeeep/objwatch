# MIT License
# Copyright (c) 2025 aeeeeeep

import sys
from functools import lru_cache
from types import FunctionType, FrameType
from typing import Optional, Any, Dict, Set

from .config import ObjWatchConfig
from .targets import Targets, TargetsDict
from .wrappers import ABCWrapper
from .events import EventType
from .event_handls import EventHandls, log_sequence_types
from .mp_handls import MPHandls
from .utils.logger import log_debug, log_warn, log_info
from .utils.weak import WeakIdKeyDictionary


class Tracer:
    """
    Tracer class to monitor and trace function calls, returns, and variable updates
    within specified target modules. Supports multi-GPU environments with PyTorch.
    """

    def __init__(
        self,
        config: ObjWatchConfig,
    ) -> None:
        """
        Initialize the Tracer with configuration parameters.

        Args:
            config (ObjWatchConfig): Configuration parameters for ObjWatch.
        """

        self.config = config

        if self.config.with_locals:
            self.tracked_locals: Dict[FrameType, Dict[str, Any]] = {}
            self.tracked_locals_lens: Dict[FrameType, Dict[str, int]] = {}

        if self.config.with_globals:
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

        # Process and determine the set of target files to monitor
        targets_cls = Targets(self.config.targets, self.config.exclude_targets)
        self.targets: TargetsDict = targets_cls.get_processed_targets()
        self.filename_targets: Set = targets_cls.get_filename_targets()
        self._build_target_index()
        log_debug(f"Processed targets:\n{'>' * 10}\n" + "\n".join(self.targets) + f"\n{'<' * 10}")

        # Initialize tracking dictionaries for objects
        self.tracked_objects: WeakIdKeyDictionary = WeakIdKeyDictionary()
        self.tracked_objects_lens: WeakIdKeyDictionary = WeakIdKeyDictionary()

        # Initialize event handlers with optional XML output
        self.event_handlers: EventHandls = EventHandls(output_xml=self.config.output_xml)

        # Initialize multi-process handler with the specified framework
        self.mp_handlers: MPHandls = MPHandls(framework=self.config.framework)
        self.index_info: str = ""
        self.current_index = None
        self.indexes: Set[int] = set(self.config.indexes if self.config.indexes is not None else [0])

        # Load the function wrapper if provided
        self.abc_wrapper: ABCWrapper = self.load_wrapper(self.config.wrapper)
        self.call_depth: int = 0

    def _build_target_index(self):
        """构建快速查询索引"""
        self.module_index = set(self.targets.keys())
        self.class_index = {}
        self.function_index = {}
        self.global_index = {}

        for module, details in self.targets.items():
            for cls in details.get('classes', {}):
                self.class_index[module].add(cls)
            for func in details.get('functions', []):
                self.function_index[module].add(func)
            for gvar in details.get('globals', []):
                self.global_index[module].add(gvar)

        self.index_map = {'class': self.class_index, 'function': self.function_index, 'global': self.global_index}

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

    @lru_cache(maxsize=sys.maxsize)
    def _should_trace_module(self, module: str) -> bool:
        """检查模块是否在监控范围"""
        return module in self.module_index

    @lru_cache(maxsize=sys.maxsize)
    def _should_trace_symbol(self, module: str, symbol_type: str, symbol: str) -> bool:
        """检查具体符号是否需要监控"""
        return symbol in self.index_map[symbol_type].get(module, set())

    @lru_cache(maxsize=sys.maxsize)
    def _filename_endswith(self, filename: str) -> bool:
        """
        Check if the filename does not end with any of the target extensions.

        Args:
            filename (str): The filename to check.

        Returns:
            bool: True if the filename does not end with the target extensions, False otherwise.
        """
        return filename.endswith(tuple(self.filename_targets))

    def _should_trace_frame(self, frame: FrameType) -> bool:
        """综合判断是否需要跟踪当前frame"""
        if self._filename_endswith(frame.f_code.co_filename):
            return True

        module = frame.f_globals.get('__name__', '')

        # 基础模块检查
        if not self._should_trace_module(module):
            return False

        # 具体符号检查
        if 'self' in frame.f_locals:
            cls_name = frame.f_locals['self'].__class__.__name__
            return self._should_trace_symbol(module, 'class', cls_name)
        return any(
            [self._should_trace_symbol(module, 'function', frame.f_code.co_name), self._check_global_changes(frame)]
        )

    def _check_global_changes(self, frame: FrameType) -> bool:
        """检查全局变量变更"""
        return any(
            var in self.global_index.get(frame.f_globals.get('__name__', ''), set()) for var in frame.f_globals.keys()
        )

    def _update_objects_lens(self, frame: FrameType) -> None:
        """
        Update tracked objects' sequence-type attribute lengths.

        Args:
            frame (FrameType): Current stack frame to inspect.
        """
        if 'self' in frame.f_locals:
            obj = frame.f_locals['self']

            if hasattr(obj, '__dict__') and hasattr(obj.__class__, '__weakref__'):
                attrs: Dict[str, Any] = {k: v for k, v in obj.__dict__.items() if not callable(v)}
                if obj not in self.tracked_objects:
                    self.tracked_objects[obj] = attrs
                if obj not in self.tracked_objects_lens:
                    self.tracked_objects_lens[obj] = {}
                for k, v in attrs.items():
                    if isinstance(v, log_sequence_types):
                        self.tracked_objects_lens[obj][k] = len(v)

    def _get_function_info(self, frame: FrameType) -> Dict[str, Any]:
        """
        Extract information about the currently executing function.

        Args:
            frame (FrameType): The current stack frame.

        Returns:
            Dict[str, Any]: Dictionary containing function information.
        """
        func_info = {}
        module = frame.f_globals.get('__name__', '')

        # 构造完整调用路径
        if 'self' in frame.f_locals:
            cls = frame.f_locals['self'].__class__.__name__
            func_name = f"{cls}.{frame.f_code.co_name}"
            symbol_type = 'method' if self._should_trace_symbol(module, 'class', cls) else None
        else:
            func_name = frame.f_code.co_name
            symbol_type = 'function' if self._should_trace_symbol(module, 'function', func_name) else None

        func_info.update(
            {
                'module': module,
                'symbol': func_name,
                'symbol_type': symbol_type,
                'qualified_name': f"{module}.{func_name}" if module else func_name,
                'frame': frame,
            }
        )
        return func_info

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
                    self.index_info,
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
                    self.index_info,
                )
        elif change_type == EventType.UPD:
            self.event_handlers.handle_upd(
                lineno,
                class_name,
                key,
                old_value,
                current_value,
                self.call_depth,
                self.index_info,
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
                index_info=self.index_info,
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
            if not self._should_trace_frame(frame):
                return trace_func

            if self.current_index is None:
                # Check if multi-process framework is initialized and set the current process index
                if self.mp_handlers.is_initialized():
                    self.current_index = self.mp_handlers.get_index()
                    self.index_info = f"[#{self.current_index}] "
            elif self.current_index not in self.indexes:
                # Skip tracing for processes that are not part of the tracked indexes
                return trace_func

            lineno = frame.f_lineno
            if event == "call":
                # Handle function call event
                func_info = self._get_function_info(frame)
                self._update_objects_lens(frame)
                self.event_handlers.handle_run(lineno, func_info, self.abc_wrapper, self.call_depth, self.index_info)
                self.call_depth += 1

                # Track local variables if needed
                if self.config.with_locals:
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
                self._update_objects_lens(frame)
                self.event_handlers.handle_end(
                    lineno, func_info, self.abc_wrapper, self.call_depth, self.index_info, arg
                )

                # Clean up local tracking after function return
                if self.config.with_locals and frame in self.tracked_locals:
                    del self.tracked_locals[frame]
                    del self.tracked_locals_lens[frame]

                return trace_func

            elif event == "line":
                # Handle line event (track changes at each line of code)
                if 'self' in frame.f_locals:
                    self._track_object_change(frame, lineno)

                if self.config.with_locals:
                    self._track_locals_change(frame, lineno)

                if self.config.with_globals:
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
        self.mp_handlers.sync()

    def stop(self) -> None:
        """
        Stop the tracing process by removing the trace function and saving XML logs.
        """
        log_info("Stopping tracing.")
        sys.settrace(None)
        self.event_handlers.save_xml()
