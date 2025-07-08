# MIT License
# Copyright (c) 2025 aeeeeeep

import ast
import inspect
import importlib
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

    def _parse_target(
        self, target: Union[str, ModuleType, ClassType, FunctionType, MethodType]
    ) -> tuple:
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
                    'classes': {cls.__name__: {'methods': [func.__name__], 'attributes': []}},
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
                            'classes': {class_name: {'methods': [method_name], 'attributes': []}},
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
        file_path = inspect.getfile(module)
        return (module.__name__, self._parse_py_file(file_path))

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
        class_methods = [method[0] for method in inspect.getmembers(cls, inspect.isfunction)]
        class_attributes = list(cls.__dict__.keys())
        class_details = {
            'methods': class_methods,
            'attributes': class_attributes,
        }
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
                    if method_name in class_info['methods']:
                        details['classes'][class_part] = {
                            'methods': [method_name],
                        }
                else:
                    if member in class_info['attributes']:
                        details['classes'][class_part] = {'attributes': [member]}
        else:
            if current_symbol.endswith('()'):
                func_name = current_symbol[:-2]
                if func_name in full_module['functions']:
                    details['functions'].append(func_name)
            elif current_symbol in full_module['classes']:
                class_info = full_module['classes'][current_symbol]
                details['classes'][current_symbol] = {
                    'methods': class_info['methods'],
                    'attributes': class_info['attributes'],
                }

        return (resolved_module_name, details)

    def _parse_module_by_name(self, module_name: str) -> ModuleStructure:
        """Locate and parse module structure by its import name.

        Args:
            module_name: Full dotted import path (e.g. 'package.module')

        Returns:
            ModuleStructure: Parsed module structure if found, otherwise
                returns empty structure with warning logged
        """
        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin:
            return self._parse_py_file(spec.origin)
        log_warn(f"Module {module_name} not found")
        return {'classes': {}, 'functions': [], 'globals': []}

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
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'attributes': self._extract_class_attributes(node),
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

    def _diff_targets(self) -> TargetsDict:
        """Calculate effective targets by excluding specified patterns.

        Returns:
            Filtered targets dictionary after applying exclusion rules
        """
        filtered_targets: TargetsDict = {}
        for module_path, target_details in self.targets.items():
            exclude_details = self.exclude_targets.get(module_path, {})

            # Calculate filtered target details
            filtered_details = {
                'classes': self._diff_level(target_details.get('classes', {}), exclude_details.get('classes', {})),
                'functions': list(set(target_details.get('functions', [])) - set(exclude_details.get('functions', []))),
                'globals': list(set(target_details.get('globals', [])) - set(exclude_details.get('globals', []))),
            }

            # Only keep targets with content
            if any([filtered_details['classes'], filtered_details['functions'], filtered_details['globals']]):
                filtered_targets[module_path] = filtered_details

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

            if key not in exclude:
                filtered = value
            else:
                if isinstance(value, dict) and isinstance(exclude[key], dict):
                    filtered = self._diff_level(value, exclude[key])
                elif isinstance(value, list) and isinstance(exclude[key], list):
                    filtered = list(set(value) - set(exclude[key]))
                elif value != exclude[key]:
                    filtered = value

            if isinstance(filtered, dict):
                diff[key] = filtered
            elif isinstance(filtered, list):
                diff[key] = filtered if filtered else []
            else:
                diff[key] = filtered if filtered is not None else value

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

    def get_filename_targets(self) -> Set:
        """Get monitored filesystem paths.

        Returns:
            Set[str]: Absolute paths to Python files being monitored,
            including both directly specified files and module origins
        """
        return self.filename_targets
