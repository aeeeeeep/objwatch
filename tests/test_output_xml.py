# MIT License
# Copyright (c) 2025 aeeeeeep

import os
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from objwatch.tracer import Tracer
from objwatch.wrappers import BaseWrapper
from tests.util import compare_xml_elements


class TestOutputXML(unittest.TestCase):
    def setUp(self):
        self.test_output = "test_trace.xml"
        self.golden_output = "tests/utils/golden_output_xml.xml"

        self.tracer = Tracer(
            targets="tests/test_output_xml.py",
            output_xml=self.test_output,
            wrapper=BaseWrapper,
            with_module_path=True,
            with_locals=True,
        )

    def tearDown(self):
        self.tracer.stop()
        if os.path.exists(self.test_output):
            os.remove(self.test_output)

    def test_output_xml(self):
        class TestClass:
            def outer_function(self):
                self.a = 10

                self.b = [1, 2, 3]
                self.b.append(4)
                self.b.remove(2)
                self.b[0] = 100

                self.c = {'key1': 'value1'}
                self.c['key2'] = 'value2'
                self.c['key1'] = 'updated_value1'
                del self.c['key2']

                self.d = {1, 2, 3}
                self.d.add(4)
                self.d.remove(2)
                self.d.update({5, 6})
                self.d.discard(1)

                self.a = 20

                self.a = self.inner_function(self.b)
                return self.a

            def inner_function(self, lst):
                a = 10

                b = [1, 2, 3]
                b.append(4)
                b.remove(1)
                b[0] = 100

                self.lst = lst
                self.lst.append(5)
                self.lst[0] = 200

                self.e = {'inner_key1': 'inner_value1'}
                self.e['inner_key2'] = 'inner_value2'
                self.e['inner_key1'] = 'updated_inner_value1'
                del self.e['inner_key2']

                self.f = {10, 20, 30}
                self.f.add(40)
                self.f.remove(20)
                self.f.update({50, 60})
                self.f.discard(10)

                return self.lst

        with patch.object(self.tracer, 'trace_factory', return_value=self.tracer.trace_factory()):
            self.tracer.start()
            try:
                t = TestClass()
                t.outer_function()
            finally:
                self.tracer.stop()

        self.assertTrue(os.path.exists(self.test_output), "XML trace file was not generated.")

        generated_tree = ET.parse(self.test_output)
        generated_root = generated_tree.getroot()

        self.assertTrue(os.path.exists(self.golden_output), "Golden XML trace file does not exist.")
        golden_tree = ET.parse(self.golden_output)
        golden_root = golden_tree.getroot()

        self.assertTrue(
            compare_xml_elements(generated_root, golden_root), "Generated XML does not match the golden XML."
        )


if __name__ == '__main__':
    unittest.main()
