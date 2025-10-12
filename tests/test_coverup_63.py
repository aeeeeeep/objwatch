# file: objwatch/targets.py:489-515
# asked: {"lines": [489, 503, 504, 505, 506, 507, 508, 510, 511, 512, 513, 515], "branches": [[504, 505], [504, 506], [506, 507], [506, 508], [510, 511], [510, 515]]}
# gained: {"lines": [489, 503, 504, 505, 506, 507, 508, 510, 511, 512, 513, 515], "branches": [[504, 505], [504, 506], [506, 507], [506, 508], [510, 511], [510, 515]]}

import pytest
import json
from unittest.mock import Mock, patch
from objwatch.targets import Targets
from objwatch.constants import Constants


class TestTargetsSerialize:
    """Test cases for Targets.serialize_targets method."""

    def test_serialize_targets_with_sets(self):
        """Test serialization of targets containing sets."""
        # Create a mock targets structure that simulates processed targets
        # The serialize_targets method works on self.targets, which is the processed structure
        mock_targets = {
            'module1': {
                'classes': {'TestClass': {'methods': ['method1', 'method2']}},
                'functions': ['func1', 'func2'],
                'globals': ['var1', 'var2'],
            }
        }

        # Create Targets instance and directly set the targets attribute
        targets = Targets([])  # Empty initial targets
        targets.targets = mock_targets

        result = targets.serialize_targets()
        parsed = json.loads(result)

        # Verify the structure is properly serialized
        assert 'module1' in parsed
        assert parsed['module1']['classes'] == {'TestClass': {'methods': ['method1', 'method2']}}
        assert parsed['module1']['functions'] == ['func1', 'func2']
        assert parsed['module1']['globals'] == ['var1', 'var2']

    def test_serialize_targets_with_custom_objects(self):
        """Test serialization of targets containing custom objects."""

        class CustomObject:
            def __init__(self):
                self.value = 42
                self.name = "test"

        custom_obj = CustomObject()

        # Create a targets structure with custom objects
        mock_targets = {'test_module': {'custom_obj': custom_obj, 'regular_data': {'a': 1, 'b': 2}}}

        targets = Targets([])
        targets.targets = mock_targets

        result = targets.serialize_targets()
        parsed = json.loads(result)

        # Verify custom objects are converted to their __dict__
        assert parsed['test_module']['custom_obj'] == {'value': 42, 'name': 'test'}
        assert parsed['test_module']['regular_data'] == {'a': 1, 'b': 2}

    def test_serialize_targets_with_objects_without_dict(self):
        """Test serialization of objects without __dict__ attribute."""

        # Create an object that doesn't have __dict__ but can be stringified
        class NoDictObject:
            __slots__ = ['value']

            def __init__(self):
                self.value = 100

            def __str__(self):
                return f"NoDictObject(value={self.value})"

        no_dict_obj = NoDictObject()

        mock_targets = {'module': {'no_dict': no_dict_obj, 'regular': 'data'}}

        targets = Targets([])
        targets.targets = mock_targets

        result = targets.serialize_targets()
        parsed = json.loads(result)

        # Verify objects without __dict__ are converted to string
        assert parsed['module']['no_dict'] == "NoDictObject(value=100)"
        assert parsed['module']['regular'] == 'data'

    def test_serialize_targets_truncation_scenario(self):
        """Test serialization when targets exceed MAX_TARGETS_DISPLAY limit."""
        # Create more module targets than the display limit
        many_modules = {f'module_{i}': {'functions': [f'func_{i}']} for i in range(Constants.MAX_TARGETS_DISPLAY + 1)}

        targets = Targets([])
        targets.targets = many_modules

        result = targets.serialize_targets()
        parsed = json.loads(result)

        # Verify truncation occurred - the warning message is added as an additional key
        assert "Warning: too many top-level keys, only showing values like" in parsed

        # Count how many module keys are present (excluding the warning)
        module_keys = [k for k in parsed.keys() if k.startswith('module_')]

        # The actual behavior shows all original keys are preserved but values are truncated
        # Let's verify the behavior we're actually seeing
        assert len(parsed) == Constants.MAX_TARGETS_DISPLAY + 1 + 1  # original keys + warning
        assert len(module_keys) == Constants.MAX_TARGETS_DISPLAY + 1

        # Verify all module values are truncated to "..."
        for key in module_keys:
            assert parsed[key] == "..."

    def test_serialize_targets_with_indent_parameter(self):
        """Test serialization with custom indent parameter."""
        mock_targets = {'module_a': {'classes': {'ClassA': {'methods': ['method1']}}, 'functions': ['func_a']}}

        targets = Targets([])
        targets.targets = mock_targets

        custom_indent = 4
        result = targets.serialize_targets(indent=custom_indent)

        # Verify custom indent is used by checking the structure
        parsed = json.loads(result)
        expected = {'module_a': {'classes': {'ClassA': {'methods': ['method1']}}, 'functions': ['func_a']}}
        assert parsed == expected

        # Also verify the string has proper indentation by checking newlines
        lines = result.split('\n')
        if len(lines) > 1:
            # Check that second line has the expected indentation
            second_line = lines[1]
            leading_spaces = len(second_line) - len(second_line.lstrip())
            assert leading_spaces == custom_indent

    def test_serialize_targets_mixed_types(self):
        """Test serialization with mixed data types including edge cases."""

        class MixedObject:
            def __init__(self):
                self.nested_set = {10, 20}
                self.regular_value = "test"

        mixed_obj = MixedObject()

        mock_targets = {
            'module1': {
                'set_data': {1, 2, 3},
                'custom_obj': mixed_obj,
                'string_data': 'hello',
                'number_data': 42,
                'list_data': [4, 5, 6],
                'none_data': None,
                'bool_data': True,
            }
        }

        targets = Targets([])
        targets.targets = mock_targets

        result = targets.serialize_targets()
        parsed = json.loads(result)

        # Verify all types are handled correctly
        assert set(parsed['module1']['set_data']) == {1, 2, 3}
        assert parsed['module1']['custom_obj'] == {'nested_set': [10, 20], 'regular_value': 'test'}
        assert parsed['module1']['string_data'] == 'hello'
        assert parsed['module1']['number_data'] == 42
        assert parsed['module1']['list_data'] == [4, 5, 6]
        assert parsed['module1']['none_data'] is None
        assert parsed['module1']['bool_data'] is True
