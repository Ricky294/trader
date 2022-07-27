from abc import abstractmethod

import trader.core.strategy.strategy as strategy

from trader.core.interface import FuturesBroker
from trader.core.model import Position, Balance, Order

from trader.data.model import Candles


class ManagedPositionStrategy(strategy.Strategy):

    def __init__(self, broker: FuturesBroker, candles: Candles, asset: str):
        super(ManagedPositionStrategy, self).__init__(broker=broker, candles=candles, asset=asset)

    def __call__(
            self,
            candles: Candles,
            balance: Balance,
            open_orders: list[Order],
            position: Position | None,
            leverage: int,
            *args,
            **kwargs
    ):
        if position:
            self.in_position(
                candles=candles,
                balance=balance,
                open_orders=open_orders,
                position=position,
                leverage=leverage,
                *args, **kwargs
            )
        else:
            self.not_in_position(
                candles=candles,
                balance=balance,
                open_orders=open_orders,
                leverage=leverage,
                *args, **kwargs
            )

    @abstractmethod
    def in_position(self, candles: Candles, balance: Balance, open_order: list[Order], position: Position, leverage: int, *args, **kwargs): ...

    @abstractmethod
    def not_in_position(self, candles: Candles, balance: Balance, open_order: list[Order], leverage: int, *args, **kwargs): ...
