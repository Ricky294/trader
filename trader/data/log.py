import logging


def create_logger(
        name: str,
        fmt="%(levelname)s-%(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
):
    """
    Creates a new logger with a StreamHandler and a FileHandler if `file_path` is not None.

    If logger with `name` already exits returns existing logger.

    :param name: Logger name.
    :param fmt: Log message format.
    :param datefmt: Log message date format.
    :param level: Minimum logging level.
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

    return logger


TRADER_DATA_LOGGER = create_logger("data")

