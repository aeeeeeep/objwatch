# MIT License
# Copyright (c) 2025 aeeeeeep

GLOBAL_VAR = 42


class SampleClass:
    class_attr = 'value'

    def __init__(self):
        self.instance_attr = 0

    @classmethod
    def class_method(self):
        return 'method_result'

    @staticmethod
    def static_method():
        return 'static_result'

    def method(self):
        return 'result'


def module_function():
    return 'function_result'
