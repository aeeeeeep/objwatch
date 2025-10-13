# file: objwatch/core.py:19-68
# asked: {"lines": [19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 65, 68], "branches": []}
# gained: {"lines": [19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 65, 68], "branches": []}

import pytest
import logging
import tempfile
import os
from types import ModuleType
from typing import List, Union, Optional
from unittest.mock import Mock, patch
from objwatch.core import ObjWatch
from objwatch.config import ObjWatchConfig
from objwatch.tracer import Tracer
from objwatch.wrappers import ABCWrapper
from objwatch.utils.logger import create_logger


class TestObjWatchInit:
    """Test cases for ObjWatch.__init__ method to achieve full coverage."""

    def test_init_with_minimal_parameters(self):
        """Test ObjWatch initialization with only required parameters."""
        targets = ["test_module"]
        objwatch = ObjWatch(targets=targets)

        assert isinstance(objwatch.tracer, Tracer)
        assert objwatch.tracer.config.targets == targets
        assert objwatch.tracer.config.exclude_targets is None
        assert objwatch.tracer.config.framework is None
        assert objwatch.tracer.config.indexes is None
        assert objwatch.tracer.config.output is None
        assert objwatch.tracer.config.output_xml is None
        assert objwatch.tracer.config.level == logging.DEBUG
        assert objwatch.tracer.config.simple is False
        assert objwatch.tracer.config.wrapper is None
        assert objwatch.tracer.config.with_locals is False
        assert objwatch.tracer.config.with_globals is False

    def test_init_with_all_parameters_except_wrapper(self):
        """Test ObjWatch initialization with all parameters except wrapper."""
        targets = ["test_module"]
        exclude_targets = ["excluded_module"]
        framework = "multiprocessing"
        indexes = [1, 2, 3]
        output = "test.log"
        output_xml = "test.xml"
        level = logging.INFO
        simple = True
        with_locals = True
        with_globals = True

        objwatch = ObjWatch(
            targets=targets,
            exclude_targets=exclude_targets,
            framework=framework,
            indexes=indexes,
            output=output,
            output_xml=output_xml,
            level=level,
            simple=simple,
            wrapper=None,
            with_locals=with_locals,
            with_globals=with_globals,
        )

        assert isinstance(objwatch.tracer, Tracer)
        assert objwatch.tracer.config.targets == targets
        assert objwatch.tracer.config.exclude_targets == exclude_targets
        assert objwatch.tracer.config.framework == framework
        assert objwatch.tracer.config.indexes == indexes
        assert objwatch.tracer.config.output == output
        assert objwatch.tracer.config.output_xml == output_xml
        assert objwatch.tracer.config.level == level
        assert objwatch.tracer.config.simple == simple
        assert objwatch.tracer.config.wrapper is None
        assert objwatch.tracer.config.with_locals == with_locals
        assert objwatch.tracer.config.with_globals == with_globals

    def test_init_with_module_type_targets(self):
        """Test ObjWatch initialization with ModuleType targets."""
        test_module = ModuleType("test_module")
        targets = [test_module]

        objwatch = ObjWatch(targets=targets)

        assert isinstance(objwatch.tracer, Tracer)
        assert objwatch.tracer.config.targets == targets

    def test_init_with_mixed_target_types(self):
        """Test ObjWatch initialization with mixed string and ModuleType targets."""
        test_module = ModuleType("test_module")
        targets = ["string_target", test_module]

        objwatch = ObjWatch(targets=targets)

        assert isinstance(objwatch.tracer, Tracer)
        assert objwatch.tracer.config.targets == targets

    def test_init_with_file_output(self, tmp_path):
        """Test ObjWatch initialization with file output."""
        log_file = tmp_path / "test.log"
        targets = ["test_module"]

        objwatch = ObjWatch(targets=targets, output=str(log_file))

        assert isinstance(objwatch.tracer, Tracer)
        assert objwatch.tracer.config.output == str(log_file)

    def test_init_with_different_log_levels(self):
        """Test ObjWatch initialization with different logging levels."""
        targets = ["test_module"]

        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]:
            objwatch = ObjWatch(targets=targets, level=level)
            assert objwatch.tracer.config.level == level

    def test_init_with_simple_logging(self):
        """Test ObjWatch initialization with simple logging enabled."""
        targets = ["test_module"]

        objwatch = ObjWatch(targets=targets, simple=True)

        assert objwatch.tracer.config.simple is True

    def test_init_with_none_exclude_targets(self):
        """Test ObjWatch initialization with explicit None exclude_targets."""
        targets = ["test_module"]

        objwatch = ObjWatch(targets=targets, exclude_targets=None)

        assert objwatch.tracer.config.exclude_targets is None

    def test_init_with_empty_exclude_targets(self):
        """Test ObjWatch initialization with empty exclude_targets list."""
        targets = ["test_module"]
        exclude_targets = []

        objwatch = ObjWatch(targets=targets, exclude_targets=exclude_targets)

        assert objwatch.tracer.config.exclude_targets == exclude_targets

    def test_init_with_none_indexes(self):
        """Test ObjWatch initialization with explicit None indexes."""
        targets = ["test_module"]

        objwatch = ObjWatch(targets=targets, indexes=None)

        assert objwatch.tracer.config.indexes is None

    def test_init_with_empty_indexes(self):
        """Test ObjWatch initialization with empty indexes list."""
        targets = ["test_module"]
        indexes = []

        objwatch = ObjWatch(targets=targets, indexes=indexes)

        assert objwatch.tracer.config.indexes == indexes

    def test_init_with_none_wrapper(self):
        """Test ObjWatch initialization with explicit None wrapper."""
        targets = ["test_module"]

        objwatch = ObjWatch(targets=targets, wrapper=None)

        assert objwatch.tracer.config.wrapper is None

    def test_init_with_locals_tracking(self):
        """Test ObjWatch initialization with locals tracking enabled."""
        targets = ["test_module"]

        objwatch = ObjWatch(targets=targets, with_locals=True)

        assert objwatch.tracer.config.with_locals is True

    def test_init_with_globals_tracking(self):
        """Test ObjWatch initialization with globals tracking enabled."""
        targets = ["test_module"]

        objwatch = ObjWatch(targets=targets, with_globals=True)

        assert objwatch.tracer.config.with_globals is True

    def test_init_with_both_locals_and_globals_tracking(self):
        """Test ObjWatch initialization with both locals and globals tracking enabled."""
        targets = ["test_module"]

        objwatch = ObjWatch(targets=targets, with_locals=True, with_globals=True)

        assert objwatch.tracer.config.with_locals is True
        assert objwatch.tracer.config.with_globals is True

    @patch('objwatch.core.create_logger')
    def test_create_logger_called_with_config(self, mock_create_logger):
        """Test that create_logger is called with configuration parameters."""
        targets = ["test_module"]
        output = "test.log"
        level = logging.INFO
        simple = True

        objwatch = ObjWatch(targets=targets, output=output, level=level, simple=simple)

        mock_create_logger.assert_called_once_with(output=output, level=level, simple=simple)

    @patch('objwatch.core.Tracer')
    def test_tracer_initialized_with_config(self, mock_tracer):
        """Test that Tracer is initialized with the configuration."""
        targets = ["test_module"]

        objwatch = ObjWatch(targets=targets)

        # Get the config passed to Tracer
        call_args = mock_tracer.call_args
        assert call_args is not None
        config_arg = call_args[1]['config']  # kwargs are in position 1
        assert isinstance(config_arg, ObjWatchConfig)
        assert config_arg.targets == targets

    def test_init_with_valid_wrapper_class(self):
        """Test ObjWatch initialization with a valid wrapper class."""
        targets = ["test_module"]

        # Create a valid wrapper class implementing all abstract methods
        class ValidWrapper(ABCWrapper):
            def wrap_call(self, func_name: str, frame):
                return f"Call: {func_name}"

            def wrap_return(self, func_name: str, result):
                return f"Return: {func_name}"

            def wrap_upd(self, old_value, current_value):
                return f"Old: {old_value}", f"New: {current_value}"

        objwatch = ObjWatch(targets=targets, wrapper=ValidWrapper)

        assert isinstance(objwatch.tracer, Tracer)
        assert objwatch.tracer.config.wrapper == ValidWrapper

    @patch('objwatch.core.Tracer')
    def test_init_with_wrapper_instance(self, mock_tracer):
        """Test ObjWatch initialization with a wrapper instance."""
        targets = ["test_module"]

        # Create a mock wrapper instance
        wrapper_instance = Mock(spec=ABCWrapper)

        objwatch = ObjWatch(targets=targets, wrapper=wrapper_instance)

        # When Tracer is mocked, objwatch.tracer is the mock, not a real Tracer
        assert objwatch.tracer is mock_tracer.return_value
        # Verify Tracer was called with the correct config
        mock_tracer.assert_called_once()
        call_args = mock_tracer.call_args
        config_arg = call_args[1]['config']
        assert config_arg.wrapper == wrapper_instance
