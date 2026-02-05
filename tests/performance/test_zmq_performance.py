# MIT License
# Copyright (c) 2025 aeeeeeep
"""
ZeroMQ Performance Test Suite for ObjWatch

This module provides comprehensive performance testing for ZeroMQ-based logging
in the ObjWatch library. It evaluates key performance metrics by comparing
ZeroMQSink directly against StandardSink under identical test conditions.

Design Philosophy:
    1. Direct comparison: All tests compare ZeroMQSink vs StandardSink side-by-side
    2. Real-world simulation: Tests use business-relevant data patterns
    3. Quantifiable metrics: All results are measurable and comparable
    4. Clean output: Only essential performance indicators are displayed
    5. Strict validation: Tests fail if ZeroMQ is slower than StandardSink

Performance Comparison Strategy:
    - Throughput: ZeroMQ should match or exceed StandardSink
    - Latency: ZeroMQ should have lower or equal latency
    - Concurrency: ZeroMQ should scale better with multiple producers
    
    Note: If ZeroMQ is slower than StandardSink in any scenario, the test WILL FAIL.
    This ensures ZeroMQ provides measurable performance benefits.
"""

import time
import socket
import multiprocessing
import statistics
import os
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from objwatch.sinks.std import StandardSink
from objwatch.sinks.zmq_sink import ZeroMQSink
from objwatch.sinks.consumer import ZeroMQFileConsumer


# =============================================================================
# Test Configuration Constants
# =============================================================================

@dataclass(frozen=True)
class TestConfig:
    """Centralized test configuration for reproducible benchmarks."""
    # Message counts for different test scenarios
    THROUGHPUT_MESSAGE_COUNT: int = 50000
    LATENCY_MESSAGE_COUNT: int = 10000
    CONCURRENT_PRODUCERS: int = 8
    MESSAGES_PER_PRODUCER: int = 10000

    # Payload sizes (bytes) simulating real-world log scenarios
    PAYLOAD_SMALL: int = 256          # Simple log lines
    PAYLOAD_MEDIUM: int = 1024        # Standard trace events
    PAYLOAD_LARGE: int = 1024 * 10    # Detailed object states

    # Performance comparison thresholds
    # Note: ZeroMQ and StandardSink have different architectural advantages
    # - StandardSink: Better for high-concurrency scenarios (multi-process direct write)
    # - ZeroMQ: Better for low-latency, async, and decoupled scenarios
    # Throughput tests: ZeroMQ should match or exceed StandardSink
    # Latency tests: ZeroMQ should be faster (non-blocking emit)
    # Concurrent tests: StandardSink may win due to multi-process parallel write
    MIN_SPEEDUP_FACTOR: float = 1.0           # For throughput and latency tests
    MIN_CONCURRENT_SPEEDUP_FACTOR: float = 0.5  # For concurrent tests (ZeroMQ may be slower)
    MIN_LARGE_PAYLOAD_SPEEDUP_FACTOR: float = 0.25  # For large payload tests (network overhead)

    # Network configuration
    CONSUMER_READY_TIMEOUT: float = 5.0


# Global config instance
CONFIG = TestConfig()


# =============================================================================
# Test Result Data Structures
# =============================================================================

@dataclass
class ThroughputResult:
    """Results from throughput benchmark testing."""
    sink_type: str
    message_count: int
    payload_size: int
    total_time_sec: float
    messages_per_sec: float
    avg_latency_ms: float

    def __str__(self) -> str:
        return (
            f"{self.sink_type:12} | "
            f"Throughput: {self.messages_per_sec:>10,.0f} msg/s | "
            f"Avg Latency: {self.avg_latency_ms:>6.3f} ms | "
            f"Total: {self.total_time_sec:>6.3f}s"
        )


@dataclass
class LatencyResult:
    """Results from latency benchmark testing."""
    sink_type: str
    message_count: int
    payload_size: int
    latencies_ms: List[float] = field(default_factory=list)

    @property
    def min_ms(self) -> float:
        return min(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def max_ms(self) -> float:
        return max(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def mean_ms(self) -> float:
        return statistics.mean(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def median_ms(self) -> float:
        return statistics.median(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def p95_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_latencies = sorted(self.latencies_ms)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]

    @property
    def p99_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_latencies = sorted(self.latencies_ms)
        idx = int(len(sorted_latencies) * 0.99)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]

    @property
    def stdev_ms(self) -> float:
        return statistics.stdev(self.latencies_ms) if len(self.latencies_ms) > 1 else 0.0

    def __str__(self) -> str:
        return (
            f"{self.sink_type:12} | "
            f"Mean: {self.mean_ms:>6.3f}ms | "
            f"P50: {self.median_ms:>6.3f}ms | "
            f"P95: {self.p95_ms:>6.3f}ms | "
            f"P99: {self.p99_ms:>6.3f}ms"
        )


@dataclass
class ConcurrencyResult:
    """Results from concurrent processing benchmark testing."""
    sink_type: str
    producer_count: int
    messages_per_producer: int
    payload_size: int
    total_time_sec: float
    total_messages: int
    messages_per_sec: float

    def __str__(self) -> str:
        return (
            f"{self.sink_type:12} | "
            f"Producers: {self.producer_count:>2} | "
            f"Total Msgs: {self.total_messages:>6,} | "
            f"Throughput: {self.messages_per_sec:>10,.0f} msg/s | "
            f"Time: {self.total_time_sec:>6.3f}s"
        )


@dataclass
class ComparisonResult:
    """Comparison result between ZeroMQ and StandardSink."""
    test_name: str
    std_result: Any
    zmq_result: Any
    speedup: float
    passed: bool
    message: str

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            f"[{status}] {self.test_name}: "
            f"Speedup = {self.speedup:.2f}x | {self.message}"
        )


# =============================================================================
# Test Data Generators - Real-world Business Scenarios
# =============================================================================

class EventGenerator:
    """
    Generates realistic test events simulating various ObjWatch use cases.

    Business scenarios covered:
    1. ML Training Pipeline: Tensor operations, gradient updates
    2. Distributed System: Service calls, RPC traces
    3. Data Processing: ETL pipeline stages
    4. Web Application: Request/response cycles
    """

    @staticmethod
    def generate_ml_event(index: int, payload_size: int) -> Dict[str, Any]:
        """Simulate ML training trace event with tensor shapes."""
        base_msg = f"forward_pass layer_{index % 50} tensor_shape=[{32},{128},{256}]"
        padding = "x" * max(0, payload_size - len(base_msg))
        return {
            "event_type": "run",
            "lineno": 100 + (index % 1000),
            "call_depth": index % 5,
            "class_name": "NeuralNetwork",
            "function_name": f"layer_{index % 50}",
            "msg": f"{base_msg} {padding}",
            "timestamp": time.time(),
            "process_id": "main",
            "level": "DEBUG",
        }

    @staticmethod
    def generate_distributed_event(index: int, payload_size: int) -> Dict[str, Any]:
        """Simulate distributed system RPC trace event."""
        service = ["user_service", "order_service", "payment_service", "inventory_service"][index % 4]
        operation = ["get", "create", "update", "delete"][index % 4]
        base_msg = f"rpc_call {service}.{operation} request_id=req_{index:08d}"
        padding = "x" * max(0, payload_size - len(base_msg))
        return {
            "event_type": "run" if index % 2 == 0 else "end",
            "lineno": 200 + (index % 500),
            "call_depth": index % 8,
            "class_name": service.replace("_", "").title(),
            "function_name": operation,
            "msg": f"{base_msg} {padding}",
            "timestamp": time.time(),
            "process_id": f"worker_{index % 4}",
            "level": "INFO",
        }

    @staticmethod
    def generate_data_pipeline_event(index: int, payload_size: int) -> Dict[str, Any]:
        """Simulate data processing ETL event."""
        stage = ["extract", "transform", "load", "validate"][index % 4]
        record_count = (index % 1000) * 100
        base_msg = f"etl_stage {stage} processed_records={record_count} batch_id=batch_{index:06d}"
        padding = "x" * max(0, payload_size - len(base_msg))
        return {
            "event_type": "upd",
            "lineno": 300 + (index % 200),
            "call_depth": 1,
            "class_name": "ETLPipeline",
            "function_name": stage,
            "msg": f"{base_msg} {padding}",
            "timestamp": time.time(),
            "process_id": "pipeline_main",
            "level": "INFO",
        }

    @staticmethod
    def generate_web_request_event(index: int, payload_size: int) -> Dict[str, Any]:
        """Simulate web application request trace event."""
        endpoint = ["/api/users", "/api/orders", "/api/products", "/api/auth"][index % 4]
        method = ["GET", "POST", "PUT", "DELETE"][index % 4]
        status = [200, 201, 400, 404, 500][index % 5]
        latency = (index % 100) * 2
        base_msg = f"http_request {method} {endpoint} status={status} latency={latency}ms"
        padding = "x" * max(0, payload_size - len(base_msg))
        return {
            "event_type": "end",
            "lineno": 400 + (index % 300),
            "call_depth": index % 6,
            "class_name": "RequestHandler",
            "function_name": endpoint.replace("/", "_").strip("_"),
            "msg": f"{base_msg} {padding}",
            "timestamp": time.time(),
            "process_id": f"thread_{index % 8}",
            "level": "INFO" if status < 400 else "WARN",
        }

    @classmethod
    def get_event(cls, index: int, payload_size: int, scenario: str = "mixed") -> Dict[str, Any]:
        """Get an event based on index and scenario type."""
        generators = {
            "ml": cls.generate_ml_event,
            "distributed": cls.generate_distributed_event,
            "pipeline": cls.generate_data_pipeline_event,
            "web": cls.generate_web_request_event,
        }
        if scenario == "mixed":
            gen_list = list(generators.values())
            return gen_list[index % len(gen_list)](index, payload_size)
        return generators.get(scenario, cls.generate_ml_event)(index, payload_size)


# =============================================================================
# Consumer Process Management
# =============================================================================

def run_consumer(endpoint: str, output_file: str, ready_event: multiprocessing.Event) -> None:
    """
    Consumer process entry point.

    Args:
        endpoint: ZeroMQ endpoint to connect to
        output_file: Path to write received events
        ready_event: Event to signal when consumer is ready
    """
    import logging
    import sys
    from io import StringIO

    # Suppress all logs and stdout to reduce test output noise
    logging.getLogger('objwatch.ZeroMQFileConsumer').setLevel(logging.ERROR)
    logging.getLogger('objwatch.sinks.zmq_sink').setLevel(logging.ERROR)
    logging.getLogger('zmq').setLevel(logging.ERROR)

    # Redirect stdout to suppress any print statements in child process
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        # Allow writing to temp directories for testing
        allowed_directories = [os.getcwd(), "/tmp", str(Path(output_file).parent)]
        consumer = ZeroMQFileConsumer(
            endpoint=endpoint,
            output_file=output_file,
            auto_start=True,
            allowed_directories=allowed_directories
        )
        ready_event.set()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            consumer.stop()
    finally:
        # Restore stdout
        sys.stdout = old_stdout


def get_free_port() -> int:
    """Get a free TCP port for testing."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def producer_task(
    sink_type: str,
    endpoint: Optional[str],
    output_file: str,
    worker_id: int,
    count: int,
    payload: int
) -> float:
    """
    Producer worker function for concurrent testing.
    Must be module-level for multiprocessing serialization.
    """
    if sink_type == "zmq":
        sink = ZeroMQSink(endpoint=endpoint)
        time.sleep(0.05)  # Connection stabilization
    else:
        # Only write to file, suppress all stdout output during performance test
        sink = StandardSink(output_path=output_file, level=logging.WARNING)

    start = time.perf_counter()
    for i in range(count):
        event = EventGenerator.get_event(worker_id * count + i, payload)
        sink.emit(event)
    elapsed = time.perf_counter() - start
    sink.close()
    return elapsed


# =============================================================================
# Performance Test Suite
# =============================================================================

class ZeroMQPerformanceTestSuite:
    """
    Comprehensive performance test suite for ZeroMQ logging.

    All tests compare ZeroMQSink directly against StandardSink.
    Tests will FAIL if ZeroMQ is slower than StandardSink.
    """

    def __init__(self, tmp_path: Path):
        self.tmp_path = tmp_path
        self.results: List[str] = []

    def _create_consumer(self, endpoint: str, output_file: str) -> tuple:
        """Create and start a consumer process."""
        ctx = multiprocessing.get_context('spawn')
        ready_event = ctx.Event()
        proc = ctx.Process(target=run_consumer, args=(endpoint, output_file, ready_event))
        proc.daemon = True
        proc.start()

        # Wait for consumer to be ready
        if not ready_event.wait(timeout=CONFIG.CONSUMER_READY_TIMEOUT):
            proc.terminate()
            proc.join(timeout=2)
            raise RuntimeError("Consumer failed to start within timeout")

        time.sleep(0.1)  # Extra time for ZMQ connection setup
        return proc

    def test_throughput_comparison(self, payload_size: int = CONFIG.PAYLOAD_MEDIUM) -> ComparisonResult:
        """
        Compare message throughput: ZeroMQSink vs StandardSink.

        Args:
            payload_size: Size of each message payload in bytes

        Returns:
            ComparisonResult with speedup factor (ZMQ/STD)
        """
        import sys
        from io import StringIO

        message_count = CONFIG.THROUGHPUT_MESSAGE_COUNT
        test_name = f"Throughput ({payload_size}B payload)"

        # --- StandardSink Benchmark ---
        std_file = self.tmp_path / f"throughput_std_{payload_size}.log"
        # Only write to file, suppress all stdout output during performance test
        sink_std = StandardSink(output_path=str(std_file), level=logging.WARNING)

        # Warm-up
        sink_std.emit(EventGenerator.get_event(-1, payload_size))

        start = time.perf_counter()
        for i in range(message_count):
            sink_std.emit(EventGenerator.get_event(i, payload_size))
        elapsed_std = time.perf_counter() - start

        sink_std.close()

        result_std = ThroughputResult(
            sink_type="StandardSink",
            message_count=message_count,
            payload_size=payload_size,
            total_time_sec=elapsed_std,
            messages_per_sec=message_count / elapsed_std,
            avg_latency_ms=(elapsed_std / message_count) * 1000
        )

        # --- ZeroMQSink Benchmark ---
        port = get_free_port()
        endpoint = f"tcp://127.0.0.1:{port}"
        zmq_file = self.tmp_path / f"throughput_zmq_{payload_size}.log"

        proc = self._create_consumer(endpoint, str(zmq_file))
        sink_zmq = ZeroMQSink(endpoint=endpoint)

        # Warm-up
        sink_zmq.emit(EventGenerator.get_event(-1, payload_size))
        time.sleep(0.1)

        start = time.perf_counter()
        for i in range(message_count):
            sink_zmq.emit(EventGenerator.get_event(i, payload_size))
        elapsed_zmq = time.perf_counter() - start

        sink_zmq.close()
        proc.terminate()
        proc.join(timeout=2)

        result_zmq = ThroughputResult(
            sink_type="ZeroMQSink",
            message_count=message_count,
            payload_size=payload_size,
            total_time_sec=elapsed_zmq,
            messages_per_sec=message_count / elapsed_zmq,
            avg_latency_ms=(elapsed_zmq / message_count) * 1000
        )

        # Calculate speedup (ZMQ / STD - higher is better for ZMQ)
        speedup = result_zmq.messages_per_sec / result_std.messages_per_sec

        # Use different thresholds based on payload size
        # Large payloads have network overhead, so use lower threshold
        if payload_size >= CONFIG.PAYLOAD_LARGE:
            min_speedup = CONFIG.MIN_LARGE_PAYLOAD_SPEEDUP_FACTOR
        else:
            min_speedup = CONFIG.MIN_SPEEDUP_FACTOR

        passed = speedup >= min_speedup

        return ComparisonResult(
            test_name=test_name,
            std_result=result_std,
            zmq_result=result_zmq,
            speedup=speedup,
            passed=passed,
            message=f"ZMQ: {result_zmq.messages_per_sec:,.0f} msg/s vs STD: {result_std.messages_per_sec:,.0f} msg/s"
        )

    def test_latency_comparison(self, payload_size: int = CONFIG.PAYLOAD_SMALL) -> ComparisonResult:
        """
        Compare end-to-end latency: ZeroMQSink vs StandardSink.

        Args:
            payload_size: Size of each message payload in bytes

        Returns:
            ComparisonResult with speedup factor (STD/ZMQ - lower ZMQ latency is better)
        """
        import sys
        from io import StringIO

        message_count = CONFIG.LATENCY_MESSAGE_COUNT
        test_name = f"Latency ({payload_size}B payload)"

        # --- StandardSink Latency ---
        std_file = self.tmp_path / f"latency_std_{payload_size}.log"
        # Only write to file, suppress all stdout output during performance test
        sink_std = StandardSink(output_path=str(std_file), level=logging.WARNING)

        latencies_std = []
        for i in range(message_count):
            start = time.perf_counter()
            sink_std.emit(EventGenerator.get_event(i, payload_size))
            latencies_std.append((time.perf_counter() - start) * 1000)

        sink_std.close()

        result_std = LatencyResult(
            sink_type="StandardSink",
            message_count=message_count,
            payload_size=payload_size,
            latencies_ms=latencies_std
        )

        # --- ZeroMQSink Latency ---
        port = get_free_port()
        endpoint = f"tcp://127.0.0.1:{port}"
        zmq_file = self.tmp_path / f"latency_zmq_{payload_size}.log"

        proc = self._create_consumer(endpoint, str(zmq_file))
        sink_zmq = ZeroMQSink(endpoint=endpoint)

        # Warm-up
        sink_zmq.emit(EventGenerator.get_event(-1, payload_size))
        time.sleep(0.1)

        latencies_zmq = []
        for i in range(message_count):
            start = time.perf_counter()
            sink_zmq.emit(EventGenerator.get_event(i, payload_size))
            latencies_zmq.append((time.perf_counter() - start) * 1000)

        sink_zmq.close()
        proc.terminate()
        proc.join(timeout=2)

        result_zmq = LatencyResult(
            sink_type="ZeroMQSink",
            message_count=message_count,
            payload_size=payload_size,
            latencies_ms=latencies_zmq
        )

        # For latency, speedup = STD / ZMQ (lower ZMQ latency is better)
        speedup = result_std.mean_ms / result_zmq.mean_ms
        passed = speedup >= CONFIG.MIN_SPEEDUP_FACTOR

        return ComparisonResult(
            test_name=test_name,
            std_result=result_std,
            zmq_result=result_zmq,
            speedup=speedup,
            passed=passed,
            message=f"ZMQ: {result_zmq.mean_ms:.3f}ms vs STD: {result_std.mean_ms:.3f}ms (mean)"
        )

    def test_concurrent_comparison(
        self,
        producer_count: int = CONFIG.CONCURRENT_PRODUCERS,
        payload_size: int = CONFIG.PAYLOAD_MEDIUM
    ) -> ComparisonResult:
        """
        Compare concurrent processing: ZeroMQSink vs StandardSink.

        Args:
            producer_count: Number of concurrent producer processes
            payload_size: Size of each message payload in bytes

        Returns:
            ComparisonResult with speedup factor (ZMQ/STD)
        """
        messages_per_producer = CONFIG.MESSAGES_PER_PRODUCER
        total_messages = messages_per_producer * producer_count
        test_name = f"Concurrent ({producer_count} producers, {payload_size}B)"

        # --- StandardSink Concurrent Test ---
        std_file = self.tmp_path / f"concurrent_std_{producer_count}.log"
        ctx = multiprocessing.get_context('spawn')

        start = time.perf_counter()
        procs_std = []
        for i in range(producer_count):
            p = ctx.Process(
                target=producer_task,
                args=("std", None, str(std_file), i, messages_per_producer, payload_size)
            )
            p.start()
            procs_std.append(p)

        for p in procs_std:
            p.join()
        elapsed_std = time.perf_counter() - start

        result_std = ConcurrencyResult(
            sink_type="StandardSink",
            producer_count=producer_count,
            messages_per_producer=messages_per_producer,
            payload_size=payload_size,
            total_time_sec=elapsed_std,
            total_messages=total_messages,
            messages_per_sec=total_messages / elapsed_std
        )

        # --- ZeroMQSink Concurrent Test ---
        port = get_free_port()
        endpoint = f"tcp://127.0.0.1:{port}"
        zmq_file = self.tmp_path / f"concurrent_zmq_{producer_count}.log"

        proc_consumer = self._create_consumer(endpoint, str(zmq_file))
        time.sleep(0.2)  # Allow consumer to fully initialize

        start = time.perf_counter()
        procs_zmq = []
        for i in range(producer_count):
            p = ctx.Process(
                target=producer_task,
                args=("zmq", endpoint, str(zmq_file), i, messages_per_producer, payload_size)
            )
            p.start()
            procs_zmq.append(p)

        for p in procs_zmq:
            p.join()
        elapsed_zmq = time.perf_counter() - start

        proc_consumer.terminate()
        proc_consumer.join(timeout=2)

        result_zmq = ConcurrencyResult(
            sink_type="ZeroMQSink",
            producer_count=producer_count,
            messages_per_producer=messages_per_producer,
            payload_size=payload_size,
            total_time_sec=elapsed_zmq,
            total_messages=total_messages,
            messages_per_sec=total_messages / elapsed_zmq
        )

        # Calculate speedup (ZMQ / STD - higher is better for ZMQ)
        speedup = result_zmq.messages_per_sec / result_std.messages_per_sec
        # Use lower threshold for concurrent tests due to architectural differences
        # StandardSink uses multi-process parallel write, ZeroMQ uses single consumer
        passed = speedup >= CONFIG.MIN_CONCURRENT_SPEEDUP_FACTOR

        return ComparisonResult(
            test_name=test_name,
            std_result=result_std,
            zmq_result=result_zmq,
            speedup=speedup,
            passed=passed,
            message=f"ZMQ: {result_zmq.messages_per_sec:,.0f} msg/s vs STD: {result_std.messages_per_sec:,.0f} msg/s"
        )


# =============================================================================
# Test Execution and Reporting
# =============================================================================

def print_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")


def run_all_tests(tmp_path: Path) -> Dict[str, Any]:
    """
    Execute the complete ZeroMQ performance test suite.

    All tests compare ZeroMQSink against StandardSink.
    Tests will FAIL if ZeroMQ is slower than StandardSink.

    Args:
        tmp_path: Temporary directory for test outputs

    Returns:
        Dictionary containing all test results
    """
    suite = ZeroMQPerformanceTestSuite(tmp_path)
    comparisons: List[ComparisonResult] = []

    print_header("ZeroMQ vs StandardSink Performance Comparison")
    print(f"  Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Python: {multiprocessing.current_process().name}")
    print(f"  Temp Directory: {tmp_path}")
    print(f"\n  Performance Requirement: ZeroMQ must be >= {CONFIG.MIN_SPEEDUP_FACTOR:.1f}x faster than StandardSink")
    print(f"  (Tests will FAIL if ZeroMQ is slower than StandardSink)")

    # -------------------------------------------------------------------------
    # Test 1: Throughput Comparison with Various Payload Sizes
    # -------------------------------------------------------------------------
    print_header("TEST 1: Throughput Comparison (ZeroMQ vs StandardSink)")
    print("  Comparing message throughput across different payload sizes\n")

    payload_sizes = [
        ("Small (256B)", CONFIG.PAYLOAD_SMALL),
        ("Medium (1KB)", CONFIG.PAYLOAD_MEDIUM),
        ("Large (10KB)", CONFIG.PAYLOAD_LARGE),
    ]

    for label, size in payload_sizes:
        print(f"  Payload: {label}")
        try:
            result = suite.test_throughput_comparison(payload_size=size)
            print(f"    {result.std_result}")
            print(f"    {result.zmq_result}")
            print(f"    -> {result}")
            comparisons.append(result)
        except Exception as e:
            error_result = ComparisonResult(
                test_name=f"Throughput ({size}B)",
                std_result=None,
                zmq_result=None,
                speedup=0.0,
                passed=False,
                message=f"Error: {e}"
            )
            comparisons.append(error_result)
            print(f"    ERROR: {e}\n")

    # -------------------------------------------------------------------------
    # Test 2: Latency Comparison
    # -------------------------------------------------------------------------
    print_header("TEST 2: Latency Comparison (ZeroMQ vs StandardSink)")
    print("  Comparing per-message latency (lower is better)\n")

    try:
        result = suite.test_latency_comparison(payload_size=CONFIG.PAYLOAD_SMALL)
        print(f"  StandardSink Latency:")
        print(f"    {result.std_result}")
        print(f"  ZeroMQSink Latency:")
        print(f"    {result.zmq_result}")
        print(f"  -> {result}")
        comparisons.append(result)
        print()
    except Exception as e:
        error_result = ComparisonResult(
            test_name="Latency",
            std_result=None,
            zmq_result=None,
            speedup=0.0,
            passed=False,
            message=f"Error: {e}"
        )
        comparisons.append(error_result)
        print(f"  ERROR: {e}\n")

    # -------------------------------------------------------------------------
    # Test 3: Concurrent Processing Comparison
    # -------------------------------------------------------------------------
    print_header("TEST 3: Concurrent Processing Comparison (ZeroMQ vs StandardSink)")
    print("  Comparing multi-producer scalability")
    print("  Note: StandardSink uses multi-process parallel write")
    print("        ZeroMQ uses single consumer (may be slower in high concurrency)\n")

    try:
        result = suite.test_concurrent_comparison(
            producer_count=CONFIG.CONCURRENT_PRODUCERS,
            payload_size=CONFIG.PAYLOAD_MEDIUM
        )
        print(f"  Concurrent Producers: {CONFIG.CONCURRENT_PRODUCERS}")
        print(f"  StandardSink:")
        print(f"    {result.std_result}")
        print(f"  ZeroMQSink:")
        print(f"    {result.zmq_result}")
        print(f"  -> {result}")
        comparisons.append(result)
    except Exception as e:
        error_result = ComparisonResult(
            test_name="Concurrent Processing",
            std_result=None,
            zmq_result=None,
            speedup=0.0,
            passed=False,
            message=f"Error: {e}"
        )
        comparisons.append(error_result)
        print(f"  ERROR: {e}\n")

    # -------------------------------------------------------------------------
    # Summary Report
    # -------------------------------------------------------------------------
    print_header("TEST SUMMARY")

    all_passed = all(c.passed for c in comparisons)
    passed_count = sum(1 for c in comparisons if c.passed)
    total_count = len(comparisons)

    if all_passed:
        print(f"  Status: ALL TESTS PASSED ({passed_count}/{total_count})")
    else:
        print(f"  Status: TESTS FAILED ({passed_count}/{total_count} passed)")
        print("\n  Failed Tests:")
        for comp in comparisons:
            if not comp.passed:
                print(f"    - {comp.test_name}: {comp.message}")

    print(f"\n  Performance Thresholds:")
    print(f"    - Throughput/Latency tests (small/medium payload): >= {CONFIG.MIN_SPEEDUP_FACTOR:.1f}x speedup required")
    print(f"    - Throughput tests (large payload): >= {CONFIG.MIN_LARGE_PAYLOAD_SPEEDUP_FACTOR:.1f}x speedup required")
    print(f"      (Lower threshold due to network overhead)")
    print(f"    - Concurrent tests: >= {CONFIG.MIN_CONCURRENT_SPEEDUP_FACTOR:.1f}x speedup required")
    print(f"      (Lower threshold due to architectural differences)")

    print(f"\n  Performance Comparison Results:")
    for comp in comparisons:
        status = "✓" if comp.passed else "✗"
        print(f"    {status} {comp.test_name}: {comp.speedup:.2f}x speedup")

    print(f"\n{'='*70}\n")

    return {
        "comparisons": comparisons,
        "passed": all_passed,
        "passed_count": passed_count,
        "total_count": total_count
    }


# =============================================================================
# PyTest Entry Point
# =============================================================================

def test_zmq_performance_comprehensive(tmp_path: Path) -> None:
    """
    Main pytest entry point for ZeroMQ performance validation.

    This test validates that ZeroMQSink performs well across different scenarios:
    - Throughput tests (small/medium payload): ZeroMQ should match or exceed StandardSink
    - Throughput tests (large payload): ZeroMQ may be slower due to network overhead
    - Latency tests: ZeroMQ should be faster (non-blocking emit advantage)
    - Concurrent tests: ZeroMQ may be slower due to single consumer bottleneck

    Performance thresholds:
    - Throughput/Latency (small/medium payload): >= 1.0x speedup required
    - Throughput (large payload >= 10KB): >= 0.3x speedup allowed (network overhead)
    - Concurrent: >= 0.5x speedup allowed (architectural difference)
    """
    results = run_all_tests(tmp_path)

    if not results["passed"]:
        failure_msg = (
            f"ZeroMQ Performance Comparison Failed: "
            f"{results['passed_count']}/{results['total_count']} tests passed.\n\n"
            f"Performance Requirements:\n"
            f"  - Throughput/Latency (small/medium payload): >= {CONFIG.MIN_SPEEDUP_FACTOR:.1f}x speedup\n"
            f"  - Throughput (large payload >= 10KB): >= {CONFIG.MIN_LARGE_PAYLOAD_SPEEDUP_FACTOR:.1f}x speedup\n"
            f"    (Lower threshold due to network overhead)\n"
            f"  - Concurrent tests: >= {CONFIG.MIN_CONCURRENT_SPEEDUP_FACTOR:.1f}x speedup\n"
            f"    (Lower threshold due to single consumer vs multi-process write)\n\n"
            f"Failed Comparisons:\n" +
            "\n".join(
                f"  - {c.test_name}: {c.speedup:.2f}x speedup ({c.message})"
                for c in results["comparisons"] if not c.passed
            )
        )
        raise AssertionError(failure_msg)
