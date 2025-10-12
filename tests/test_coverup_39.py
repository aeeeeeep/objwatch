# file: objwatch/mp_handls.py:84-95
# asked: {"lines": [84, 89, 91, 92, 93, 94, 95], "branches": [[91, 0], [91, 92]]}
# gained: {"lines": [84, 89, 91, 92, 93, 94, 95], "branches": [[91, 0], [91, 92]]}

import pytest
from unittest.mock import patch, MagicMock


class TestMPHandls:
    """Test cases for MPHandls class _check_init_torch method"""

    def test_check_init_torch_initialized(self):
        """Test _check_init_torch when torch.distributed is initialized"""
        from objwatch.mp_handls import MPHandls

        # Mock torch.distributed.is_initialized to return True
        mock_dist = MagicMock()
        mock_dist.is_initialized.return_value = True
        mock_dist.get_rank.return_value = 0

        # Mock torch.distributed module
        mock_torch = MagicMock()
        mock_torch.distributed = mock_dist

        # Mock log_info to capture the log message
        mock_log_info = MagicMock()

        with patch('objwatch.mp_handls.log_info', mock_log_info):
            with patch.dict('sys.modules', {'torch': mock_torch}):
                # Create MPHandls instance
                handler = MPHandls()

                # Call the method directly
                handler._check_init_torch()

                # Verify the state was set correctly
                assert handler.initialized == True
                assert handler.index == 0
                assert handler.sync_fn == mock_dist.barrier

                # Verify the log message
                mock_log_info.assert_called_once_with("torch.distributed initialized. index: 0")

    def test_check_init_torch_not_initialized(self):
        """Test _check_init_torch when torch.distributed is not initialized"""
        from objwatch.mp_handls import MPHandls

        # Mock torch.distributed.is_initialized to return False
        mock_dist = MagicMock()
        mock_dist.is_initialized.return_value = False

        # Mock torch.distributed module
        mock_torch = MagicMock()
        mock_torch.distributed = mock_dist

        # Mock log_info to ensure it's not called
        mock_log_info = MagicMock()

        with patch('objwatch.mp_handls.log_info', mock_log_info):
            with patch.dict('sys.modules', {'torch': mock_torch}):
                # Create MPHandls instance
                handler = MPHandls()

                # Call the method directly
                handler._check_init_torch()

                # Verify the state was not changed
                assert handler.initialized == False
                assert handler.index is None
                assert handler.sync_fn is None

                # Verify log_info was not called
                mock_log_info.assert_not_called()

    def test_check_init_torch_no_distributed(self):
        """Test _check_init_torch when torch.distributed is None"""
        from objwatch.mp_handls import MPHandls

        # Mock torch without distributed module
        mock_torch = MagicMock()
        mock_torch.distributed = None

        # Mock log_info to ensure it's not called
        mock_log_info = MagicMock()

        with patch('objwatch.mp_handls.log_info', mock_log_info):
            with patch.dict('sys.modules', {'torch': mock_torch}):
                # Create MPHandls instance
                handler = MPHandls()

                # Call the method directly
                handler._check_init_torch()

                # Verify the state was not changed
                assert handler.initialized == False
                assert handler.index is None
                assert handler.sync_fn is None

                # Verify log_info was not called
                mock_log_info.assert_not_called()
