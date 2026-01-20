# MIT License
# Copyright (c) 2025 aeeeeeep

import logging
import sys
from typing import Dict, Any, Optional, Union

from .abc import BaseSink


class StandardSink(BaseSink):
    """
    Standard sink that logs to stdout/stderr or a file using Python's logging module.
    Preserves the original behavior of objwatch.
    """

    def __init__(self, output: Optional[str] = None, level: Union[int, str] = logging.DEBUG, simple: bool = True):
        self.logger_name = 'objwatch_std_sink'
        self.output_file = output
        self.output = output
        self.level = level
        self.simple = simple
        self.force_print = level == "force"
        self.logger: Optional[logging.Logger] = None

        if not self.force_print:
            self._configure_logger()

    def _configure_logger(self) -> None:
        self.logger = logging.getLogger(self.logger_name)
        self.logger.propagate = False

        # Clear existing handlers to avoid duplication
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        if self.simple:
            formatter = logging.Formatter('%(message)s')
        else:
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] objwatch: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
            )

        # Safely set level
        try:
            self.logger.setLevel(self.level)
        except (ValueError, TypeError):
            self.logger.setLevel(logging.DEBUG)

        # Stream Handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        # File Handler
        if self.output:
            try:
                file_handler = logging.FileHandler(self.output, mode='a', encoding='utf-8')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                sys.stderr.write(f"objwatch: Failed to setup file logging to {self.output}: {e}\n")

    def emit(self, event: Dict[str, Any]) -> None:
        """
        Event expected format:
        {
            'level': 'INFO' | 'DEBUG' | 'WARN' | 'ERROR',
            'msg': 'Log message',
            ...
        }
        """
        level_str = event.get('level', 'INFO').upper()
        msg = event.get('msg', '')

        if self.force_print:
            print(msg, flush=True)
            return

        if not self.logger:
            return

        # Map level string to method using getattr
        log_method = getattr(self.logger, level_str.lower(), self.logger.info)
        # Handle WARN as WARNING
        if level_str == 'WARN':
            log_method = self.logger.warning
        log_method(msg)

    def close(self) -> None:
        if self.logger:
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)
