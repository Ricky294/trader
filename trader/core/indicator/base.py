from abc import ABC, abstractmethod
from typing import Callable

import numpy as np
import pandas as pd

from trader.core.const.trade_actions import BUY, SELL, NONE
from trader.core.model import Candles
from trader.core.util.common import Storable


class _AdditionalIndicatorData:

    def __init__(self, *lines: str):
        for key in lines:
            self.__dict__[key] = np.array([])


class Indicator(_AdditionalIndicatorData, Storable, ABC, Callable):

    __slots__ = "buy_signal", "sell_signal"

    def __init__(self, *lines: str):
        self.buy_signal = np.array([])
        self.sell_signal = np.array([])
        super(Indicator, self).__init__(*lines)

    def latest_signal(self) -> int:
        if self.buy_signal[-1]:
            return BUY
        elif self.sell_signal[-1]:
            return SELL
        return NONE

    @abstractmethod
    def __call__(self, candles: Candles) -> None: ...

    def to_dataframe(self, candles: Candles) -> pd.DataFrame:
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
