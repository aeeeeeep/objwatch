import os
import runpy
import unittest
from objwatch import ObjWatch
from objwatch.wrappers import BaseWrapper
from unittest.mock import patch
from tests.util import strip_line_numbers

golden_log = """DEBUG:objwatch:    run <module> <- 
DEBUG:objwatch:   | run worker <- 
DEBUG:objwatch:   | | run main_calculate <- '0':1
DEBUG:objwatch:   | | end main_calculate -> 1012
DEBUG:objwatch:   | end worker -> None
DEBUG:objwatch:   end <module> -> None"""

golden_index_0_log = """DEBUG: [#0]     4 | | run calculate <- '0':0, '1':(type)Queue
DEBUG: [#0]    11 | | end calculate -> 6"""

golden_index_12_log = """DEBUG: [#12]     4 | | run calculate <- '0':12, '1':(type)Queue
DEBUG: [#12]    11 | | end calculate -> 12078"""


class TestMultiprocessingCalculations(unittest.TestCase):
    def setUp(self):
        self.test_script = 'tests/utils/multiprocessing_calculate.py'
        self.output_log = 'test_multiprocessing_handls.log'
        self.index_0_log = 'multiprocessing-0.log'
        self.index_12_log = 'multiprocessing-12.log'

    def tearDown(self):
        # os.remove(self.output_log)
        os.remove(self.index_0_log)
        os.remove(self.index_12_log)

    @patch('objwatch.utils.logger.get_logger')
    def test_multiprocessing_calculations(self, mock_logger):
        mock_logger.return_value = unittest.mock.Mock()
        obj_watch = ObjWatch(
            [self.test_script],
            framework='multiprocessing',
            indexes=[0, 12],
            simple=True,
            output=self.output_log,
            with_locals=False,
            wrapper=BaseWrapper,
        )
        obj_watch.start()

        with self.assertLogs('objwatch', level='DEBUG') as log:
            runpy.run_path(self.test_script, run_name="__main__")

        obj_watch.stop()

        test_log = '\n'.join(log.output)
        with open(self.index_0_log, 'r') as f:
            index_0_log = f.read()
        with open(self.index_12_log, 'r') as f:
            index_12_log = f.read()

        # self.assertIn(strip_line_numbers(test_log), strip_line_numbers(golden_log))
        self.assertIn(strip_line_numbers(index_0_log), strip_line_numbers(golden_index_0_log))
        self.assertIn(strip_line_numbers(index_12_log), strip_line_numbers(golden_index_12_log))


if __name__ == '__main__':
    unittest.main()
