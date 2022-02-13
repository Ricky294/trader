from abc import ABC, abstractmethod
from typing import Callable

import pandas as pd

from trader.core.const.trade_actions import BUY, SELL
from trader.core.indicator.result import IndicatorResult
from trader.core.model import Candles
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
    def __call__(self, candles: Candles) -> IndicatorResult: ...

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
