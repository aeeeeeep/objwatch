# MIT License
# Copyright (c) 2025 aeeeeeep

import logging
import threading
from typing import Optional, Any, Union

from ..sinks.abc import BaseSink
from ..sinks.std import StandardSink
from ..sinks.factory import get_sink


class LoggerManager:
    """
    Thread-safe singleton manager for logger configuration and state.
    Encapsulates global state to avoid mutable global variables.
    """

    _instance: Optional['LoggerManager'] = None
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls) -> 'LoggerManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialized = True
        self._force_print: bool = False
        self._sink: Optional[BaseSink] = None
        self._logger: logging.Logger = logging.getLogger('objwatch')
        self._logger.propagate = False
        self._setup_handlers()

    @property
    def force_print(self) -> bool:
        return self._force_print

    @property
    def sink(self) -> Optional[BaseSink]:
        return self._sink

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def _setup_handlers(self) -> None:
        has_sink_handler = any(isinstance(handler, SinkHandler) for handler in self._logger.handlers)
        if not has_sink_handler:
            self._logger.addHandler(SinkHandler())
        self._logger.setLevel(logging.DEBUG)

    def create_logger(
        self,
        name: str = 'objwatch',
        output: Optional[str] = None,
        level: Union[int, str] = logging.DEBUG,
        simple: bool = True,
    ) -> None:
        if level == "force":
            self._force_print = True
        else:
            self._force_print = False

        self._sink = StandardSink(output=output, level=level, simple=simple)

        if level != "force":
            try:
                self._logger.setLevel(level)
            except (ValueError, TypeError):
                self._logger.setLevel(logging.DEBUG)

        self._setup_handlers()

    def setup_logging_from_config(self, config: Any) -> None:
        if config.level == "force":
            self._force_print = True
        else:
            self._force_print = False

        self._sink = get_sink(config)

        if config.level != "force":
            try:
                self._logger.setLevel(config.level)
            except (ValueError, TypeError):
                self._logger.setLevel(logging.DEBUG)

        self._setup_handlers()

    def log(self, level: str, msg: str, *args: Any, **kwargs: Any) -> None:
        if self._force_print:
            print(msg, flush=True)
        else:
            log_method = getattr(self._logger, level.lower(), self._logger.info)
            if level == 'WARN':
                log_method = self._logger.warning
            log_method(msg, *args, **kwargs)


class SinkHandler(logging.Handler):
    """
    A logging handler that redirects records to the configured sink.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Prevent logging loops by skipping records from sinks module
        if record.name.startswith('objwatch.sinks'):
            return

        manager = LoggerManager()
        sink = manager.sink

        if sink is None:
            sink = StandardSink()
            manager._sink = sink

        try:
            msg = self.format(record)
            event = {
                'level': record.levelname,
                'msg': msg,
                'time': record.created,
                'name': record.name,
            }
            sink.emit(event)
        except Exception as e:
            logging.error(f"SinkHandler failed to emit record: {e}")
            self.handleError(record)


_manager = LoggerManager()


def create_logger(
    name: str = 'objwatch', output: Optional[str] = None, level: Union[int, str] = logging.DEBUG, simple: bool = True
) -> None:
    _manager.create_logger(name=name, output=output, level=level, simple=simple)


def setup_logging_from_config(config: Any) -> None:
    _manager.setup_logging_from_config(config)


def get_logger() -> logging.Logger:
    return _manager.logger


def log_info(msg: str, *args: Any, **kwargs: Any) -> None:
    _manager.log('INFO', msg, *args, **kwargs)


def log_debug(msg: str, *args: Any, **kwargs: Any) -> None:
    _manager.log('DEBUG', msg, *args, **kwargs)


def log_warn(msg: str, *args: Any, **kwargs: Any) -> None:
    _manager.log('WARN', msg, *args, **kwargs)


def log_error(msg: str, *args: Any, **kwargs: Any) -> None:
    _manager.log('ERROR', msg, *args, **kwargs)
