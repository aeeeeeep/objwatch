#!/usr/bin/env python3
"""
Comprehensive test for exclude functionality in track_all mode.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig

# Import test module from the same directory
from .utils.example_module import TestClass


def test_comprehensive_exclude():
    """Test comprehensive exclude functionality with track_all mode."""
    print("Testing comprehensive exclude functionality...")

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
    assert tracer._should_trace_method(
        'tests.utils.example_module', 'TestClass', 'tracked_method'
    ), "tracked_method should be tracked"
    assert not tracer._should_trace_method(
        'tests.utils.example_module', 'TestClass', 'excluded_method'
    ), "excluded_method should be excluded"

    # Test attribute tracking
    assert tracer._should_trace_attribute(
        'tests.utils.example_module', 'TestClass', 'tracked_attr'
    ), "tracked_attr should be tracked"
    assert not tracer._should_trace_attribute(
        'tests.utils.example_module', 'TestClass', 'excluded_attr'
    ), "excluded_attr should be excluded"

    # Test 2: Multiple exclusions
    config2 = ObjWatchConfig(
        targets=["tests.utils.example_module:TestClass"],
        exclude_targets=[
            "tests.utils.example_module:TestClass.excluded_method()",
            "tests.utils.example_module:TestClass.excluded_attr",
            "tests.utils.example_module:TestClass.tracked_method()",  # Exclude a method that would normally be tracked
        ],
        with_locals=False,
    )

    tracer2 = Tracer(config2)

    assert not tracer2._should_trace_method(
        'tests.utils.example_module', 'TestClass', 'tracked_method'
    ), "tracked_method should be excluded when explicitly excluded"
    assert not tracer2._should_trace_method(
        'tests.utils.example_module', 'TestClass', 'excluded_method'
    ), "excluded_method should be excluded"
    assert tracer2._should_trace_attribute(
        'tests.utils.example_module', 'TestClass', 'tracked_attr'
    ), "tracked_attr should still be tracked"

    # Test 3: No exclusions (everything should be tracked)
    config3 = ObjWatchConfig(targets=["tests.utils.example_module:TestClass"], exclude_targets=[], with_locals=False)

    tracer3 = Tracer(config3)

    assert tracer3._should_trace_method(
        'tests.utils.example_module', 'TestClass', 'tracked_method'
    ), "tracked_method should be tracked with no exclusions"
    assert tracer3._should_trace_method(
        'tests.utils.example_module', 'TestClass', 'excluded_method'
    ), "excluded_method should be tracked with no exclusions"
    assert tracer3._should_trace_attribute(
        'tests.utils.example_module', 'TestClass', 'tracked_attr'
    ), "tracked_attr should be tracked"
    assert tracer3._should_trace_attribute(
        'tests.utils.example_module', 'TestClass', 'excluded_attr'
    ), "excluded_attr should be tracked with no exclusions"


if __name__ == "__main__":
    test_comprehensive_exclude()
