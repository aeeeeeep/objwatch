# file: objwatch/tracer.py:26-89
# asked: {"lines": [26, 28, 29, 37, 39, 40, 41, 43, 44, 45, 47, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 75, 76, 79, 82, 83, 84, 85, 88, 89], "branches": [[39, 40], [39, 43], [43, 44], [43, 59]]}
# gained: {"lines": [26, 28, 29, 37, 39, 40, 41, 43, 44, 45, 47, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 75, 76, 79, 82, 83, 84, 85, 88, 89], "branches": [[39, 40], [39, 43], [43, 44], [43, 59]]}

import pytest
from unittest.mock import Mock, patch, MagicMock
from types import FrameType
from typing import Optional, Dict, Set, Any, Tuple
from objwatch.config import ObjWatchConfig
from objwatch.targets import Targets
from objwatch.wrappers import ABCWrapper
from objwatch.event_handls import EventHandls
from objwatch.mp_handls import MPHandls
from objwatch.utils.weak import WeakIdKeyDictionary
from objwatch.utils.logger import log_debug


class TestTracerInit:
    """Test cases for Tracer.__init__ method to achieve full coverage."""

    def test_init_with_locals_and_globals(self):
        """Test Tracer initialization with both locals and globals tracking enabled."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=True, with_globals=True)

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = {'test_module.py'}
            mock_targets_instance.get_targets.return_value = {'test_module': {}}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = "test_targets"
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls') as mock_event_handls:
                with patch('objwatch.tracer.MPHandls') as mock_mp_handls:
                    with patch('objwatch.tracer.WeakIdKeyDictionary') as mock_weak_dict:
                        with patch('objwatch.tracer.Tracer.load_wrapper') as mock_load_wrapper:
                            mock_load_wrapper.return_value = None
                            from objwatch.tracer import Tracer

                            tracer = Tracer(config)

                            # Verify locals tracking is initialized
                            assert hasattr(tracer, 'tracked_locals')
                            assert isinstance(tracer.tracked_locals, dict)
                            assert hasattr(tracer, 'tracked_locals_lens')
                            assert isinstance(tracer.tracked_locals_lens, dict)

                            # Verify globals tracking is initialized
                            assert hasattr(tracer, 'tracked_globals')
                            assert isinstance(tracer.tracked_globals, dict)
                            assert hasattr(tracer, 'tracked_globals_lens')
                            assert isinstance(tracer.tracked_globals_lens, dict)

                            # Verify builtin_fields is set
                            assert hasattr(tracer, 'builtin_fields')
                            assert isinstance(tracer.builtin_fields, set)
                            assert 'self' in tracer.builtin_fields
                            assert '__builtins__' in tracer.builtin_fields

                            # Verify targets processing
                            mock_targets_cls.assert_called_once_with(config.targets, config.exclude_targets)
                            assert tracer.filename_targets == {'test_module.py'}
                            assert tracer.targets == {'test_module': {}}
                            assert tracer.exclude_targets == {}

                            # Verify other attributes
                            assert tracer.config == config
                            assert isinstance(tracer.tracked_objects, Mock)
                            assert isinstance(tracer.tracked_objects_lens, Mock)
                            assert isinstance(tracer.event_handlers, Mock)
                            assert isinstance(tracer.mp_handlers, Mock)
                            assert tracer.index_info == ""
                            assert tracer.current_index is None
                            assert tracer.indexes == {0}
                            assert tracer._call_depth == 0

    def test_init_with_locals_only(self):
        """Test Tracer initialization with only locals tracking enabled."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=True, with_globals=False)

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = set()
            mock_targets_instance.get_targets.return_value = {}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = ""
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls'):
                with patch('objwatch.tracer.MPHandls'):
                    with patch('objwatch.tracer.WeakIdKeyDictionary'):
                        with patch('objwatch.tracer.Tracer.load_wrapper') as mock_load_wrapper:
                            mock_load_wrapper.return_value = None
                            from objwatch.tracer import Tracer

                            tracer = Tracer(config)

                            # Verify locals tracking is initialized
                            assert hasattr(tracer, 'tracked_locals')
                            assert hasattr(tracer, 'tracked_locals_lens')

                            # Verify globals tracking is NOT initialized
                            assert not hasattr(tracer, 'tracked_globals')
                            assert not hasattr(tracer, 'tracked_globals_lens')
                            assert not hasattr(tracer, 'builtin_fields')

    def test_init_with_globals_only(self):
        """Test Tracer initialization with only globals tracking enabled."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=False, with_globals=True)

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = set()
            mock_targets_instance.get_targets.return_value = {}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = ""
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls'):
                with patch('objwatch.tracer.MPHandls'):
                    with patch('objwatch.tracer.WeakIdKeyDictionary'):
                        with patch('objwatch.tracer.Tracer.load_wrapper') as mock_load_wrapper:
                            mock_load_wrapper.return_value = None
                            from objwatch.tracer import Tracer

                            tracer = Tracer(config)

                            # Verify locals tracking is NOT initialized
                            assert not hasattr(tracer, 'tracked_locals')
                            assert not hasattr(tracer, 'tracked_locals_lens')

                            # Verify globals tracking is initialized
                            assert hasattr(tracer, 'tracked_globals')
                            assert hasattr(tracer, 'tracked_globals_lens')
                            assert hasattr(tracer, 'builtin_fields')

    def test_init_without_locals_or_globals(self):
        """Test Tracer initialization without locals or globals tracking."""
        config = ObjWatchConfig(targets=['test_module'], with_locals=False, with_globals=False)

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = set()
            mock_targets_instance.get_targets.return_value = {}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = ""
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls'):
                with patch('objwatch.tracer.MPHandls'):
                    with patch('objwatch.tracer.WeakIdKeyDictionary'):
                        with patch('objwatch.tracer.Tracer.load_wrapper') as mock_load_wrapper:
                            mock_load_wrapper.return_value = None
                            from objwatch.tracer import Tracer

                            tracer = Tracer(config)

                            # Verify neither locals nor globals tracking is initialized
                            assert not hasattr(tracer, 'tracked_locals')
                            assert not hasattr(tracer, 'tracked_locals_lens')
                            assert not hasattr(tracer, 'tracked_globals')
                            assert not hasattr(tracer, 'tracked_globals_lens')
                            assert not hasattr(tracer, 'builtin_fields')

    def test_init_with_custom_indexes(self):
        """Test Tracer initialization with custom indexes."""
        config = ObjWatchConfig(targets=['test_module'], indexes=[1, 2, 3])

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = set()
            mock_targets_instance.get_targets.return_value = {}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = ""
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls'):
                with patch('objwatch.tracer.MPHandls'):
                    with patch('objwatch.tracer.WeakIdKeyDictionary'):
                        with patch('objwatch.tracer.Tracer.load_wrapper') as mock_load_wrapper:
                            mock_load_wrapper.return_value = None
                            from objwatch.tracer import Tracer

                            tracer = Tracer(config)

                            # Verify custom indexes are set
                            assert tracer.indexes == {1, 2, 3}

    def test_init_with_none_indexes(self):
        """Test Tracer initialization with None indexes (should default to {0})."""
        config = ObjWatchConfig(targets=['test_module'], indexes=None)

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = set()
            mock_targets_instance.get_targets.return_value = {}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = ""
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls'):
                with patch('objwatch.tracer.MPHandls'):
                    with patch('objwatch.tracer.WeakIdKeyDictionary'):
                        with patch('objwatch.tracer.Tracer.load_wrapper') as mock_load_wrapper:
                            mock_load_wrapper.return_value = None
                            from objwatch.tracer import Tracer

                            tracer = Tracer(config)

                            # Verify default index is set
                            assert tracer.indexes == {0}

    def test_init_with_wrapper(self):
        """Test Tracer initialization with a custom wrapper."""

        # Create a real subclass of ABCWrapper for testing
        class TestWrapper(ABCWrapper):
            def wrap_call(self, func_name: str, frame: FrameType) -> str:
                return f"call_{func_name}"

            def wrap_return(self, func_name: str, result: Any) -> str:
                return f"return_{func_name}"

            def wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]:
                return f"old_{old_value}", f"new_{current_value}"

        config = ObjWatchConfig(targets=['test_module'], wrapper=TestWrapper)

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = set()
            mock_targets_instance.get_targets.return_value = {}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = ""
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls'):
                with patch('objwatch.tracer.MPHandls'):
                    with patch('objwatch.tracer.WeakIdKeyDictionary'):
                        with patch('objwatch.tracer.log_warn') as mock_log_warn:
                            from objwatch.tracer import Tracer

                            tracer = Tracer(config)

                            # Verify wrapper is loaded and initialized
                            assert tracer.abc_wrapper is not None
                            assert isinstance(tracer.abc_wrapper, TestWrapper)
                            mock_log_warn.assert_called_once_with("wrapper 'TestWrapper' loaded")

    def test_init_with_framework(self):
        """Test Tracer initialization with multi-process framework."""
        config = ObjWatchConfig(targets=['test_module'], framework='multiprocessing')

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = set()
            mock_targets_instance.get_targets.return_value = {}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = ""
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls'):
                with patch('objwatch.tracer.MPHandls') as mock_mp_handls:
                    mock_mp_instance = Mock()
                    mock_mp_handls.return_value = mock_mp_instance

                    with patch('objwatch.tracer.WeakIdKeyDictionary'):
                        with patch('objwatch.tracer.Tracer.load_wrapper') as mock_load_wrapper:
                            mock_load_wrapper.return_value = None
                            from objwatch.tracer import Tracer

                            tracer = Tracer(config)

                            # Verify MPHandls is initialized with framework
                            mock_mp_handls.assert_called_once_with(framework='multiprocessing')
                            assert tracer.mp_handlers == mock_mp_instance

    def test_init_with_output_xml(self):
        """Test Tracer initialization with XML output configuration."""
        config = ObjWatchConfig(targets=['test_module'], output_xml='output.xml')

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = set()
            mock_targets_instance.get_targets.return_value = {}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = ""
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls') as mock_event_handls:
                mock_event_instance = Mock()
                mock_event_handls.return_value = mock_event_instance

                with patch('objwatch.tracer.MPHandls'):
                    with patch('objwatch.tracer.WeakIdKeyDictionary'):
                        with patch('objwatch.tracer.Tracer.load_wrapper') as mock_load_wrapper:
                            mock_load_wrapper.return_value = None
                            from objwatch.tracer import Tracer

                            tracer = Tracer(config)

                            # Verify EventHandls is initialized with output_xml
                            mock_event_handls.assert_called_once_with(output_xml='output.xml')
                            assert tracer.event_handlers == mock_event_instance

    def test_init_methods_called(self):
        """Test that _build_target_index and _build_exclude_target_index are called."""
        config = ObjWatchConfig(targets=['test_module'])

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = set()
            mock_targets_instance.get_targets.return_value = {}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = ""
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls'):
                with patch('objwatch.tracer.MPHandls'):
                    with patch('objwatch.tracer.WeakIdKeyDictionary'):
                        with patch('objwatch.tracer.Tracer.load_wrapper') as mock_load_wrapper:
                            mock_load_wrapper.return_value = None
                            from objwatch.tracer import Tracer

                            # Mock the methods we want to verify are called
                            with patch.object(Tracer, '_build_target_index') as mock_build_target:
                                with patch.object(Tracer, '_build_exclude_target_index') as mock_build_exclude:
                                    tracer = Tracer(config)

                                    # Verify the methods are called
                                    mock_build_target.assert_called_once()
                                    mock_build_exclude.assert_called_once()

    def test_init_log_debug_called(self):
        """Test that log_debug is called with appropriate arguments."""
        config = ObjWatchConfig(targets=['test_module'])

        with patch('objwatch.tracer.Targets') as mock_targets_cls:
            mock_targets_instance = Mock()
            mock_targets_instance.get_filename_targets.return_value = {'file1.py', 'file2.py'}
            mock_targets_instance.get_targets.return_value = {'module': {}}
            mock_targets_instance.get_exclude_targets.return_value = {}
            mock_targets_instance.serialize_targets.return_value = "serialized_targets"
            mock_targets_cls.return_value = mock_targets_instance

            with patch('objwatch.tracer.EventHandls'):
                with patch('objwatch.tracer.MPHandls'):
                    with patch('objwatch.tracer.WeakIdKeyDictionary'):
                        with patch('objwatch.tracer.Tracer.load_wrapper') as mock_load_wrapper:
                            mock_load_wrapper.return_value = None
                            with patch('objwatch.tracer.log_debug') as mock_log_debug:
                                from objwatch.tracer import Tracer

                                tracer = Tracer(config)

                                # Verify log_debug was called
                                mock_log_debug.assert_called_once()
                                call_args = mock_log_debug.call_args[0][0]
                                assert "Targets:" in call_args
                                assert "serialized_targets" in call_args
                                assert "Filename targets:" in call_args
                                assert "file1.py" in call_args
                                assert "file2.py" in call_args
