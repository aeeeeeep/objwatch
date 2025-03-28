# MIT License
# Copyright (c) 2025 aeeeeeep

from typing import Optional
from types import FunctionType
from .utils.logger import log_error, log_info


class MPHandls:
    """
    Handles multi-process initialization and synchronization
    using specified multi-process frameworks.

    Supported frameworks:
    - 'torch.distributed': PyTorch's distributed environment for multi-GPU support.
    - 'multiprocessing': Python's built-in multiprocessing for parallel processing.

    Manages process synchronization and provides the index of the current process.
    """

    def __init__(self, framework: Optional[str] = None) -> None:
        """
        Initializes the handler with the specified framework.

        Args:
            framework (Optional[str]): The multi-process framework to use.
        """
        self.framework: Optional[str] = framework
        self.initialized: bool = False
        self.index: Optional[int] = None
        self.sync_fn: Optional[FunctionType] = None
        self._check_initialized()

    def _check_initialized(self) -> None:
        """
        Verifies if the selected multi-process framework is initialized.
        """
        if self.framework is None:
            pass
        elif self.framework == 'torch.distributed':
            self._check_init_torch()
        elif self.framework == 'multiprocessing':
            self._check_init_multiprocessing()
        else:
            log_error(f"Invalid framework: {self.framework}")
            raise ValueError(f"Invalid framework: {self.framework}")

    def sync(self) -> None:
        """
        Synchronizes processes across all indices.
        """
        if self.initialized and self.sync_fn is not None:
            self.sync_fn()

    def get_index(self) -> Optional[int]:
        """
        Returns the index of the current process.

        Returns:
            Optional[int]: The index of the current process (e.g., rank in distributed environments).
            Returns None if the framework is not initialized.
        """
        return self.index

    def is_initialized(self) -> bool:
        """
        Checks if the multi-process framework has been initialized.

        Returns:
            bool: True if the framework is initialized, False otherwise.
        """
        if self.framework is not None and not self.initialized:
            self._check_initialized()
        return self.initialized

    def _check_init_torch(self) -> None:
        """
        Checks if the PyTorch distributed environment is initialized for multi-GPU support.
        If initialized, sets the current process index and synchronization function.
        """
        import torch

        if torch.distributed and torch.distributed.is_initialized():
            self.initialized = True
            self.index = torch.distributed.get_rank()
            self.sync_fn = torch.distributed.barrier
            log_info(f"torch.distributed initialized. index: {self.index}")

    def _check_init_multiprocessing(self) -> None:
        """
        Checks if Python's built-in multiprocessing is initialized.
        If initialized, sets the current process index and synchronization function.
        """
        import multiprocessing

        current_process = multiprocessing.current_process()
        if current_process.name != "MainProcess":
            self.initialized = True
            self.index = current_process._identity[0] - 1  # Adjusting index (starts from 1)
            self.sync_fn = None
            log_info(f"multiprocessing initialized. index: {self.index}")
