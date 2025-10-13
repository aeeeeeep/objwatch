# file: objwatch/targets.py:230-295
# asked: {"lines": [230, 240, 241, 242, 243, 244, 245, 246, 247, 250, 251, 252, 253, 254, 255, 256, 258, 259, 261, 262, 265, 266, 267, 268, 269, 271, 272, 273, 274, 278, 279, 280, 281, 284, 285, 286, 287, 288, 289, 290, 291, 292, 295], "branches": [[240, 241], [240, 250], [243, 244], [243, 246], [252, 253], [252, 255], [258, 259], [258, 261], [265, 266], [265, 284], [267, 268], [267, 295], [268, 269], [268, 278], [284, 285], [284, 288], [286, 287], [286, 295], [288, 289], [288, 295]]}
# gained: {"lines": [230, 240, 241, 242, 243, 244, 245, 246, 247, 250, 251, 252, 253, 254, 255, 256, 258, 259, 261, 262, 265, 266, 267, 268, 269, 271, 272, 273, 274, 278, 279, 280, 281, 284, 285, 286, 287, 288, 289, 290, 291, 292, 295], "branches": [[240, 241], [240, 250], [243, 244], [243, 246], [252, 253], [252, 255], [258, 259], [258, 261], [265, 266], [265, 284], [267, 268], [267, 295], [268, 269], [268, 278], [284, 285], [284, 288], [286, 287], [286, 295], [288, 289]]}

import pytest
import importlib
from unittest.mock import patch, MagicMock
from objwatch.targets import Targets
from objwatch.utils.logger import log_warn


class TestTargetsParseString:
    """Test cases for Targets._parse_string method to achieve full coverage."""

    def test_parse_string_global_variable_syntax_module_not_found(self, monkeypatch):
        """Test global variable syntax with non-existent module."""
        targets = Targets([])

        with patch('objwatch.targets.importlib.util.find_spec') as mock_find_spec:
            mock_find_spec.return_value = None

            result = targets._parse_string("nonexistent_module::GLOBAL_VAR")

            assert result == ("nonexistent_module", {'globals': []})
            mock_find_spec.assert_called_once_with("nonexistent_module")

    def test_parse_string_global_variable_syntax_valid_module(self, monkeypatch):
        """Test global variable syntax with valid module."""
        targets = Targets([])

        mock_spec = MagicMock()
        mock_spec.name = "existing_module"

        with patch('objwatch.targets.importlib.util.find_spec') as mock_find_spec:
            mock_find_spec.return_value = mock_spec

            result = targets._parse_string("existing_module::GLOBAL_VAR")

            assert result == ("existing_module", {'globals': ['GLOBAL_VAR']})
            mock_find_spec.assert_called_once_with("existing_module")

    def test_parse_string_module_not_found(self, monkeypatch):
        """Test module not found case."""
        targets = Targets([])

        with patch('objwatch.targets.importlib.util.find_spec') as mock_find_spec:
            mock_find_spec.return_value = None

            result = targets._parse_string("nonexistent_module:SomeClass")

            assert result == ("nonexistent_module", {'classes': {}, 'functions': [], 'globals': []})
            mock_find_spec.assert_called_once_with("nonexistent_module")

    def test_parse_string_empty_symbol(self, monkeypatch):
        """Test case with empty symbol (just module)."""
        targets = Targets([])

        mock_spec = MagicMock()
        mock_spec.name = "test_module"

        mock_module_structure = {'classes': {'TestClass': {}}, 'functions': ['test_func'], 'globals': []}

        with patch('objwatch.targets.importlib.util.find_spec') as mock_find_spec, patch.object(
            targets, '_parse_module_by_name'
        ) as mock_parse_module:

            mock_find_spec.return_value = mock_spec
            mock_parse_module.return_value = mock_module_structure

            result = targets._parse_string("test_module:")

            assert result == ("test_module", mock_module_structure)
            mock_find_spec.assert_called_once_with("test_module")
            mock_parse_module.assert_called_once_with("test_module")

    def test_parse_string_class_method(self, monkeypatch):
        """Test parsing class method syntax."""
        targets = Targets([])

        mock_spec = MagicMock()
        mock_spec.name = "test_module"

        mock_module_structure = {
            'classes': {'TestClass': {'methods': ['some_method', 'target_method'], 'attributes': ['attr1']}},
            'functions': ['test_func'],
            'globals': [],
        }

        with patch('objwatch.targets.importlib.util.find_spec') as mock_find_spec, patch.object(
            targets, '_parse_module_by_name'
        ) as mock_parse_module:

            mock_find_spec.return_value = mock_spec
            mock_parse_module.return_value = mock_module_structure

            result = targets._parse_string("test_module:TestClass.target_method()")

            expected_details = {
                'classes': {'TestClass': {'methods': ['target_method'], 'attributes': [], 'track_all': False}},
                'functions': [],
                'globals': [],
            }

            assert result == ("test_module", expected_details)

    def test_parse_string_class_attribute(self, monkeypatch):
        """Test parsing class attribute syntax."""
        targets = Targets([])

        mock_spec = MagicMock()
        mock_spec.name = "test_module"

        mock_module_structure = {
            'classes': {'TestClass': {'methods': ['some_method'], 'attributes': ['some_attr', 'target_attr']}},
            'functions': ['test_func'],
            'globals': [],
        }

        with patch('objwatch.targets.importlib.util.find_spec') as mock_find_spec, patch.object(
            targets, '_parse_module_by_name'
        ) as mock_parse_module:

            mock_find_spec.return_value = mock_spec
            mock_parse_module.return_value = mock_module_structure

            result = targets._parse_string("test_module:TestClass.target_attr")

            expected_details = {
                'classes': {'TestClass': {'methods': [], 'attributes': ['target_attr'], 'track_all': False}},
                'functions': [],
                'globals': [],
            }

            assert result == ("test_module", expected_details)

    def test_parse_string_class_not_found_with_member(self, monkeypatch):
        """Test class member syntax where class doesn't exist in module."""
        targets = Targets([])

        mock_spec = MagicMock()
        mock_spec.name = "test_module"

        mock_module_structure = {
            'classes': {'OtherClass': {'methods': ['some_method'], 'attributes': ['some_attr']}},
            'functions': ['test_func'],
            'globals': [],
        }

        with patch('objwatch.targets.importlib.util.find_spec') as mock_find_spec, patch.object(
            targets, '_parse_module_by_name'
        ) as mock_parse_module:

            mock_find_spec.return_value = mock_spec
            mock_parse_module.return_value = mock_module_structure

            result = targets._parse_string("test_module:NonExistentClass.some_member")

            expected_details = {'classes': {}, 'functions': [], 'globals': []}

            assert result == ("test_module", expected_details)

    def test_parse_string_function(self, monkeypatch):
        """Test parsing function syntax."""
        targets = Targets([])

        mock_spec = MagicMock()
        mock_spec.name = "test_module"

        mock_module_structure = {'classes': {}, 'functions': ['other_func', 'target_func'], 'globals': []}

        with patch('objwatch.targets.importlib.util.find_spec') as mock_find_spec, patch.object(
            targets, '_parse_module_by_name'
        ) as mock_parse_module:

            mock_find_spec.return_value = mock_spec
            mock_parse_module.return_value = mock_module_structure

            result = targets._parse_string("test_module:target_func()")

            expected_details = {'classes': {}, 'functions': ['target_func'], 'globals': []}

            assert result == ("test_module", expected_details)

    def test_parse_string_function_not_found(self, monkeypatch):
        """Test function syntax where function doesn't exist in module."""
        targets = Targets([])

        mock_spec = MagicMock()
        mock_spec.name = "test_module"

        mock_module_structure = {'classes': {}, 'functions': ['other_func'], 'globals': []}

        with patch('objwatch.targets.importlib.util.find_spec') as mock_find_spec, patch.object(
            targets, '_parse_module_by_name'
        ) as mock_parse_module:

            mock_find_spec.return_value = mock_spec
            mock_parse_module.return_value = mock_module_structure

            result = targets._parse_string("test_module:non_existent_func()")

            expected_details = {'classes': {}, 'functions': [], 'globals': []}

            assert result == ("test_module", expected_details)

    def test_parse_string_entire_class(self, monkeypatch):
        """Test parsing entire class syntax."""
        targets = Targets([])

        mock_spec = MagicMock()
        mock_spec.name = "test_module"

        mock_module_structure = {
            'classes': {'TargetClass': {'methods': ['method1', 'method2'], 'attributes': ['attr1', 'attr2']}},
            'functions': [],
            'globals': [],
        }

        with patch('objwatch.targets.importlib.util.find_spec') as mock_find_spec, patch.object(
            targets, '_parse_module_by_name'
        ) as mock_parse_module:

            mock_find_spec.return_value = mock_spec
            mock_parse_module.return_value = mock_module_structure

            result = targets._parse_string("test_module:TargetClass")

            expected_details = {
                'classes': {'TargetClass': {'methods': [], 'attributes': [], 'track_all': True}},
                'functions': [],
                'globals': [],
            }

            assert result == ("test_module", expected_details)
