# file: objwatch/tracer.py:361-372
# asked: {"lines": [361, 362, 372], "branches": []}
# gained: {"lines": [361, 362, 372], "branches": []}

import pytest
from unittest.mock import Mock, patch
from objwatch.tracer import Tracer
from objwatch.config import ObjWatchConfig


class TestTracerFilenameEndswith:
    """Test cases for Tracer._filename_endswith method."""

    def test_filename_endswith_with_non_matching_extension(self):
        """Test that _filename_endswith returns False when filename doesn't end with target extensions."""
        config = ObjWatchConfig(targets=['test.py'], exclude_targets=None, with_locals=False, with_globals=False)
        tracer = Tracer(config)

        # Clear the cache to ensure fresh test
        tracer._filename_endswith.cache_clear()

        # Test with filename that doesn't end with .py
        result = tracer._filename_endswith('test.txt')
        assert result is False

    def test_filename_endswith_with_multiple_targets(self):
        """Test _filename_endswith with multiple filename targets."""
        config = ObjWatchConfig(
            targets=['test.py', 'module.py', 'script.py'], exclude_targets=None, with_locals=False, with_globals=False
        )
        tracer = Tracer(config)

        # Clear the cache to ensure fresh test
        tracer._filename_endswith.cache_clear()

        # Test with each target extension
        assert tracer._filename_endswith('test.py') is True
        assert tracer._filename_endswith('module.py') is True
        assert tracer._filename_endswith('script.py') is True

        # Test with non-matching extensions
        assert tracer._filename_endswith('test.txt') is False
        assert tracer._filename_endswith('module.js') is False
        assert tracer._filename_endswith('script.java') is False

    def test_filename_endswith_with_single_target(self):
        """Test _filename_endswith with a single target."""
        config = ObjWatchConfig(targets=['single.py'], exclude_targets=None, with_locals=False, with_globals=False)
        tracer = Tracer(config)

        # Clear the cache to ensure fresh test
        tracer._filename_endswith.cache_clear()

        # Test with matching filename
        assert tracer._filename_endswith('single.py') is True

        # Test with non-matching filename
        assert tracer._filename_endswith('other.py') is False
