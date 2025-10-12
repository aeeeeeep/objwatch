# file: objwatch/targets.py:439-462
# asked: {"lines": [439, 462], "branches": []}
# gained: {"lines": [439, 462], "branches": []}

import pytest
from objwatch.targets import Targets


class TestTargetsGetTargets:
    """Test cases for Targets.get_targets method."""

    def test_get_targets_returns_initialized_targets_dict(self):
        """Test that get_targets returns the initialized targets dictionary."""
        # Arrange
        targets_input = ["test_module"]
        targets_obj = Targets(targets_input)

        # Act
        result = targets_obj.get_targets()

        # Assert
        assert isinstance(result, dict)
        assert result == targets_obj.targets

    def test_get_targets_with_empty_targets(self):
        """Test get_targets when targets are empty."""
        # Arrange
        targets_input = []
        targets_obj = Targets(targets_input)

        # Act
        result = targets_obj.get_targets()

        # Assert
        assert result == {}

    def test_get_targets_with_complex_targets_structure(self):
        """Test get_targets with complex targets structure including modules, classes, and functions."""
        # Arrange
        targets_input = ["os.path", "collections:defaultdict", "json:loads()"]
        targets_obj = Targets(targets_input)

        # Act
        result = targets_obj.get_targets()

        # Assert
        assert isinstance(result, dict)
        # Verify the structure contains expected keys
        for module_path in result:
            module_data = result[module_path]
            assert isinstance(module_data, dict)
            if 'classes' in module_data:
                assert isinstance(module_data['classes'], dict)
            if 'functions' in module_data:
                assert isinstance(module_data['functions'], list)
            if 'globals' in module_data:
                assert isinstance(module_data['globals'], list)

    def test_get_targets_returns_same_reference(self):
        """Test that get_targets returns the same reference to internal state."""
        # Arrange
        targets_input = ["sys"]
        targets_obj = Targets(targets_input)

        # Act
        result = targets_obj.get_targets()

        # Assert - get_targets returns the same reference, so modifications affect internal state
        assert result is targets_obj.targets
        # Verify modifying result affects internal state
        original_targets_id = id(targets_obj.targets)
        result['test_key'] = 'test_value'
        assert 'test_key' in targets_obj.targets
        assert id(targets_obj.targets) == original_targets_id

    def test_get_targets_with_exclude_targets(self):
        """Test get_targets when exclude_targets are also configured."""
        # Arrange
        targets_input = ["os", "sys"]
        exclude_input = ["os.path"]
        targets_obj = Targets(targets_input, exclude_input)

        # Act
        result = targets_obj.get_targets()

        # Assert
        assert isinstance(result, dict)
        # The result should only include targets after exclusions
        assert result == targets_obj.targets
