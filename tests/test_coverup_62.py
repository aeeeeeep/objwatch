# file: objwatch/targets.py:21-34
# asked: {"lines": [21, 32, 33, 34], "branches": [[32, 0], [32, 33]]}
# gained: {"lines": [21, 32, 33, 34], "branches": [[32, 0], [32, 33]]}

import pytest
import ast
from objwatch.targets import iter_parents


class MockNode:
    def __init__(self, parent=None):
        self.parent = parent


def test_iter_parents_single_parent():
    """Test iter_parents with one parent node."""
    child = MockNode()
    parent = MockNode()
    child.parent = parent

    parents = list(iter_parents(child))
    # The function yields until parent is None
    assert len(parents) == 2
    assert parents[0] == parent
    assert parents[1] is None


def test_iter_parents_multiple_parents():
    """Test iter_parents with multiple parent nodes in chain."""
    grandchild = MockNode()
    child = MockNode()
    parent = MockNode()
    grandparent = MockNode()

    grandchild.parent = child
    child.parent = parent
    parent.parent = grandparent

    parents = list(iter_parents(grandchild))
    assert len(parents) == 4
    assert parents[0] == child
    assert parents[1] == parent
    assert parents[2] == grandparent
    assert parents[3] is None


def test_iter_parents_no_parent():
    """Test iter_parents with node that has no parent attribute."""
    node_without_parent = object()

    parents = list(iter_parents(node_without_parent))
    assert parents == []


def test_iter_parents_parent_is_none():
    """Test iter_parents with node that has parent attribute set to None."""
    node = MockNode(parent=None)

    parents = list(iter_parents(node))
    assert len(parents) == 1
    assert parents[0] is None


def test_iter_parents_generator_behavior():
    """Test that iter_parents returns a generator and can be used in loops."""
    child = MockNode()
    parent = MockNode()
    grandparent = MockNode()

    child.parent = parent
    parent.parent = grandparent

    # Test generator behavior
    generator = iter_parents(child)
    assert next(generator) == parent
    assert next(generator) == grandparent
    assert next(generator) is None

    # Test StopIteration
    with pytest.raises(StopIteration):
        next(generator)
