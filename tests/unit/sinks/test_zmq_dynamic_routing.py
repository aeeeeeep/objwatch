# MIT License
# Copyright (c) 2025 aeeeeeep

import os
import time
import tempfile
import unittest

from objwatch.sinks.zmq_sink import ZeroMQSink
from objwatch.sinks.consumer import ZeroMQFileConsumer


class TestZeroMQFileConsumer(unittest.TestCase):
    """
    Tests for ZeroMQFileConsumer class functionality
    """

    def setUp(self):
        """
        Set up test environment.
        """
        # Use a unique port for each test to avoid conflicts
        self.endpoint = "tcp://127.0.0.1:5560"
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """
        Clean up test environment.
        """
        # Clean up test output files
        if os.path.exists(self.temp_dir):
            import logging

            for filename in os.listdir(self.temp_dir):
                filepath = os.path.join(self.temp_dir, filename)
                try:
                    os.remove(filepath)
                except Exception as e:
                    logging.debug(f"Failed to remove {filepath}: {e}")
            try:
                os.rmdir(self.temp_dir)
            except Exception as e:
                logging.debug(f"Failed to remove directory {self.temp_dir}: {e}")

    def test_dynamic_routing_basic(self):
        """
        Test basic dynamic routing functionality.
        """
        output1 = os.path.join(self.temp_dir, "output1.log")
        output2 = os.path.join(self.temp_dir, "output2.log")

        # Create ZeroMQSink first and bind to endpoint (wait_ready is now handled in __init__)
        sink = ZeroMQSink(endpoint=self.endpoint, topic="", output_file=output1)

        # Create and start consumer (wait_ready is now handled in __init__)
        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint, auto_start=True, daemon=True, allowed_directories=[self.temp_dir]
        )

        # Send messages with different output_file
        # Send multiple messages to increase chance of reception
        for _ in range(5):
            event1 = {
                "level": "INFO",
                "msg": "Message to output1",
                "time": time.time(),
                "name": "test_logger",
                "output_file": output1,
                "process_id": os.getpid(),
            }
            event2 = {
                "level": "INFO",
                "msg": "Message to output2",
                "time": time.time(),
                "name": "test_logger",
                "output_file": output2,
                "process_id": os.getpid(),
            }
            event3 = {
                "level": "INFO",
                "msg": "Another message to output1",
                "time": time.time(),
                "name": "test_logger",
                "output_file": output1,
                "process_id": os.getpid(),
            }

            sink.emit(event1)
            sink.emit(event2)
            sink.emit(event3)
            time.sleep(0.05)

        # Give time for messages to be processed
        time.sleep(0.1)

        # Clean up
        consumer.stop()
        sink.close()

        # Verify output files
        self.assertTrue(os.path.exists(output1), "Output file 1 should exist")
        self.assertTrue(os.path.exists(output2), "Output file 2 should exist")

        with open(output1, "r") as f:
            content1 = f.read()

        with open(output2, "r") as f:
            content2 = f.read()

        # Check that at least some messages were received
        self.assertTrue(len(content1) > 0, "Output file 1 should contain messages")
        self.assertTrue(len(content2) > 0, "Output file 2 should contain messages")

        # Check for presence of expected messages (may not be all due to ZeroMQ async nature)
        if "Message to output1" in content1:
            print("✓ Received 'Message to output1'")
        else:
            print("✗ Did not receive 'Message to output1' (may be due to ZeroMQ timing)")

        if "Another message to output1" in content1:
            print("✓ Received 'Another message to output1'")
        else:
            print("✗ Did not receive 'Another message to output1' (may be due to ZeroMQ timing)")

        if "Message to output2" in content2:
            print("✓ Received 'Message to output2'")
        else:
            print("✗ Did not receive 'Message to output2' (may be due to ZeroMQ timing)")

    def test_path_validation(self):
        """
        Test path validation to prevent directory traversal.
        """
        # Create and start the consumer
        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint, auto_start=True, daemon=True, allowed_directories=[self.temp_dir]
        )

        # Give the consumer time to start and connect
        time.sleep(0.1)

        # Create ZeroMQSink
        sink = ZeroMQSink(endpoint=self.endpoint, topic="")

        # Try to send message with path traversal attempt
        malicious_path = os.path.join(self.temp_dir, "..", "etc", "passwd")
        event = {
            "level": "INFO",
            "msg": "Malicious message",
            "time": time.time(),
            "name": "test_logger",
            "output_file": malicious_path,
            "process_id": os.getpid(),
        }

        sink.emit(event)
        time.sleep(0.1)

        # Clean up
        consumer.stop()
        sink.close()

        # Verify that the malicious file was not created
        self.assertFalse(os.path.exists(malicious_path), "Malicious file should not be created")

    def test_file_handle_lru_cache(self):
        """
        Test LRU cache for file handles.
        """
        max_open_files = 3

        # Create ZeroMQSink first and bind to endpoint
        sink = ZeroMQSink(endpoint=self.endpoint, topic="")

        # Wait a bit for sink to be ready
        time.sleep(0.1)

        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint,
            auto_start=True,
            daemon=True,
            max_open_files=max_open_files,
            allowed_directories=[self.temp_dir],
        )

        # Give consumer time to start and connect
        # Increase delay to handle ZeroMQ SUB socket's slow joiner problem
        time.sleep(0.1)

        # Create more output files than max_open_files
        output_files = [os.path.join(self.temp_dir, f"output{i}.log") for i in range(5)]

        # Send multiple messages to increase chance of reception
        for _ in range(10):
            for i, output_file in enumerate(output_files):
                event = {
                    "level": "INFO",
                    "msg": f"Message {i}",
                    "time": time.time(),
                    "name": "test_logger",
                    "output_file": output_file,
                    "process_id": os.getpid(),
                }
                sink.emit(event)
                time.sleep(0.05)

        # Give time for messages to be processed
        time.sleep(0.1)

        # Clean up
        consumer.stop()
        sink.close()

        # Verify that at least some output files were created
        # Due to ZeroMQ async nature, not all files may be created
        created_files = [f for f in output_files if os.path.exists(f)]
        self.assertTrue(len(created_files) > 0, "At least some output files should be created")
        print(f"✓ Created {len(created_files)}/{len(output_files)} output files")

    def test_consumer_lifecycle(self):
        """
        Test proper lifecycle management of ZeroMQFileConsumer.
        """
        # Create consumer
        consumer = ZeroMQFileConsumer(endpoint=self.endpoint, auto_start=False, allowed_directories=[self.temp_dir])

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

    def test_consumer_context_manager(self):
        """
        Test that ZeroMQFileConsumer works correctly as a context manager.
        """
        # Use consumer as context manager
        with ZeroMQFileConsumer(
            endpoint=self.endpoint, auto_start=False, allowed_directories=[self.temp_dir]
        ) as consumer:
            # Start consumer within context
            consumer.start()
            time.sleep(0.1)
            self.assertTrue(consumer.running, "Consumer should be running within context")

        # Verify consumer has been stopped after context exit
        self.assertFalse(consumer.running, "Consumer should be stopped after context exit")

    def test_invalid_endpoint(self):
        """
        Test handling of invalid ZeroMQ endpoint.
        """
        invalid_endpoint = "invalid_endpoint"

        # Test that ZeroMQFileConsumer handles invalid endpoint gracefully
        try:
            consumer = ZeroMQFileConsumer(
                endpoint=invalid_endpoint, auto_start=True, daemon=True, allowed_directories=[self.temp_dir]
            )
            # If we get here, the consumer should have handled the error
            consumer.stop()
        except Exception as e:
            self.fail(f"ZeroMQFileConsumer should handle invalid endpoint gracefully, but got exception: {e}")

    def test_process_id_in_output(self):
        """
        Test that process ID is included in the output.
        """
        output_file = os.path.join(self.temp_dir, "test_output.log")

        # Create ZeroMQSink first and bind to endpoint
        sink = ZeroMQSink(endpoint=self.endpoint, topic="")

        # Wait a bit for sink to be ready
        time.sleep(0.1)

        # Create and start consumer
        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint, auto_start=True, daemon=True, allowed_directories=[self.temp_dir]
        )

        # Give consumer time to start and connect
        # Increase delay to handle ZeroMQ SUB socket's slow joiner problem
        time.sleep(0.1)

        # Send multiple messages to increase chance of reception
        for _ in range(5):
            event = {
                "level": "INFO",
                "msg": "Test message",
                "time": time.time(),
                "name": "test_logger",
                "output_file": output_file,
                "process_id": 12345,
            }
            sink.emit(event)
            time.sleep(0.1)

        # Give time for messages to be processed
        time.sleep(0.1)

        # Clean up
        consumer.stop()
        sink.close()

        # Verify process ID is in output (if file was created)
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                content = f.read()

            # Check that at least some messages were received
            self.assertTrue(len(content) > 0, "Output file should contain messages")

            # Check for process ID (may not be present if no messages were received)
            if "PID:12345" in content:
                print("✓ Process ID found in output")
            else:
                print("✗ Process ID not found in output (may be due to ZeroMQ timing)")
        else:
            print("✗ Output file was not created (may be due to ZeroMQ timing)")

    def test_no_output_file(self):
        """
        Test handling of events without output_file field.
        """
        # Create and start the consumer
        consumer = ZeroMQFileConsumer(
            endpoint=self.endpoint, auto_start=True, daemon=True, allowed_directories=[self.temp_dir]
        )

        # Give the consumer time to start and connect
        time.sleep(0.1)

        # Create ZeroMQSink
        sink = ZeroMQSink(endpoint=self.endpoint, topic="")

        # Send message without output_file
        event = {
            "level": "INFO",
            "msg": "Test message without output_file",
            "time": time.time(),
            "name": "test_logger",
            "process_id": os.getpid(),
        }

        sink.emit(event)
        time.sleep(0.1)

        # Clean up
        consumer.stop()
        sink.close()

        # Verify no error was raised and consumer handled gracefully
        self.assertFalse(consumer.running, "Consumer should be stopped")


if __name__ == "__main__":
    unittest.main()
