import logging


CORE_LOGGER = "trader.core"

logger = logging.getLogger(name=CORE_LOGGER)
if not logger.handlers:
    logger.propagate = False
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt="%(levelname)s-%(name)s: %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level=logging.INFO)

    stream_handler.setFormatter(fmt=formatter)
    logger.addHandler(stream_handler)
