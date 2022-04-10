from abc import abstractmethod

from trader_data.core.model import Candles

from trader.core.interface import FuturesTrader
from trader.core.model import Position

from .base import Strategy


class ManagedPositionStrategy(Strategy):

    def __init__(self, symbol: str, trader: FuturesTrader):
        super(ManagedPositionStrategy, self).__init__(trader)
        self.symbol = symbol

    def on_next(self, candles: Candles):
        position = self.trader.get_position(self.symbol)
        if position is None:
            self.not_in_position(candles)
        else:
            self.in_position(candles, position)

    @abstractmethod
    def in_position(self, candles: Candles, position: Position): ...

    @abstractmethod
    def not_in_position(self, candles: Candles): ...
