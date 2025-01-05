# MIT License
# Copyright (c) 2025 aeeeeeep

"""
ObjWatch Package

A Python library to trace and monitor object attributes and method calls.

Exports:
    ObjWatch: The main class for setting up and managing tracing.
    watch: A convenience function to start tracing with default settings.
"""

from .core import ObjWatch, watch

__all__ = ['ObjWatch', 'watch']
