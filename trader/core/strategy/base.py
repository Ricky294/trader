from abc import abstractmethod
from typing import Callable

from ..interface import FuturesTrader
from trader.core.model.candles import Candles


class Strategy(Callable):

    def __init__(self, trader: FuturesTrader):
        self.trader = trader

    @abstractmethod
    def on_candle(self, candles: Candles): ...

    def __call__(self, candles: Candles):
        self.on_candle(candles)
