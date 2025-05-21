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
    while hasattr(node, 'parent'):
        node = node.parent
        yield node


class Targets:
    """
    Targets class to process and determine the set of target files to monitor.
    """

    def __init__(self, targets: TargetsType, exclude_targets: TargetsType = None):
        """
        新参数规则：
        - 字符串格式支持：
          * 文件路径：path/to/module.py
          * 模块路径：package.module
          * 类选择器：package.module:ClassName
          * 方法选择器：package.module:ClassName.method
          * 全局变量：package.module::global_var
        """
        targets, exclude_targets = self._check_targets(targets, exclude_targets)
        self.filename_targets: Set = set()
        self.targets: TargetsDict = self._process_targets(targets)
        self.exclude_targets: TargetsDict = self._process_targets(exclude_targets)
        self.processed_targets: TargetsDict = self._diff_targets()

    def _check_targets(self, targets: TargetsType, exclude_targets: TargetsType) -> Tuple[TargetsType, TargetsType]:
        if isinstance(targets, str):
            targets = [targets]
        if isinstance(exclude_targets, str):
            exclude_targets = [exclude_targets]
        for exclude_target in exclude_targets or []:
            if isinstance(exclude_target, str) and exclude_target.endswith('.py'):
                log_error("Unsupported .py files in exclude_target")
        return targets, exclude_targets

    def _process_targets(self, targets: TargetsType) -> TargetsDict:
        processed: TargetsDict = {}
        for target in targets or []:
            if isinstance(target, str) and target.endswith('.py'):
                # 处理文件路径
                self.filename_targets.add(target)
            elif isinstance(target, (str, ModuleType, FunctionType, type)):
                # 处理模块/类/方法
                module_path, details = self._parse_target(target)
                processed.setdefault(module_path, {}).update(details)
            else:
                log_warn(f"Unsupported target type: {type(target)}")
        return processed

    def _parse_target(self, target: Union[str, ModuleType, type, FunctionType]) -> tuple[str, ModuleStructure]:
        """解析不同形式的target"""
        if isinstance(target, ModuleType):
            return self._parse_module(target)
        if isinstance(target, type):
            return self._parse_class(target)
        if isinstance(target, FunctionType):  # 新增函数解析
            return self._parse_function(target)
        return self._parse_string(target)

    def _parse_function(self, func: FunctionType) -> tuple[str, ModuleStructure]:
        """解析函数对象"""
        module = inspect.getmodule(func)
        module_struct = self._parse_module(module)
        func_name = func.__name__
        # 将函数添加到模块的functions列表
        if 'functions' not in module_struct[1]:
            module_struct[1]['functions'] = []
        if func_name not in module_struct[1]['functions']:
            module_struct[1]['functions'].append(func_name)
        return module_struct

    def _parse_module(self, module: ModuleType) -> tuple[str, ModuleStructure]:
        """解析模块对象"""
        file_path = inspect.getfile(module)
        return (module.__name__, self._parse_py_file(file_path))

    def _parse_class(self, cls: type) -> tuple[str, ModuleStructure]:
        """解析类对象"""
        module = inspect.getmodule(cls)
        module_struct = self._parse_module(module)
        class_info = {
            'methods': [m[0] for m in inspect.getmembers(cls, inspect.isfunction)],
            'attributes': list(cls.__dict__.keys()),
        }
        module_struct[1]['classes'][cls.__name__] = class_info
        return module_struct

    def _parse_string(self, target: str) -> tuple[str, ModuleStructure]:
        """解析字符串格式"""
        if ':' in target and '(' in target:  # 新增函数签名支持
            module_part, func_signature = target.split(':', 1)
            details = {'functions': [func_signature]}
            return (module_part, details)
        if ':' not in target:
            return (target, self._parse_module_by_name(target))

        # 分解模块:类:方法
        parts = target.split(':')
        module_part = parts[0]
        details = {}

        # 解析类和方法
        if len(parts) > 1 and parts[1]:
            class_part = parts[1]
            details['classes'] = {class_part: {}}

            if len(parts) > 2 and parts[2]:
                method_part = parts[2]
                details['classes'][class_part]['methods'] = [method_part]

        # 解析全局变量
        if target.count(':') == 2 and parts[1] == '':
            details['globals'] = [parts[2]]

        return (module_part, details)

    def _parse_module_by_name(self, module_name: str) -> ModuleStructure:
        """通过模块名解析模块结构"""
        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin:
            return self._parse_py_file(spec.origin)
        log_warn(f"Module {module_name} not found")
        return {'classes': {}, 'functions': [], 'globals': []}

    def _parse_py_file(self, file_path: str) -> ModuleStructure:
        """使用AST解析Python文件结构"""
        result: ModuleStructure = {'classes': {}, 'functions': [], 'globals': []}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            # 新增parent属性设置逻辑
            def set_parents(node, parent):
                node.parent = parent
                for child in ast.iter_child_nodes(node):
                    set_parents(child, node)

            set_parents(tree, None)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'attributes': self._extract_class_attributes(node),
                    }
                    result['classes'][node.name] = class_info
                elif isinstance(node, ast.FunctionDef):
                    # 修复parent检查逻辑
                    if not any(isinstance(parent, ast.ClassDef) for parent in iter_parents(node)):
                        result['functions'].append(node.name)
                elif isinstance(node, ast.Assign):
                    self._process_assignment(node, result)

        except Exception as e:
            log_error(f"Failed to parse {file_path}: {str(e)}")

        return result

    def _extract_class_attributes(self, class_node: ast.ClassDef) -> List[str]:
        """提取类属性"""
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
        """计算目标差异"""
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
        """递归差异计算"""
        diff = {}
        for key, value in target.items():
            if key not in exclude:
                diff[key] = value
            else:
                # 递归比较子项
                filtered = {k: v for k, v in value.items() if k not in exclude[key] or v != exclude[key][k]}
                if filtered:
                    diff[key] = filtered
        return diff

    def _process_assignment(self, node: ast.Assign, result: ModuleStructure):
        """处理赋值语句以提取全局变量"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # 简单变量赋值：x = 10
                result['globals'].append(target.id)
            elif isinstance(target, ast.Tuple):
                # 元组解包：a, b = 1, 2
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        result['globals'].append(elt.id)

    def get_processed_targets(self) -> TargetsDict:
        return self.processed_targets

    def get_filename_targets(self) -> Set:
        return self.filename_targets
