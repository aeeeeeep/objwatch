# file: objwatch/tracer.py:171-236
# asked: {"lines": [171, 191, 192, 193, 194, 195, 196, 197, 200, 202, 203, 205, 208, 211, 212, 213, 214, 217, 218, 219, 220, 223, 224, 227, 228, 230, 231, 232, 233, 234, 235], "branches": [[200, 202], [200, 230], [203, 205], [203, 223], [212, 213], [212, 217], [218, 203], [218, 219], [223, 224], [223, 227], [227, 200], [227, 228]]}
# gained: {"lines": [171, 191, 192, 193, 194, 195, 196, 197, 200, 202, 203, 205, 208, 211, 212, 213, 214, 217, 218, 219, 220, 223, 224, 227, 228, 230, 231, 232, 233, 234, 235], "branches": [[200, 202], [200, 230], [203, 205], [203, 223], [212, 213], [212, 217], [218, 203], [218, 219], [223, 224], [223, 227], [227, 200], [227, 228]]}

import pytest
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerBuildExcludeTargetIndex:
    """Test cases for Tracer._build_exclude_target_index method."""

    def test_build_exclude_target_index_empty(self):
        """Test _build_exclude_target_index with empty exclude_targets."""
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Clear any existing exclude targets
        tracer.exclude_targets = {}

        # Call the method
        tracer._build_exclude_target_index()

        # Verify all indexes are empty
        assert tracer.exclude_module_index == set()
        assert tracer.exclude_class_index == {}
        assert tracer.exclude_method_index == {}
        assert tracer.exclude_attribute_index == {}
        assert tracer.exclude_function_index == {}
        assert tracer.exclude_global_index == {}
        assert tracer.exclude_class_info == {}
        assert tracer.exclude_index_map == {'class': {}, 'method': {}, 'attribute': {}, 'function': {}, 'global': {}}

    def test_build_exclude_target_index_with_classes_only(self):
        """Test _build_exclude_target_index with only classes in exclude_targets."""
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Set up exclude targets with classes only
        tracer.exclude_targets = {
            'module1': {
                'classes': {'ClassA': {'methods': [], 'attributes': []}, 'ClassB': {'methods': [], 'attributes': []}},
                'functions': [],
                'globals': [],
            }
        }

        # Call the method
        tracer._build_exclude_target_index()

        # Verify module index
        assert tracer.exclude_module_index == {'module1'}

        # Verify class index
        assert tracer.exclude_class_index == {'module1': {'ClassA', 'ClassB'}}

        # Verify method index (empty since no methods specified)
        assert tracer.exclude_method_index == {}

        # Verify attribute index (empty since no attributes specified)
        assert tracer.exclude_attribute_index == {}

        # Verify function index (empty)
        assert tracer.exclude_function_index == {}

        # Verify global index (empty)
        assert tracer.exclude_global_index == {}

        # Verify class info
        assert tracer.exclude_class_info == {
            'module1': {'ClassA': {'methods': [], 'attributes': []}, 'ClassB': {'methods': [], 'attributes': []}}
        }

        # Verify index map
        assert tracer.exclude_index_map == {
            'class': {'module1': {'ClassA', 'ClassB'}},
            'method': {},
            'attribute': {},
            'function': {},
            'global': {},
        }

    def test_build_exclude_target_index_with_methods_and_attributes(self):
        """Test _build_exclude_target_index with methods and attributes in classes."""
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Set up exclude targets with classes containing methods and attributes
        tracer.exclude_targets = {
            'module1': {
                'classes': {
                    'ClassA': {'methods': ['method1', 'method2'], 'attributes': ['attr1', 'attr2']},
                    'ClassB': {'methods': ['method3'], 'attributes': ['attr3']},
                },
                'functions': [],
                'globals': [],
            }
        }

        # Call the method
        tracer._build_exclude_target_index()

        # Verify module index
        assert tracer.exclude_module_index == {'module1'}

        # Verify class index
        assert tracer.exclude_class_index == {'module1': {'ClassA', 'ClassB'}}

        # Verify method index
        assert tracer.exclude_method_index == {'module1': {'ClassA': {'method1', 'method2'}, 'ClassB': {'method3'}}}

        # Verify attribute index
        assert tracer.exclude_attribute_index == {'module1': {'ClassA': {'attr1', 'attr2'}, 'ClassB': {'attr3'}}}

        # Verify function index (empty)
        assert tracer.exclude_function_index == {}

        # Verify global index (empty)
        assert tracer.exclude_global_index == {}

        # Verify class info
        assert tracer.exclude_class_info == {
            'module1': {
                'ClassA': {'methods': ['method1', 'method2'], 'attributes': ['attr1', 'attr2']},
                'ClassB': {'methods': ['method3'], 'attributes': ['attr3']},
            }
        }

        # Verify index map
        assert tracer.exclude_index_map == {
            'class': {'module1': {'ClassA', 'ClassB'}},
            'method': {'module1': {'ClassA': {'method1', 'method2'}, 'ClassB': {'method3'}}},
            'attribute': {'module1': {'ClassA': {'attr1', 'attr2'}, 'ClassB': {'attr3'}}},
            'function': {},
            'global': {},
        }

    def test_build_exclude_target_index_with_functions_and_globals(self):
        """Test _build_exclude_target_index with functions and globals."""
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Set up exclude targets with functions and globals
        tracer.exclude_targets = {
            'module1': {'classes': {}, 'functions': ['func1', 'func2'], 'globals': ['global1', 'global2']},
            'module2': {'classes': {}, 'functions': ['func3'], 'globals': ['global3']},
        }

        # Call the method
        tracer._build_exclude_target_index()

        # Verify module index
        assert tracer.exclude_module_index == {'module1', 'module2'}

        # Verify class index (empty)
        assert tracer.exclude_class_index == {}

        # Verify method index (empty)
        assert tracer.exclude_method_index == {}

        # Verify attribute index (empty)
        assert tracer.exclude_attribute_index == {}

        # Verify function index
        assert tracer.exclude_function_index == {'module1': {'func1', 'func2'}, 'module2': {'func3'}}

        # Verify global index
        assert tracer.exclude_global_index == {'module1': {'global1', 'global2'}, 'module2': {'global3'}}

        # Verify class info (empty)
        assert tracer.exclude_class_info == {}

        # Verify index map
        assert tracer.exclude_index_map == {
            'class': {},
            'method': {},
            'attribute': {},
            'function': {'module1': {'func1', 'func2'}, 'module2': {'func3'}},
            'global': {'module1': {'global1', 'global2'}, 'module2': {'global3'}},
        }

    def test_build_exclude_target_index_complete_scenario(self):
        """Test _build_exclude_target_index with complete scenario including all types."""
        config = ObjWatchConfig(targets=['test_module'])
        tracer = Tracer(config)

        # Set up comprehensive exclude targets
        tracer.exclude_targets = {
            'module1': {
                'classes': {
                    'ClassA': {'methods': ['method_a1', 'method_a2'], 'attributes': ['attr_a1', 'attr_a2']},
                    'ClassB': {'methods': ['method_b1'], 'attributes': ['attr_b1']},
                },
                'functions': ['func1', 'func2'],
                'globals': ['global1', 'global2'],
            },
            'module2': {
                'classes': {'ClassC': {'methods': ['method_c1'], 'attributes': ['attr_c1', 'attr_c2']}},
                'functions': ['func3'],
                'globals': ['global3'],
            },
        }

        # Call the method
        tracer._build_exclude_target_index()

        # Verify module index
        assert tracer.exclude_module_index == {'module1', 'module2'}

        # Verify class index
        assert tracer.exclude_class_index == {'module1': {'ClassA', 'ClassB'}, 'module2': {'ClassC'}}

        # Verify method index
        assert tracer.exclude_method_index == {
            'module1': {'ClassA': {'method_a1', 'method_a2'}, 'ClassB': {'method_b1'}},
            'module2': {'ClassC': {'method_c1'}},
        }

        # Verify attribute index
        assert tracer.exclude_attribute_index == {
            'module1': {'ClassA': {'attr_a1', 'attr_a2'}, 'ClassB': {'attr_b1'}},
            'module2': {'ClassC': {'attr_c1', 'attr_c2'}},
        }

        # Verify function index
        assert tracer.exclude_function_index == {'module1': {'func1', 'func2'}, 'module2': {'func3'}}

        # Verify global index
        assert tracer.exclude_global_index == {'module1': {'global1', 'global2'}, 'module2': {'global3'}}

        # Verify class info
        assert tracer.exclude_class_info == {
            'module1': {
                'ClassA': {'methods': ['method_a1', 'method_a2'], 'attributes': ['attr_a1', 'attr_a2']},
                'ClassB': {'methods': ['method_b1'], 'attributes': ['attr_b1']},
            },
            'module2': {'ClassC': {'methods': ['method_c1'], 'attributes': ['attr_c1', 'attr_c2']}},
        }

        # Verify index map
        assert tracer.exclude_index_map == {
            'class': {'module1': {'ClassA', 'ClassB'}, 'module2': {'ClassC'}},
            'method': {
                'module1': {'ClassA': {'method_a1', 'method_a2'}, 'ClassB': {'method_b1'}},
                'module2': {'ClassC': {'method_c1'}},
            },
            'attribute': {
                'module1': {'ClassA': {'attr_a1', 'attr_a2'}, 'ClassB': {'attr_b1'}},
                'module2': {'ClassC': {'attr_c1', 'attr_c2'}},
            },
            'function': {'module1': {'func1', 'func2'}, 'module2': {'func3'}},
            'global': {'module1': {'global1', 'global2'}, 'module2': {'global3'}},
        }
