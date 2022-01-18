from abc import abstractmethod
from typing import Callable

import numpy as np

from ..interface import FuturesTrader


class Strategy(Callable):

    def __init__(self, trader: FuturesTrader):
        self.trader = trader

    @abstractmethod
    def on_candle(self, candles: np.ndarray): ...

    def __call__(self, candles: np.ndarray):
        self.on_candle(candles)
