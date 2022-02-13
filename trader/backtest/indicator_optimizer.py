import numpy as np

from trader.core.indicator import Indicator
from trader.core.model import Candles


class OptimizedIndicator(Indicator):
    def __init__(self, candles: Candles, indicator: Indicator):
        self.__indicator = indicator
        self.__result = self.__indicator.__call__(candles)

    def __call__(self, candles: Candles) -> np.ndarray:
        return self.__result[:candles.shape[0]]
