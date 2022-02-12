from abc import ABC, abstractmethod
from typing import Union, Iterable

import numpy as np
import pandas as pd

from trader.core.strategy import Strategy


class TradingBot(ABC):

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
