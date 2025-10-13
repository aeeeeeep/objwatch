# file: objwatch/targets.py:203-212
# asked: {"lines": [203, 212], "branches": []}
# gained: {"lines": [203, 212], "branches": []}

import pytest
from types import ModuleType
from unittest.mock import Mock, patch
import sys


class TestTargetsParseModule:
    def test_parse_module_with_valid_module(self, monkeypatch):
        """Test _parse_module with a valid module object."""
        from objwatch.targets import Targets

        # Create a mock module
        mock_module = Mock(spec=ModuleType)
        mock_module.__name__ = "test_module"

        # Mock the _parse_module_by_name method and initialize Targets with required arguments
        targets = Targets(targets=[], exclude_targets=[])
        expected_result = ("test_module", {"parsed": "structure"})
        monkeypatch.setattr(targets, '_parse_module_by_name', Mock(return_value={"parsed": "structure"}))

        # Call the method
        result = targets._parse_module(mock_module)

        # Verify the result
        assert result == expected_result
        targets._parse_module_by_name.assert_called_once_with("test_module")

    def test_parse_module_with_builtin_module(self):
        """Test _parse_module with a built-in module."""
        from objwatch.targets import Targets

        targets = Targets(targets=[], exclude_targets=[])

        # Use sys module as a real module example
        with patch.object(targets, '_parse_module_by_name') as mock_parse:
            mock_parse.return_value = {"sys": "module"}
            result = targets._parse_module(sys)

            assert result == (sys.__name__, {"sys": "module"})
            mock_parse.assert_called_once_with(sys.__name__)

    def test_parse_module_with_custom_module(self, monkeypatch):
        """Test _parse_module with a custom module object."""
        from objwatch.targets import Targets

        # Create a custom module
        custom_module = ModuleType("custom_module")

        targets = Targets(targets=[], exclude_targets=[])
        monkeypatch.setattr(targets, '_parse_module_by_name', Mock(return_value={"custom": "data"}))

        result = targets._parse_module(custom_module)

        assert result == ("custom_module", {"custom": "data"})
        targets._parse_module_by_name.assert_called_once_with("custom_module")
