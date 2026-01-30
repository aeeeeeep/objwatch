# MIT License
# Copyright (c) 2025 aeeeeeep

import logging
import time
from typing import Dict, Any, Optional

import msgpack
import zmq

from .abc import BaseSink

logger = logging.getLogger(__name__)


class ZeroMQSink(BaseSink):
    """
    A high-performance sink that publishes events via ZeroMQ PUB socket.
    Uses msgpack for fast binary serialization.
    """

    def __init__(
        self, endpoint: str = "tcp://127.0.0.1:5555", topic: str = "", output_path: Optional[str] = None, **kwargs
    ):
        super().__init__(output_path=output_path, **kwargs)
        self.endpoint = endpoint
        self.topic = topic.encode('utf-8')
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self.connected: bool = False

        # Connect and wait for ready if requested
        self._connect()
        self._wait_ready()

    def _wait_ready(self, timeout: float = 5.0) -> bool:
        """
        Wait for the ZeroMQ sink to be fully ready to send messages.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if sink is ready, False if timeout occurred
        """
        import time

        start_time = time.time()

        # Wait for connection to be established
        while not self.connected:
            if time.time() - start_time > timeout:
                logger.error("Timeout waiting for ZeroMQ sink to connect")
                return False
            self._connect()
            time.sleep(0.01)

        # Give some extra time for ZeroMQ to complete the binding setup
        time.sleep(0.05)

        logger.info("ZeroMQ sink is ready to send messages")
        return True

    def _connect(self) -> None:
        if self.connected:
            return

        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.PUB)
            # Set LINGER to 0 to prevent hanging on exit if messages are unsent
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.bind(self.endpoint)
            self.connected = True
            logger.info(f"ZeroMQ Sink bound to {self.endpoint}")
        except zmq.ZMQError as e:
            logger.error(f"Failed to bind ZeroMQ socket to {self.endpoint}: {e}")
            self.connected = False

    def emit(self, event: Dict[str, Any]) -> None:
        # Ensure we're connected before emitting
        if not self.connected:
            self._connect()

        if not self.socket or not self.connected:
            logger.error("Cannot emit event: ZeroMQ socket not initialized or connected")
            return

        try:
            event_obj = event.get('_event')

            if event_obj is not None:
                event_data = event_obj.to_dict()
            else:
                event_data = event

            payload = msgpack.packb(event_data, default=str)

            retries = 3
            for i in range(retries):
                try:
                    self.socket.send_multipart([self.topic, payload], flags=zmq.NOBLOCK)
                    logger.debug(f"Sent message on topic '{self.topic.decode('utf-8')}'")
                    break
                except zmq.Again:
                    if i < retries - 1:
                        time.sleep(0.1)
                    else:
                        logger.warning(f"Failed to send after {retries} retries")
        except Exception as e:
            logger.error(f"Error emitting event to ZeroMQ: {e}")

    def close(self) -> None:
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.context:
            self.context.term()
            self.context = None
        self.connected = False
        logger.info("ZeroMQ Sink closed")
