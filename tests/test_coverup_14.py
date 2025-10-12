# file: objwatch/config.py:12-51
# asked: {"lines": [12, 13, 14, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 43, 47, 48, 50, 51], "branches": [[47, 48], [47, 50], [50, 0], [50, 51]]}
# gained: {"lines": [12, 13, 14, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 43, 47, 48, 50, 51], "branches": [[47, 48], [47, 50], [50, 0], [50, 51]]}

import pytest
import logging
import dataclasses
from types import ModuleType
from typing import List, Union
from objwatch.config import ObjWatchConfig
from objwatch.wrappers import ABCWrapper


class MockWrapper(ABCWrapper):
    """Mock wrapper for testing"""

    def wrap_call(self, func_name: str, frame):
        return f"call:{func_name}"

    def wrap_return(self, func_name: str, result):
        return f"return:{func_name}"

    def wrap_upd(self, old_value, current_value):
        return f"old:{old_value}", f"new:{current_value}"


class TestObjWatchConfig:
    """Test cases for ObjWatchConfig class"""

    def test_init_with_valid_targets(self):
        """Test initialization with valid targets"""
        config = ObjWatchConfig(targets=["test_module"])
        assert config.targets == ["test_module"]
        assert config.exclude_targets is None
        assert config.framework is None
        assert config.indexes is None
        assert config.output is None
        assert config.output_xml is None
        assert config.level == logging.DEBUG
        assert config.simple is False
        assert config.wrapper is None
        assert config.with_locals is False
        assert config.with_globals is False

    def test_init_with_module_target(self):
        """Test initialization with module target"""
        test_module = ModuleType("test_module")
        config = ObjWatchConfig(targets=[test_module])
        assert config.targets == [test_module]

    def test_init_with_mixed_targets(self):
        """Test initialization with mixed string and module targets"""
        test_module = ModuleType("test_module")
        config = ObjWatchConfig(targets=["string_target", test_module])
        assert len(config.targets) == 2
        assert "string_target" in config.targets
        assert test_module in config.targets

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters specified"""
        test_module = ModuleType("test_module")
        wrapper = MockWrapper()

        config = ObjWatchConfig(
            targets=["main_module", test_module],
            exclude_targets=["excluded_module"],
            framework="torch",
            indexes=[0, 1],
            output="log.txt",
            output_xml="log.xml",
            level=logging.INFO,
            simple=True,
            wrapper=wrapper,
            with_locals=True,
            with_globals=True,
        )

        assert len(config.targets) == 2
        assert config.exclude_targets == ["excluded_module"]
        assert config.framework == "torch"
        assert config.indexes == [0, 1]
        assert config.output == "log.txt"
        assert config.output_xml == "log.xml"
        assert config.level == logging.INFO
        assert config.simple is True
        assert config.wrapper == wrapper
        assert config.with_locals is True
        assert config.with_globals is True

    def test_post_init_empty_targets_raises_value_error(self):
        """Test that empty targets list raises ValueError"""
        with pytest.raises(ValueError, match="At least one monitoring target must be specified"):
            ObjWatchConfig(targets=[])

    def test_post_init_none_targets_raises_value_error(self):
        """Test that None targets raises ValueError"""
        with pytest.raises(ValueError, match="At least one monitoring target must be specified"):
            ObjWatchConfig(targets=None)

    def test_post_init_level_force_with_output_raises_value_error(self):
        """Test that level='force' with output specified raises ValueError"""
        with pytest.raises(ValueError, match="output cannot be specified when level is 'force'"):
            ObjWatchConfig(targets=["test_module"], level="force", output="log.txt")

    def test_post_init_level_force_without_output_succeeds(self):
        """Test that level='force' without output succeeds"""
        config = ObjWatchConfig(targets=["test_module"], level="force")
        assert config.level == "force"
        assert config.output is None

    def test_post_init_level_not_force_with_output_succeeds(self):
        """Test that level not 'force' with output succeeds"""
        config = ObjWatchConfig(targets=["test_module"], level=logging.INFO, output="log.txt")
        assert config.level == logging.INFO
        assert config.output == "log.txt"

    def test_frozen_dataclass_prevents_modification(self):
        """Test that frozen dataclass prevents attribute modification"""
        config = ObjWatchConfig(targets=["test_module"])

        with pytest.raises(dataclasses.FrozenInstanceError):
            config.targets = ["new_target"]

        with pytest.raises(dataclasses.FrozenInstanceError):
            config.level = logging.INFO
