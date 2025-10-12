# file: objwatch/mp_handls.py:97-109
# asked: {"lines": [97, 102, 104, 105, 106, 107, 108, 109], "branches": [[105, 0], [105, 106]]}
# gained: {"lines": [97, 102, 104, 105, 106, 107, 108, 109], "branches": [[105, 0], [105, 106]]}

import pytest
import multiprocessing
from unittest.mock import patch, MagicMock
from objwatch.mp_handls import MPHandls


def test_check_init_multiprocessing_non_main_process():
    """Test _check_init_multiprocessing when current process is not MainProcess."""
    with patch('multiprocessing.current_process') as mock_current_process:
        # Mock a non-main process with identity
        mock_process = MagicMock()
        mock_process.name = "Process-1"
        mock_process._identity = [2]  # Process identity (starts from 1)
        mock_current_process.return_value = mock_process

        # Create MPHandls instance and call the method
        handler = MPHandls()
        handler._check_init_multiprocessing()

        # Verify the state was set correctly
        assert handler.initialized is True
        assert handler.index == 1  # identity[0] - 1 = 2 - 1 = 1
        assert handler.sync_fn is None


def test_check_init_multiprocessing_main_process():
    """Test _check_init_multiprocessing when current process is MainProcess."""
    with patch('multiprocessing.current_process') as mock_current_process:
        # Mock the main process
        mock_process = MagicMock()
        mock_process.name = "MainProcess"
        mock_current_process.return_value = mock_process

        # Create MPHandls instance and call the method
        handler = MPHandls()
        handler._check_init_multiprocessing()

        # Verify the state was not changed (should remain default)
        assert handler.initialized is False
        assert handler.index is None
        assert handler.sync_fn is None


def test_check_init_multiprocessing_with_logging():
    """Test _check_init_multiprocessing verifies logging is called."""
    with patch('multiprocessing.current_process') as mock_current_process, patch(
        'objwatch.mp_handls.log_info'
    ) as mock_log_info:
        # Mock a non-main process with identity
        mock_process = MagicMock()
        mock_process.name = "Process-1"
        mock_process._identity = [3]  # Process identity (starts from 1)
        mock_current_process.return_value = mock_process

        # Create MPHandls instance and call the method
        handler = MPHandls()
        handler._check_init_multiprocessing()

        # Verify logging was called with correct message
        mock_log_info.assert_called_once_with("multiprocessing initialized. index: 2")
