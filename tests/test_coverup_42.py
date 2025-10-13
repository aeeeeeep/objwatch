# file: objwatch/targets.py:392-415
# asked: {"lines": [392, 401, 402, 403, 404, 408, 409, 412, 413, 414, 415], "branches": [[408, 409], [408, 412], [412, 0], [412, 413], [413, 412], [413, 414]]}
# gained: {"lines": [392, 401, 402, 403, 404, 408, 409, 412, 413, 414, 415], "branches": [[408, 409], [408, 412], [412, 0], [412, 413], [413, 412], [413, 414]]}

import pytest


class TestTargetsFlattenModuleStructure:
    """Test cases for Targets._flatten_module_structure method."""

    def test_empty_module_structure(self):
        """Test with empty module structure - should not add anything to result."""
        from objwatch.targets import Targets

        targets = Targets(targets={}, exclude_targets=None)
        result = {}
        module_structure = {}

        targets._flatten_module_structure("test.module", module_structure, result)

        assert result == {}

    def test_module_with_only_classes(self):
        """Test module structure containing only classes."""
        from objwatch.targets import Targets

        targets = Targets(targets={}, exclude_targets=None)
        result = {}
        module_structure = {'classes': {'TestClass': {}}, 'functions': [], 'globals': []}

        targets._flatten_module_structure("test.module", module_structure, result)

        assert "test.module" in result
        assert result["test.module"]["classes"] == {'TestClass': {}}
        assert result["test.module"]["functions"] == []
        assert result["test.module"]["globals"] == []

    def test_module_with_only_functions(self):
        """Test module structure containing only functions."""
        from objwatch.targets import Targets

        targets = Targets(targets={}, exclude_targets=None)
        result = {}
        module_structure = {'classes': {}, 'functions': ['func1', 'func2'], 'globals': []}

        targets._flatten_module_structure("test.module", module_structure, result)

        assert "test.module" in result
        assert result["test.module"]["classes"] == {}
        assert result["test.module"]["functions"] == ['func1', 'func2']
        assert result["test.module"]["globals"] == []

    def test_module_with_only_globals(self):
        """Test module structure containing only globals."""
        from objwatch.targets import Targets

        targets = Targets(targets={}, exclude_targets=None)
        result = {}
        module_structure = {'classes': {}, 'functions': [], 'globals': ['CONSTANT', 'VARIABLE']}

        targets._flatten_module_structure("test.module", module_structure, result)

        assert "test.module" in result
        assert result["test.module"]["classes"] == {}
        assert result["test.module"]["functions"] == []
        assert result["test.module"]["globals"] == ['CONSTANT', 'VARIABLE']

    def test_module_with_nested_submodules(self):
        """Test module structure with nested submodules."""
        from objwatch.targets import Targets

        targets = Targets(targets={}, exclude_targets=None)
        result = {}
        module_structure = {
            'classes': {'MainClass': {}},
            'functions': ['main_func'],
            'submodule1': {
                'classes': {'SubClass1': {}},
                'functions': ['sub_func1'],
                'subsubmodule': {'classes': {'DeepClass': {}}, 'functions': ['deep_func']},
            },
            'submodule2': {'classes': {'SubClass2': {}}, 'functions': ['sub_func2']},
        }

        targets._flatten_module_structure("test", module_structure, result)

        # Check main module
        assert "test" in result
        assert result["test"]["classes"] == {'MainClass': {}}
        assert result["test"]["functions"] == ['main_func']

        # Check submodule1
        assert "test.submodule1" in result
        assert result["test.submodule1"]["classes"] == {'SubClass1': {}}
        assert result["test.submodule1"]["functions"] == ['sub_func1']

        # Check subsubmodule
        assert "test.submodule1.subsubmodule" in result
        assert result["test.submodule1.subsubmodule"]["classes"] == {'DeepClass': {}}
        assert result["test.submodule1.subsubmodule"]["functions"] == ['deep_func']

        # Check submodule2
        assert "test.submodule2" in result
        assert result["test.submodule2"]["classes"] == {'SubClass2': {}}
        assert result["test.submodule2"]["functions"] == ['sub_func2']

    def test_module_with_mixed_content_and_extra_keys(self):
        """Test module structure with mixed content and extra non-dict keys."""
        from objwatch.targets import Targets

        targets = Targets(targets={}, exclude_targets=None)
        result = {}
        module_structure = {
            'classes': {'TestClass': {}},
            'functions': ['test_func'],
            'globals': ['TEST_VAR'],
            'extra_string': 'should_be_ignored',
            'extra_number': 42,
            'nested_module': {'classes': {'NestedClass': {}}, 'functions': ['nested_func']},
        }

        targets._flatten_module_structure("test", module_structure, result)

        # Check main module
        assert "test" in result
        assert result["test"]["classes"] == {'TestClass': {}}
        assert result["test"]["functions"] == ['test_func']
        assert result["test"]["globals"] == ['TEST_VAR']

        # Check nested module
        assert "test.nested_module" in result
        assert result["test.nested_module"]["classes"] == {'NestedClass': {}}
        assert result["test.nested_module"]["functions"] == ['nested_func']

        # Verify extra non-dict keys were ignored
        assert 'test.extra_string' not in result
        assert 'test.extra_number' not in result

    def test_module_with_no_standard_sections(self):
        """Test module structure with no standard sections but has nested modules."""
        from objwatch.targets import Targets

        targets = Targets(targets={}, exclude_targets=None)
        result = {}
        module_structure = {'nested': {'classes': {'NestedClass': {}}, 'functions': ['nested_func']}}

        targets._flatten_module_structure("test", module_structure, result)

        # Main module should not be added (no standard sections)
        assert "test" not in result

        # But nested module should be added
        assert "test.nested" in result
        assert result["test.nested"]["classes"] == {'NestedClass': {}}
        assert result["test.nested"]["functions"] == ['nested_func']
