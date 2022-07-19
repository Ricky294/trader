from abc import abstractmethod

from trader.core.interface import FuturesBroker
from trader.core.model import Position, Balance, Order
from trader.core.strategy import Strategy

from trader.data.model import Candles


class ManagedPositionStrategy(Strategy):

    def __init__(self, broker: FuturesBroker, candles: Candles, asset: str):
        super(ManagedPositionStrategy, self).__init__(broker=broker, candles=candles, asset=asset)

    def __call__(self, candles: Candles):
        position = self.broker.get_position(candles.symbol)
        balance = self.broker.get_balance(self.asset)
        open_orders = self.broker.get_open_orders(candles.symbol)
        if position:
            self.in_position(candles, balance, open_orders, position)
        else:
            self.not_in_position(candles, balance, open_orders)

    @abstractmethod
    def in_position(self, candles: Candles, balance: Balance, open_order: list[Order], position: Position): ...

    @abstractmethod
    def not_in_position(self, candles: Candles, balance: Balance, open_order: list[Order]): ...
