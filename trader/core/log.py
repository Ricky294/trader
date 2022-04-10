import logging
import os
from datetime import datetime

from trader.core.util.common import singleton


def create_logger(
        name: str,
        fmt="%(levelname)s-%(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
        file_path: str = None,
):
    """
    Creates a new logger with a StreamHandler and a FileHandler if `file_path` is not None.

    If logger with `name` already exits returns existing logger.

    :param name: Logger name.
    :param fmt: Log message format.
    :param datefmt: Log message date format.
    :param level: Minimum logging level.
    :param file_path: If not None, creates a file and logs messages to `file_path`.
    :return: Logger object
    """

    logger = logging.getLogger(name=name)
    if not logger.handlers:
        logger.propagate = False
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt=fmt,
            datefmt=datefmt,
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level=level)

        stream_handler.setFormatter(fmt=formatter)
        logger.addHandler(stream_handler)

        if file_path is not None:
            directory = "logs/live"
            if not os.path.exists(directory):
                os.makedirs(directory)

            create_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            file_handler = logging.FileHandler(filename=f"{directory}/{create_time}.logs")
            file_handler.setLevel(level=logging.INFO)
            file_handler.setFormatter(fmt=formatter)
            logger.addHandler(file_handler)

    return logger


@singleton
def get_core_logger():
    return create_logger("trader.core")


@singleton
def get_exception_logger():
    return create_logger("trader.exception", file_path="logs/exceptions")
