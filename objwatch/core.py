from .tracer import Tracer
from .logger import get_logger

logger = get_logger()


class ObjWatch:
    def __init__(self, targets, ranks=None):
        self.tracer = Tracer(targets, ranks=ranks)

    def start(self):
        logger.info("Starting ObjWatch tracing.")
        self.tracer.start()

    def stop(self):
        logger.info("Stopping ObjWatch tracing.")
        self.tracer.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def watch(targets, ranks=None):
    obj_watch = ObjWatch(targets, ranks=ranks)
    obj_watch.start()
    return obj_watch
