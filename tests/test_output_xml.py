import os
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from objwatch.tracer import Tracer


class TestOutputXML(unittest.TestCase):
    def setUp(self):
        self.test_output = "test_trace.xml"
        self.golden_output = "tests/utils/golden_output_xml.xml"

        self.tracer = Tracer(targets="tests/test_output_xml.py", with_module_path=True, output_xml=self.test_output)

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
                self.a = 20
                self.a = self.inner_function(self.b)

            def inner_function(self, lst):
                self.lst = lst
                self.lst.append(5)
                self.lst[0] = 100
                return self.lst

        with patch.object(self.tracer, 'trace_func_factory', return_value=self.tracer.trace_func_factory()):
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
            self.compare_elements(generated_root, golden_root), "Generated XML does not match the golden XML."
        )

    def compare_elements(self, elem1, elem2):
        if elem1.tag != elem2.tag:
            return False
        if elem1.attrib != elem2.attrib:
            return False
        if (elem1.text or '').strip() != (elem2.text or '').strip():
            return False
        if len(elem1) != len(elem2):
            return False
        return all(self.compare_elements(c1, c2) for c1, c2 in zip(elem1, elem2))


if __name__ == '__main__':
    unittest.main()
