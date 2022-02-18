from abc import ABC, abstractmethod
from logging import getLogger
from typing import Union, Iterable, Optional

import numpy as np
import pandas as pd

from crypto_data.binance.pd.extract import get_candles
from crypto_data.binance.schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, VOLUME, CLOSE_PRICE
from crypto_data.enum.market import Market
from crypto_data.shared.candle_db import CandleDB

from trader.core.exception import TraderException
from trader.core.model import Candles
from trader.core.strategy import Strategy, LIVE_STRATEGY_LOGGER, BACKTEST_STRATEGY_LOGGER


class TradingBot(ABC):

    def __init__(self):
        self.candles = Candles()
        self.strategy: Optional[Strategy] = None

    def add_strategy(self, strategy: Strategy):
        self.strategy = strategy

    def __setup_logger(self, enable_logging: bool):
        from trader.backtest.futures_trader import BacktestFuturesTrader
        if isinstance(self.strategy.trader, BacktestFuturesTrader):
            self.strategy.logger = getLogger(BACKTEST_STRATEGY_LOGGER)
        else:
            self.strategy.logger = getLogger(LIVE_STRATEGY_LOGGER)

        self.strategy.logger.disabled = not enable_logging
        self.strategy.logger.propagate = True

    def with_binance_data(
            self,
            symbol: str,
            interval: str,
            db_path: str,
            market: Union[Market, str],
    ):
        candle_db = CandleDB(db_path)
        candles = get_candles(
            symbol=symbol,
            interval=interval,
            market=str(market),
            db=candle_db,
            columns=[OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME],
        )

        self.candles.next(candles_as_numpy_array(candles))

    def add_data(self, candles: Union[np.ndarray, pd.DataFrame, Iterable]):
        self.candles.next(candles_as_numpy_array(candles))

    @abstractmethod
    def _run(self, *args, **kwargs): ...

    def run(self, enable_logging=True, *args, **kwargs):
        if self.strategy is None or self.candles is None:
            raise TraderException(
                "Unable to run bot.\n"
                "Reason: 'self.strategy' and 'self.candles' must not be None.\n"
                "Solution: Use 'add_data' and 'add_strategy' methods."
            )
        self.__setup_logger(enable_logging)
        self._run(*args, **kwargs)


def candles_as_numpy_array(
        candles: Union[np.ndarray, pd.DataFrame, Iterable],
):
    if isinstance(candles, pd.DataFrame):
        candles = candles.to_numpy(dtype="float")
    elif isinstance(candles, Iterable):
        candles = np.array(candles)
    elif not isinstance(candles, np.ndarray):
        raise ValueError(f"Invalid type for parameter 'candles'. Type: {type(candles)}")

    if candles.shape[1] < 6:
        raise ValueError(
            f"Pandas dataframe must have at least 6 columns.\n"
            f"Columns must be present in TOHLCV order \n"
            f"(open time, open price, high price, low price, close price, volume)."
        )
    return candles
