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

    def __init__(self, endpoint: str = "tcp://127.0.0.1:5555", topic: str = "", output_file: Optional[str] = None):
        self.endpoint = endpoint
        self.topic = topic.encode('utf-8')
        self.output_file = output_file
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self.connected: bool = False

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
            # Serialize payload with msgpack
            # msgpack is faster and more compact than JSON
            payload = msgpack.packb(event)

            # Send multipart message: [topic, payload]
            # This allows subscribers to filter by topic efficiently
            # NOBLOCK ensures we don't block the main thread
            # But we'll retry a few times if the socket buffer is full
            retries = 3
            for i in range(retries):
                try:
                    self.socket.send_multipart([self.topic, payload], flags=zmq.NOBLOCK)
                    logger.debug(f"Successfully sent message on topic '{self.topic.decode('utf-8')}'")
                    break
                except zmq.Again:
                    if i < retries - 1:
                        # Wait a bit and retry
                        time.sleep(0.1)
                    else:
                        logger.warning(f"Failed to send message after {retries} retries: socket buffer full")
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
