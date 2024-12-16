import logging


def create_logger(name='objwatch', output=None, level=logging.DEBUG, simple=False):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        if simple:
            formatter = logging.Formatter('%(levelname)s: %(message)s')
        else:
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
            )
        logger.setLevel(level)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        if output:
            file_handler = logging.FileHandler(output)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    logger.propagate = False

    return logger


def get_logger(name='objwatch'):
    logger = logging.getLogger(name)
    return logger
