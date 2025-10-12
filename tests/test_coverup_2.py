# file: objwatch/targets.py:94-114
# asked: {"lines": [94, 95, 96, 107, 108, 109, 110, 111, 112, 113, 114], "branches": [[107, 108], [107, 109], [109, 110], [109, 111], [111, 112], [111, 114], [112, 111], [112, 113]]}
# gained: {"lines": [94, 95, 96, 107, 108, 109, 110, 111, 112, 113, 114], "branches": [[107, 108], [107, 109], [109, 110], [109, 111], [111, 112], [111, 114], [112, 111], [112, 113]]}

import pytest
from unittest.mock import patch, MagicMock
from objwatch.targets import Targets
from objwatch.utils.logger import log_error
from typing import Optional, List, Union

TargetsType = Union[str, List[str], None]


class TestTargetsCheckTargets:
    """Test cases for Targets._check_targets method."""

    def test_check_targets_with_string_targets(self):
        """Test _check_targets when targets is a string."""
        targets = Targets([], [])
        result_targets, result_exclude = targets._check_targets("module_name", None)
        assert result_targets == ["module_name"]
        assert result_exclude is None

    def test_check_targets_with_string_exclude_targets(self):
        """Test _check_targets when exclude_targets is a string."""
        targets = Targets([], [])
        result_targets, result_exclude = targets._check_targets(["module1"], "module2")
        assert result_targets == ["module1"]
        assert result_exclude == ["module2"]

    def test_check_targets_with_py_file_in_exclude_targets(self):
        """Test _check_targets when exclude_targets contains .py files."""
        targets = Targets([], [])
        with patch('objwatch.targets.log_error') as mock_log_error:
            result_targets, result_exclude = targets._check_targets(["module1"], ["file.py", "module2"])
            assert result_targets == ["module1"]
            assert result_exclude == ["file.py", "module2"]
            mock_log_error.assert_called_once_with("Unsupported .py files in exclude_target")

    def test_check_targets_with_multiple_py_files_in_exclude_targets(self):
        """Test _check_targets when exclude_targets contains multiple .py files."""
        targets = Targets([], [])
        with patch('objwatch.targets.log_error') as mock_log_error:
            result_targets, result_exclude = targets._check_targets(["module1"], ["file1.py", "file2.py", "module2"])
            assert result_targets == ["module1"]
            assert result_exclude == ["file1.py", "file2.py", "module2"]
            assert mock_log_error.call_count == 2

    def test_check_targets_with_none_exclude_targets(self):
        """Test _check_targets when exclude_targets is None."""
        targets = Targets([], [])
        result_targets, result_exclude = targets._check_targets(["module1"], None)
        assert result_targets == ["module1"]
        assert result_exclude is None

    def test_check_targets_with_empty_exclude_targets(self):
        """Test _check_targets when exclude_targets is empty list."""
        targets = Targets([], [])
        result_targets, result_exclude = targets._check_targets(["module1"], [])
        assert result_targets == ["module1"]
        assert result_exclude == []

    def test_check_targets_with_both_strings(self):
        """Test _check_targets when both targets and exclude_targets are strings."""
        targets = Targets([], [])
        with patch('objwatch.targets.log_error') as mock_log_error:
            result_targets, result_exclude = targets._check_targets("module1", "file.py")
            assert result_targets == ["module1"]
            assert result_exclude == ["file.py"]
            mock_log_error.assert_called_once_with("Unsupported .py files in exclude_target")
