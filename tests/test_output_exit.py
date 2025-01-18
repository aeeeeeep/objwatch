# MIT License
# Copyright (c) 2025 aeeeeeep

import os
import runpy
import signal
import time
import unittest
from unittest.mock import patch
from tests.util import compare_xml_elements
import xml.etree.ElementTree as ET

try:
    import torch
except ImportError:
    torch = None


class TestForceKill(unittest.TestCase):
    def setUp(self):
        self.test_script = 'tests/test_script.py'
        self.test_output = 'test_exit.xml'
        self.golden_output = "tests/utils/golden_output_exit.xml"
        with open(self.test_script, 'w') as f:
            f.write(
                f"""
import time

class TestClass:
    def method(self):
        self.attr = 1
        self.attr += 1
        time.sleep(10)  # Simulate long-running process

def main():
    obj = TestClass()
    obj.method()
    obj.method()

if __name__ == '__main__':
    from objwatch import ObjWatch
    obj_watch = ObjWatch(['tests/test_script.py'], output_xml='{self.test_output}')
    obj_watch.start()
    main()
"""
            )

    def tearDown(self):
        os.remove(self.test_script)

    @patch('objwatch.utils.logger.get_logger')
    def test_force_kill(self, mock_logger):
        mock_logger.return_value = unittest.mock.Mock()

        signal_dict = {
            "SIGTERM": signal.SIGTERM,  # Termination signal (default)
            "SIGINT": signal.SIGINT,  # Interrupt from keyboard (Ctrl + C)
            "SIGABRT": signal.SIGABRT,  # Abort signal from program (e.g., abort() call)
            "SIGHUP": signal.SIGHUP,  # Hangup signal (usually for daemon processes)
            "SIGQUIT": signal.SIGQUIT,  # Quit signal (generates core dump)
            "SIGUSR1": signal.SIGUSR1,  # User-defined signal 1
            "SIGUSR2": signal.SIGUSR2,  # User-defined signal 2
            "SIGALRM": signal.SIGALRM,  # Alarm signal (usually for timers)
            "SIGSEGV": signal.SIGSEGV,  # Segmentation fault (access violation)
        }

        for signal_key, test_signal in signal_dict.items():
            print(f"signal type: {signal_key}")

            pid = os.fork()

            if pid == 0:
                try:
                    runpy.run_path(self.test_script, run_name="__main__")
                except Exception as e:
                    print(f"Error during script execution: {e}")
                finally:
                    os._exit(0)
            else:
                time.sleep(0.1)

                os.kill(pid, test_signal)

                os.waitpid(pid, 0)

                self.assertTrue(
                    os.path.exists(self.test_output), f"XML trace file was not generated for signal {signal_key}."
                )

                generated_tree = ET.parse(self.test_output)
                generated_root = generated_tree.getroot()

                self.assertTrue(os.path.exists(self.golden_output), "Golden XML trace file does not exist.")
                golden_tree = ET.parse(self.golden_output)
                golden_root = golden_tree.getroot()

                self.assertTrue(
                    compare_xml_elements(generated_root, golden_root),
                    f"Generated XML does not match the golden XML for signal {signal_key}.",
                )

                if os.path.exists(self.test_output):
                    os.remove(self.test_output)


if __name__ == '__main__':
    unittest.main()
