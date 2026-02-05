#!/usr/bin/env python3
# MIT License
# Copyright (c) 2025 aeeeeeep

"""
ZeroMQ File Consumer Tool

This script demonstrates how to use the ZeroMQFileConsumer class to receive
log events from ZeroMQSink and write them to a local file.

It can be run as an independent process on a different machine to collect
logs from an objwatch instance running in ZeroMQ mode.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from objwatch.sinks.consumer import ZeroMQFileConsumer


def setup_logging():
    """
    Setup logging for the tool.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    """
    Main function to parse arguments and start the consumer.
    """
    setup_logging()
    logger = logging.getLogger('zmq_consumer_tool')

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='ZeroMQ File Consumer Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example usage:\n  python zmq_consumer_tool.py --endpoint tcp://127.0.0.1:5555 --output zmq_logs.log --topic objwatch',
    )

    parser.add_argument(
        '--endpoint',
        type=str,
        default='tcp://127.0.0.1:5555',
        help='ZeroMQ endpoint to connect to (default: tcp://127.0.0.1:5555)',
    )

    parser.add_argument('--topic', type=str, default='', help='Topic to subscribe to (default: all topics)')

    parser.add_argument('--output', type=str, default='zmq_logs.log', help='Output file path (default: zmq_logs.log)')

    parser.add_argument(
        '--no-daemon',
        action='store_false',
        dest='daemon',
        default=True,
        help='Do not run the consumer in a daemon thread',
    )

    parser.add_argument(
        '--no-auto-start',
        action='store_false',
        dest='auto_start',
        default=True,
        help='Do not automatically start the consumer',
    )

    args = parser.parse_args()

    logger.info(f"Starting ZeroMQ File Consumer with configuration:")
    logger.info(f"  Endpoint: {args.endpoint}")
    logger.info(f"  Topic: {args.topic if args.topic else 'all topics'}")
    logger.info(f"  Output file: {args.output}")
    logger.info(f"  Auto start: {args.auto_start}")
    logger.info(f"  Daemon thread: {args.daemon}")

    try:
        # Create and start the consumer
        consumer = ZeroMQFileConsumer(
            endpoint=args.endpoint,
            topic=args.topic,
            output_file=args.output,
            auto_start=args.auto_start,
            daemon=args.daemon,
        )

        if not args.auto_start:
            consumer.start(daemon=args.daemon)

        logger.info("ZeroMQ File Consumer started successfully")
        logger.info("Press Ctrl+C to stop...")

        # Keep the main thread running
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Received Ctrl+C, stopping consumer...")
            consumer.stop()
            logger.info("Consumer stopped")

    except Exception as e:
        logger.error(f"Error running consumer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import time

    main()
