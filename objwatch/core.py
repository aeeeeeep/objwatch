# MIT License
# Copyright (c) 2025 aeeeeeep

import logging
import os
from types import ModuleType
from typing import Optional, Union, List, Any

from .config import ObjWatchConfig
from .tracer import Tracer
from .wrappers import ABCWrapper
from .sinks.consumer import DynamicRoutingConsumer
from .utils.logger import log_info, setup_logging_from_config
from .runtime_info import runtime_info


class ObjWatch:
    """
    Tracing and logging of specified Python modules to aid in debugging and monitoring.
    """

    def __init__(
        self,
        targets: List[Union[str, ModuleType]],
        exclude_targets: Optional[List[Union[str, ModuleType]]] = None,
        with_locals: bool = False,
        with_globals: bool = False,
        output: Optional[str] = None,
        output_json: Optional[str] = None,
        level: int = logging.DEBUG,
        simple: bool = True,
        wrapper: Optional[ABCWrapper] = None,
        framework: Optional[str] = None,
        indexes: Optional[List[int]] = None,
        output_mode: str = "std",
        zmq_endpoint: str = "tcp://127.0.0.1:5555",
        zmq_topic: str = "",
        auto_start_consumer: bool = True,
    ) -> None:
        """
        Initialize the ObjWatch instance with configuration parameters.

        Args:
            targets (List[Union[str, ModuleType]]): Files or modules to monitor.
            exclude_targets (Optional[List[Union[str, ModuleType]]]): Files or modules to exclude from monitoring.
            with_locals (bool): Enable tracing and logging of local variables within functions.
            with_globals (bool): Enable tracing and logging of global variables across function calls.
            output (Optional[str]): File path for writing logs, must end with '.objwatch' for ObjWatch Log Viewer extension.
            output_json (Optional[str]): JSON file path for writing structured logs.
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
            simple (bool): Defaults to True, disable simple logging mode with the format "[{time}] [{level}] objwatch: {msg}".
            wrapper (Optional[ABCWrapper]): Custom wrapper to extend tracing and logging functionality.
            framework (Optional[str]): The multi-process framework module to use.
            indexes (Optional[List[int]]): The indexes to track in a multi-process environment.
            output_mode (str): Output mode for logs. Options: 'std', 'zmq'. Defaults to 'std'.
            zmq_endpoint (str): ZeroMQ endpoint for 'zmq' mode. Defaults to "tcp://127.0.0.1:5555".
            zmq_topic (str): ZeroMQ topic for 'zmq' mode. Defaults to "".
            auto_start_consumer (bool): Whether to automatically start the ZeroMQ consumer. Defaults to True.
        """
        # Create configuration parameters for ObjWatch
        config = ObjWatchConfig(**{k: v for k, v in locals().items() if k != 'self'})

        # Create and configure the logger based on provided parameters
        setup_logging_from_config(config)

        # Initialize the Tracer with the given configuration
        self.tracer = Tracer(config=config)

        # Initialize ZeroMQ consumer if configured
        self.consumer = None
        if config.output_mode == 'zmq' and config.auto_start_consumer:
            log_info(f"Auto-starting ZeroMQ consumer on endpoint {config.zmq_endpoint}")
            # Use DynamicRoutingConsumer for dynamic routing support
            self.consumer = DynamicRoutingConsumer(
                endpoint=config.zmq_endpoint,
                auto_start=True,
                daemon=True,
                allowed_directories=[os.getcwd()],
            )

    def start(self) -> None:
        """
        Start the ObjWatch tracing process.
        """
        log_info("Starting ObjWatch tracing.")
        runtime_info.update()
        self.tracer.start()

    def stop(self) -> None:
        """
        Stop the ObjWatch tracing process and clean up resources.
        """
        log_info("Stopping ObjWatch tracing.")
        self.tracer.stop()

        # Stop the ZeroMQ consumer if it was started
        if self.consumer:
            log_info("Stopping ZeroMQ consumer.")
            self.consumer.stop()
            self.consumer = None

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
    with_locals: bool = False,
    with_globals: bool = False,
    output: Optional[str] = None,
    output_json: Optional[str] = None,
    level: int = logging.DEBUG,
    simple: bool = True,
    wrapper: Optional[ABCWrapper] = None,
    framework: Optional[str] = None,
    indexes: Optional[List[int]] = None,
    output_mode: str = "std",
    zmq_endpoint: str = "tcp://127.0.0.1:5555",
    zmq_topic: str = "",
    auto_start_consumer: bool = True,
) -> ObjWatch:
    """
    Initialize and start an ObjWatch instance.

    Args:
        targets (List[Union[str, ModuleType]]): Files or modules to monitor.
        exclude_targets (Optional[List[Union[str, ModuleType]]]): Files or modules to exclude from monitoring.
        with_locals (bool): Enable tracing and logging of local variables within functions.
        with_globals (bool): Enable tracing and logging of global variables across function calls.
        output (Optional[str]): File path for writing logs, must end with '.objwatch' for ObjWatch Log Viewer extension.
        output_json (Optional[str]): JSON file path for writing structured logs.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
        simple (bool): Defaults to True, disable simple logging mode with the format "[{time}] [{level}] objwatch: {msg}".
        wrapper (Optional[ABCWrapper]): Custom wrapper to extend tracing and logging functionality.
        framework (Optional[str]): The multi-process framework module to use.
        indexes (Optional[List[int]]): The indexes to track in a multi-process environment.
        output_mode (str): Output mode for logs. Options: 'std', 'zmq'. Defaults to 'std'.
        zmq_endpoint (str): ZeroMQ endpoint for 'zmq' mode. Defaults to "tcp://127.0.0.1:5555".
        zmq_topic (str): ZeroMQ topic for 'zmq' mode. Defaults to "".
        auto_start_consumer (bool): Whether to automatically start the ZeroMQ consumer. Defaults to True.

    Returns:
        ObjWatch: The initialized and started ObjWatch instance.
    """
    # Instantiate the ObjWatch with the provided configuration
    obj_watch = ObjWatch(**locals())

    # Start the tracing process
    obj_watch.start()

    return obj_watch
