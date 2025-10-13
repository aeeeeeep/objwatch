# file: objwatch/wrappers/abc_wrapper.py:17-20
# asked: {"lines": [17, 20], "branches": []}
# gained: {"lines": [17, 20], "branches": []}

import pytest
from objwatch.wrappers.abc_wrapper import ABCWrapper


class TestABCBWrapper:
    def test_init_sets_format_sequence_func_to_none(self):
        """Test that ABCWrapper.__init__ sets format_sequence_func to None."""

        # Create a concrete subclass to test the abstract base class
        class ConcreteWrapper(ABCWrapper):
            def wrap_call(self, func_name, frame):
                return ""

            def wrap_return(self, func_name, result):
                return ""

            def wrap_upd(self, old_value, current_value):
                return "", ""

        wrapper = ConcreteWrapper()
        assert wrapper.format_sequence_func is None
