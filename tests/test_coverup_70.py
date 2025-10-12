# file: objwatch/targets.py:517-524
# asked: {"lines": [517, 524], "branches": []}
# gained: {"lines": [517, 524], "branches": []}

import pytest
from objwatch.targets import Targets


class TestTargetsGetFilenameTargets:
    """Test cases for Targets.get_filename_targets method."""

    def test_get_filename_targets_empty(self):
        """Test get_filename_targets returns empty set when no filename targets exist."""
        # Arrange
        targets = Targets([])

        # Act
        result = targets.get_filename_targets()

        # Assert
        assert result == set()
        assert isinstance(result, set)

    def test_get_filename_targets_with_files(self, monkeypatch):
        """Test get_filename_targets returns populated set when filename targets exist."""
        # Arrange
        targets = Targets([])
        expected_files = {'/path/to/file1.py', '/path/to/file2.py'}

        # Use monkeypatch to set the filename_targets attribute
        monkeypatch.setattr(targets, 'filename_targets', expected_files.copy())

        # Act
        result = targets.get_filename_targets()

        # Assert
        assert result == expected_files
        assert isinstance(result, set)
        assert len(result) == 2
