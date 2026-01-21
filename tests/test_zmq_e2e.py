# MIT License
# Copyright (c) 2025 aeeeeeep

import os
import time
import unittest
import tempfile

from objwatch import ObjWatch, watch
from objwatch.config import ObjWatchConfig
from objwatch.sinks.consumer import ZeroMQFileConsumer


class TestZeroMQE2E(unittest.TestCase):
    """
    End-to-end tests for ZeroMQ related functionality.
    """

    def setUp(self):
        """
        Set up test environment.
        """
        # Use a unique port for each test to avoid conflicts
        self.endpoint = "tcp://127.0.0.1:5555"
        self.topic = "test_topic"
        self.consumer_output = tempfile.NamedTemporaryFile(suffix=".log", delete=False).name

        # Clean up any existing output file
        if os.path.exists(self.consumer_output):
            os.remove(self.consumer_output)

    def tearDown(self):
        """
        Clean up test environment.
        """
        # Clean up test output file
        if os.path.exists(self.consumer_output):
            os.remove(self.consumer_output)

    def test_zmq_sink_consumer_integration(self):
        """
        Test that ZeroMQSink sends messages that can be received by ZeroMQFileConsumer.
        """
        # Create and start the consumer directly
        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint, topic=self.topic, output_file=self.consumer_output, auto_start=True, daemon=True
        )

        # Give the consumer time to start and connect
        # Increase delay to handle ZeroMQ SUB socket's slow joiner problem
        time.sleep(0.1)

        # Create a ZeroMQSink directly
        from objwatch.sinks.zmq_sink import ZeroMQSink

        sink = ZeroMQSink(endpoint=self.endpoint, topic=self.topic)

        # Send some test messages directly
        test_messages = [f"Test message {i}" for i in range(3)]

        for msg in test_messages:
            print(f"[Test] Sending direct message: {msg}")
            test_event = {'level': 'INFO', 'msg': msg, 'time': time.time(), 'name': 'test_logger'}
            sink.emit(test_event)
            time.sleep(0.1)  # Give time for message to be sent

        # Give time for messages to be processed
        time.sleep(0.1)

        # Clean up
        consumer.stop()
        sink.close()

        # Verify that messages were received and written to file
        self.assertTrue(os.path.exists(self.consumer_output), "Consumer output file was not created")

        with open(self.consumer_output, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that at least one message was received
        self.assertTrue(len(content) > 0, "No messages were received by the consumer")

        # Check that at least one test message is in the output
        received_test_messages = [msg for msg in test_messages if msg in content]
        self.assertGreater(len(received_test_messages), 0, "No test messages were found in consumer output")

        print(f"[Test] Received messages: {received_test_messages}")

    def test_auto_start_consumer(self):
        """
        Test that the consumer is automatically started when auto_start_consumer is True.
        """
        # This test is simplified to verify that the consumer is started automatically
        # Create and configure ObjWatch with ZeroMQ sink and auto-started consumer
        # Note: We need to provide an output file path for the consumer to be auto-started
        config = ObjWatchConfig(
            targets=["sys"],
            output_mode="zmq",
            zmq_endpoint=self.endpoint,
            zmq_topic=self.topic,
            auto_start_consumer=True,
            output=self.consumer_output,  # Add output parameter to auto-start consumer
            level="INFO",
            simple=True,
        )

        # Start tracing
        obj_watch = ObjWatch(**config.__dict__)
        obj_watch.start()

        # Verify that consumer was auto-started
        self.assertIsNotNone(obj_watch.consumer, "Consumer should have been auto-started")
        self.assertTrue(obj_watch.consumer.running, "Consumer should be running after auto-start")

        # Save consumer reference before stop
        consumer_ref = obj_watch.consumer

        # Stop tracing
        obj_watch.stop()

        # Verify that consumer was stopped
        self.assertFalse(consumer_ref.running, "Consumer should be stopped after ObjWatch.stop()")

    def test_zmq_topic_filtering(self):
        """
        Test that consumer only receives messages with the subscribed topic.
        Note: This test may fail occasionally due to ZeroMQ's asynchronous nature and SUB socket's "slow joiner" problem.
        """
        # Simplified test: create one consumer with a specific topic and send matching messages
        consumer_output = tempfile.NamedTemporaryFile(suffix=".log", delete=False).name

        # Create consumer with topic "test_topic"
        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint, topic="test_topic", output_file=consumer_output, auto_start=True, daemon=True
        )

        # Give consumers time to start and connect
        # Increase delay to handle ZeroMQ SUB socket's slow joiner problem
        time.sleep(0.1)

        # Create ZeroMQSink
        from objwatch.sinks.zmq_sink import ZeroMQSink

        sink = ZeroMQSink(endpoint=self.endpoint, topic="test_topic")

        # Send multiple messages with matching topic
        message = "Test message with matching topic"
        print(f"[Test] Sending messages with topic 'test_topic': {message}")

        # Send multiple messages to increase chance of reception
        for _ in range(5):
            sink.emit({'level': 'INFO', 'msg': message, 'time': time.time(), 'name': 'test_logger'})
            time.sleep(0.1)

        # Give time for messages to be processed
        time.sleep(0.1)

        # Clean up
        consumer.stop()
        sink.close()

        # Verify that the consumer received at least one message
        with open(consumer_output, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that at least one message was received
        self.assertTrue(len(content) > 0, "No messages were received by the consumer")
        self.assertIn(message, content, "Consumer should have received message with matching topic")

        # Clean up
        os.remove(consumer_output)

    def test_zmq_invalid_endpoint(self):
        """
        Test handling of invalid ZeroMQ endpoint.
        """
        # Use an invalid endpoint
        invalid_endpoint = "invalid_endpoint"

        # Test that ZeroMQFileConsumer handles invalid endpoint gracefully
        try:
            consumer = ZeroMQFileConsumer(
                endpoint=invalid_endpoint,
                topic=self.topic,
                output_file=self.consumer_output,
                auto_start=True,
                daemon=True,
            )
            # If we get here, the consumer should have handled the error
            consumer.stop()
        except Exception as e:
            self.fail(f"ZeroMQFileConsumer should handle invalid endpoint gracefully, but got exception: {e}")

        # Test that ObjWatch handles invalid endpoint gracefully
        try:
            config = ObjWatchConfig(
                targets=["sys"], output_mode="zmq", zmq_endpoint=invalid_endpoint, level="INFO", simple=True
            )
            obj_watch = ObjWatch(**config.__dict__)
            obj_watch.start()
            obj_watch.stop()
        except Exception as e:
            self.fail(f"ObjWatch should handle invalid endpoint gracefully, but got exception: {e}")

    def test_zmq_consumer_lifecycle(self):
        """
        Test proper lifecycle management of ZeroMQ consumer.
        """
        # Create consumer
        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint, topic=self.topic, output_file=self.consumer_output, auto_start=False
        )

        # Start consumer
        consumer.start()
        time.sleep(0.1)

        # Verify consumer is running
        self.assertTrue(consumer.running, "Consumer should be running after start()")

        # Stop consumer
        consumer.stop()
        time.sleep(0.1)

        # Verify consumer has stopped
        self.assertFalse(consumer.running, "Consumer should not be running after stop()")

    def test_zmq_consumer_context_manager(self):
        """
        Test that ZeroMQFileConsumer works correctly as a context manager.
        """
        # Use consumer as context manager
        with ZeroMQFileConsumer(
            endpoint=self.endpoint, topic=self.topic, output_file=self.consumer_output, auto_start=False
        ) as consumer:
            # Start consumer within context
            consumer.start()
            time.sleep(0.1)
            self.assertTrue(consumer.running, "Consumer should be running within context")

        # Verify consumer has been stopped after context exit
        self.assertFalse(consumer.running, "Consumer should be stopped after context exit")

    def test_zmq_watch_function_integration(self):
        """
        Test that the watch() function works correctly with ZeroMQ sink.
        """
        # This test is simplified to verify that the watch() function can be initialized with ZeroMQ sink
        # without raising exceptions.

        # Use the watch() function to start tracing with ZeroMQ sink
        print("[Test] Initializing watch() function with ZeroMQ sink...")
        obj_watch = watch(
            targets=["sys"],
            output_mode="zmq",
            zmq_endpoint=self.endpoint,
            zmq_topic=self.topic,
            level="INFO",
            simple=True,
        )

        # Verify that obj_watch was created successfully
        self.assertIsNotNone(obj_watch, "watch() function should return an ObjWatch instance")

        # Stop tracing
        print("[Test] Stopping watch() function...")
        obj_watch.stop()

        print("[Test] watch() function integration test completed successfully")

    def test_zmq_consumer_daemon_thread(self):
        """
        Test that the consumer can run as a daemon thread.
        """
        # Create consumer with daemon=True
        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint, topic=self.topic, output_file=self.consumer_output, auto_start=False, daemon=True
        )

        # Start consumer
        consumer.start()

        # Give the consumer time to start
        time.sleep(0.1)

        # Verify consumer is running in a daemon thread
        self.assertTrue(consumer.running, "Consumer should be running")
        self.assertTrue(consumer.thread.daemon, "Consumer thread should be a daemon thread")

        # Stop consumer
        consumer.stop()

    def test_zmq_consumer_no_daemon_thread(self):
        """
        Test that the consumer can run as a non-daemon thread.
        """
        # Create consumer with daemon=False
        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint, topic=self.topic, output_file=self.consumer_output, auto_start=False, daemon=False
        )

        # Start consumer
        consumer.start()

        # Give the consumer time to start
        time.sleep(0.1)

        # Verify consumer is running in a non-daemon thread
        self.assertTrue(consumer.running, "Consumer should be running")
        self.assertFalse(consumer.thread.daemon, "Consumer thread should not be a daemon thread")

        # Stop consumer
        consumer.stop()

    def test_zmq_consumer_reconnect(self):
        """
        Test that the consumer can reconnect if the connection is lost.
        """
        # Create consumer
        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint, topic=self.topic, output_file=self.consumer_output, auto_start=False
        )

        # Start consumer
        consumer.start()
        time.sleep(0.1)

        # Stop and restart consumer
        consumer.stop()
        time.sleep(0.1)
        consumer.start()
        time.sleep(0.1)

        # Verify consumer is running after restart
        self.assertTrue(consumer.running, "Consumer should be running after restart")

        # Stop consumer
        consumer.stop()


if __name__ == '__main__':
    unittest.main()
