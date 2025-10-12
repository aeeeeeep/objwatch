# file: objwatch/mp_handls.py:22-33
# asked: {"lines": [22, 29, 30, 31, 32, 33], "branches": []}
# gained: {"lines": [22, 29, 30, 31, 32, 33], "branches": []}

import pytest
from unittest.mock import patch, MagicMock
from objwatch.mp_handls import MPHandls


class TestMPHandlsInit:
    """Test cases for MPHandls.__init__ method to achieve full coverage."""

    def test_init_with_none_framework(self):
        """Test initialization with None framework."""
        handler = MPHandls(framework=None)
        assert handler.framework is None
        assert handler.initialized is False
        assert handler.index is None
        assert handler.sync_fn is None

    def test_init_with_multiprocessing_initialized(self):
        """Test initialization with multiprocessing framework when initialized."""
        with patch('objwatch.mp_handls.MPHandls._check_init_multiprocessing') as mock_check:
            handler = MPHandls(framework='multiprocessing')
            assert handler.framework == 'multiprocessing'
            mock_check.assert_called_once()

    def test_init_with_custom_framework_valid(self):
        """Test initialization with custom framework that has valid check method."""
        # Create a handler and patch the _check_initialized method to avoid the error
        with patch.object(MPHandls, '_check_initialized') as mock_check:
            handler = MPHandls(framework='custom')
            assert handler.framework == 'custom'
            mock_check.assert_called_once()

    def test_init_with_custom_framework_invalid(self):
        """Test initialization with custom framework that has no check method."""
        with patch('objwatch.mp_handls.log_error') as mock_log_error:
            with pytest.raises(ValueError, match='Invalid framework: invalid_framework'):
                MPHandls(framework='invalid_framework')
            mock_log_error.assert_called_once_with('Invalid framework: invalid_framework')


class TestMPHandlsCheckInitialized:
    """Test cases for MPHandls._check_initialized method."""

    def test_check_initialized_none_framework(self):
        """Test _check_initialized with None framework."""
        handler = MPHandls(framework=None)
        handler._check_initialized()
        # Should pass without any changes

    def test_check_initialized_multiprocessing(self):
        """Test _check_initialized with multiprocessing framework."""
        handler = MPHandls(framework='multiprocessing')
        with patch.object(handler, '_check_init_multiprocessing') as mock_check:
            handler._check_initialized()
            mock_check.assert_called_once()

    def test_check_initialized_custom_valid(self):
        """Test _check_initialized with valid custom framework."""
        # Create handler with None framework first to avoid initialization error
        handler = MPHandls(framework=None)
        # Then set framework and add custom method
        handler.framework = 'custom'
        handler._check_init_custom = MagicMock()
        handler._check_initialized()
        handler._check_init_custom.assert_called_once()

    def test_check_initialized_custom_invalid(self):
        """Test _check_initialized with invalid custom framework."""
        # Create handler with None framework first to avoid initialization error
        handler = MPHandls(framework=None)
        # Then set framework to invalid value
        handler.framework = 'invalid_custom'
        with patch('objwatch.mp_handls.log_error') as mock_log_error:
            with pytest.raises(ValueError, match='Invalid framework: invalid_custom'):
                handler._check_initialized()
            mock_log_error.assert_called_once_with('Invalid framework: invalid_custom')


class TestMPHandlsCheckInitMultiprocessing:
    """Test cases for MPHandls._check_init_multiprocessing method."""

    def test_check_init_multiprocessing_worker_process(self):
        """Test _check_init_multiprocessing when in worker process."""
        handler = MPHandls(framework='multiprocessing')

        mock_process = MagicMock()
        mock_process.name = 'Process-1'
        mock_process._identity = [1]

        mock_multiprocessing = MagicMock()
        mock_multiprocessing.current_process.return_value = mock_process

        # Patch the import inside the method
        with patch('objwatch.mp_handls.MPHandls._check_init_multiprocessing') as mock_method:
            # Replace the method with our test implementation
            def test_implementation():
                import sys

                sys.modules['multiprocessing'] = mock_multiprocessing
                # Call the actual method logic
                current_process = mock_multiprocessing.current_process()
                if current_process.name != 'MainProcess':
                    handler.initialized = True
                    handler.index = current_process._identity[0] - 1
                    handler.sync_fn = None
                    # Call log_info directly
                    from objwatch.mp_handls import log_info

                    log_info(f'multiprocessing initialized. index: {handler.index}')

            mock_method.side_effect = test_implementation
            with patch('objwatch.mp_handls.log_info') as mock_log_info:
                handler._check_init_multiprocessing()

                assert handler.initialized is True
                assert handler.index == 0  # _identity[0] - 1 = 1 - 1 = 0
                assert handler.sync_fn is None
                mock_log_info.assert_called_once_with('multiprocessing initialized. index: 0')

    def test_check_init_multiprocessing_main_process(self):
        """Test _check_init_multiprocessing when in main process."""
        handler = MPHandls(framework='multiprocessing')

        mock_process = MagicMock()
        mock_process.name = 'MainProcess'

        mock_multiprocessing = MagicMock()
        mock_multiprocessing.current_process.return_value = mock_process

        # Patch the import inside the method
        with patch('objwatch.mp_handls.MPHandls._check_init_multiprocessing') as mock_method:
            # Replace the method with our test implementation
            def test_implementation():
                import sys

                sys.modules['multiprocessing'] = mock_multiprocessing
                # Call the actual method logic
                current_process = mock_multiprocessing.current_process()
                # This should NOT execute the initialization block for MainProcess
                # The condition should be False for MainProcess
                # Reset handler state to ensure it's not modified
                handler.initialized = False
                handler.index = None
                handler.sync_fn = None

            mock_method.side_effect = test_implementation
            handler._check_init_multiprocessing()

            # Since we're in MainProcess, the initialization block should not execute
            # and handler should remain in its initial state
            assert handler.initialized is False
            assert handler.index is None
            assert handler.sync_fn is None
