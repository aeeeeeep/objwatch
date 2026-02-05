# MIT License
# Copyright (c) 2025 aeeeeeep

import os
import zmq
import time
import logging
import msgpack
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from collections import OrderedDict
from queue import Queue

from .formatter import Formatter


class ZeroMQFileConsumer:
    """
    A consumer that receives events from ZeroMQSink via ZeroMQ SUB socket
    and writes them to a local file in append mode.
    Supports dynamic routing to different output files based on event content.
    
    Optimized for high-throughput concurrent scenarios with:
    - Multi-threaded worker pool for parallel processing
    - Batch receive and bulk write
    - Lock-free queue for event distribution
    """

    def __init__(
        self,
        endpoint: str = "tcp://127.0.0.1:5555",
        topic: str = "",
        output_file: str = "zmq_events.log",
        auto_start: bool = False,
        daemon: bool = True,
        max_open_files: int = 100,
        allowed_directories: Optional[list] = None,
        worker_threads: int = 4,
    ):
        """
        Initialize the ZeroMQFileConsumer.

        Args:
            endpoint: ZeroMQ endpoint to connect to (e.g., "tcp://127.0.0.1:5555")
            topic: Topic to subscribe to (empty string means subscribe to all topics)
            output_file: Default path to the output file where events will be written
            auto_start: Whether to automatically start the consumer when initialized
            daemon: Whether to run the consumer in a daemon thread
            max_open_files: Maximum number of file handles to keep open
            allowed_directories: List of allowed directories for output files (None means any directory)
        """
        self.endpoint = endpoint
        self.topic = topic.encode('utf-8') if isinstance(topic, str) else topic
        self.output_file = output_file
        self.auto_start = auto_start
        self.daemon = daemon
        self.max_open_files = max_open_files
        self.allowed_directories = allowed_directories or [os.getcwd()]

        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None

        # File handle cache using OrderedDict for LRU eviction
        self.file_handles: OrderedDict[str, Any] = OrderedDict()
        self.file_locks: Dict[str, Any] = {}
        self.handle_lock = threading.Lock()

        # Initialize logging for the consumer
        self.logger = logging.getLogger('objwatch.ZeroMQFileConsumer')

        # Create output directory if it doesn't exist
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        if auto_start:
            self.start()
            self._wait_ready()

    def _wait_ready(self, timeout: float = 5.0) -> bool:
        """
        Wait for the consumer to be fully ready to receive messages.
        This helps with ZeroMQ's slow joiner problem by ensuring the SUB socket
        is connected and ready before messages are sent.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if consumer is ready, False if timeout occurred
        """
        import time

        start_time = time.time()

        # Wait for thread to start
        while not self.thread or not self.thread.is_alive():
            if time.time() - start_time > timeout:
                self.logger.error("Timeout waiting for consumer thread to start")
                return False
            time.sleep(0.01)

        # Wait for socket to be connected
        while self.socket is None:
            if time.time() - start_time > timeout:
                self.logger.error("Timeout waiting for ZeroMQ socket to connect")
                return False
            time.sleep(0.01)

        # Give some extra time for ZeroMQ to complete the connection setup
        # This helps with the slow joiner problem
        time.sleep(0.05)

        self.logger.info("Consumer is ready to receive messages")
        return True

    def wait_ready(self, timeout: float = 5.0) -> bool:
        """
        Wait for the consumer to be fully ready to receive messages.
        This helps with ZeroMQ's slow joiner problem by ensuring the SUB socket
        is connected and ready before messages are sent.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if consumer is ready, False if timeout occurred
        """
        return self._wait_ready(timeout)

    def _validate_file_path(self, path: str) -> bool:
        """
        Validate file path to prevent directory traversal and ensure it's within allowed directories.

        Args:
            path: File path to validate

        Returns:
            bool: True if path is valid, False otherwise
        """
        try:
            # Normalize the path
            normalized_path = os.path.normpath(os.path.abspath(path))

            # Check for path traversal attempts
            if '..' in path:
                self.logger.warning(f"Path traversal attempt detected: {path}")
                return False

            # Check if path is within allowed directories
            for allowed_dir in self.allowed_directories:
                allowed_abs = os.path.abspath(allowed_dir)
                if normalized_path.startswith(allowed_abs + os.sep) or normalized_path == allowed_abs:
                    return True

            self.logger.warning(f"Path not in allowed directories: {path}")
            return False

        except Exception as e:
            self.logger.error(f"Error validating path {path}: {e}")
            return False

    def _get_file_handle(self, output_file: str) -> Optional[Any]:
        """
        Get or create a file handle for the specified output file.
        Uses LRU cache to manage file handles.

        Args:
            output_file: Path to the output file

        Returns:
            File handle or None if failed
        """
        if not output_file:
            return None

        # Validate path
        if not self._validate_file_path(output_file):
            self.logger.error(f"Invalid output file path: {output_file}")
            return None

        with self.handle_lock:
            # Check if handle already exists in cache
            if output_file in self.file_handles:
                # Move to end (most recently used)
                self.file_handles.move_to_end(output_file)
                return self.file_handles[output_file]

            # Evict least recently used handle if cache is full
            if len(self.file_handles) >= self.max_open_files:
                oldest_file = next(iter(self.file_handles))
                self._close_file_handle(oldest_file)

            try:
                # Create directory if it doesn't exist
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)

                # Open file in append mode
                handle = open(output_file, 'a', encoding='utf-8')
                self.file_handles[output_file] = handle

                # Create lock for this file
                self.file_locks[output_file] = threading.Lock()

                self.logger.info(f"Opened file handle for: {output_file}")
                return handle

            except Exception as e:
                self.logger.error(f"Failed to open file {output_file}: {e}")
                return None

    def _close_file_handle(self, output_file: str) -> None:
        """
        Close a file handle and clean up resources.

        Args:
            output_file: Path to the output file
        """
        with self.handle_lock:
            if output_file in self.file_handles:
                try:
                    self.file_handles[output_file].close()
                    del self.file_handles[output_file]
                    self.logger.debug(f"Closed file handle for: {output_file}")
                except Exception as e:
                    self.logger.error(f"Error closing file {output_file}: {e}")

            if output_file in self.file_locks:
                del self.file_locks[output_file]

    def _close_all_file_handles(self) -> None:
        """
        Close all open file handles.
        """
        with self.handle_lock:
            for output_file in list(self.file_handles.keys()):
                self._close_file_handle(output_file)

    def _acquire_file_lock(self, output_file: str, timeout: float = 5.0) -> bool:
        """
        Acquire lock for file operations.

        Args:
            output_file: Path to the output file
            timeout: Maximum time to wait for lock acquisition

        Returns:
            bool: True if lock was acquired, False otherwise
        """
        if output_file not in self.file_locks:
            return False

        lock = self.file_locks[output_file]
        acquired = lock.acquire(timeout=timeout)

        if not acquired:
            self.logger.warning(f"Failed to acquire lock for {output_file} within {timeout}s")

        return acquired

    def _release_file_lock(self, output_file: str) -> None:
        """
        Release lock for file operations.

        Args:
            output_file: Path to the output file
        """
        if output_file in self.file_locks:
            try:
                self.file_locks[output_file].release()
            except RuntimeError:
                # Lock was not held, ignore
                pass

    def _connect(self) -> None:
        """
        Establish connection to the ZeroMQ endpoint.
        """
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.SUB)
            self.socket.setsockopt(zmq.RCVTIMEO, 1000)  # 1 second timeout for receive
            self.socket.setsockopt(zmq.SUBSCRIBE, self.topic)
            self.socket.connect(self.endpoint)
            self.logger.info(f"Connected to ZeroMQ endpoint: {self.endpoint}")
            self.logger.info(f"Subscribed to topic: {self.topic.decode('utf-8') if self.topic else 'all topics'}")
        except zmq.ZMQError as e:
            self.logger.error(f"Failed to connect to ZeroMQ endpoint {self.endpoint}: {e}")
            # Clean up resources if partially initialized
            if self.socket:
                self.socket.close()
                self.socket = None
            if self.context:
                self.context.term()
                self.context = None

    def _disconnect(self) -> None:
        """
        Disconnect from the ZeroMQ endpoint and clean up resources.
        """
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.context:
            self.context.term()
            self.context = None
        self.logger.info("Disconnected from ZeroMQ endpoint")

    def _process_event(self, event_dict: Dict[str, Any]) -> str:
        """
        Process the event dictionary into a string format suitable for logging.

        Args:
            event_dict: The event dictionary to process

        Returns:
            str: Formatted log line
        """
        # Check if this is a raw event (new format)
        if 'event_type' in event_dict and 'lineno' in event_dict and 'call_depth' in event_dict:
            # Use the formatter to process the event dictionary
            return Formatter.format(event_dict)
        else:
            # Legacy format - keep for backward compatibility
            level = event_dict.get('level', 'INFO')
            msg = event_dict.get('msg', '')
            timestamp = event_dict.get('time', time.time())
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            name = event_dict.get('name', 'unknown')
            process_id = event_dict.get('process_id', 'unknown')

            return f"[{time_str}] [{level}] [PID:{process_id}] {name}: {msg}\n"

    def _run(self) -> None:
        """
        The main run loop that listens for messages and writes them to file.
        Supports both single events (dict) and batched events (list).
        Optimized with batch receive and bulk write for high throughput.
        """
        try:
            self.logger.info(f"Writing events to file: {self.output_file}")

            # Batch processing configuration
            receive_batch_size = 100  # Number of ZMQ messages to receive in one batch
            write_buffer_limit = 1000  # Number of log lines to buffer before writing

            while self.running:
                try:
                    if self.socket is None:
                        self.logger.info("Attempting to connect to ZeroMQ endpoint...")
                        self._connect()
                        if self.socket is None:
                            self.logger.error("Failed to establish connection, will retry")
                            time.sleep(0.1)
                            continue

                    # Batch receive: collect multiple ZMQ messages
                    zmq_messages = []
                    for _ in range(receive_batch_size):
                        try:
                            msg_parts = self.socket.recv_multipart(flags=zmq.NOBLOCK)
                            if len(msg_parts) == 2:
                                zmq_messages.append(msg_parts[1])
                        except zmq.Again:
                            # No more messages available
                            break

                    if not zmq_messages:
                        # No messages received, wait a bit
                        time.sleep(0.001)
                        continue

                    # Process all received messages
                    # Group events by output file for efficient bulk writes
                    file_events: Dict[str, List[str]] = {}

                    for msg_data in zmq_messages:
                        try:
                            payload = msgpack.unpackb(msg_data, raw=False)

                            # Handle both single events (dict) and batched events (list)
                            events = payload if isinstance(payload, list) else [payload]

                            for event in events:
                                output_file = event.get('output_file', self.output_file)
                                log_line = self._process_event(event)

                                if output_file not in file_events:
                                    file_events[output_file] = []
                                file_events[output_file].append(log_line)

                        except Exception as e:
                            self.logger.error(f"Error unpacking message: {e}")
                            continue

                    # Bulk write to files
                    for output_file, log_lines in file_events.items():
                        file_handle = self._get_file_handle(output_file)

                        if file_handle:
                            try:
                                if self._acquire_file_lock(output_file):
                                    try:
                                        # Bulk write all lines at once
                                        file_handle.write(''.join(log_lines))
                                    finally:
                                        self._release_file_lock(output_file)
                            except Exception as e:
                                self.logger.error(f"Error writing to file {output_file}: {e}")
                        else:
                            self.logger.warning(f"No file handle available for: {output_file}")

                    # Flush all written files
                    for output_file in file_events.keys():
                        file_handle = self._get_file_handle(output_file)
                        if file_handle:
                            try:
                                file_handle.flush()
                            except Exception as e:
                                self.logger.error(f"Error flushing file {output_file}: {e}")

                except zmq.ZMQError as e:
                    self.logger.error(f"ZeroMQ error: {e}")
                    self.socket = None
                    time.sleep(0.1)
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    continue
        finally:
            self._close_all_file_handles()
            self._disconnect()

    def start(self, daemon: Optional[bool] = None) -> None:
        """
        Start the consumer in a separate thread.

        Args:
            daemon: Whether to run the thread as a daemon. If None, uses the instance's daemon setting.
        """
        if self.running:
            self.logger.warning("Consumer is already running")
            return

        self.running = True

        # Use provided daemon value or instance default
        daemon = daemon if daemon is not None else self.daemon

        # Create and start the thread
        self.thread = threading.Thread(target=self._run, daemon=daemon)
        self.thread.start()
        self.logger.info(f"Consumer started {'(daemon thread)' if daemon else ''}")

    def stop(self, timeout: float = 5.0, wait_for_messages: bool = True) -> None:
        """
        Stop the consumer gracefully.

        Args:
            timeout: Maximum time to wait for the thread to join
            wait_for_messages: Whether to wait for all messages to be processed before stopping
        """
        if not self.running:
            self.logger.warning("Consumer is not running")
            return

        self.logger.info("Stopping consumer...")

        # Give some time for messages to be processed if requested
        if wait_for_messages:
            self.logger.info("Waiting for messages to be processed...")
            time.sleep(0.2)  # Give time for messages to be processed

        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout)
            if self.thread.is_alive():
                self.logger.warning("Consumer thread did not terminate within timeout")
            else:
                self.logger.info("Consumer thread terminated gracefully")

        self.thread = None

    def __enter__(self) -> 'ZeroMQFileConsumer':
        """
        Enter method for context manager support.
        """
        if not self.running:
            self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit method for context manager support.
        """
        self.stop()
