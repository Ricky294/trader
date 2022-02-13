from abc import ABC, abstractmethod
from typing import Callable

import numpy as np
import pandas as pd

from trader.core.const.trade_actions import BUY, SELL, NONE
from trader.core.util.common import Storable


class Indicator(ABC, Callable, Storable):

    slot_types = ()

    @classmethod
    def slot_type_dict(cls):
        return {
            name: type
            for name, type in zip(cls.__slots__, cls.slot_types)
        }

    @abstractmethod
    def __init__(self, *args, **data): ...

    @abstractmethod
    def __call__(self, candles: np.ndarray) -> np.ndarray: ...

    def signal(self, candles) -> int:
        latest_result = self.__call__(candles)[-1]
        if latest_result[BUY]:
            return BUY
        elif latest_result[SELL]:
            return SELL
        return NONE

    def buy_signal(self, candles) -> bool:
        return bool(self.__call__(candles)[-1][BUY])

    def sell_signal(self, candles) -> bool:
        return bool(self.__call__(candles)[-1][SELL])

    def to_dataframe(self, candles: np.ndarray) -> pd.DataFrame:
        result = self.__call__(candles)
        index_str = "_INDEX"
        index_columns = {
            val: key[:-len(index_str)]
            for key, val in type(self).mro()[0].__dict__.items()
            if index_str in key
        }
        index_columns[BUY] = "BUY"
        index_columns[SELL] = "SELL"
        columns = tuple(name for index, name in sorted(index_columns.items()))
        return pd.DataFrame(data=result, columns=columns)

    @staticmethod
    def concatenate_array(
            buy_signal_line: np.ndarray,
            sell_signal_line: np.ndarray,
            *lines: np.ndarray,
    ):
        if len(lines) == 0:
            return np.concatenate((
                [buy_signal_line],
                [sell_signal_line],
            )).T

        return np.concatenate((
            [buy_signal_line],
            [sell_signal_line],
            [line for line in lines],
        )).T
