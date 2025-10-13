# file: objwatch/core.py:106-156
# asked: {"lines": [106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 154, 156], "branches": []}
# gained: {"lines": [106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 154, 156], "branches": []}

import pytest
import logging
from types import ModuleType
from typing import List, Union
from unittest.mock import Mock, patch
from objwatch.core import watch
from objwatch.wrappers import ABCWrapper


class TestWatchFunction:
    """Test cases for the watch function to achieve full coverage."""

    def test_watch_with_all_parameters(self, monkeypatch):
        """Test watch function with all parameters provided."""
        # Mock the ObjWatch class and its start method
        mock_objwatch_instance = Mock()
        mock_objwatch_instance.start = Mock()

        with patch('objwatch.core.ObjWatch') as mock_objwatch_class:
            mock_objwatch_class.return_value = mock_objwatch_instance

            # Call watch with all parameters
            targets = ['test_module.py']
            exclude_targets = ['excluded_module.py']
            framework = 'torch'
            indexes = [0, 1]
            output = 'test_output.log'
            output_xml = 'test_output.xml'
            level = logging.INFO
            simple = True
            wrapper = Mock(spec=ABCWrapper)
            with_locals = True
            with_globals = True

            result = watch(
                targets=targets,
                exclude_targets=exclude_targets,
                framework=framework,
                indexes=indexes,
                output=output,
                output_xml=output_xml,
                level=level,
                simple=simple,
                wrapper=wrapper,
                with_locals=with_locals,
                with_globals=with_globals,
            )

            # Verify ObjWatch was instantiated with correct parameters
            mock_objwatch_class.assert_called_once_with(
                targets=targets,
                exclude_targets=exclude_targets,
                framework=framework,
                indexes=indexes,
                output=output,
                output_xml=output_xml,
                level=level,
                simple=simple,
                wrapper=wrapper,
                with_locals=with_locals,
                with_globals=with_globals,
            )

            # Verify start was called
            mock_objwatch_instance.start.assert_called_once()

            # Verify the returned instance
            assert result == mock_objwatch_instance

    def test_watch_with_minimal_parameters(self, monkeypatch):
        """Test watch function with minimal parameters (only required ones)."""
        # Mock the ObjWatch class and its start method
        mock_objwatch_instance = Mock()
        mock_objwatch_instance.start = Mock()

        with patch('objwatch.core.ObjWatch') as mock_objwatch_class:
            mock_objwatch_class.return_value = mock_objwatch_instance

            # Call watch with only required parameters
            targets = ['test_module.py']

            result = watch(targets=targets)

            # Verify ObjWatch was instantiated with correct default parameters
            mock_objwatch_class.assert_called_once_with(
                targets=targets,
                exclude_targets=None,
                framework=None,
                indexes=None,
                output=None,
                output_xml=None,
                level=logging.DEBUG,
                simple=False,
                wrapper=None,
                with_locals=False,
                with_globals=False,
            )

            # Verify start was called
            mock_objwatch_instance.start.assert_called_once()

            # Verify the returned instance
            assert result == mock_objwatch_instance

    def test_watch_with_module_targets(self, monkeypatch):
        """Test watch function with module type targets."""
        # Mock the ObjWatch class and its start method
        mock_objwatch_instance = Mock()
        mock_objwatch_instance.start = Mock()

        with patch('objwatch.core.ObjWatch') as mock_objwatch_class:
            mock_objwatch_class.return_value = mock_objwatch_instance

            # Create mock modules
            mock_module1 = Mock(spec=ModuleType)
            mock_module1.__name__ = 'test_module1'
            mock_module2 = Mock(spec=ModuleType)
            mock_module2.__name__ = 'test_module2'

            # Call watch with module targets
            targets = [mock_module1, mock_module2]

            result = watch(targets=targets)

            # Verify ObjWatch was instantiated with module targets
            mock_objwatch_class.assert_called_once_with(
                targets=targets,
                exclude_targets=None,
                framework=None,
                indexes=None,
                output=None,
                output_xml=None,
                level=logging.DEBUG,
                simple=False,
                wrapper=None,
                with_locals=False,
                with_globals=False,
            )

            # Verify start was called
            mock_objwatch_instance.start.assert_called_once()

            # Verify the returned instance
            assert result == mock_objwatch_instance

    def test_watch_with_mixed_targets(self, monkeypatch):
        """Test watch function with mixed string and module targets."""
        # Mock the ObjWatch class and its start method
        mock_objwatch_instance = Mock()
        mock_objwatch_instance.start = Mock()

        with patch('objwatch.core.ObjWatch') as mock_objwatch_class:
            mock_objwatch_class.return_value = mock_objwatch_instance

            # Create mock module
            mock_module = Mock(spec=ModuleType)
            mock_module.__name__ = 'test_module'

            # Call watch with mixed targets
            targets = ['test_file.py', mock_module]

            result = watch(targets=targets)

            # Verify ObjWatch was instantiated with mixed targets
            mock_objwatch_class.assert_called_once_with(
                targets=targets,
                exclude_targets=None,
                framework=None,
                indexes=None,
                output=None,
                output_xml=None,
                level=logging.DEBUG,
                simple=False,
                wrapper=None,
                with_locals=False,
                with_globals=False,
            )

            # Verify start was called
            mock_objwatch_instance.start.assert_called_once()

            # Verify the returned instance
            assert result == mock_objwatch_instance

    def test_watch_with_exclude_targets(self, monkeypatch):
        """Test watch function with exclude_targets parameter."""
        # Mock the ObjWatch class and its start method
        mock_objwatch_instance = Mock()
        mock_objwatch_instance.start = Mock()

        with patch('objwatch.core.ObjWatch') as mock_objwatch_class:
            mock_objwatch_class.return_value = mock_objwatch_instance

            # Call watch with exclude_targets
            targets = ['test_module.py']
            exclude_targets = ['excluded1.py', 'excluded2.py']

            result = watch(targets=targets, exclude_targets=exclude_targets)

            # Verify ObjWatch was instantiated with exclude_targets
            mock_objwatch_class.assert_called_once_with(
                targets=targets,
                exclude_targets=exclude_targets,
                framework=None,
                indexes=None,
                output=None,
                output_xml=None,
                level=logging.DEBUG,
                simple=False,
                wrapper=None,
                with_locals=False,
                with_globals=False,
            )

            # Verify start was called
            mock_objwatch_instance.start.assert_called_once()

            # Verify the returned instance
            assert result == mock_objwatch_instance

    def test_watch_with_custom_wrapper(self, monkeypatch):
        """Test watch function with custom wrapper."""
        # Mock the ObjWatch class and its start method
        mock_objwatch_instance = Mock()
        mock_objwatch_instance.start = Mock()

        with patch('objwatch.core.ObjWatch') as mock_objwatch_class:
            mock_objwatch_class.return_value = mock_objwatch_instance

            # Create a custom wrapper
            custom_wrapper = Mock(spec=ABCWrapper)

            # Call watch with custom wrapper
            targets = ['test_module.py']

            result = watch(targets=targets, wrapper=custom_wrapper)

            # Verify ObjWatch was instantiated with custom wrapper
            mock_objwatch_class.assert_called_once_with(
                targets=targets,
                exclude_targets=None,
                framework=None,
                indexes=None,
                output=None,
                output_xml=None,
                level=logging.DEBUG,
                simple=False,
                wrapper=custom_wrapper,
                with_locals=False,
                with_globals=False,
            )

            # Verify start was called
            mock_objwatch_instance.start.assert_called_once()

            # Verify the returned instance
            assert result == mock_objwatch_instance
