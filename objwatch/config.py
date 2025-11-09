# MIT License
# Copyright (c) 2025 aeeeeeep

import logging
from types import ModuleType
from dataclasses import dataclass
from typing import Optional, Union, List, Dict, Any


@dataclass(frozen=True)
class ObjWatchConfig:
    """
    Configuration parameters for ObjWatch.

    Args:
        targets (List[Union[str, ModuleType]]): Files or modules to monitor.
        exclude_targets (Optional[List[Union[str, ModuleType]]]): Files or modules to exclude from monitoring.
        framework (Optional[str]): The multi-process framework module to use.
        indexes (Optional[List[int]]): The indexes to track in a multi-process environment.
        output (Optional[str]): Path to a file for writing logs, must end with '.objwatch' for ObjWatch Log Viewer extension.
        output_json (Optional[str]): Path to the JSON file for writing structured logs.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
        simple (bool): Defaults to True, disable simple logging mode with the format "[{time}] [{level}] objwatch: {msg}".
        wrapper (Optional[ABCWrapper]): Custom wrapper to extend tracing and logging functionality.
        with_locals (bool): Enable tracing and logging of local variables within functions.
        with_globals (bool): Enable tracing and logging of global variables across function calls.
    """

    targets: List[Union[str, ModuleType]]
    exclude_targets: Optional[List[Union[str, ModuleType]]] = None
    framework: Optional[str] = None
    indexes: Optional[List[int]] = None
    output: Optional[str] = None
    output_json: Optional[str] = None
    level: int = logging.DEBUG
    simple: bool = True
    wrapper: Optional[Any] = None
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

        if self.output is not None and not self.output.endswith('.objwatch'):
            raise ValueError("output file must end with '.objwatch' for ObjWatch Log Viewer extension")

        if self.output_json is not None and not self.output_json.endswith('.json'):
            raise ValueError("output_json file must end with '.json'")

    def __str__(self) -> str:
        """
        Return a simple string representation of the configuration.
        """
        config_lines = []
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, list):
                # For lists, print each element on a new line
                config_lines.append(f"* {field_name}:")
                for item in field_value:
                    config_lines.append(f"  - {item}")
            elif field_name == 'level' and isinstance(field_value, int):
                config_lines.append(f"* {field_name}: {logging.getLevelName(field_value)}")
            elif field_name == 'wrapper' and field_value is not None:
                config_lines.append(f"* {field_name}: {field_value.__name__}")
            else:
                # For other types, print directly
                config_lines.append(f"* {field_name}: {field_value}")
        return "\n".join(config_lines)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration object to a dictionary representation.

        Returns:
            Dict[str, Any]: A dictionary containing all configuration fields.
        """
        result: Dict[str, Any] = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, list):
                # Convert list elements to string representation if needed
                result[field_name] = [str(item) if isinstance(item, ModuleType) else item for item in field_value]
            elif isinstance(field_value, (ModuleType, type)):
                # Convert module objects to their __name__
                result[field_name] = field_value.__name__
            elif field_name == 'level' and isinstance(field_value, int):
                # For level field, include both numeric value and name
                result[field_name] = logging.getLevelName(field_value)
            else:
                # For other types, add as is
                result[field_name] = field_value
        return result
