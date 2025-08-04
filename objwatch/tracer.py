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
        log_debug(
            f"\nProcessed targets:\n{'>' * 10}\n"
            + targets_cls.serialize_targets()
            + f"\n{'<' * 10}\n"
            + f"Filename targets:\n{'>' * 10}\n"
            + "\n".join(self.filename_targets)
            + f"\n{'<' * 10}"
        )

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
        """Build fast lookup indexes for monitoring targets.

        Creates three-level indexes:
        - module_index: Set of monitored module names
        - class_index: Nested mapping of modules to their classes
        - function_index: Nested mapping of modules to their functions
        - global_index: Nested mapping of modules to their global variables

        Final structure example:
        index_map = {
            'class': {'module1': {'ClassA', 'ClassB'}, ...},
            'function': {'module1': {'func1', 'func2'}, ...},
            'global': {'module1': {'var1', 'var2'}, ...}
        }
        """
        self.module_index = set(self.targets.keys())
        self.class_index = {}
        self.method_index = {}
        self.attribute_index = {}
        self.function_index = {}
        self.global_index = {}
        for module, details in self.targets.items():
            # Process classes
            classes = details.get('classes', {})
            for cls_name, cls_info in classes.items():
                # Add class to class index
                self.class_index.setdefault(module, set()).add(cls_name)

                # Process methods
                methods = cls_info.get('methods', [])
                if methods:
                    class_methods = self.method_index.setdefault(module, {}).setdefault(cls_name, set())
                    class_methods.update(methods)

                # Process attributes
                attributes = cls_info.get('attributes', [])
                if attributes:
                    class_attrs = self.attribute_index.setdefault(module, {}).setdefault(cls_name, set())
                    class_attrs.update(attributes)

            # Process functions
            for func in details.get('functions', []):
                self.function_index.setdefault(module, set()).add(func)

            # Process globals
            for gvar in details.get('globals', []):
                self.global_index.setdefault(module, set()).add(gvar)

        self.index_map = {
            'class': self.class_index,
            'method': self.method_index,
            'attribute': self.attribute_index,
            'function': self.function_index,
            'global': self.global_index,
        }

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
        """Check if a module is within monitoring scope.

        Args:
            module (str): Full module name to check

        Returns:
            bool: True if the module is in monitoring targets
        """
        return module in self.module_index

    @lru_cache(maxsize=sys.maxsize)
    def _should_trace_class(self, module: str, class_name: str) -> bool:
        """Check if a specific class should be traced.

        Args:
            module (str): Parent module name
            class_name (str): Class name to check

        Returns:
            bool: True if the class should be traced
        """
        return class_name in self.class_index.get(module, set())

    @lru_cache(maxsize=sys.maxsize)
    def _should_trace_method(self, module: str, class_name: str, method_name: str) -> bool:
        """Check if a specific method should be traced.

        Args:
            module (str): Parent module name
            class_name (str): Class name containing the method
            method_name (str): Method name to check

        Returns:
            bool: True if the method should be traced
        """
        return method_name in self.method_index.get(module, {}).get(class_name, set())

    @lru_cache(maxsize=sys.maxsize)
    def _should_trace_attribute(self, module: str, class_name: str, attr_name: str) -> bool:
        """Check if a specific attribute should be traced.

        Args:
            module (str): Parent module name
            class_name (str): Class name containing the attribute
            attr_name (str): Attribute name to check

        Returns:
            bool: True if the attribute should be traced
        """
        return attr_name in self.attribute_index.get(module, {}).get(class_name, set())

    @lru_cache(maxsize=sys.maxsize)
    def _should_trace_function(self, module: str, func_name: str) -> bool:
        """Check if a specific function should be traced.

        Args:
            module (str): Parent module name
            func_name (str): Function name to check

        Returns:
            bool: True if the function should be traced
        """
        return func_name in self.function_index.get(module, set())

    @lru_cache(maxsize=sys.maxsize)
    def _should_trace_global(self, module: str, global_name: str) -> bool:
        """Check if a specific global variable should be traced.

        Args:
            module (str): Parent module name
            global_name (str): Global variable name to check

        Returns:
            bool: True if the global variable should be traced
        """
        if not self.config.with_globals:
            return False

        if not self.global_index:
            return global_name not in self.builtin_fields

        return global_name in self.global_index.get(module, set())

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
        """Determine if a stack frame should be traced.

        Args:
            frame (FrameType): Execution frame to evaluate

        Returns:
            bool: True if tracing should occur for this frame
        """
        # Check if file extension matches target patterns
        if self._filename_endswith(frame.f_code.co_filename):
            return True

        module = frame.f_globals.get('__name__', '')

        # Check if module is in tracing targets
        if not self._should_trace_module(module):
            return False

        # Handle class methods and attributes
        if 'self' in frame.f_locals:
            cls_name = frame.f_locals['self'].__class__.__name__
            method_name = frame.f_code.co_name

            # Check if class is traced and method is traced
            class_is_traced = self._should_trace_class(module, cls_name)
            method_is_traced = self._should_trace_method(module, cls_name, method_name)

            # If method is traced, no need to check attributes
            if class_is_traced and method_is_traced:
                return True

            # Check if any attribute is traced
            if class_is_traced:
                obj = frame.f_locals['self']
                current_attrs = {k: v for k, v in obj.__dict__.items() if not callable(v)}
                any_attr_traced = any(
                    self._should_trace_attribute(module, cls_name, attr) for attr in current_attrs.keys()
                )
                return any_attr_traced

            return False
        # Handle regular functions
        func_name = frame.f_code.co_name
        if self._should_trace_function(module, func_name):
            return True
        # Check for global variable changes
        return self._check_global_changes(frame)

    def _check_global_changes(self, frame: FrameType) -> bool:
        """Detect monitored global variables in current frame.

        Args:
            frame (FrameType): Execution frame containing globals

        Returns:
            bool: True if any tracked global variables exist
        """
        module_name = frame.f_globals.get('__name__', '')

        if not self.global_index and self.config.with_globals:
            return any(var not in self.builtin_fields for var in frame.f_globals.keys())

        if not self.config.with_globals:
            return False

        return bool(self.global_index.get(module_name))

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

        if 'self' in frame.f_locals:
            cls = frame.f_locals['self'].__class__.__name__
            func_name = f"{cls}.{frame.f_code.co_name}"
            symbol_type = 'method' if self._should_trace_method(module, cls, func_name) else None
        else:
            func_name = frame.f_code.co_name
            symbol_type = 'function' if self._should_trace_function(module, func_name) else None

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
        if 'self' not in frame.f_locals:
            return

        obj = frame.f_locals['self']
        class_name = obj.__class__.__name__
        should_trace_all_attrs = self._filename_endswith(frame.f_code.co_filename)

        if obj in self.tracked_objects:
            old_attrs = self.tracked_objects[obj]
            old_attrs_lens = self.tracked_objects_lens[obj]
            module_name = frame.f_globals.get('__name__', '')
            current_attrs = {k: v for k, v in obj.__dict__.items() if not callable(v)}

            for key, current_value in current_attrs.items():
                if not (should_trace_all_attrs or self._should_trace_attribute(module_name, class_name, key)):
                    continue

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
        if not self.config.with_locals or frame not in self.tracked_locals:
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
        module_name = frame.f_globals.get('__name__', '')

        if not self.config.with_globals:
            return

        if module_name not in self.tracked_globals:
            self.tracked_globals[module_name] = {}
        if module_name not in self.tracked_globals_lens:
            self.tracked_globals_lens[module_name] = {}

        for key, current_value in list(global_vars.items()):
            if not self._should_trace_global(module_name, key):
                continue

            old_value = self.tracked_globals[module_name].get(key, None)
            old_value_len = self.tracked_globals_lens[module_name].get(key, None)
            is_current_seq = isinstance(current_value, log_sequence_types)
            current_value_len = len(current_value) if old_value_len is not None and is_current_seq else None

            self._handle_change_type(lineno, "@", key, old_value, current_value, old_value_len, current_value_len)

            self.tracked_globals[module_name][key] = current_value
            if is_current_seq:
                self.tracked_globals_lens[module_name][key] = len(current_value)

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
                self._track_object_change(frame, lineno)
                self._track_locals_change(frame, lineno)
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
