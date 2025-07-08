# MIT License
# Copyright (c) 2025 aeeeeeep

import unittest
from objwatch.targets import Targets
from tests.utils.example_targets import sample_module


class TestTargets(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_module_monitoring(self):
        targets = Targets(['tests.utils.example_targets.sample_module'])
        processed = targets.get_processed_targets()

        self.assertIn('tests.utils.example_targets.sample_module', processed)
        mod = processed['tests.utils.example_targets.sample_module']
        self.assertIn('SampleClass', mod['classes'])
        self.assertIn('module_function', mod['functions'])
        self.assertIn('GLOBAL_VAR', mod['globals'])

    def test_class_definition(self):
        targets = Targets(['tests.utils.example_targets.sample_module:SampleClass'])
        processed = targets.get_processed_targets()

        cls_info = processed['tests.utils.example_targets.sample_module']['classes']['SampleClass']
        self.assertIn('class_method', cls_info['methods'])
        self.assertIn('static_method', cls_info['methods'])
        self.assertIn('method', cls_info['methods'])
        self.assertIn('class_attr', cls_info['attributes'])

    def test_class_attribute(self):
        targets = Targets(['tests.utils.example_targets.sample_module:SampleClass.class_attr'])
        processed = targets.get_processed_targets()

        cls_info = processed['tests.utils.example_targets.sample_module']['classes']['SampleClass']
        self.assertIn('class_attr', cls_info['attributes'])

    def test_class_method(self):
        targets = Targets(['tests.utils.example_targets.sample_module:SampleClass.class_method()'])
        processed = targets.get_processed_targets()

        cls_info = processed['tests.utils.example_targets.sample_module']['classes']['SampleClass']
        self.assertIn('class_method', cls_info['methods'])

    def test_function_target(self):
        targets = Targets(['tests.utils.example_targets.sample_module:module_function()'])
        processed = targets.get_processed_targets()

        self.assertIn('module_function', processed['tests.utils.example_targets.sample_module']['functions'])

    def test_global_variable(self):
        targets = Targets(['tests.utils.example_targets.sample_module::GLOBAL_VAR'])
        processed = targets.get_processed_targets()

        self.assertIn('GLOBAL_VAR', processed['tests.utils.example_targets.sample_module']['globals'])

    def test_exclusion_rules(self):
        targets = Targets(
            ['tests.utils.example_targets.sample_module'],
            exclude_targets=['tests.utils.example_targets.sample_module:SampleClass.class_method()'],
        )
        processed = targets.get_processed_targets()

        cls_info = processed['tests.utils.example_targets.sample_module']['classes']['SampleClass']
        self.assertNotIn('class_method', cls_info['methods'])

    def test_exclude_class_attribute(self):
        targets = Targets(
            ['tests.utils.example_targets.sample_module'],
            exclude_targets=['tests.utils.example_targets.sample_module:SampleClass.class_attr'],
        )
        processed = targets.get_processed_targets()

        cls_info = processed['tests.utils.example_targets.sample_module']['classes']['SampleClass']
        self.assertNotIn('class_attr', cls_info['attributes'])

    def test_exclude_module_function(self):
        targets = Targets(
            ['tests.utils.example_targets.sample_module'],
            exclude_targets=['tests.utils.example_targets.sample_module:module_function()'],
        )
        processed = targets.get_processed_targets()

        mod_info = processed['tests.utils.example_targets.sample_module']
        self.assertNotIn('module_function', mod_info['functions'])

    def test_exclude_global_variable(self):
        targets = Targets(
            ['tests.utils.example_targets.sample_module'],
            exclude_targets=['tests.utils.example_targets.sample_module::GLOBAL_VAR'],
        )
        processed = targets.get_processed_targets()

        mod_info = processed['tests.utils.example_targets.sample_module']
        self.assertNotIn('GLOBAL_VAR', mod_info['globals'])

    def test_mixed_exclusions(self):
        targets = Targets(
            ['tests.utils.example_targets.sample_module'],
            exclude_targets=[
                'tests.utils.example_targets.sample_module:SampleClass.static_method()',
                'tests.utils.example_targets.sample_module::GLOBAL_VAR',
                'tests.utils.example_targets.sample_module:module_function()',
            ],
        )
        processed = targets.get_processed_targets()

        mod_info = processed['tests.utils.example_targets.sample_module']
        cls_info = mod_info['classes']['SampleClass']
        self.assertNotIn('static_method', cls_info['methods'])
        self.assertNotIn('GLOBAL_VAR', mod_info['globals'])
        self.assertNotIn('module_function', mod_info['functions'])

    def test_object_module_monitoring(self):
        targets = Targets([sample_module])
        processed = targets.get_processed_targets()

        self.assertIn(sample_module.__name__, processed)
        mod = processed[sample_module.__name__]
        self.assertIn('SampleClass', mod['classes'])
        self.assertIn('module_function', mod['functions'])
        self.assertIn('GLOBAL_VAR', mod['globals'])

    def test_object_class_methods(self):
        from tests.utils.example_targets.sample_module import SampleClass

        targets = Targets([SampleClass.class_method, SampleClass.static_method, SampleClass.method])
        processed = targets.get_processed_targets()

        cls_info = processed[sample_module.__name__]['classes']['SampleClass']
        self.assertIn('class_method', cls_info['methods'])
        self.assertIn('static_method', cls_info['methods'])
        self.assertIn('method', cls_info['methods'])

    def test_object_functions_and_globals(self):
        targets = Targets([sample_module.module_function, "tests.utils.example_targets.sample_module::GLOBAL_VAR"])
        processed = targets.get_processed_targets()

        mod_info = processed[sample_module.__name__]
        self.assertIn('module_function', mod_info['functions'])
        self.assertIn('GLOBAL_VAR', mod_info['globals'])


if __name__ == '__main__':
    unittest.main()
