from abc import ABC, abstractmethod
from typing import Callable

import numpy as np

from ..const.trade_actions import BUY, SELL, NONE
from ..util.common import Storable


class EntryIndicator(ABC, Callable, Storable):
    @abstractmethod
    def __init__(self, *args, **data): ...

    @abstractmethod
    def __call__(self, candles: np.ndarray) -> np.ndarray: ...

    def signal(self, candles) -> int:
        latest_result = self.__call__(candles).T[-1]
        if latest_result[BUY]:
            return BUY
        elif latest_result[SELL]:
            return SELL
        return NONE

    def buy_signal(self, candles) -> bool:
        return bool(self.__call__(candles).T[-1][BUY])

    def sell_signal(self, candles) -> bool:
        return bool(self.__call__(candles).T[-1][SELL])

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
            ))

        return np.concatenate((
            [buy_signal_line],
            [sell_signal_line],
            [line for line in lines],
        ))
