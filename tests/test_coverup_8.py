# file: objwatch/targets.py:48-65
# asked: {"lines": [48, 58, 59, 60, 61, 62, 64, 65], "branches": [[58, 59], [58, 65], [59, 60], [59, 61], [61, 62], [61, 64]]}
# gained: {"lines": [48, 58, 59, 60, 61, 62, 64, 65], "branches": [[58, 59], [58, 65], [59, 60], [59, 61], [61, 62], [61, 64]]}

import pytest
from objwatch.targets import deep_merge


def test_deep_merge_dict_recursion():
    """Test deep_merge with nested dictionaries to cover recursive dict merging."""
    source = {"a": {"b": 1, "c": 2}}
    update = {"a": {"b": 3, "d": 4}}
    result = deep_merge(source, update)
    expected = {"a": {"b": 3, "c": 2, "d": 4}}
    assert result == expected
    assert result is source  # Should return reference to source


def test_deep_merge_list_union():
    """Test deep_merge with lists to cover list union functionality."""
    source = {"items": [1, 2, 3]}
    update = {"items": [3, 4, 5]}
    result = deep_merge(source, update)
    expected_items = sorted([1, 2, 3, 4, 5])  # set union removes duplicates
    assert sorted(result["items"]) == expected_items
    assert result is source


def test_deep_merge_scalar_overwrite():
    """Test deep_merge with scalar values to cover the else branch."""
    source = {"name": "old", "value": 10}
    update = {"name": "new", "value": 20}
    result = deep_merge(source, update)
    expected = {"name": "new", "value": 20}
    assert result == expected
    assert result is source


def test_deep_merge_mixed_types():
    """Test deep_merge with mixed nested structures."""
    source = {"config": {"debug": True, "items": [1, 2]}, "name": "test"}
    update = {"config": {"debug": False, "items": [2, 3], "timeout": 30}, "name": "updated"}
    result = deep_merge(source, update)
    expected = {"config": {"debug": False, "items": [1, 2, 3], "timeout": 30}, "name": "updated"}
    assert result["config"]["debug"] == False
    assert sorted(result["config"]["items"]) == [1, 2, 3]
    assert result["config"]["timeout"] == 30
    assert result["name"] == "updated"
    assert result is source


def test_deep_merge_empty_dicts():
    """Test deep_merge with empty dictionaries."""
    source = {}
    update = {"a": 1, "b": {"c": 2}}
    result = deep_merge(source, update)
    expected = {"a": 1, "b": {"c": 2}}
    assert result == expected
    assert result is source


def test_deep_merge_nonexistent_key():
    """Test deep_merge when source doesn't have a key that update has."""
    source = {"existing": "value"}
    update = {"new_key": "new_value", "nested": {"a": 1}}
    result = deep_merge(source, update)
    expected = {"existing": "value", "new_key": "new_value", "nested": {"a": 1}}
    assert result == expected
    assert result is source
