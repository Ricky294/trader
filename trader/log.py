import logging
import types

from trader.core.const import BrokerEvent
from trader.settings import Settings

from util.format_util import concat_params
from util.log import get_logger


def __update(self, event: BrokerEvent, *args, **kwargs):
    self.info(f'{event.text()}: {concat_params(*args, **kwargs)}')


def core():
    """
    Returns core logger.

    * Name: 'trader.core'
    * Console log: Yes
    * File log: No
    """
    logger = None

    def wrapper() -> logging.Logger:
        nonlocal logger

        if logger is None:
            logger = get_logger(
                'trader.core',
                level=logging.INFO,
            )
        return logger

    return wrapper


def backtest():
    """
    Returns backtest logger.

    * Name: 'trader.backtest'
    * Console log: Yes
    * File log: No
    """
    logger = None

    def wrapper() -> logging.Logger:
        nonlocal logger

        if logger is None:
            logger = get_logger(
                'trader.backtest',
                level=Settings.backtest_log_level,
            )

            logger.update = types.MethodType(__update, logger)
        return logger

    return wrapper


def binance():
    """
    Returns binance logger.

    * Name: 'trader.binance'
    * Console log: Yes
    * File log: Defined in Settings class.
    """
    logger = None

    def wrapper() -> logging.Logger:
        nonlocal logger

        if logger is None:
            logger = get_logger(
                'trader.binance',
                level=Settings.live_log_level,
                file_path=Settings.live_file_log_path,
                fmt='%(asctime)s-%(levelname)s-%(name)s: %(message)s',
            )
            logger.update = types.MethodType(__update, logger)
        return logger

    return wrapper


core = core()
backtest = backtest()
binance = binance()
