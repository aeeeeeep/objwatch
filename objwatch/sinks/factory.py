# MIT License
# Copyright (c) 2025 aeeeeeep

from ..config import ObjWatchConfig
from .abc import BaseSink
from .std import StandardSink
from .zmq_sink import ZeroMQSink


def get_sink(config: ObjWatchConfig) -> BaseSink:
    """
    Factory function to create a sink based on configuration.

    Args:
        config (ObjWatchConfig): The configuration object.

    Returns:
        BaseSink: The configured sink instance.
    """
    if config.output_mode == 'zmq':
        return ZeroMQSink(endpoint=config.zmq_endpoint, topic=config.zmq_topic, output_path=config.output)
    else:
        # Default to StandardSink
        # It handles output file internally if config.output is set
        return StandardSink(output_path=config.output, level=config.level, simple=config.simple)
