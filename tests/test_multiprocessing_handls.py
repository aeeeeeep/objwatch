import runpy
import unittest
from objwatch import ObjWatch
from objwatch.wrappers import BaseWrapper
from unittest.mock import patch
from tests.util import strip_line_numbers


class TestMultiprocessingCalculations(unittest.TestCase):
    def setUp(self):
        self.test_script = 'tests/utils/multiprocessing_calculate.py'

    @patch('objwatch.utils.logger.get_logger')
    def test_multiprocessing_calculations(self, mock_logger):
        mock_logger.return_value = unittest.mock.Mock()
        obj_watch = ObjWatch(
            [self.test_script],
            framework='multiprocessing',
            indexes=[0, 4],
            with_locals=False,
            wrapper=BaseWrapper,
        )
        obj_watch.start()

        with self.assertLogs('objwatch', level='DEBUG') as log:
            runpy.run_path(self.test_script, run_name="__main__")

        obj_watch.stop()

        test_log = '\n'.join(log.output)
        golden_log_path = 'tests/utils/multiprocessing_calculate.txt'
        with open(golden_log_path, 'r') as f:
            golden_log = f.read()
        print(test_log)
        self.assertIn(strip_line_numbers(test_log), strip_line_numbers(golden_log))


if __name__ == '__main__':
    unittest.main()
