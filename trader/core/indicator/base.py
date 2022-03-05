from abc import ABC, abstractmethod
from typing import Callable

import numpy as np
import pandas as pd

from trader.core.model import Candles


class Indicator(ABC, Callable):

    @abstractmethod
    def __call__(self, candles: Candles): ...


class Result(ABC):

    @abstractmethod
    def __init__(self): ...

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, val):
        if isinstance(val, slice):
            return np.array(tuple(signal[val.start:val.stop:val.step] for signal in self.__dict__.values()))
        else:
            return np.array(tuple(signal[val] for signal in self.__dict__.values()))

    def to_np_array(self):
        return np.array(tuple(
            val
            for val in self.__dict__.values()
            if hasattr(val, "__getitem__")
        ))

    def to_pd_dataframe(self):
        return pd.DataFrame(data={
            key: val
            for key, val in self.__dict__.items()
            if hasattr(val, "__getitem__")
        })
