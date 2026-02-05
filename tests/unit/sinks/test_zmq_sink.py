# MIT License
# Copyright (c) 2025 aeeeeeep

import time
import pytest

from objwatch.config import ObjWatchConfig
from objwatch.sinks.std import StandardSink
from objwatch.sinks.zmq_sink import ZeroMQSink
from objwatch.sinks.factory import get_sink


class TestZeroMQSink:
    """Tests for the ZeroMQSink class functionality"""

    def test_zmq_sink_init(self):
        """Test ZeroMQSink initialization"""
        sink = ZeroMQSink(endpoint="tcp://127.0.0.1:5556")
        assert sink.endpoint == "tcp://127.0.0.1:5556"
        assert sink.topic == b""
        sink.close()

    def test_zmq_sink_with_topic(self):
        """Test ZeroMQSink initialization with topic"""
        sink = ZeroMQSink(endpoint="tcp://127.0.0.1:5557", topic="test_topic")
        assert sink.topic == b"test_topic"
        sink.close()

    def test_zmq_sink_emit(self):
        """Test ZeroMQSink message emission"""
        # This test primarily verifies that the ZeroMQSink emit method doesn't throw exceptions
        # Due to the nature of ZeroMQ PUB-SUB pattern, it's difficult to reliably verify message reception in unit tests
        # Therefore, we mainly test the basic functionality and exception handling of the emit method

        endpoint = "tcp://127.0.0.1:5558"
        topic = "test"

        # Create ZeroMQSink
        sink = ZeroMQSink(endpoint=endpoint, topic=topic)

        # Test emit method whether it can execute normally without throwing exceptions
        test_event = {'level': 'INFO', 'msg': 'Test message', 'time': time.time(), 'name': 'test_logger'}

        # Send multiple messages to ensure the method can execute stably
        for _ in range(10):
            sink.emit(test_event)

        # Verify that the method execution does not affect the availability of the sink
        assert sink.endpoint == endpoint
        assert sink.topic == topic.encode('utf-8')

        sink.close()

    def test_zmq_sink_emit_without_socket(self):
        """Test calling emit method without a valid socket"""
        # Create a ZeroMQSink, but use an invalid endpoint to ensure socket is None
        # Note: We need to modify the test method because ZeroMQSink tries to bind the endpoint, even if it's invalid
        # Here we use an internal method to simulate socket being None
        sink = ZeroMQSink(endpoint="tcp://127.0.0.1:5559")
        # Manually set socket to None
        sink.socket = None
        # Call emit method, should not throw an exception
        sink.emit({'level': 'INFO', 'msg': 'Test message'})
        sink.close()

    def test_zmq_sink_close(self):
        """Test ZeroMQSink close method"""
        sink = ZeroMQSink(endpoint="tcp://127.0.0.1:5560")
        sink.close()
        # Verify resources have been released
        assert sink.socket is None
        assert sink.context is None

    def test_zmq_sink_factory_creation(self):
        """Test creating ZeroMQSink through factory function"""
        # Create a configuration with zmq output mode
        config = ObjWatchConfig(
            targets=['tests.utils.example_module'], output_mode='zmq', zmq_endpoint='tcp://127.0.0.1:5561'
        )

        # Create sink using factory function
        sink = get_sink(config)
        assert isinstance(sink, ZeroMQSink)
        assert sink.endpoint == 'tcp://127.0.0.1:5561'
        sink.close()

    def test_zmq_sink_factory_default(self):
        """Test factory function returns StandardSink by default"""
        # Create a configuration with default output mode
        config = ObjWatchConfig(targets=['tests.utils.example_module'], output_mode='std')

        # Create sink using factory function
        sink = get_sink(config)
        assert isinstance(sink, StandardSink)

    def test_zmq_sink_invalid_endpoint(self):
        """Test invalid endpoint handling"""
        # Use an invalid endpoint format
        sink = ZeroMQSink(endpoint="invalid_endpoint")
        # Should initialize normally without throwing exceptions
        # But socket might be None
        # Note: Since ZeroMQSink's _connect method catches exceptions, socket could be None
        # We don't directly assert socket is None because different ZeroMQ versions might have different behaviors
        sink.close()

    def test_zmq_sink_multiple_messages(self):
        """Test sending multiple messages"""
        endpoint = "tcp://127.0.0.1:5562"
        topic = "multi"
        message_count = 10

        # Create ZeroMQSink
        sink = ZeroMQSink(endpoint=endpoint, topic=topic)

        # Send multiple messages continuously to test the stability of the emit method
        for i in range(message_count):
            test_event = {'level': 'INFO', 'msg': f'Test message {i}', 'time': time.time(), 'name': 'test_logger'}
            sink.emit(test_event)

        # Verify sink is still usable
        assert sink.endpoint == endpoint
        assert sink.topic == topic.encode('utf-8')

        sink.close()

    def test_zmq_sink_different_event_types(self):
        """Test sending different event types"""
        endpoint = "tcp://127.0.0.1:5563"
        topic = "events"

        # Create ZeroMQSink
        sink = ZeroMQSink(endpoint=endpoint, topic=topic)

        # Send events with different levels to test emit method's handling of different event types
        event_types = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']
        for event_type in event_types:
            test_event = {
                'level': event_type,
                'msg': f'{event_type} message',
                'time': time.time(),
                'name': 'test_logger',
            }
            sink.emit(test_event)

        # Verify sink is still usable
        assert sink.endpoint == endpoint
        assert sink.topic == topic.encode('utf-8')

        sink.close()

    def test_zmq_sink_reconnect(self):
        """Test ZeroMQSink reconnection"""
        endpoint = "tcp://127.0.0.1:5564"

        # First create and close a sink
        sink1 = ZeroMQSink(endpoint=endpoint)
        sink1.close()

        # Second create a sink, should be able to bind to the same endpoint normally
        sink2 = ZeroMQSink(endpoint=endpoint)
        assert sink2.endpoint == endpoint
        sink2.close()

    def test_zmq_sink_emit_none_socket(self):
        """Test calling emit method when socket is None"""
        # Create a sink, then manually set socket to None
        sink = ZeroMQSink(endpoint="tcp://127.0.0.1:5565")
        sink.socket = None

        # Call emit method, should not throw an exception
        sink.emit({'level': 'INFO', 'msg': 'Test message'})
        sink.close()

    def test_zmq_sink_context_termination(self):
        """Test context termination"""
        sink = ZeroMQSink(endpoint="tcp://127.0.0.1:5566")
        # Close sink
        sink.close()
        # Context should have been terminated
        # Note: We can't directly check if the context has been terminated because ZeroMQ doesn't provide such a method
        # Here we just verify that the code can execute normally without throwing exceptions
        pass


if __name__ == "__main__":
    pytest.main([__file__])
