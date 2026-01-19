# MIT License
# Copyright (c) 2025 aeeeeeep

import os
import sys
import time
from objwatch import ObjWatch
from objwatch.config import ObjWatchConfig


def test_zmq_integration():
    """
    Test the integration between ZeroMQSink and ZeroMQFileConsumer.
    """
    # Configuration
    endpoint = "tcp://127.0.0.1:5555"
    topic = "test_topic"
    output = "test_zmq_output.log"

    # Clean up previous test file if it exists
    if os.path.exists(output):
        os.remove(output)

    print("=== ZeroMQ Integration Test ===")
    print(f"Endpoint: {endpoint}")
    print(f"Topic: {topic}")
    print(f"Consumer Output: {output}")
    print("-" * 50)

    try:
        # Create and start an ObjWatch instance with ZeroMQ sink and auto-started consumer
        config = ObjWatchConfig(
            targets=["sys"],
            output_mode="zmq",
            zmq_endpoint=endpoint,
            zmq_topic=topic,
            auto_start_consumer=True,
            output=output,
            level="INFO",
            simple=True,
        )

        print("Starting ObjWatch with ZeroMQSink and auto-started ZeroMQFileConsumer...")
        obj_watch = ObjWatch(**config.__dict__)
        obj_watch.start()

        # Give some time for connections to establish
        time.sleep(0.1)

        # Generate some log messages
        print("Generating log messages...")
        import logging

        logger = logging.getLogger("objwatch")

        for i in range(5):
            logger.info(f"Test message {i}")
            time.sleep(0.1)

        # Give some time for messages to be processed
        time.sleep(0.1)

        # Stop the ObjWatch instance
        print("Stopping ObjWatch...")
        obj_watch.stop()

        # Verify the output file was created and contains messages
        print("Verifying output file...")
        if os.path.exists(output):
            with open(output, 'r') as f:
                content = f.read()

            newline = '\n'
            print(f"Output file contains {content.count(newline)} lines")
            print("First 3 lines:")
            for line in content.split('\n')[:3]:
                if line:
                    print(f"  {line}")

            # Check if test messages are present
            test_messages_found = sum(1 for i in range(5) if f"Test message {i}" in content)
            print(f"Found {test_messages_found}/5 test messages in the output file")
            if test_messages_found > 0:
                print("Test PASSED: ZeroMQ integration works correctly!")
                assert True  # For pytest
            else:
                print("Test FAILED: No test messages found in the output file")
                assert False  # For pytest
        else:
            print(f"Test FAILED: Output file {output} was not created")
            assert False  # For pytest

    except Exception as e:
        print(f"Test FAILED with exception: {e}")
        import traceback

        traceback.print_exc()
        assert False  # For pytest

    finally:
        # Clean up
        if os.path.exists(output):
            os.remove(output)


if __name__ == "__main__":
    success = test_zmq_integration()
    sys.exit(0 if success else 1)
