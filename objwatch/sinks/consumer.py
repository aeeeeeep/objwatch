# MIT License
# Copyright (c) 2025 aeeeeeep

import zmq
import time
import logging
import msgpack
import threading
from pathlib import Path
from typing import Dict, Any, Optional


class ZeroMQFileConsumer:
    """
    A consumer that receives events from ZeroMQSink via ZeroMQ SUB socket
    and writes them to a local file in append mode.
    """

    def __init__(
        self,
        endpoint: str = "tcp://127.0.0.1:5555",
        topic: str = "",
        output_file: str = "zmq_events.log",
        auto_start: bool = False,
        daemon: bool = True,
    ):
        """
        Initialize the ZeroMQFileConsumer.

        Args:
            endpoint: ZeroMQ endpoint to connect to (e.g., "tcp://127.0.0.1:5555")
            topic: Topic to subscribe to (empty string means subscribe to all topics)
            output_file: Path to the output file where events will be written
            auto_start: Whether to automatically start the consumer when initialized
            daemon: Whether to run the consumer in a daemon thread
        """
        self.endpoint = endpoint
        self.topic = topic.encode('utf-8') if isinstance(topic, str) else topic
        self.output_file = output_file
        self.auto_start = auto_start
        self.daemon = daemon

        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None

        # Initialize logging for the consumer
        self.logger = logging.getLogger('objwatch.ZeroMQFileConsumer')

        # Create output directory if it doesn't exist
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        if auto_start:
            self.start()

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

    def _process_event(self, event: Dict[str, Any]) -> str:
        """
        Process the event into a string format suitable for logging.

        Args:
            event: The event dictionary to process

        Returns:
            str: Formatted log line
        """
        # Extract event fields
        level = event.get('level', 'INFO')
        msg = event.get('msg', '')
        timestamp = event.get('time', time.time())
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        name = event.get('name', 'unknown')

        # Format the log line similar to standard logging format
        return f"[{time_str}] [{level}] {name}: {msg}\n"

    def _run(self) -> None:
        """
        The main run loop that listens for messages and writes them to file.
        """
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                self.logger.info(f"Writing events to file: {self.output_file}")

                while self.running:
                    try:
                        if self.socket is None:
                            self.logger.info("Attempting to connect to ZeroMQ endpoint...")
                            self._connect()
                            if self.socket is None:
                                self.logger.error("Failed to establish connection, will retry")
                                time.sleep(0.1)
                                continue

                        # Receive multipart message [topic, payload]
                        msg_parts = self.socket.recv_multipart()
                        if len(msg_parts) == 2:
                            payload = msgpack.unpackb(msg_parts[1], raw=False)

                            # Process and write the event to file
                            log_line = self._process_event(payload)
                            f.write(log_line)
                            f.flush()  # Ensure immediate write to disk
                    except zmq.Again:
                        # Timeout occurred, continue the loop
                        continue
                    except zmq.ZMQError as e:
                        self.logger.error(f"ZeroMQ error: {e}")
                        # Reset socket to trigger reconnection
                        self.socket = None
                        time.sleep(0.1)
                        continue
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")
                        continue
        finally:
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

    def stop(self, timeout: float = 5.0) -> None:
        """
        Stop the consumer gracefully.

        Args:
            timeout: Maximum time to wait for the thread to join
        """
        if not self.running:
            self.logger.warning("Consumer is not running")
            return

        self.logger.info("Stopping consumer...")
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
