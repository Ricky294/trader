from typing import Iterable

from trader.config import MARKET

from trader.data.super_enum import SuperEnum, Market


class OrderSide(SuperEnum):
    BUY = LONG = 0
    SELL = SHORT = 1

    def to_long_short(self):
        return 'LONG' if self.value == 0 else 'SHORT'

    def to_buy_sell(self):
        return 'BUY' if self.value == 0 else 'SELL'

    def __str__(self):
        return self.to_long_short() if MARKET == Market.FUTURES else self.to_buy_sell()

    def __int__(self):
        return self.value

    def opposite(self):
        return OrderSide.BUY if self is OrderSide.SELL else OrderSide.SELL


def side_to_long_short(sides: Iterable[OrderSide]):
    return [side.to_long_short() for side in sides]


def side_to_buy_sell(sides: Iterable[OrderSide]):
    return [side.to_buy_sell() for side in sides]


def side_to_int(sides: Iterable[OrderSide]):
    return [int(side) for side in sides]
