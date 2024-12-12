import os
import runpy
import unittest
from unittest.mock import patch
import objwatch
from objwatch.core import ObjWatch


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

    @patch('objwatch.logger.get_logger')
    def test_tracer(self, mock_logger):
        mock_logger.return_value = unittest.mock.Mock()
        obj_watch = ObjWatch([self.test_script])
        obj_watch.start()

        runpy.run_path(self.test_script, run_name="__main__")

        with self.assertLogs('objwatch', level='DEBUG') as log:
            runpy.run_path(self.test_script, run_name="__main__")

        obj_watch.stop()

        self.assertIn('run <module>', log.output[0])
        self.assertIn('run TestClass', log.output[1])
        self.assertIn('run main', log.output[2])
        self.assertIn('run TestClass.method', log.output[3])
        self.assertIn('upd TestClass.attr', log.output[4])


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

    @patch('objwatch.logger.get_logger')
    def test_tracer(self, mock_logger):
        mock_logger.return_value = unittest.mock.Mock()
        obj_watch = objwatch.watch([self.test_script])

        runpy.run_path(self.test_script, run_name="__main__")

        with self.assertLogs('objwatch', level='DEBUG') as log:
            runpy.run_path(self.test_script, run_name="__main__")

        obj_watch.stop()

        self.assertIn('run <module>', log.output[0])
        self.assertIn('run TestClass', log.output[1])
        self.assertIn('run main', log.output[2])
        self.assertIn('run TestClass.method', log.output[3])
        self.assertIn('upd TestClass.attr', log.output[4])


if __name__ == '__main__':
    unittest.main()
