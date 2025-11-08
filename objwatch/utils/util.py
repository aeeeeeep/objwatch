# MIT License
# Copyright (c) 2025 aeeeeeep


def target_handler(o):
    if isinstance(o, set):
        return list(o)
    if hasattr(o, '__dict__'):
        return o.__dict__
    return str(o)
