from abc import abstractmethod

from trader.data.model import Candles
from trader.core.interface import FuturesTrader
from trader.core.model import Position
from trader.core.strategy import Strategy


class ManagedPositionStrategy(Strategy):

    def __init__(self, trader: FuturesTrader, candles: Candles):
        super(ManagedPositionStrategy, self).__init__(trader, candles)

    def __call__(self, candles: Candles):
        position = self.trader.get_position(candles.symbol)
        if position is None:
            self.not_in_position(candles)
        else:
            self.in_position(candles, position)

    @abstractmethod
    def in_position(self, candles: Candles, position: Position): ...

    @abstractmethod
    def not_in_position(self, candles: Candles): ...
