import logging
from .tracer import Tracer
from .utils.logger import create_logger, log_info


class ObjWatch:
    def __init__(
        self, targets, ranks=None, output=None, level=logging.DEBUG, simple=False, wrapper=None, with_locals=False
    ):
        create_logger(output=output, level=level, simple=simple)
        self.tracer = Tracer(targets, ranks=ranks, wrapper=wrapper, with_locals=with_locals)

    def start(self):
        log_info("Starting ObjWatch tracing.")
        self.tracer.start()

    def stop(self):
        log_info("Stopping ObjWatch tracing.")
        self.tracer.stop()

    def load_wrapper(self, wrapper):
        return self.tracer.load_wrapper(wrapper)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def watch(targets, ranks=None, output=None, level=logging.DEBUG, simple=False, wrapper=None, with_locals=False):
    obj_watch = ObjWatch(
        targets, ranks=ranks, output=output, level=level, simple=simple, wrapper=wrapper, with_locals=with_locals
    )
    obj_watch.start()
    return obj_watch
