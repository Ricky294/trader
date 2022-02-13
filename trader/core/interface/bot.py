from abc import ABC, abstractmethod
from typing import Union, Iterable, Optional

import numpy as np
import pandas as pd
from crypto_data.binance.pd.extract import get_candles
from crypto_data.binance.schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, VOLUME, CLOSE_PRICE
from crypto_data.enum.market import Market
from crypto_data.shared.candle_db import CandleDB

from trader.core.exceptions import TraderException
from trader.core.strategy import Strategy


class TradingBot(ABC):

    def __init__(self):
        self.candles: Optional[np.ndarray] = None
        self.strategy: Optional[Strategy] = None

    def add_strategy(self, strategy: Strategy):
        self.strategy = strategy

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

        self.candles = candles_as_numpy_array(candles)

    def add_data(self, candles: Union[np.ndarray, pd.DataFrame, Iterable]):
        self.candles = candles_as_numpy_array(candles)

    @abstractmethod
    def _run(self, *args, **kwargs): ...

    def run(self, *args, **kwargs):
        if self.strategy is None or self.candles is None:
            raise TraderException(
                "Unable to run bot.\n"
                "Reason: self.strategy and self.candles must not be None.\n"
                "Solution: Use add_data and add_strategy methods."
            )
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
