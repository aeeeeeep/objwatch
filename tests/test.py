# MIT License
# Copyright (c) 2025 aeeeeeep

import os
import runpy
import importlib
import unittest
from unittest.mock import MagicMock, patch
import logging
from io import StringIO
import objwatch
from objwatch.wrappers import BaseWrapper, TensorShapeWrapper, ABCWrapper
from objwatch.core import ObjWatch
from objwatch.tracer import Tracer
from tests.util import strip_line_numbers

try:
    import torch
except ImportError:
    torch = None


golden_log = """DEBUG:objwatch:    run <module>
DEBUG:objwatch:    | run TestClass
DEBUG:objwatch:    | end TestClass
DEBUG:objwatch:    | run main
DEBUG:objwatch:    | | run TestClass.method
DEBUG:objwatch:    | | | upd TestClass.attr None -> 1
DEBUG:objwatch:    | | end TestClass.method
DEBUG:objwatch:    | end main
DEBUG:objwatch:   end <module>"""


class TestTracer(unittest.TestCase):
    def setUp(self):
        self.test_script = 'tests/test_script.py'
        with open(self.test_script, 'w') as f:
            f.write(
                """
class TestClass:
    def method(self):
        self.attr = 1
        self.attr += 1

def main():
    obj = TestClass()
    obj.method()

if __name__ == '__main__':
    main()
"""
            )

    def tearDown(self):
        os.remove(self.test_script)

    @patch('objwatch.utils.logger.get_logger')
    def test_tracer(self, mock_logger):
        mock_logger.return_value = unittest.mock.Mock()
        obj_watch = ObjWatch([self.test_script])
        obj_watch.start()

        with self.assertLogs('objwatch', level='DEBUG') as log:
            runpy.run_path(self.test_script, run_name="__main__")

        obj_watch.stop()

        test_log = '\n'.join(log.output)
        self.assertIn(golden_log, strip_line_numbers(test_log))


class TestWatch(unittest.TestCase):
    def setUp(self):
        self.test_script = 'tests/test_script.py'
        with open(self.test_script, 'w') as f:
            f.write(
                """
class TestClass:
    def method(self):
        self.attr = 1
        self.attr += 1

def main():
    obj = TestClass()
    obj.method()

if __name__ == '__main__':
    main()
"""
            )

    def tearDown(self):
        os.remove(self.test_script)

    @patch('objwatch.utils.logger.get_logger')
    def test_tracer(self, mock_logger):
        mock_logger.return_value = unittest.mock.Mock()
        obj_watch = objwatch.watch([self.test_script], simple=True)

        with self.assertLogs('objwatch', level='DEBUG') as log:
            runpy.run_path(self.test_script, run_name="__main__")

        obj_watch.stop()

        test_log = '\n'.join(log.output)
        self.assertIn(golden_log, strip_line_numbers(test_log))


class TestBaseWrapper(unittest.TestCase):
    def setUp(self):
        self.base_logger = BaseWrapper()

    def test_wrap_call_with_simple_args(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg1', 'arg2')
        mock_frame.f_code.co_argcount = 2
        mock_frame.f_locals = {'arg1': 10, 'arg2': [1, 2, 3, 4, 5]}
        expected_call_msg = "'0':10, '1':(list)[1, 2, 3, '... (2 more elements)']"
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_return_with_simple_return(self):
        result = 20
        expected_return_msg = "20"
        actual_return_msg = self.base_logger.wrap_return('test_func', result)
        self.assertEqual(actual_return_msg, expected_return_msg)

    def test_wrap_call_with_no_args(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ()
        mock_frame.f_code.co_argcount = 0
        mock_frame.f_locals = {}
        expected_call_msg = ""
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_return_with_list(self):
        result = [True, False, True, False]
        expected_return_msg = "[(list)[True, False, True, '... (1 more elements)']]"
        actual_return_msg = self.base_logger.wrap_return('test_func', result)
        self.assertEqual(actual_return_msg, expected_return_msg)

    def test_wrap_call_with_dict_under_limit(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg1',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'arg1': {'a': 1, 'b': 2}}
        expected_call_msg = "'0':(dict)[('a', 1), ('b', 2)]"
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_call_with_dict_over_limit(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg1',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'arg1': {'a': 1, 'b': 2, 'c': 3, 'd': 4}}
        expected_call_msg = "'0':(dict)[('a', 1), ('b', 2), ('c', 3), '... (1 more elements)']"
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_call_with_set_under_limit(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg1',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'arg1': {1, 2}}
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertTrue(actual_call_msg.startswith("'0':(set)["))
        self.assertIn("1", actual_call_msg)
        self.assertIn("2", actual_call_msg)
        self.assertFalse("..." in actual_call_msg, "Should not contain '...' for set under limit")

    def test_wrap_call_with_set_over_limit(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg1',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'arg1': {1, 2, 3, 4, 5}}
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertTrue(actual_call_msg.startswith("'0':(set)["))
        self.assertIn("... (2 more elements)", actual_call_msg)

    def test_wrap_call_with_empty_list(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg1',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'arg1': []}
        expected_call_msg = "'0':(list)[]"
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_call_with_empty_set(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg1',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'arg1': set()}
        expected_call_msg = "'0':(set)[]"
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_call_with_empty_dict(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg1',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'arg1': {}}
        expected_call_msg = "'0':(dict)[]"
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_call_with_dict_non_element_keys(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg1',)
        mock_frame.f_code.co_argcount = 1

        class CustomObj:
            pass

        test_dict = {CustomObj(): 123, 'a': 456}
        mock_frame.f_locals = {'arg1': test_dict}

        expected_call_msg = "'0':(dict)[2 elements]"
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)


@unittest.skipIf(torch is None, "PyTorch not installed, skipping TensorShapeWrapper tests.")
class TestTensorShapeWrapper(unittest.TestCase):
    def setUp(self):
        self.tensor_shape_logger = TensorShapeWrapper()

    def test_wrap_call_with_tensor(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('tensor_arg',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'tensor_arg': torch.randn(3, 4)}
        tensor_shape = mock_frame.f_locals['tensor_arg'].shape
        expected_call_msg = f"'0':{tensor_shape}"
        actual_call_msg = self.tensor_shape_logger.wrap_call('test_tensor_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_return_with_tensor(self):
        tensor = torch.randn(5, 6)
        expected_return_msg = f"{tensor.shape}"
        actual_return_msg = self.tensor_shape_logger.wrap_return('test_tensor_func', tensor)
        self.assertEqual(actual_return_msg, expected_return_msg)

    def test_wrap_call_with_mixed_args(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('tensor_arg', 'value')
        mock_frame.f_code.co_argcount = 2
        mock_frame.f_locals = {'tensor_arg': torch.randn(2, 2), 'value': 42}
        tensor_shape = mock_frame.f_locals['tensor_arg'].shape
        expected_call_msg = f"'0':{tensor_shape}, '1':42"
        actual_call_msg = self.tensor_shape_logger.wrap_call('test_mixed_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_call_with_tensor_list_over_limit(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg_tensors',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'arg_tensors': [torch.randn(2, 2) for _ in range(5)]}
        expected_call_msg = (
            "'0':(list)[torch.Size([2, 2]), torch.Size([2, 2]), torch.Size([2, 2]), '... (2 more elements)']"
        )
        actual_call_msg = self.tensor_shape_logger.wrap_call('test_tensor_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_call_with_tensor_set_over_limit(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg_tensors',)
        mock_frame.f_code.co_argcount = 1

        tensors_set = {torch.randn(2, 2) for _ in range(5)}
        mock_frame.f_locals = {'arg_tensors': tensors_set}
        expected_call_msg = (
            "'0':(set)[torch.Size([2, 2]), torch.Size([2, 2]), torch.Size([2, 2]), '... (2 more elements)']"
        )
        actual_call_msg = self.tensor_shape_logger.wrap_call('test_tensor_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_call_with_tensor_dict_over_limit(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg_tensors',)
        mock_frame.f_code.co_argcount = 1

        tensors_dict = {f"key_{i}": torch.randn(2, 2) for i in range(5)}
        mock_frame.f_locals = {'arg_tensors': tensors_dict}
        expected_call_msg = "'0':(dict)[('key_0', torch.Size([2, 2])), ('key_1', torch.Size([2, 2])), ('key_2', torch.Size([2, 2])), '... (2 more elements)']"
        actual_call_msg = self.tensor_shape_logger.wrap_call('test_tensor_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_call_with_empty_tensor_list(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg_tensors',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'arg_tensors': []}
        expected_call_msg = "'0':(list)[]"
        actual_call_msg = self.tensor_shape_logger.wrap_call('test_tensor_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)


class TestCustomWrapper(unittest.TestCase):
    def setUp(self):
        class CustomWrapper(ABCWrapper):
            def wrap_call(self, func_name, frame):
                return f"CustomCall: {func_name} called with args {frame.f_locals}"

            def wrap_return(self, func_name, result):
                return f"CustomReturn: {func_name} returned {result}"

            def wrap_upd(self, old_value, current_value):
                old_msg = self._format_value(old_value)
                current_msg = self._format_value(current_value)
                return old_msg, current_msg

        self.custom_wrapper = CustomWrapper

        self.log_stream = StringIO()
        self.logger = logging.getLogger('objwatch')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(self.log_stream)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.propagate = False

        self.obj_watch = ObjWatch(
            targets=['example_module.py'], wrapper=self.custom_wrapper, output=None, level=logging.DEBUG, simple=True
        )
        self.obj_watch.start()

    def test_custom_wrapper_call_and_return(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_filename = 'example_module.py'
        mock_frame.f_code.co_name = 'custom_func'
        mock_frame.f_locals = {'arg1': 'value1'}
        mock_frame.f_lineno = 42

        trace_func = self.obj_watch.tracer.trace_factory()

        trace_func(mock_frame, 'call', None)

        trace_func(mock_frame, 'return', 'custom_result')

        self.obj_watch.stop()

        self.log_stream.seek(0)
        logs = self.log_stream.read()

        self.assertIn("run custom_func <- CustomCall: custom_func called with args {'arg1': 'value1'}", logs)
        self.assertIn("end custom_func -> CustomReturn: custom_func returned custom_result", logs)

    def tearDown(self):
        self.obj_watch.stop()
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)


class TestTracerProcessTargetsStr(unittest.TestCase):
    def test_process_targets_with_submodules(self):
        tracer = Tracer(targets=['importlib'])
        processed = tracer._process_targets(['importlib'])

        main_module_file = importlib.__file__
        self.assertIn(main_module_file, processed, "Main module file was not processed.")

        submodules = [
            'importlib/metadata/_functools.py',
            'importlib/metadata/__init__.py',
            'importlib/resources/simple.py',
            'importlib/metadata/_adapters.py',
            'importlib/resources/_adapters.py',
            'importlib/__init__.py',
            'importlib/resources/_legacy.py',
            'importlib/metadata/_meta.py',
            'importlib/simple.py',
            'importlib/resources/__init__.py',
            'importlib/resources/readers.py',
            'importlib/metadata/_itertools.py',
            'importlib/metadata/_collections.py',
            'importlib/abc.py',
            'importlib/_abc.py',
            'importlib/resources/_common.py',
            'importlib/readers.py',
            'importlib/resources/abc.py',
            'importlib/metadata/_text.py',
            'importlib/resources/_itertools.py',
        ]

        for submodule_path in submodules:
            full_path = None
            try:
                submodule = importlib.import_module(submodule_path.replace('/', '.').rstrip('.py'))
                if hasattr(submodule, '__file__') and submodule.__file__:
                    full_path = submodule.__file__
                    self.assertIn(full_path, processed, f"Submodule {submodule_path} was not processed.")
            except ImportError:
                pass


class TestTracerProcessTargetsModule(unittest.TestCase):
    def test_process_targets_with_submodules(self):
        tracer = Tracer(targets=[importlib])
        processed = tracer._process_targets([importlib])

        main_module_file = importlib.__file__
        self.assertIn(main_module_file, processed, "Main module file was not processed.")

        submodules = [
            'importlib/metadata/_functools.py',
            'importlib/metadata/__init__.py',
            'importlib/resources/simple.py',
            'importlib/metadata/_adapters.py',
            'importlib/resources/_adapters.py',
            'importlib/__init__.py',
            'importlib/resources/_legacy.py',
            'importlib/metadata/_meta.py',
            'importlib/simple.py',
            'importlib/resources/__init__.py',
            'importlib/resources/readers.py',
            'importlib/metadata/_itertools.py',
            'importlib/metadata/_collections.py',
            'importlib/abc.py',
            'importlib/_abc.py',
            'importlib/resources/_common.py',
            'importlib/readers.py',
            'importlib/resources/abc.py',
            'importlib/metadata/_text.py',
            'importlib/resources/_itertools.py',
        ]

        for submodule_path in submodules:
            full_path = None
            try:
                submodule = importlib.import_module(submodule_path.replace('/', '.').rstrip('.py'))
                if hasattr(submodule, '__file__') and submodule.__file__:
                    full_path = submodule.__file__
                    self.assertIn(full_path, processed, f"Submodule {submodule_path} was not processed.")
            except ImportError:
                pass


class TestLoggerForce(unittest.TestCase):
    def setUp(self):
        import objwatch.utils.logger

        objwatch.utils.logger.FORCE = False

    def tearDown(self):
        import objwatch.utils.logger

        objwatch.utils.logger.FORCE = False

    @patch('builtins.print')
    def test_log_info_force_true(self, mock_print):
        import objwatch.utils.logger

        objwatch.utils.logger.create_logger(level='force')

        msg = "Forced log message"
        objwatch.utils.logger.log_info(msg)

        mock_print.assert_called_with(msg, flush=True)

    @patch('builtins.print')
    def test_log_debug_force_true(self, mock_print):
        import objwatch.utils.logger

        objwatch.utils.logger.create_logger(level='force')

        msg = "Forced debug message"
        objwatch.utils.logger.log_debug(msg)

        mock_print.assert_called_with(msg, flush=True)

    @patch('builtins.print')
    def test_log_warn_force_true(self, mock_print):
        import objwatch.utils.logger

        objwatch.utils.logger.create_logger(level='force')

        msg = "Forced warning message"
        objwatch.utils.logger.log_warn(msg)

        mock_print.assert_called_with(msg, flush=True)

    @patch('objwatch.utils.logger.logger.info')
    @patch('objwatch.utils.logger.logger.debug')
    @patch('objwatch.utils.logger.logger.warning')
    @patch('builtins.print')
    def test_log_functions_force_false(self, mock_print, mock_warning, mock_debug, mock_info):
        import objwatch.utils.logger

        objwatch.utils.logger.create_logger(level=logging.DEBUG)

        info_msg = "Normal log message"
        objwatch.utils.logger.log_info(info_msg)
        mock_info.assert_called_with(info_msg)
        mock_print.assert_not_called()

        debug_msg = "Normal debug message"
        objwatch.utils.logger.log_debug(debug_msg)
        mock_debug.assert_called_with(debug_msg)
        mock_print.assert_not_called()

        warn_msg = "Normal warning message"
        objwatch.utils.logger.log_warn(warn_msg)
        mock_warning.assert_called_with(warn_msg)
        mock_print.assert_not_called()


if __name__ == '__main__':
    unittest.main()
