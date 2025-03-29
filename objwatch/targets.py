# MIT License
# Copyright (c) 2025 aeeeeeep

import importlib
import pkgutil
from types import ModuleType
from typing import Optional, List, Union, Set

from .utils.logger import log_error, log_warn


class Targets:
    """
    Targets class to process and determine the set of target files to monitor.
    """

    def __init__(
        self, targets: Optional[List[Union[str, type]]], exclude_targets: Optional[List[Union[str, type]]] = None
    ):
        """
        Initialize the Targets with target modules or files and exclude targets.

        Args:
            targets ([List[Union[str, ModuleType]]): List of target modules or file paths.
            exclude_targets (Optional[List[Union[str, ModuleType]]): List of modules or file paths to exclude.
        """
        self.targets = self._process_modules(targets)
        self.exclude_targets = self._process_modules(exclude_targets)
        self.processed_targets = self.targets - self.exclude_targets

    def _process_modules(self, targets: Optional[List[Union[str, type]]]) -> Set[str]:
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
