# MIT License
# Copyright (c) 2025 aeeeeeep

import sys
import unittest

from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestExcludeFunctionality(unittest.TestCase):
    """Test that exclude targets work correctly with track_all."""

    def test_exclude_basic(self):
        """Test basic exclude functionality."""
        # Create config with track_all=True and exclude specific methods/attributes
        config = ObjWatchConfig(
            targets=["tests.utils.example_module:TestClass"],
            exclude_targets=[
                "tests.utils.example_module:TestClass.excluded_method()",
                "tests.utils.example_module:TestClass.excluded_attr",
            ],
            with_locals=False,
            with_globals=False,
        )

        # Create tracer
        tracer = Tracer(config)

        # Test method tracing
        should_track_tracked = tracer._should_trace_method("tests.utils.example_module", "TestClass", "tracked_method")
        should_track_excluded = tracer._should_trace_method(
            "tests.utils.example_module", "TestClass", "excluded_method"
        )

        # Test attribute tracing
        should_track_attr_tracked = tracer._should_trace_attribute(
            "tests.utils.example_module", "TestClass", "tracked_attr"
        )
        should_track_attr_excluded = tracer._should_trace_attribute(
            "tests.utils.example_module", "TestClass", "excluded_attr"
        )

        # Verify results
        self.assertTrue(should_track_tracked, "tracked_method should be tracked")
        self.assertFalse(should_track_excluded, "excluded_method should be excluded")
        self.assertTrue(should_track_attr_tracked, "tracked_attr should be tracked")
        self.assertFalse(should_track_attr_excluded, "excluded_attr should be excluded")

    def test_comprehensive_exclude(self):
        """Test comprehensive exclude functionality with track_all mode."""
        # Test 1: Basic method and attribute exclusion
        config = ObjWatchConfig(
            targets=["tests.utils.example_module:TestClass"],
            exclude_targets=[
                "tests.utils.example_module:TestClass.excluded_method()",
                "tests.utils.example_module:TestClass.excluded_attr",
            ],
            with_locals=False,
        )

        tracer = Tracer(config)

        # Test method tracking
        self.assertTrue(
            tracer._should_trace_method('tests.utils.example_module', 'TestClass', 'tracked_method'),
            "tracked_method should be tracked",
        )
        self.assertFalse(
            tracer._should_trace_method('tests.utils.example_module', 'TestClass', 'excluded_method'),
            "excluded_method should be excluded",
        )

        # Test attribute tracking
        self.assertTrue(
            tracer._should_trace_attribute('tests.utils.example_module', 'TestClass', 'tracked_attr'),
            "tracked_attr should be tracked",
        )
        self.assertFalse(
            tracer._should_trace_attribute('tests.utils.example_module', 'TestClass', 'excluded_attr'),
            "excluded_attr should be excluded",
        )

    def test_multiple_exclusions(self):
        """Test multiple exclusions."""
        config = ObjWatchConfig(
            targets=["tests.utils.example_module:TestClass"],
            exclude_targets=[
                "tests.utils.example_module:TestClass.excluded_method()",
                "tests.utils.example_module:TestClass.excluded_attr",
                "tests.utils.example_module:TestClass.tracked_method()",
            ],
            with_locals=False,
        )

        tracer = Tracer(config)

        self.assertFalse(
            tracer._should_trace_method('tests.utils.example_module', 'TestClass', 'tracked_method'),
            "tracked_method should be excluded when explicitly excluded",
        )
        self.assertFalse(
            tracer._should_trace_method('tests.utils.example_module', 'TestClass', 'excluded_method'),
            "excluded_method should be excluded",
        )
        self.assertTrue(
            tracer._should_trace_attribute('tests.utils.example_module', 'TestClass', 'tracked_attr'),
            "tracked_attr should still be tracked",
        )

    def test_no_exclusions(self):
        """Test with no exclusions (everything should be tracked)."""
        config = ObjWatchConfig(targets=["tests.utils.example_module:TestClass"], exclude_targets=[], with_locals=False)

        tracer = Tracer(config)

        self.assertTrue(
            tracer._should_trace_method('tests.utils.example_module', 'TestClass', 'tracked_method'),
            "tracked_method should be tracked with no exclusions",
        )
        self.assertTrue(
            tracer._should_trace_method('tests.utils.example_module', 'TestClass', 'excluded_method'),
            "excluded_method should be tracked with no exclusions",
        )
        self.assertTrue(
            tracer._should_trace_attribute('tests.utils.example_module', 'TestClass', 'tracked_attr'),
            "tracked_attr should be tracked",
        )
        self.assertTrue(
            tracer._should_trace_attribute('tests.utils.example_module', 'TestClass', 'excluded_attr'),
            "excluded_attr should be tracked with no exclusions",
        )


if __name__ == "__main__":
    unittest.main()
