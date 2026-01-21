# MIT License
# Copyright (c) 2025 aeeeeeep

import sys

from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


def test_exclude_functionality():
    """Test that exclude targets work correctly with track_all."""
    print("Testing exclude functionality with track_all...")

    # Create config with track_all=True and exclude specific methods/attributes
    config = ObjWatchConfig(
        targets=["tests.utils.example_module:TestClass"],  # Track all of TestClass
        exclude_targets=[
            "tests.utils.example_module:TestClass.excluded_method()",  # Exclude this method
            "tests.utils.example_module:TestClass.excluded_attr",  # Exclude this attribute
        ],
        with_locals=False,
        with_globals=False,
    )

    # Create tracer
    tracer = Tracer(config)

    # Test method tracing
    should_track_tracked = tracer._should_trace_method("tests.utils.example_module", "TestClass", "tracked_method")
    should_track_excluded = tracer._should_trace_method("tests.utils.example_module", "TestClass", "excluded_method")

    # Test attribute tracing
    should_track_attr_tracked = tracer._should_trace_attribute(
        "tests.utils.example_module", "TestClass", "tracked_attr"
    )
    should_track_attr_excluded = tracer._should_trace_attribute(
        "tests.utils.example_module", "TestClass", "excluded_attr"
    )

    print(f"Should track tracked_method: {should_track_tracked}")
    print(f"Should track excluded_method: {should_track_excluded}")
    print(f"Should track tracked_attr: {should_track_attr_tracked}")
    print(f"Should track excluded_attr: {should_track_attr_excluded}")

    # Verify results
    assert should_track_tracked, "tracked_method should be tracked"
    assert not should_track_excluded, "excluded_method should be excluded"
    assert should_track_attr_tracked, "tracked_attr should be tracked"
    assert not should_track_attr_excluded, "excluded_attr should be excluded"

    print("All exclude functionality tests passed!")
    # All assertions passed, no return value needed for pytest


if __name__ == "__main__":
    try:
        test_exclude_functionality()
        print("Exclude functionality test completed successfully!")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
