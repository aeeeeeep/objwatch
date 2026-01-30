# MIT License
# Copyright (c) 2025 aeeeeeep

import time
import socket
import multiprocessing

from objwatch.sinks.std import StandardSink
from objwatch.sinks.zmq_sink import ZeroMQSink
from objwatch.sinks.consumer import ZeroMQFileConsumer


# Define consumer process logic
def run_consumer(endpoint, fpath):
    consumer = ZeroMQFileConsumer(endpoint=endpoint, output_file=str(fpath), auto_start=True)
    # Keep alive loop
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.stop()


def test_perf_zmq_vs_standard_io_bound(tmp_path):
    """
    Performance guardrail: Asserts ZeroMQSink is at least 4x faster than StandardSink
    in IO-heavy scenarios (blocking Main Thread Latency).
    """
    # Configuration
    MIN_SPEEDUP_FACTOR = 4.0
    N_EVENTS = 2000
    PAYLOAD_SIZE = 1024 * 1024  # 1MB

    # Generate a static large payload to avoid CPU overhead skewing results during loop
    # We want to measure Transport/IO cost, not String creation cost.
    LARGE_PAYLOAD = "x" * PAYLOAD_SIZE

    def get_event(i):
        return {
            "level": "INFO",
            "msg": f"Msg {i} payload: {LARGE_PAYLOAD}",
            "time": time.time(),
            "name": "perf_test",
        }

    # Baseline: StandardSink (Synchronous File IO)
    print("\n[Baseline] Testing StandardSink...")
    baseline_file = tmp_path / "baseline.log"

    sink_std = StandardSink(output=str(baseline_file), level="INFO")

    # Pre-warm (exclude from timing)
    sink_std.emit(get_event(-1))

    start_t = time.perf_counter()  # Use high-precision timer
    try:
        for i in range(N_EVENTS):
            sink_std.emit(get_event(i))
            # CRITICAL: Force flush to simulate true IO blocking,
            # otherwise we are just benchmarking OS PageCache RAM write speed.
            # Assuming StandardSink has a flush method or accessing the handler.
            # # If not available, the shear size of 100MB data helps, but explicit flush is better.
            # if hasattr(sink_std, 'flush'):
            #     sink_std.flush()
            # elif hasattr(sink_std, 'handler') and hasattr(sink_std.handler, 'flush'):
            #     sink_std.handler.flush()
    finally:
        end_t = time.perf_counter()
        sink_std.close()

    t_std = end_t - start_t
    avg_std = (t_std / N_EVENTS) * 1000  # ms
    print(f"StandardSink: Total={t_std:.4f}s | Avg={avg_std:.3f}ms/op")

    # Target: ZeroMQSink (Asynchronous / Offloaded IO)
    print("[Target] Testing ZeroMQSink...")
    target_file = tmp_path / "target.log"

    # Bind to random port
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    zmq_endpoint = f"tcp://127.0.0.1:{port}"

    ctx = multiprocessing.get_context('spawn')
    p_consumer = ctx.Process(target=run_consumer, args=(zmq_endpoint, target_file))
    p_consumer.daemon = True
    p_consumer.start()

    sink_zmq = None
    try:
        # Give consumer time to bind
        time.sleep(1.0)

        sink_zmq = ZeroMQSink(endpoint=zmq_endpoint)

        # Warm-up (ZMQ slow joiner mitigation)
        sink_zmq.emit(get_event(-1))
        time.sleep(0.2)

        start_t = time.perf_counter()
        for i in range(N_EVENTS):
            sink_zmq.emit(get_event(i))
            # No flush here - that's the point of ZMQ!
        end_t = time.perf_counter()

        t_zmq = end_t - start_t
        avg_zmq = (t_zmq / N_EVENTS) * 1000  # ms
        print(f"ZeroMQSink:   Total={t_zmq:.4f}s | Avg={avg_zmq:.3f}ms/op")

    finally:
        if sink_zmq:
            sink_zmq.close()
        if p_consumer.is_alive():
            p_consumer.terminate()
            p_consumer.join(timeout=2)

    # Assertion
    speedup = t_std / t_zmq
    print(f"\n>>> Speedup Factor: {speedup:.2f}x (Threshold: {MIN_SPEEDUP_FACTOR}x)")

    assert speedup >= MIN_SPEEDUP_FACTOR, (
        f"Performance Regression! ZMQ is only {speedup:.2f}x faster than Standard IO "
        f"(Expected >{MIN_SPEEDUP_FACTOR}x).\n"
        f"Std Avg: {avg_std:.3f}ms | ZMQ Avg: {avg_zmq:.3f}ms"
    )
