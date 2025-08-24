# MIT License
# Copyright (c) 2025 aeeeeeep

import logging
from types import ModuleType
from dataclasses import dataclass
from typing import Optional, Union, List

from .wrappers import ABCWrapper


@dataclass(frozen=True)
class ObjWatchConfig:
    """
    Configuration parameters for ObjWatch.

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

    targets: List[Union[str, ModuleType]]
    exclude_targets: Optional[List[Union[str, ModuleType]]] = None
    framework: Optional[str] = None
    indexes: Optional[List[int]] = None
    output: Optional[str] = None
    output_xml: Optional[str] = None
    level: int = logging.DEBUG
    simple: bool = False
    wrapper: Optional[ABCWrapper] = None
    with_locals: bool = False
    with_globals: bool = False

    def __post_init__(self) -> None:
        """
        Post-initialization configuration validation
        """
        if not self.targets:
            raise ValueError("At least one monitoring target must be specified")

        if self.level == "force" and self.output is not None:
            raise ValueError("output cannot be specified when level is 'force'")
