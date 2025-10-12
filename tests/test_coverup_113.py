# file: objwatch/targets.py:464-487
# asked: {"lines": [464, 487], "branches": []}
# gained: {"lines": [464, 487], "branches": []}

import pytest
from objwatch.targets import Targets


class TestTargetsGetExcludeTargets:
    """Test cases for Targets.get_exclude_targets method."""

    def test_get_exclude_targets_empty(self, monkeypatch):
        """Test get_exclude_targets with empty exclude targets."""

        # Mock the _parse_target method to avoid actual module imports
        def mock_parse_target(self, target):
            if target == "builtins":
                return "builtins", {"classes": {}, "functions": [], "globals": []}
            return target, {"classes": {}, "functions": [], "globals": []}

        monkeypatch.setattr(Targets, "_parse_target", mock_parse_target)
        targets = Targets(targets=["builtins"])
        result = targets.get_exclude_targets()
        assert isinstance(result, dict)
        assert result == {}

    def test_get_exclude_targets_with_exclusions(self, monkeypatch):
        """Test get_exclude_targets with populated exclude targets."""
        exclude_targets = {
            "test.module": {
                "classes": {"TestClass": {"methods": ["method1", "method2"], "attributes": ["attr1", "attr2"]}},
                "functions": ["func1", "func2"],
                "globals": ["GLOBAL_VAR1", "GLOBAL_VAR2"],
            }
        }

        def mock_parse_target(self, target):
            if target == "builtins":
                return "builtins", {"classes": {}, "functions": [], "globals": []}
            return target, {"classes": {}, "functions": [], "globals": []}

        def mock_process_targets(self, targets):
            # Return the exclude_targets directly without processing
            if targets == exclude_targets:
                return exclude_targets
            return {}

        monkeypatch.setattr(Targets, "_parse_target", mock_parse_target)
        monkeypatch.setattr(Targets, "_process_targets", mock_process_targets)
        targets = Targets(targets=["builtins"], exclude_targets=exclude_targets)
        result = targets.get_exclude_targets()
        assert isinstance(result, dict)
        assert result == exclude_targets
        assert "test.module" in result
        assert "classes" in result["test.module"]
        assert "TestClass" in result["test.module"]["classes"]
        assert "methods" in result["test.module"]["classes"]["TestClass"]
        assert "attributes" in result["test.module"]["classes"]["TestClass"]
        assert "functions" in result["test.module"]
        assert "globals" in result["test.module"]

    def test_get_exclude_targets_multiple_modules(self, monkeypatch):
        """Test get_exclude_targets with multiple modules in exclude targets."""
        exclude_targets = {
            "module1": {"functions": ["func1"], "globals": ["global1"]},
            "module2": {"classes": {"ClassA": {"methods": ["method_a"], "attributes": ["attr_a"]}}},
        }

        def mock_parse_target(self, target):
            if target == "builtins":
                return "builtins", {"classes": {}, "functions": [], "globals": []}
            return target, {"classes": {}, "functions": [], "globals": []}

        def mock_process_targets(self, targets):
            # Return the exclude_targets directly without processing
            if targets == exclude_targets:
                return exclude_targets
            return {}

        monkeypatch.setattr(Targets, "_parse_target", mock_parse_target)
        monkeypatch.setattr(Targets, "_process_targets", mock_process_targets)
        targets = Targets(targets=["builtins"], exclude_targets=exclude_targets)
        result = targets.get_exclude_targets()
        assert isinstance(result, dict)
        assert result == exclude_targets
        assert "module1" in result
        assert "module2" in result
        assert result["module1"]["functions"] == ["func1"]
        assert result["module1"]["globals"] == ["global1"]
        assert "ClassA" in result["module2"]["classes"]
        assert result["module2"]["classes"]["ClassA"]["methods"] == ["method_a"]
        assert result["module2"]["classes"]["ClassA"]["attributes"] == ["attr_a"]
