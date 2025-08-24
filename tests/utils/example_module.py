# MIT License
# Copyright (c) 2025 aeeeeeep


def test_func():
    return "result"


def custom_func(arg1):
    return f"custom_result with {arg1}"


class SampleClass:
    def __init__(self, value):
        self.value = value

    def increment(self):
        self.value += 1
        return self.value

    def decrement(self):
        self.value -= 1
        return self.value


class TestClass:
    """Test class for exclude functionality testing."""

    def __init__(self):
        self.tracked_attr = "tracked"
        self.excluded_attr = "excluded"

    def tracked_method(self):
        return "tracked method result"

    def excluded_method(self):
        return "excluded method result"
