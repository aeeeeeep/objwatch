# MIT License
# Copyright (c) 2025 aeeeeeep

import ast
import inspect
import importlib
from types import ModuleType, FunctionType
from typing import Tuple, List, Union, Dict, Set, Any

from .utils.logger import log_error, log_warn

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


class Targets:
    """
    Target processor for monitoring file changes and module structures.

    Handles:
    - File paths (path/to/module.py)
    - Module paths (package.module)
    - Class selectors (package.module:ClassName)
    - Method selectors (package.module:ClassName.method)
    - Global variables (package.module::global_var)
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
                {
                    'module': {
                        'classes': {'ClassName': {'methods': [...]}},
                        'functions': [...],
                        'globals': [...]
                    }
                }
        """
        processed: TargetsDict = {}
        for target in targets or []:
            if isinstance(target, str) and target.endswith('.py'):
                self.filename_targets.add(target)
            elif isinstance(target, (str, ModuleType, FunctionType, type)):
                module_path, details = self._parse_target(target)
                processed.setdefault(module_path, {}).update(details)
            else:
                log_warn(f"Unsupported target type: {type(target)}")
        return processed

    def _parse_target(self, target: Union[str, ModuleType, type, FunctionType]) -> tuple[str, ModuleStructure]:
        """
        Parse different target formats into module structure.

        Args:
            target: Target specification (module/class/function/string selector)

        Returns:
            tuple: (module_path, parsed_structure)
        """
        if isinstance(target, ModuleType):
            return self._parse_module(target)
        if isinstance(target, type):
            return self._parse_class(target)
        if isinstance(target, FunctionType):
            return self._parse_function(target)
        return self._parse_string(target)

    def _parse_function(self, func: FunctionType) -> tuple[str, ModuleStructure]:
        """Parse function object and integrate into module structure.

        Args:
            func: Function object to parse

        Returns:
            tuple: (module_path, updated_structure) with function added
        """
        module = inspect.getmodule(func)
        module_struct = self._parse_module(module)
        func_name = func.__name__
        if 'functions' not in module_struct[1]:
            module_struct[1]['functions'] = []
        if func_name not in module_struct[1]['functions']:
            module_struct[1]['functions'].append(func_name)
        return module_struct

    def _parse_module(self, module: ModuleType) -> tuple[str, ModuleStructure]:
        """Parse module structure using AST analysis.

        Args:
            module: Python module object to analyze

        Returns:
            tuple: (module_name, parsed_structure) pair
        """
        file_path = inspect.getfile(module)
        return (module.__name__, self._parse_py_file(file_path))

    def _parse_class(self, cls: type) -> tuple[str, ModuleStructure]:
        """Parse class structure including methods and attributes.

        Args:
            cls: Class object to analyze

        Returns:
            tuple: (module_path, updated_structure) with class info added
        """
        module = inspect.getmodule(cls)
        module_struct = self._parse_module(module)
        class_info = {
            'methods': [m[0] for m in inspect.getmembers(cls, inspect.isfunction)],
            'attributes': list(cls.__dict__.keys()),
        }
        module_struct[1]['classes'][cls.__name__] = class_info
        return module_struct

    def _parse_string(self, target: str) -> tuple[str, ModuleStructure]:
        """Parse string-formatted target specification.

        Handles three patterns:
        1. Function signatures: 'module:function(params)'
        2. Hierarchical selectors: 'module:class:method'
        3. Global variables: 'module::global_var'

        Args:
            target: String-formatted target specification

        Returns:
            tuple: (module_path, parsed_structure)
        """
        if ':' in target and '(' in target:
            module_part, func_signature = target.split(':', 1)
            details = {'functions': [func_signature]}
            return (module_part, details)
        if ':' not in target:
            return (target, self._parse_module_by_name(target))

        parts = target.split(':')
        module_part = parts[0]
        details = {}

        if len(parts) > 1 and parts[1]:
            class_part = parts[1]
            details['classes'] = {class_part: {}}

            if len(parts) > 2 and parts[2]:
                method_part = parts[2]
                details['classes'][class_part]['methods'] = [method_part]

        if target.count(':') == 2 and parts[1] == '':
            details['globals'] = [parts[2]]

        return (module_part, details)

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

        Processes:
        - Class definitions with methods and attributes
        - Top-level function definitions
        - Global variable assignments

        Args:
            file_path: Absolute path to Python file

        Returns:
            ModuleStructure: Parsed file structure dictionary

        Raises:
            Logs error on parsing failure
        """
        result: ModuleStructure = {'classes': {}, 'functions': [], 'globals': []}

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
                    result['classes'][node.name] = class_info
                elif isinstance(node, ast.FunctionDef):
                    if not any(isinstance(parent, ast.ClassDef) for parent in iter_parents(node)):
                        result['functions'].append(node.name)
                elif isinstance(node, ast.Assign):
                    self._process_assignment(node, result)

        except Exception as e:
            log_error(f"Failed to parse {file_path}: {str(e)}")

        return result

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
        diff: TargetsDict = {}
        for module_path, target_details in self.targets.items():
            exclude_details = self.exclude_targets.get(module_path, {})

            diff_details = {
                'classes': self._diff_level(target_details.get('classes', {}), exclude_details.get('classes', {})),
                'functions': list(set(target_details.get('functions', [])) - set(exclude_details.get('functions', []))),
                'globals': list(set(target_details.get('globals', [])) - set(exclude_details.get('globals', []))),
            }

            if any([diff_details['classes'], diff_details['functions'], diff_details['globals']]):
                diff[module_path] = diff_details

        return diff

    def _diff_level(self, target: dict, exclude: dict) -> dict:
        """Recursively filter nested structures by exclusion rules.

        Args:
            target: Original nested structure (dict of dicts)
            exclude: Exclusion patterns to apply

        Returns:
            dict: Filtered structure with excluded elements removed
        """
        diff = {}
        for key, value in target.items():
            if key not in exclude:
                diff[key] = value
            else:
                filtered = {k: v for k, v in value.items() if k not in exclude[key] or v != exclude[key][k]}
                if filtered:
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
        for target in node.targets:
            if isinstance(target, ast.Name):
                result['globals'].append(target.id)
            elif isinstance(target, ast.Tuple):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        result['globals'].append(elt.id)

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
                    'classes': {'ClassName': {'methods': [...]}},
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
