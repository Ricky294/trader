from abc import abstractmethod
from typing import Callable, Union

import numpy as np

from ..interface import FuturesTrader
from trader.core.model.candles import Candles


class Strategy(Callable):

    def __init__(self, trader: FuturesTrader):
        self.trader = trader

    @abstractmethod
    def on_candle(self, candles: Candles): ...

    def __call__(self, candles: Union[Candles, np.ndarray]):
        if isinstance(candles, np.ndarray):
            candles_ = Candles()
            candles_.next(candles)
            candles = candles_

        self.on_candle(candles)
