# ---------------------------------------------------------------------------
# This file is based on python_test/async_logger.py from https://github.com/wqj97/logger_optimize with modifications.
# Modifications include removing certain parts of the code and other adjustments.
# Modified by: aeeeeeep
# Modification Date: 2025-02-03
# ---------------------------------------------------------------------------

import atexit
from time import sleep
from queue import SimpleQueue
from threading import Thread, Event
from logging import FileHandler, LogRecord
from logging.handlers import QueueHandler


class AsyncFileHandler(QueueHandler):
    """
    Asynchronously handles logging by offloading log writing to a separate thread,
    reducing performance overhead caused by GIL and disk I/O bottlenecks in multi-threaded environments.
    """

    def __init__(self, file_handler: FileHandler) -> None:
        """
        Initialize the AsyncFileHandler instance with the provided FileHandler and a queue.

        Args:
            file_handler (FileHandler): The original file handler to write log records to disk.
        """

        queue = SimpleQueue()
        super().__init__(queue)
        # Use Event to control graceful shutdown
        self.shutdown_event = Event()
        # Original FileHandler
        self._file_handler = file_handler
        self._exit = False
        # Writing thread
        self._write_thread = Thread(target=self.write, daemon=True)
        self._write_thread.start()
        atexit.register(self.close)

    def close(self) -> None:
        """
        Gracefully shuts down the AsyncFileHandler by flushing and closing the queue.
        This method is called at program exit to ensure no logs are lost.
        """
        super().close()
        if self.shutdown_event.is_set():
            return

        self.shutdown_event.set()
        self._write_thread.join()

        # Flush the queue
        while True:
            try:
                record = self.queue.get_nowait()
                self._file_handler.handle(record)
            except:
                break

    def write(self):
        """
        Continuously retrieves log records from the queue and writes them to disk.
        This method runs in a separate thread to offload log writing and avoid blocking the main thread.
        """
        while not self.shutdown_event.is_set():
            try:
                record = self.queue.get_nowait()
                self._file_handler.handle(record)
            except:
                sleep(0.01)

    def handle(self, record: LogRecord) -> None:
        """
        Adds a log record to the queue for asynchronous processing.

        Args:
            record (LogRecord): The log record to be added to the queue.
        """
        self.enqueue(record)

    def enqueue(self, record: LogRecord) -> None:
        """
        Puts the log record into the queue for asynchronous writing.

        Args:
            record (LogRecord): The log record to be enqueued.
        """
        self.queue.put_nowait(record)
