from abc import ABC, abstractmethod
from typing import Union, Iterable

import numpy as np
import pandas as pd
from crypto_data.binance.pd.extract import get_candles
from crypto_data.binance.schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, VOLUME, CLOSE_PRICE
from crypto_data.enum.market import Market
from crypto_data.shared.candle_db import CandleDB

from trader.core.strategy import Strategy


class TradingBot(ABC):

    @classmethod
    def binance_feed(
            cls,
            strategy: Strategy,
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

        return cls(candles=candles, strategy=strategy)

    def __init__(
            self,
            candles: Union[np.ndarray, pd.DataFrame, Iterable],
            strategy: Strategy,
    ):
        self.candles = candles_as_numpy_array(candles)
        self.strategy = strategy

    @abstractmethod
    def run(self, *args, **kwargs): ...


def candles_as_numpy_array(
        candles: Union[np.ndarray, pd.DataFrame, Iterable],
):
    if isinstance(candles, pd.DataFrame):
        candles = candles.to_numpy(dtype="float").T
    elif isinstance(candles, Iterable):
        candles = np.array(candles)
    elif not isinstance(candles, np.ndarray):
        raise ValueError(f"Invalid type for parameter 'candles'. Type: {type(candles)}")

    if candles.shape[1] < 6:
        raise ValueError(
            f"Pandas dataframe must have at least 6 columns.\n"
            f"Columns should be present TOHLCV order \n"
            f"(open time, open price, high price, low price, close price, volume)."
        )
    return candles
