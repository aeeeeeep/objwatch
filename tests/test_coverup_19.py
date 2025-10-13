# file: objwatch/targets.py:417-437
# asked: {"lines": [417, 428, 429, 431, 432, 433, 434, 435, 436, 437], "branches": [[428, 429], [428, 431], [431, 0], [431, 432], [432, 433], [432, 434], [434, 431], [434, 435], [435, 431], [435, 436], [436, 435], [436, 437]]}
# gained: {"lines": [417, 428, 429, 431, 432, 433, 434, 435, 436, 437], "branches": [[428, 429], [428, 431], [431, 0], [431, 432], [432, 433], [432, 434], [434, 435], [435, 431], [435, 436], [436, 435], [436, 437]]}

import ast
import pytest
from objwatch.targets import Targets


class TestTargetsProcessAssignment:
    def test_process_assignment_simple_assignment(self):
        """Test simple assignment: var = value"""
        targets = Targets([])
        result = {'globals': []}
        node = ast.parse("x = 42").body[0]
        targets._process_assignment(node, result)
        assert result['globals'] == ['x']

    def test_process_assignment_tuple_unpacking(self):
        """Test tuple unpacking: a, b = (1, 2)"""
        targets = Targets([])
        result = {'globals': []}
        node = ast.parse("a, b = (1, 2)").body[0]
        targets._process_assignment(node, result)
        assert sorted(result['globals']) == ['a', 'b']

    def test_process_assignment_inside_function(self, monkeypatch):
        """Test assignment inside function definition (should be skipped)"""
        targets = Targets([])
        result = {'globals': []}

        # Create a function with an assignment inside
        func_code = """
def test_func():
    x = 42
"""
        func_node = ast.parse(func_code).body[0]
        assignment_node = func_node.body[0]

        # Mock iter_parents to return function as parent
        def mock_iter_parents(node):
            return [func_node]

        monkeypatch.setattr('objwatch.targets.iter_parents', mock_iter_parents)
        targets._process_assignment(assignment_node, result)
        assert result['globals'] == []

    def test_process_assignment_inside_class(self, monkeypatch):
        """Test assignment inside class definition (should be skipped)"""
        targets = Targets([])
        result = {'globals': []}

        # Create a class with an assignment inside
        class_code = """
class TestClass:
    x = 42
"""
        class_node = ast.parse(class_code).body[0]
        assignment_node = class_node.body[0]

        # Mock iter_parents to return class as parent
        def mock_iter_parents(node):
            return [class_node]

        monkeypatch.setattr('objwatch.targets.iter_parents', mock_iter_parents)
        targets._process_assignment(assignment_node, result)
        assert result['globals'] == []

    def test_process_assignment_complex_tuple(self):
        """Test complex tuple unpacking with nested structure - only top-level names are captured"""
        targets = Targets([])
        result = {'globals': []}
        node = ast.parse("a, (b, c) = (1, (2, 3))").body[0]
        targets._process_assignment(node, result)
        # The current implementation only captures top-level names in tuples
        # Nested tuples like (b, c) are not processed recursively
        assert result['globals'] == ['a']

    def test_process_assignment_multiple_targets(self):
        """Test assignment with multiple targets: x = y = 42"""
        targets = Targets([])
        result = {'globals': []}
        node = ast.parse("x = y = 42").body[0]
        targets._process_assignment(node, result)
        assert sorted(result['globals']) == ['x', 'y']

    def test_process_assignment_tuple_with_non_name_elements(self):
        """Test tuple unpacking with non-name elements (should be ignored)"""
        targets = Targets([])
        result = {'globals': []}
        node = ast.parse("a, b[0] = (1, 2)").body[0]
        targets._process_assignment(node, result)
        # Only 'a' should be captured, 'b[0]' is not a Name node
        assert result['globals'] == ['a']
