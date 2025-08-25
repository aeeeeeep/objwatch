# MIT License
# Copyright (c) 2025 aeeeeeep

import logging
from types import ModuleType
from typing import Optional, Union, List, Any

from .config import ObjWatchConfig
from .tracer import Tracer
from .wrappers import ABCWrapper
from .utils.logger import create_logger, log_info


class ObjWatch:
    """
    Tracing and logging of specified Python modules to aid in debugging and monitoring.
    """

    def __init__(
        self,
        targets: List[Union[str, ModuleType]],
        exclude_targets: Optional[List[Union[str, ModuleType]]] = None,
        framework: Optional[str] = None,
        indexes: Optional[List[int]] = None,
        output: Optional[str] = None,
        output_xml: Optional[str] = None,
        level: int = logging.DEBUG,
        simple: bool = False,
        wrapper: Optional[ABCWrapper] = None,
        with_locals: bool = False,
        with_globals: bool = False,
    ) -> None:
        """
        Initialize the ObjWatch instance with configuration parameters.

        Args:
            targets (List[Union[str, ModuleType]]): Files or modules to monitor.
            exclude_targets (Optional[List[Union[str, ModuleType]]]): Files or modules to exclude from monitoring.
            framework (Optional[str]): The multi-process framework module to use.
            indexes (Optional[List[int]]): The indexes to track in a multi-process environment.
            output (Optional[str]): Path to a file for writing logs.
            output_xml (Optional[str]): Path to the XML file for writing structured logs.
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
            simple (bool): Enable simple logging mode with the format "DEBUG: {msg}".
            wrapper (Optional[ABCWrapper]): Custom wrapper to extend tracing and logging functionality.
            with_locals (bool): Enable tracing and logging of local variables within functions.
            with_globals (bool): Enable tracing and logging of global variables across function calls.
        """
        # Create configuration parameters for ObjWatch
        config = ObjWatchConfig(
            targets=targets,
            exclude_targets=exclude_targets,
            framework=framework,
            indexes=indexes,
            output=output,
            output_xml=output_xml,
            level=level,
            simple=simple,
            wrapper=wrapper,
            with_locals=with_locals,
            with_globals=with_globals,
        )

        # Create and configure the logger based on provided parameters
        create_logger(output=config.output, level=config.level, simple=config.simple)

        # Initialize the Tracer with the given configuration
        self.tracer = Tracer(config=config)

    def start(self) -> None:
        """
        Start the ObjWatch tracing process.
        """
        log_info("Starting ObjWatch tracing.")
        self.tracer.start()

    def stop(self) -> None:
        """
        Stop the ObjWatch tracing process.
        """
        log_info("Stopping ObjWatch tracing.")
        self.tracer.stop()

    def __enter__(self) -> 'ObjWatch':
        """
        Enter the runtime context related to this object.

        Returns:
            ObjWatch: The ObjWatch instance itself.
        """
        self.start()
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        """
        Exit the runtime context and stop tracing.

        Args:
            exc_type (Optional[type]): The exception type.
            exc_val (Optional[BaseException]): The exception value.
            exc_tb (Optional[Any]): The traceback object.
        """
        self.stop()


def watch(
    targets: List[Union[str, ModuleType]],
    exclude_targets: Optional[List[Union[str, ModuleType]]] = None,
    framework: Optional[str] = None,
    indexes: Optional[List[int]] = None,
    output: Optional[str] = None,
    output_xml: Optional[str] = None,
    level: int = logging.DEBUG,
    simple: bool = False,
    wrapper: Optional[ABCWrapper] = None,
    with_locals: bool = False,
    with_globals: bool = False,
) -> ObjWatch:
    """
    Initialize and start an ObjWatch instance.

    Args:
        targets (List[Union[str, ModuleType]]): Files or modules to monitor.
        exclude_targets (Optional[List[Union[str, ModuleType]]]): Files or modules to exclude from monitoring.
        framework (Optional[str]): The multi-process framework module to use.
        indexes (Optional[List[int]]): The indexes to track in a multi-process environment.
        output (Optional[str]): Path to a file for writing logs.
        output_xml (Optional[str]): Path to the XML file for writing structured logs.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
        simple (bool): Enable simple logging mode with the format "DEBUG: {msg}".
        wrapper (Optional[ABCWrapper]): Custom wrapper to extend tracing and logging functionality.
        with_locals (bool): Enable tracing and logging of local variables within functions.
        with_globals (bool): Enable tracing and logging of global variables across function calls.

    Returns:
        ObjWatch: The initialized and started ObjWatch instance.
    """
    # Instantiate the ObjWatch with the provided configuration
    obj_watch = ObjWatch(
        targets=targets,
        exclude_targets=exclude_targets,
        framework=framework,
        indexes=indexes,
        output=output,
        output_xml=output_xml,
        level=level,
        simple=simple,
        wrapper=wrapper,
        with_locals=with_locals,
        with_globals=with_globals,
    )

    # Start the tracing process
    obj_watch.start()

    return obj_watch
