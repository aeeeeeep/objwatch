# MIT License
# Copyright (c) 2025 aeeeeeep

import logging
from typing import Optional, Any, Union

global FORCE, LOGGER

# Global flag to force print logs instead of using the logger
FORCE: bool = False

# Initialize the logger for 'objwatch'
LOGGER: logging.Logger = logging.getLogger('objwatch')


def create_logger(
    name: str = 'objwatch', output: Optional[str] = None, level: Union[int, str] = logging.DEBUG, simple: bool = False
) -> None:
    """
    Create and configure a logger.

    Args:
        name (str): Name of the logger.
        output (Optional[str]): Path to a file for writing logs.
        level (Union[int, str]): Logging level (e.g., logging.DEBUG, logging.INFO, "force").
        simple (bool): Enable simple logging mode with a basic format.
    """
    if level == "force":
        global FORCE
        FORCE = True
        return

    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        # Define the log message format based on the simplicity flag
        if simple:
            formatter = logging.Formatter('%(levelname)s: %(message)s')
        else:
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
            )
        logger.setLevel(level)

        # Create and add a stream handler to the logger
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # If an output file is specified, create and add a file handler
        if output:
            file_handler = logging.FileHandler(output)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    # Prevent log messages from being propagated to the root logger
    logger.propagate = False


def get_logger() -> logging.Logger:
    """
    Retrieve the configured logger.

    Returns:
        logging.Logger: The logger instance.
    """
    global LOGGER
    return LOGGER


def switch_logger(name: str):
    global LOGGER
    LOGGER = logging.getLogger(name)


def log_info(msg: str, *args: Any, **kwargs: Any) -> None:
    """
    Log an informational message or print it if FORCE is enabled.

    Args:
        msg (str): The message to log.
        *args (Any): Variable length argument list.
        **kwargs (Any): Arbitrary keyword arguments.
    """
    global FORCE, LOGGER
    if FORCE:
        print(msg, flush=True)
    else:
        LOGGER.info(msg, *args, **kwargs)


def log_debug(msg: str, *args: Any, **kwargs: Any) -> None:
    """
    Log a debug message or print it if FORCE is enabled.

    Args:
        msg (str): The message to log.
        *args (Any): Variable length argument list.
        **kwargs (Any): Arbitrary keyword arguments.
    """
    global FORCE, LOGGER
    if FORCE:
        print(msg, flush=True)
    else:
        LOGGER.debug(msg, *args, **kwargs)


def log_warn(msg: str, *args: Any, **kwargs: Any) -> None:
    """
    Log a warning message or print it if FORCE is enabled.

    Args:
        msg (str): The message to log.
        *args (Any): Variable length argument list.
        **kwargs (Any): Arbitrary keyword arguments.
    """
    global FORCE, LOGGER
    if FORCE:
        print(msg, flush=True)
    else:
        LOGGER.warning(msg, *args, **kwargs)


def log_error(msg: str, *args: Any, **kwargs: Any) -> None:
    """
    Log an error message or print it if FORCE is enabled.

    Args:
        msg (str): The message to log.
        *args (Any): Variable length argument list.
        **kwargs (Any): Arbitrary keyword arguments.
    """
    global FORCE, LOGGER
    if FORCE:
        print(msg, flush=True)
    else:
        LOGGER.error(msg, *args, **kwargs)
