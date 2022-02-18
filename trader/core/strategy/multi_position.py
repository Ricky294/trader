from abc import abstractmethod

from trader.core.interface import FuturesTrader
from trader.core.model import Candles
from .base import Strategy


class MultiPositionStrategy(Strategy):

    def __init__(self, trader: FuturesTrader):
        super(MultiPositionStrategy, self).__init__(trader)
        self.trader = trader

    @abstractmethod
    def on_next(self, candles: Candles): ...
