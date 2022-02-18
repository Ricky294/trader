import logging
import os
from datetime import datetime


LIVE_LOGGER = "trader.live"

logger = logging.getLogger(name=LIVE_LOGGER)
if not logger.handlers:
    logger.propagate = False
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(levelname)s-%(name)s-%(asctime)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level=logging.INFO)
    stream_handler.setFormatter(fmt=formatter)
    logger.addHandler(stream_handler)

    if not os.path.exists("logs/live"):
        os.makedirs("logs/live")

    create_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    file_handler = logging.FileHandler(filename=f"logs/live/{create_time}.log")
    file_handler.setLevel(level=logging.INFO)
    file_handler.setFormatter(fmt=formatter)
    logger.addHandler(file_handler)
