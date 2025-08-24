# MIT License
# Copyright (c) 2025 aeeeeeep

import ast
import json
import inspect
import importlib
import pkgutil
from types import ModuleType, MethodType, FunctionType
from typing import Tuple, List, Union, Dict, Set, Any

from .utils.logger import log_error, log_warn

ClassType = type
TargetsType = List[Union[str, ModuleType]]
ModuleStructure = Dict[str, Union[Dict[str, Any], List[str]]]
TargetsDict = Dict[str, ModuleStructure]


def iter_parents(node):
    """Generator for traversing AST node parent hierarchy.

    Yields:
        ast.AST: Parent nodes in bottom-up order (nearest ancestor first)

    Example:
        for parent in iter_parents(some_node):
            if isinstance(parent, ast.ClassDef):
                break
    """
    while hasattr(node, 'parent'):
        node = node.parent
        yield node


def set_parents(node, parent):
    """Recursively set parent references in AST nodes.

    Enables parent traversal via node.parent attribute
    Required for accurate scope determination during analysis
    """
    node.parent = parent
    for child in ast.iter_child_nodes(node):
        set_parents(child, node)


def deep_merge(source: dict, update: dict) -> dict:
    """Recursively merge two dictionaries.

    Args:
        source: Base dictionary to be updated
        update: Dictionary with update values

    Returns:
        Reference to the modified source dictionary
    """
    for key, val in update.items():
        if isinstance(val, dict) and isinstance(source.get(key), dict):
            source[key] = deep_merge(source.get(key, {}), val)
        elif isinstance(val, list) and isinstance(source.get(key), list):
            source[key] = list(set(source[key] + val))
        else:
            source[key] = val
    return source


class Targets:
    """
    Target processor for monitoring file changes and module structures.

    Supported syntax:
    1. Module: 'package.module'
    2. Class: 'package.module:ClassName'
    3. Class attribute: 'package.module:ClassName.attribute'
    4. Class method: 'package.module:ClassName.method()'
    5. Function: 'package.module:function()'
    6. Global variable: 'package.module::GLOBAL_VAR'
    """

    def __init__(self, targets: TargetsType, exclude_targets: TargetsType = None):
        """
        Initialize target processor.

        Args:
            targets: Monitoring targets in various formats
            exclude_targets: Exclusion targets in same formats
        """
        targets, exclude_targets = self._check_targets(targets, exclude_targets)
        self.filename_targets: Set = set()
        self.targets: TargetsDict = self._process_targets(targets)
        self.exclude_targets: TargetsDict = self._process_targets(exclude_targets)
        self.processed_targets: TargetsDict = self._diff_targets()

    def _check_targets(self, targets: TargetsType, exclude_targets: TargetsType) -> Tuple[TargetsType, TargetsType]:
        """
        Normalize and validate target inputs.

        Args:
            targets: Raw monitoring targets input
            exclude_targets: Raw exclusion targets input

        Returns:
            Tuple[TargetsType, TargetsType]: Normalized (targets, exclude_targets)
        """
        if isinstance(targets, str):
            targets = [targets]
        if isinstance(exclude_targets, str):
            exclude_targets = [exclude_targets]
        for exclude_target in exclude_targets or []:
            if isinstance(exclude_target, str) and exclude_target.endswith('.py'):
                log_error("Unsupported .py files in exclude_target")
        return targets, exclude_targets

    def _process_targets(self, targets: TargetsType) -> TargetsDict:
        """
        Convert heterogeneous targets to structured data model.

        Args:
            targets: List of targets

        Returns:
            TargetsDict: Hierarchical structure:
        """
        processed_targets: TargetsDict = {}
        for target in targets or []:
            if isinstance(target, str) and target.endswith('.py'):
                self.filename_targets.add(target)
            elif isinstance(target, (str, ModuleType, ClassType, FunctionType, MethodType)):
                module_path, target_details = self._parse_target(target)
                existing_details = processed_targets.setdefault(module_path, {})
                processed_targets[module_path] = deep_merge(existing_details, target_details)
            else:
                log_warn(f"Unsupported target type: {type(target)}")
        return processed_targets

    def _parse_target(self, target: Union[str, ModuleType, ClassType, FunctionType, MethodType]) -> tuple:
        """
        Parse different target formats into module structure.

        Args:
            target: Target specification

        Returns:
            tuple: (module_path, parsed_structure)
        """
        if isinstance(target, ModuleType):
            return self._parse_module(target)
        if isinstance(target, ClassType):
            return self._parse_class(target)
        if isinstance(target, (FunctionType, MethodType)):
            return self._parse_function(target)
        return self._parse_string(target)

    def _parse_function(self, func: Union[FunctionType, MethodType]) -> tuple:
        """Parse function object and create module structure containing this function or method

        Args:
            func: Function object to parse

        Returns:
            tuple: (module name, module structure containing only this function or method)
        """
        # Check if this is a class method (bound to class)
        if hasattr(func, '__self__') and isinstance(func.__self__, type):
            cls = func.__self__
            module = inspect.getmodule(cls)
            module_name = module.__name__ if module else ''
            return (
                module_name,
                {
                    'classes': {cls.__name__: {'methods': [func.__name__], 'attributes': [], 'track_all': False}},
                    'functions': [],
                    'globals': [],
                },
            )

        # Check if this is a static/class method using qualname (e.g. 'Class.method')
        if hasattr(func, '__qualname__') and '.' in func.__qualname__:
            class_name, method_name = func.__qualname__.split('.', 1)
            module = inspect.getmodule(func)
            if module and hasattr(module, class_name):
                cls = getattr(module, class_name)
                if isinstance(cls, type):
                    module_name = module.__name__ if module else ''
                    return (
                        module_name,
                        {
                            'classes': {class_name: {'methods': [method_name], 'attributes': [], 'track_all': False}},
                            'functions': [],
                            'globals': [],
                        },
                    )

        # Regular function handling
        module = inspect.getmodule(func)
        module_name = module.__name__ if module else ''
        function_name = func.__name__
        parsed_structure = {'classes': {}, 'functions': [function_name], 'globals': []}
        return (module_name, parsed_structure)

    def _parse_module(self, module: ModuleType) -> tuple:
        """Parse module structure using AST analysis.

        Args:
            module: Python module object to analyze

        Returns:
            tuple: (module_name, parsed_structure) pair
        """
        return (module.__name__, self._parse_module_by_name(module.__name__))

    def _parse_class(self, cls: ClassType) -> tuple:
        """Parse class object and create module structure containing this class

        Args:
            cls: Class object to parse

        Returns:
            tuple: (module name, module structure containing only this class)
        """
        module = inspect.getmodule(cls)
        module_name = module.__name__ if module else ''
        class_name = cls.__name__
        class_details = {'methods': [], 'attributes': [], 'track_all': True}  # Flag to track all methods and attributes
        parsed_structure = {'classes': {class_name: class_details}, 'functions': [], 'globals': []}
        return (module_name, parsed_structure)

    def _parse_string(self, target: str) -> tuple:
        """Parse string-formatted target definitions

        Args:
            target: Target definition string

        Returns:
            tuple: (module_path, parsed_structure)
        """
        # Handle global variable syntax
        if '::' in target:
            module_part, _, global_var = target.partition('::')
            spec = importlib.util.find_spec(module_part)
            if spec is None:
                log_warn(f"Module {module_part} not found")
                return (module_part, {'globals': []})
            resolved_module_name = spec.name
            return (resolved_module_name, {'globals': [global_var.strip()]})

        # Split module path and symbol definition
        module_part, _, symbol = target.partition(':')
        spec = importlib.util.find_spec(module_part)
        if spec is None:
            log_warn(f"Module {module_part} not found")
            return (module_part, {'classes': {}, 'functions': [], 'globals': []})
        resolved_module_name = spec.name
        full_module = self._parse_module_by_name(resolved_module_name)

        if not symbol:
            return (resolved_module_name, full_module)

        details = {'classes': {}, 'functions': [], 'globals': []}
        current_symbol = symbol

        # Parse class members (methods or attributes)
        if '.' in symbol:
            class_part, _, member = current_symbol.partition('.')
            if class_part in full_module['classes']:
                class_info = full_module['classes'][class_part]
                if member.endswith('()'):
                    method_name = member[:-2]
                    # Directly add method without checking if it exists in class_info
                    details['classes'][class_part] = {
                        'methods': [method_name],
                        'attributes': [],
                        'track_all': False,  # Not tracking all, just specific method
                    }
                else:
                    # Directly add attribute without checking if it exists in class_info
                    details['classes'][class_part] = {
                        'methods': [],
                        'attributes': [member],
                        'track_all': False,  # Not tracking all, just specific attribute
                    }
        else:
            if current_symbol.endswith('()'):
                func_name = current_symbol[:-2]
                if func_name in full_module['functions']:
                    details['functions'].append(func_name)
            elif current_symbol in full_module['classes']:
                details['classes'][current_symbol] = {
                    'methods': [],
                    'attributes': [],
                    'track_all': True,  # Track entire class
                }

        return (resolved_module_name, details)

    def _parse_module_by_name(self, module_name: str, recursive: bool = True) -> ModuleStructure:
        """Locate and parse module structure by its import name, supporting recursive parsing.

        Args:
            module_name: Full dotted import path (e.g. 'package.module')
            recursive: Whether to recursively parse submodules

        Returns:
            ModuleStructure: Parsed module structure with submodules if recursive=True
        """
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            log_warn(f"Module {module_name} not found")
            return {'classes': {}, 'functions': [], 'globals': []}

        # Parse the current module
        module_structure = {'classes': {}, 'functions': [], 'globals': []}
        if spec.origin and spec.origin.endswith('.py'):
            module_structure = self._parse_py_file(spec.origin)

        # Recursively parse submodules if enabled
        if recursive and hasattr(spec, 'submodule_search_locations') and spec.submodule_search_locations:
            for _, submodule_name, is_pkg in pkgutil.iter_modules(spec.submodule_search_locations):
                full_submodule_name = f"{module_name}.{submodule_name}"
                try:
                    submodule_structure = self._parse_module_by_name(full_submodule_name, recursive)
                    # Add submodule structure to current module
                    module_structure[submodule_name] = submodule_structure
                except Exception as e:
                    log_warn(f"Failed to parse submodule {full_submodule_name}: {str(e)}")

        return module_structure

    def _parse_py_file(self, file_path: str) -> ModuleStructure:
        """Analyze Python file structure using Abstract Syntax Tree.

        Args:
            file_path: Absolute path to Python file

        Returns:
            ModuleStructure: Parsed file structure dictionary

        Raises:
            Logs error on parsing failure
        """
        parsed_structure: ModuleStructure = {'classes': {}, 'functions': [], 'globals': []}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            set_parents(tree, None)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'methods': [],
                        'attributes': [],
                        'track_all': True,  # Flag to track all methods and attributes
                    }
                    parsed_structure['classes'][node.name] = class_info
                elif isinstance(node, ast.FunctionDef):
                    if not any(isinstance(parent, ast.ClassDef) for parent in iter_parents(node)):
                        parsed_structure['functions'].append(node.name)
                elif isinstance(node, ast.Assign):
                    self._process_assignment(node, parsed_structure)

        except Exception as e:
            log_error(f"Failed to parse {file_path}: {str(e)}")

        return parsed_structure

    def _extract_class_attributes(self, class_node: ast.ClassDef) -> List[str]:
        """Extract class attributes from AST node.

        Includes:
        - Assignment statements
        - Annotated assignments
        """
        attrs = []
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        attrs.append(target.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                attrs.append(node.target.id)
        return attrs

    def _flatten_module_structure(self, module_path: str, module_structure: dict, result: TargetsDict):
        """Flatten nested module structure into a TargetsDict.

        Args:
            module_path: Full module path
            module_structure: Module structure dictionary
            result: TargetsDict to populate
        """
        # Extract standard sections (classes, functions, globals)
        standard_sections = {
            'classes': module_structure.get('classes', {}),
            'functions': module_structure.get('functions', []),
            'globals': module_structure.get('globals', []),
        }

        # Only add to result if there's content
        if any([standard_sections['classes'], standard_sections['functions'], standard_sections['globals']]):
            result[module_path] = standard_sections

        # Process nested submodules
        for key, value in module_structure.items():
            if key not in ['classes', 'functions', 'globals'] and isinstance(value, dict):
                submodule_path = f"{module_path}.{key}"
                self._flatten_module_structure(submodule_path, value, result)

    def _diff_targets(self) -> TargetsDict:
        """Calculate effective targets by excluding specified patterns.

        Returns:
            Filtered targets dictionary after applying exclusion rules
        """
        filtered_targets: TargetsDict = {}
        for module_path, target_details in self.targets.items():
            exclude_details = self.exclude_targets.get(module_path, {})

            # Handle track_all exclusion at the module level
            filtered_classes = self._diff_level(target_details.get('classes', {}), exclude_details.get('classes', {}))

            # Calculate filtered target details
            filtered_details = {
                'classes': filtered_classes,
                'functions': list(set(target_details.get('functions', [])) - set(exclude_details.get('functions', []))),
                'globals': list(set(target_details.get('globals', [])) - set(exclude_details.get('globals', []))),
            }

            # Process nested submodules
            for key, value in target_details.items():
                if key not in ['classes', 'functions', 'globals'] and isinstance(value, dict):
                    submodule_path = f"{module_path}.{key}"
                    submodule_exclude = exclude_details.get(key, {})
                    filtered_sub = self._diff_level(value, submodule_exclude)
                    if filtered_sub:
                        filtered_details[key] = filtered_sub

            # Flatten the module structure
            self._flatten_module_structure(module_path, filtered_details, filtered_targets)

        return filtered_targets

    def _diff_level(self, target: dict, exclude: dict) -> dict:
        """Recursively filter nested structures by exclusion rules.

        Args:
            target: Original nested structure (dict of dicts)
            exclude: Exclusion patterns to apply

        Returns:
            dict: Filtered structure with empty containers preserved
        """
        diff = {}
        for key, value in target.items():
            filtered = None

            if key in exclude:
                if isinstance(value, dict) and isinstance(exclude[key], dict):
                    # Handle class details with track_all flag
                    if (
                        'track_all' in value
                        and value['track_all']
                        and 'track_all' in exclude[key]
                        and exclude[key]['track_all']
                    ):
                        # If both are tracking all, exclude the entire class
                        filtered = None
                    else:
                        filtered = self._diff_level(value, exclude[key])
                elif isinstance(value, list) and isinstance(exclude[key], list):
                    filtered = list(set(value) - set(exclude[key]))
                elif value != exclude[key]:
                    filtered = value
            else:
                filtered = value

            if filtered is None:
                # Skip this key entirely (excluded)
                continue
            elif isinstance(filtered, dict):
                diff[key] = filtered
            elif isinstance(filtered, list):
                diff[key] = filtered if filtered else []
            else:
                diff[key] = filtered

        return diff

    def _process_assignment(self, node: ast.Assign, result: ModuleStructure):
        """Extract global variables from assignment AST nodes.

        Handles two patterns:
        1. Simple assignments: `var = value`
        2. Tuple unpacking: `a, b = (1, 2)`

        Args:
            node: AST assignment node to analyze
            result: ModuleStructure to update with found globals
        """
        if any(isinstance(parent, ast.ClassDef) for parent in iter_parents(node)):
            return

        for assign_target in node.targets:
            if isinstance(assign_target, ast.Name):
                result['globals'].append(assign_target.id)
            elif isinstance(assign_target, ast.Tuple):
                for element in assign_target.elts:
                    if isinstance(element, ast.Name):
                        result['globals'].append(element.id)

    def get_processed_targets(self) -> TargetsDict:
        """Retrieve final monitoring targets after exclusion processing.

        Returns:
            TargetsDict: Filtered dictionary containing:
                - classes: Non-excluded class methods
                - functions: Non-excluded functions
                - globals: Non-excluded global variables

        Example:
            {
                'module.path': {
                    'classes': {
                        'ClassName': {
                            'methods': [...],
                            'attributes': [...]
                        }
                    },
                    'functions': [...],
                    'globals': [...]
                }
            }
        """
        return self.processed_targets

    def serialize_targets(self, indent=2):
        """Serialize objects that JSON cannot handle by default.

        Converts sets to lists, and other objects to their __dict__ or string representation.
        If the input is a dictionary with more than 8 top-level keys, only the keys are retained
        with a placeholder value and a warning message is added.

        Args:
            indent: Number of spaces for JSON indentation

        Returns:
            str: JSON serialized string
        """

        def target_handler(o):
            if isinstance(o, set):
                return list(o)
            if hasattr(o, '__dict__'):
                return o.__dict__
            return str(o)

        if len(self.processed_targets) > 80000:
            truncated_obj = {key: "..." for key in self.processed_targets.keys()}
            truncated_obj["Warning: too many top-level keys, only showing values like"] = "..."
            return json.dumps(truncated_obj, indent=indent, default=target_handler)

        return json.dumps(self.processed_targets, indent=indent, default=target_handler)

    def get_filename_targets(self) -> Set:
        """Get monitored filesystem paths.

        Returns:
            Set[str]: Absolute paths to Python files being monitored,
            including both directly specified files and module origins
        """
        return self.filename_targets
