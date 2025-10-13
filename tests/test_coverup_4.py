# file: objwatch/mp_handls.py:35-54
# asked: {"lines": [35, 40, 41, 42, 43, 44, 45, 48, 49, 50, 51, 53, 54], "branches": [[40, 41], [40, 42], [42, 43], [42, 44], [44, 45], [44, 48], [49, 50], [49, 53]]}
# gained: {"lines": [35, 40, 41, 42, 43, 44, 45, 48, 49, 50, 51, 53, 54], "branches": [[40, 41], [40, 42], [42, 43], [42, 44], [44, 45], [44, 48], [49, 50], [49, 53]]}

import pytest
from unittest.mock import Mock, patch, MagicMock
from objwatch.mp_handls import MPHandls
from objwatch.utils.logger import log_error


class TestMPHandlsCheckInitialized:
    """Test cases for MPHandls._check_initialized method"""

    def test_check_initialized_framework_none(self):
        """Test when framework is None - should pass without doing anything"""
        mp_handls = MPHandls()
        mp_handls.framework = None

        # This should not raise any exception and not call any methods
        mp_handls._check_initialized()

        # Verify no initialization occurred
        assert not hasattr(mp_handls, 'initialized') or not mp_handls.initialized

    def test_check_initialized_torch_distributed(self, monkeypatch):
        """Test when framework is 'torch.distributed'"""
        mp_handls = MPHandls()
        mp_handls.framework = 'torch.distributed'

        # Mock the _check_init_torch method
        mock_check_torch = Mock()
        mp_handls._check_init_torch = mock_check_torch

        mp_handls._check_initialized()

        # Verify _check_init_torch was called
        mock_check_torch.assert_called_once()

    def test_check_initialized_multiprocessing(self, monkeypatch):
        """Test when framework is 'multiprocessing'"""
        mp_handls = MPHandls()
        mp_handls.framework = 'multiprocessing'

        # Mock the _check_init_multiprocessing method
        mock_check_mp = Mock()
        mp_handls._check_init_multiprocessing = mock_check_mp

        mp_handls._check_initialized()

        # Verify _check_init_multiprocessing was called
        mock_check_mp.assert_called_once()

    def test_check_initialized_custom_framework_valid(self, monkeypatch):
        """Test when framework is a custom framework with valid method"""
        mp_handls = MPHandls()
        mp_handls.framework = 'custom_framework'

        # Create a mock custom method
        mock_custom_method = Mock()

        # Set the custom method on the instance
        mp_handls._check_init_custom_framework = mock_custom_method

        mp_handls._check_initialized()

        # Verify the custom method was called
        mock_custom_method.assert_called_once()

    def test_check_initialized_custom_framework_invalid(self, monkeypatch):
        """Test when framework is a custom framework without valid method"""
        mp_handls = MPHandls()
        mp_handls.framework = 'invalid_framework'

        # Mock log_error to verify it's called
        with patch('objwatch.mp_handls.log_error') as mock_log_error:
            with pytest.raises(ValueError, match="Invalid framework: invalid_framework"):
                mp_handls._check_initialized()

            # Verify log_error was called with the correct message
            mock_log_error.assert_called_once_with("Invalid framework: invalid_framework")

    def test_check_initialized_custom_framework_hasattr_false(self, monkeypatch):
        """Test when hasattr returns False for custom framework method"""
        mp_handls = MPHandls()
        mp_handls.framework = 'another_invalid'

        # Ensure the custom method doesn't exist
        assert not hasattr(mp_handls, '_check_init_another_invalid')

        # Mock log_error to verify it's called
        with patch('objwatch.mp_handls.log_error') as mock_log_error:
            with pytest.raises(ValueError, match="Invalid framework: another_invalid"):
                mp_handls._check_initialized()

            # Verify log_error was called with the correct message
            mock_log_error.assert_called_once_with("Invalid framework: another_invalid")
