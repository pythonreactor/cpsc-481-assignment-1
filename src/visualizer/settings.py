import logging

LOG_STREAM_HANDLER = logging.StreamHandler()
LOG_STREAM_FORMATTER = logging.Formatter('%(asctime)s::%(levelname)s::%(name)s - %(message)s')

LOG_STREAM_HANDLER.setLevel(logging.DEBUG)
LOG_STREAM_HANDLER.setFormatter(LOG_STREAM_FORMATTER)


def getLogger(name: str = None):
    """
    Custom method to retrieve a logger instance with a given name
    and set the necessary configurations.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        logger.addHandler(LOG_STREAM_HANDLER)

    return logger


MAIN_EXIT_CHAR = 'q'
