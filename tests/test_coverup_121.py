# file: objwatch/targets.py:116-136
# asked: {"lines": [116, 126, 127, 128, 129, 130, 131, 132, 133, 135, 136], "branches": [[127, 128], [127, 136], [128, 129], [128, 130], [130, 131], [130, 135]]}
# gained: {"lines": [116, 126, 127, 128, 129, 130, 131, 132, 133, 135, 136], "branches": [[127, 128], [127, 136], [128, 129], [128, 130], [130, 131], [130, 135]]}

import pytest
from types import ModuleType, MethodType, FunctionType
from unittest.mock import Mock, patch
import sys
import tempfile
import os


class TestTargetsProcessTargets:

    def test_process_targets_with_none_targets(self):
        """Test _process_targets with None targets parameter."""
        from objwatch.targets import Targets

        targets_obj = Targets(targets=[])
        result = targets_obj._process_targets(None)

        assert result == {}

    def test_process_targets_with_empty_list(self):
        """Test _process_targets with empty targets list."""
        from objwatch.targets import Targets

        targets_obj = Targets(targets=[])
        result = targets_obj._process_targets([])

        assert result == {}

    def test_process_targets_with_python_file_string(self):
        """Test _process_targets with .py file string target."""
        from objwatch.targets import Targets

        targets_obj = Targets(targets=[])
        result = targets_obj._process_targets(["test_module.py"])

        assert result == {}
        assert "test_module.py" in targets_obj.filename_targets

    def test_process_targets_with_module_type(self, monkeypatch):
        """Test _process_targets with ModuleType target."""
        from objwatch.targets import Targets

        # Create a mock module
        mock_module = Mock(spec=ModuleType)
        mock_module.__name__ = "test_module"

        # Mock the _parse_target method to return expected structure
        targets_obj = Targets(targets=[])

        with patch.object(targets_obj, '_parse_target') as mock_parse:
            mock_parse.return_value = ("test_module", {"classes": {}, "functions": [], "globals": []})
            result = targets_obj._process_targets([mock_module])

            mock_parse.assert_called_once_with(mock_module)
            assert result == {"test_module": {"classes": {}, "functions": [], "globals": []}}

    def test_process_targets_with_class_type(self, monkeypatch):
        """Test _process_targets with ClassType target."""
        from objwatch.targets import Targets

        # Create a mock class
        class MockClass:
            pass

        targets_obj = Targets(targets=[])

        with patch.object(targets_obj, '_parse_target') as mock_parse:
            mock_parse.return_value = (
                "test_module",
                {
                    "classes": {"MockClass": {"methods": [], "attributes": [], "track_all": True}},
                    "functions": [],
                    "globals": [],
                },
            )
            result = targets_obj._process_targets([MockClass])

            mock_parse.assert_called_once_with(MockClass)
            assert result == {
                "test_module": {
                    "classes": {"MockClass": {"methods": [], "attributes": [], "track_all": True}},
                    "functions": [],
                    "globals": [],
                }
            }

    def test_process_targets_with_function_type(self, monkeypatch):
        """Test _process_targets with FunctionType target."""
        from objwatch.targets import Targets

        def test_function():
            pass

        targets_obj = Targets(targets=[])

        with patch.object(targets_obj, '_parse_target') as mock_parse:
            mock_parse.return_value = ("test_module", {"classes": {}, "functions": ["test_function"], "globals": []})
            result = targets_obj._process_targets([test_function])

            mock_parse.assert_called_once_with(test_function)
            assert result == {"test_module": {"classes": {}, "functions": ["test_function"], "globals": []}}

    def test_process_targets_with_method_type(self, monkeypatch):
        """Test _process_targets with MethodType target."""
        from objwatch.targets import Targets

        class TestClass:
            def test_method(self):
                pass

        test_method = TestClass().test_method

        targets_obj = Targets(targets=[])

        with patch.object(targets_obj, '_parse_target') as mock_parse:
            mock_parse.return_value = (
                "test_module",
                {
                    "classes": {"TestClass": {"methods": ["test_method"], "attributes": [], "track_all": False}},
                    "functions": [],
                    "globals": [],
                },
            )
            result = targets_obj._process_targets([test_method])

            mock_parse.assert_called_once_with(test_method)
            assert result == {
                "test_module": {
                    "classes": {"TestClass": {"methods": ["test_method"], "attributes": [], "track_all": False}},
                    "functions": [],
                    "globals": [],
                }
            }

    def test_process_targets_with_string_target(self, monkeypatch):
        """Test _process_targets with string target."""
        from objwatch.targets import Targets

        targets_obj = Targets(targets=[])

        with patch.object(targets_obj, '_parse_target') as mock_parse:
            mock_parse.return_value = ("test_module", {"classes": {}, "functions": [], "globals": []})
            result = targets_obj._process_targets(["test_module"])

            mock_parse.assert_called_once_with("test_module")
            assert result == {"test_module": {"classes": {}, "functions": [], "globals": []}}

    def test_process_targets_with_unsupported_type(self, monkeypatch):
        """Test _process_targets with unsupported target type."""
        from objwatch.targets import Targets

        targets_obj = Targets(targets=[])

        # Use monkeypatch to capture the log_warn call
        log_warn_calls = []

        def mock_log_warn(msg):
            log_warn_calls.append(msg)

        # Patch the log_warn function in the module where it's imported
        monkeypatch.setattr('objwatch.targets.log_warn', mock_log_warn)

        result = targets_obj._process_targets([123])  # int is unsupported

        assert len(log_warn_calls) == 1
        assert "Unsupported target type: <class 'int'>" in log_warn_calls[0]
        assert result == {}

    def test_process_targets_deep_merge_functionality(self, monkeypatch):
        """Test _process_targets deep merge functionality for same module."""
        from objwatch.targets import Targets

        targets_obj = Targets(targets=[])

        with patch.object(targets_obj, '_parse_target') as mock_parse:
            # Set up different return values for different calls
            call_results = [
                (
                    "test_module",
                    {
                        "classes": {"Class1": {"methods": ["method1"], "attributes": [], "track_all": False}},
                        "functions": [],
                        "globals": [],
                    },
                ),
                (
                    "test_module",
                    {
                        "classes": {"Class2": {"methods": ["method2"], "attributes": [], "track_all": False}},
                        "functions": [],
                        "globals": [],
                    },
                ),
            ]
            mock_parse.side_effect = call_results

            # Process both targets in a single call to test deep merge
            result = targets_obj._process_targets(["test_module:Class1.method1", "test_module:Class2.method2"])

            # Verify both classes are present in the same module
            assert "test_module" in result
            assert "Class1" in result["test_module"]["classes"]
            assert "Class2" in result["test_module"]["classes"]
            assert result["test_module"]["classes"]["Class1"]["methods"] == ["method1"]
            assert result["test_module"]["classes"]["Class2"]["methods"] == ["method2"]

    def test_process_targets_multiple_targets_mixed_types(self, monkeypatch):
        """Test _process_targets with multiple targets of mixed types."""
        from objwatch.targets import Targets

        def test_function():
            pass

        class TestClass:
            def test_method(self):
                pass

        test_method = TestClass().test_method

        targets_obj = Targets(targets=[])

        with patch.object(targets_obj, '_parse_target') as mock_parse:
            # Set up different return values for different target types
            def parse_target_side_effect(target):
                if target == "test_module":
                    return ("test_module", {"classes": {}, "functions": [], "globals": []})
                elif target == test_function:
                    return ("test_module", {"classes": {}, "functions": ["test_function"], "globals": []})
                elif target == TestClass:
                    return (
                        "test_module",
                        {
                            "classes": {"TestClass": {"methods": [], "attributes": [], "track_all": True}},
                            "functions": [],
                            "globals": [],
                        },
                    )
                elif target == test_method:
                    return (
                        "test_module",
                        {
                            "classes": {
                                "TestClass": {"methods": ["test_method"], "attributes": [], "track_all": False}
                            },
                            "functions": [],
                            "globals": [],
                        },
                    )
                return ("unknown", {})

            mock_parse.side_effect = parse_target_side_effect

            result = targets_obj._process_targets(["test_module", test_function, TestClass, test_method])

            assert mock_parse.call_count == 4
            assert "test_module" in result
            # Verify all components are merged into the same module
            module_result = result["test_module"]
            assert "test_function" in module_result["functions"]
            assert "TestClass" in module_result["classes"]
            assert "test_method" in module_result["classes"]["TestClass"]["methods"]
