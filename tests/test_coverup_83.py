# file: objwatch/tracer.py:106-169
# asked: {"lines": [106, 122, 123, 124, 125, 126, 127, 128, 131, 133, 134, 136, 139, 142, 143, 144, 145, 146, 149, 150, 151, 152, 153, 156, 157, 160, 161, 163, 164, 165, 166, 167, 168], "branches": [[131, 133], [131, 163], [134, 136], [134, 156], [142, 143], [142, 149], [144, 145], [144, 149], [149, 134], [149, 150], [151, 134], [151, 152], [156, 157], [156, 160], [160, 131], [160, 161]]}
# gained: {"lines": [106, 122, 123, 124, 125, 126, 127, 128, 131, 133, 134, 136, 139, 142, 143, 144, 145, 146, 149, 150, 151, 152, 153, 156, 157, 160, 161, 163, 164, 165, 166, 167, 168], "branches": [[131, 133], [131, 163], [134, 136], [134, 156], [142, 143], [142, 149], [144, 145], [144, 149], [149, 134], [149, 150], [151, 134], [151, 152], [156, 157], [156, 160], [160, 131], [160, 161]]}

import pytest
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerBuildTargetIndex:
    """Test cases for Tracer._build_target_index method"""

    def test_build_target_index_empty_targets(self):
        """Test _build_target_index with empty targets - should handle gracefully"""
        # Create a minimal valid config with empty targets dict
        # The tracer should handle this gracefully by creating empty indexes
        config = ObjWatchConfig(targets=['dummy_module'])
        tracer = Tracer(config)

        # Manually set empty targets to test the _build_target_index behavior
        tracer.targets = {}
        tracer._build_target_index()

        # Verify all indexes are empty
        assert tracer.module_index == set()
        assert tracer.class_index == {}
        assert tracer.method_index == {}
        assert tracer.attribute_index == {}
        assert tracer.function_index == {}
        assert tracer.global_index == {}
        assert tracer.class_info == {}
        assert tracer.index_map == {'class': {}, 'method': {}, 'attribute': {}, 'function': {}, 'global': {}}

    def test_build_target_index_with_classes_methods_attributes(self):
        """Test _build_target_index with classes, methods, and attributes"""
        targets = ['test_module']
        config = ObjWatchConfig(targets=targets)
        tracer = Tracer(config)

        # Manually set targets to test specific structure
        tracer.targets = {
            'test_module': {
                'classes': {
                    'TestClass': {
                        'track_all': False,
                        'methods': ['method1', 'method2'],
                        'attributes': ['attr1', 'attr2'],
                    }
                }
            }
        }
        tracer._build_target_index()

        # Verify module index
        assert tracer.module_index == {'test_module'}

        # Verify class index
        assert tracer.class_index == {'test_module': {'TestClass'}}

        # Verify method index
        assert tracer.method_index == {'test_module': {'TestClass': {'method1', 'method2'}}}

        # Verify attribute index
        assert tracer.attribute_index == {'test_module': {'TestClass': {'attr1', 'attr2'}}}

        # Verify class info
        assert tracer.class_info == {
            'test_module': {
                'TestClass': {'track_all': False, 'methods': ['method1', 'method2'], 'attributes': ['attr1', 'attr2']}
            }
        }

        # Verify index map
        assert tracer.index_map == {
            'class': {'test_module': {'TestClass'}},
            'method': {'test_module': {'TestClass': {'method1', 'method2'}}},
            'attribute': {'test_module': {'TestClass': {'attr1', 'attr2'}}},
            'function': {},
            'global': {},
        }

    def test_build_target_index_with_track_all_classes(self):
        """Test _build_target_index with classes that have track_all=True"""
        targets = ['test_module']
        config = ObjWatchConfig(targets=targets)
        tracer = Tracer(config)

        # Manually set targets to test track_all behavior
        tracer.targets = {
            'test_module': {
                'classes': {
                    'TestClass': {
                        'track_all': True,
                        'methods': ['method1', 'method2'],
                        'attributes': ['attr1', 'attr2'],
                    }
                }
            }
        }
        tracer._build_target_index()

        # Verify module index
        assert tracer.module_index == {'test_module'}

        # Verify class index
        assert tracer.class_index == {'test_module': {'TestClass'}}

        # Verify method index is empty (because track_all=True)
        assert tracer.method_index == {}

        # Verify attribute index is empty (because track_all=True)
        assert tracer.attribute_index == {}

        # Verify class info
        assert tracer.class_info == {
            'test_module': {
                'TestClass': {'track_all': True, 'methods': ['method1', 'method2'], 'attributes': ['attr1', 'attr2']}
            }
        }

        # Verify index map
        assert tracer.index_map == {
            'class': {'test_module': {'TestClass'}},
            'method': {},
            'attribute': {},
            'function': {},
            'global': {},
        }

    def test_build_target_index_with_functions(self):
        """Test _build_target_index with functions"""
        targets = ['test_module']
        config = ObjWatchConfig(targets=targets)
        tracer = Tracer(config)

        # Manually set targets to test functions
        tracer.targets = {'test_module': {'functions': ['func1', 'func2', 'func3']}}
        tracer._build_target_index()

        # Verify module index
        assert tracer.module_index == {'test_module'}

        # Verify function index
        assert tracer.function_index == {'test_module': {'func1', 'func2', 'func3'}}

        # Verify index map
        assert tracer.index_map == {
            'class': {},
            'method': {},
            'attribute': {},
            'function': {'test_module': {'func1', 'func2', 'func3'}},
            'global': {},
        }

    def test_build_target_index_with_globals(self):
        """Test _build_target_index with global variables"""
        targets = ['test_module']
        config = ObjWatchConfig(targets=targets)
        tracer = Tracer(config)

        # Manually set targets to test globals
        tracer.targets = {'test_module': {'globals': ['global_var1', 'global_var2']}}
        tracer._build_target_index()

        # Verify module index
        assert tracer.module_index == {'test_module'}

        # Verify global index
        assert tracer.global_index == {'test_module': {'global_var1', 'global_var2'}}

        # Verify index map
        assert tracer.index_map == {
            'class': {},
            'method': {},
            'attribute': {},
            'function': {},
            'global': {'test_module': {'global_var1', 'global_var2'}},
        }

    def test_build_target_index_complete_scenario(self):
        """Test _build_target_index with complete scenario including all components"""
        targets = ['module1', 'module2']
        config = ObjWatchConfig(targets=targets)
        tracer = Tracer(config)

        # Manually set targets for complete scenario
        tracer.targets = {
            'module1': {
                'classes': {
                    'ClassA': {'track_all': False, 'methods': ['method_a1', 'method_a2'], 'attributes': ['attr_a1']},
                    'ClassB': {'track_all': True, 'methods': ['method_b1'], 'attributes': ['attr_b1', 'attr_b2']},
                },
                'functions': ['func1', 'func2'],
                'globals': ['global1'],
            },
            'module2': {
                'classes': {'ClassC': {'track_all': False, 'methods': ['method_c1'], 'attributes': []}},
                'functions': ['func3'],
                'globals': ['global2', 'global3'],
            },
        }
        tracer._build_target_index()

        # Verify module index
        assert tracer.module_index == {'module1', 'module2'}

        # Verify class index
        assert tracer.class_index == {'module1': {'ClassA', 'ClassB'}, 'module2': {'ClassC'}}

        # Verify method index (only for classes with track_all=False)
        assert tracer.method_index == {
            'module1': {'ClassA': {'method_a1', 'method_a2'}},
            'module2': {'ClassC': {'method_c1'}},
        }

        # Verify attribute index (only for classes with track_all=False)
        # Note: ClassC has empty attributes list, so it should not appear in attribute_index
        assert tracer.attribute_index == {'module1': {'ClassA': {'attr_a1'}}}

        # Verify function index
        assert tracer.function_index == {'module1': {'func1', 'func2'}, 'module2': {'func3'}}

        # Verify global index
        assert tracer.global_index == {'module1': {'global1'}, 'module2': {'global2', 'global3'}}

        # Verify class info
        assert tracer.class_info == {
            'module1': {
                'ClassA': {'track_all': False, 'methods': ['method_a1', 'method_a2'], 'attributes': ['attr_a1']},
                'ClassB': {'track_all': True, 'methods': ['method_b1'], 'attributes': ['attr_b1', 'attr_b2']},
            },
            'module2': {'ClassC': {'track_all': False, 'methods': ['method_c1'], 'attributes': []}},
        }

        # Verify index map
        assert tracer.index_map == {
            'class': {'module1': {'ClassA', 'ClassB'}, 'module2': {'ClassC'}},
            'method': {'module1': {'ClassA': {'method_a1', 'method_a2'}}, 'module2': {'ClassC': {'method_c1'}}},
            'attribute': {'module1': {'ClassA': {'attr_a1'}}},
            'function': {'module1': {'func1', 'func2'}, 'module2': {'func3'}},
            'global': {'module1': {'global1'}, 'module2': {'global2', 'global3'}},
        }

    def test_build_target_index_with_empty_methods_attributes(self):
        """Test _build_target_index with classes that have empty methods and attributes lists"""
        targets = ['test_module']
        config = ObjWatchConfig(targets=targets)
        tracer = Tracer(config)

        # Manually set targets to test empty lists
        tracer.targets = {
            'test_module': {'classes': {'TestClass': {'track_all': False, 'methods': [], 'attributes': []}}}
        }
        tracer._build_target_index()

        # Verify module index
        assert tracer.module_index == {'test_module'}

        # Verify class index
        assert tracer.class_index == {'test_module': {'TestClass'}}

        # Verify method index is empty (because methods list is empty)
        assert tracer.method_index == {}

        # Verify attribute index is empty (because attributes list is empty)
        assert tracer.attribute_index == {}

        # Verify class info
        assert tracer.class_info == {
            'test_module': {'TestClass': {'track_all': False, 'methods': [], 'attributes': []}}
        }

        # Verify index map
        assert tracer.index_map == {
            'class': {'test_module': {'TestClass'}},
            'method': {},
            'attribute': {},
            'function': {},
            'global': {},
        }
