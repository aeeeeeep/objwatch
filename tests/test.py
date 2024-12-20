import os
import runpy
import unittest
from unittest.mock import MagicMock, patch
import logging
from io import StringIO
import objwatch
from objwatch.wrappers import BaseLogger, TensorShapeLogger, FunctionWrapper
from objwatch.core import ObjWatch

try:
    import torch
except ImportError:
    torch = None


golden_log = """DEBUG:objwatch:run <module>
DEBUG:objwatch:| run TestClass
DEBUG:objwatch:| end TestClass
DEBUG:objwatch:| run main
DEBUG:objwatch:| | run TestClass.method
DEBUG:objwatch:| | | upd TestClass.attr
DEBUG:objwatch:| | end TestClass.method
DEBUG:objwatch:| end main
DEBUG:objwatch:end <module>"""


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
        self.assertIn(golden_log, test_log)


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
        obj_watch = objwatch.watch([self.test_script])

        with self.assertLogs('objwatch', level='DEBUG') as log:
            runpy.run_path(self.test_script, run_name="__main__")

        obj_watch.stop()

        test_log = '\n'.join(log.output)
        self.assertIn(golden_log, test_log)


class TestBaseLogger(unittest.TestCase):
    def setUp(self):
        self.base_logger = BaseLogger()

    def test_wrap_call_with_simple_args(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('arg1', 'arg2')
        mock_frame.f_code.co_argcount = 2
        mock_frame.f_locals = {'arg1': 10, 'arg2': [1, 2, 3, 4, 5]}
        expected_call_msg = " <- '0':10, '1':[value_0:1, value_1:2, value_2:3...(2 more elements)]"
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_return_with_simple_return(self):
        result = 20
        expected_return_msg = " -> 'result':20"
        actual_return_msg = self.base_logger.wrap_return('test_func', result)
        self.assertEqual(actual_return_msg, expected_return_msg)

    def test_wrap_call_with_no_args(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ()
        mock_frame.f_code.co_argcount = 0
        mock_frame.f_locals = {}
        expected_call_msg = " <- "
        actual_call_msg = self.base_logger.wrap_call('test_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_return_with_list(self):
        result = [True, False, True, False]
        expected_return_msg = " -> ['result':[value_0:True, value_1:False, value_2:True...(1 more elements)]]"
        actual_return_msg = self.base_logger.wrap_return('test_func', result)
        self.assertEqual(actual_return_msg, expected_return_msg)


@unittest.skipIf(torch is None, "PyTorch not installed, skipping TensorShapeLogger tests.")
class TestTensorShapeLogger(unittest.TestCase):
    def setUp(self):
        self.tensor_shape_logger = TensorShapeLogger()

    def test_wrap_call_with_tensor(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('tensor_arg',)
        mock_frame.f_code.co_argcount = 1
        mock_frame.f_locals = {'tensor_arg': torch.randn(3, 4)}
        tensor_shape = mock_frame.f_locals['tensor_arg'].shape
        expected_call_msg = f" <- '0':{tensor_shape}"
        actual_call_msg = self.tensor_shape_logger.wrap_call('test_tensor_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)

    def test_wrap_return_with_tensor(self):
        tensor = torch.randn(5, 6)
        expected_return_msg = f" -> {tensor.shape}"
        actual_return_msg = self.tensor_shape_logger.wrap_return('test_tensor_func', tensor)
        self.assertEqual(actual_return_msg, expected_return_msg)

    def test_wrap_call_with_mixed_args(self):
        mock_frame = MagicMock()
        mock_frame.f_code.co_varnames = ('tensor_arg', 'value')
        mock_frame.f_code.co_argcount = 2
        mock_frame.f_locals = {'tensor_arg': torch.randn(2, 2), 'value': 42}
        tensor_shape = mock_frame.f_locals['tensor_arg'].shape
        expected_call_msg = f" <- '0':{tensor_shape}, '1':42"
        actual_call_msg = self.tensor_shape_logger.wrap_call('test_mixed_func', mock_frame)
        self.assertEqual(actual_call_msg, expected_call_msg)


class TestCustomWrapper(unittest.TestCase):
    def setUp(self):
        class CustomWrapper(FunctionWrapper):
            def wrap_call(self, func_name, frame):
                return f" <- CustomCall: {func_name} called with args {frame.f_locals}"

            def wrap_return(self, func_name, result):
                return f" -> CustomReturn: {func_name} returned {result}"

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

        trace_func = self.obj_watch.tracer.trace_func_factory()

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


if __name__ == '__main__':
    unittest.main()
