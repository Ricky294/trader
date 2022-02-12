import logging

LOGGER_NAME = "trader"


def __create_logger():
    _logger = logging.getLogger(name=LOGGER_NAME)
    if not _logger.handlers:
        _logger.propagate = False
        _logger.setLevel(logging.INFO)

        formatter = logging.Formatter(fmt="%(levelname)s-%(name)s: %(message)s")

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level=logging.INFO)

        stream_handler.setFormatter(fmt=formatter)
        _logger.addHandler(stream_handler)

    return _logger


logger = __create_logger()
