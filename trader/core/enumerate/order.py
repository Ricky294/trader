from __future__ import annotations

from enum import Enum

from trader.core.const.trade_actions import (
    BUY as BUY_,
    SELL as SELL_,
)
from trader.core.const.order_type import (
    LIMIT as LIMIT_,
    MARKET as MARKET_,
    STOP_LIMIT as STOP_,
    STOP_MARKET as STOP_MARKET_,
    TAKE_PROFIT_LIMIT as TAKE_PROFIT_,
    TAKE_PROFIT_MARKET as TAKE_PROFIT_MARKET_,
    TRAILING_STOP_MARKET as TRAILING_STOP_MARKET_,
)
from trader.core.const.time_in_force import (
    GTC as GTC_,
    IOC as IOC_,
    FOK as FOK_,
    GTX as GTX_,
)


class OrderSide(Enum):
    BUY = BUY_
    SELL = SELL_

    LONG = BUY_
    SHORT = SELL_

    @classmethod
    def from_value(cls, side: str | int):
        from ..util.trade import side_to_int
        return side_to_int(side)

    @classmethod
    def from_quantity(cls, quantity: float):
        if quantity > 0:
            return cls.BUY
        elif quantity < 0:
            return cls.SELL
        else:
            raise ValueError('Quantity must not be 0.')

    def opposite(self):
        if self.value == BUY_:
            return self.SELL
        return self.BUY

    def __str__(self):
        from trader.core.util.trade import side_to_buy_sell
        return side_to_buy_sell(self.value)

    def __repr__(self):
        from trader.core.util.trade import side_to_buy_sell
        return f"{self.__class__.__name__}.{side_to_buy_sell(self.value)}: {int(self)}"

    def __int__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return (
                    (other in ('SELL', 'SHORT') and self.value == SELL_)
                    or (other in ('BUY', 'LONG') and self.value == BUY_)
            )
        elif isinstance(other, int):
            return other == self.value
        elif isinstance(other, OrderSide):
            return other.value == self.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class TimeInForce(Enum):
    GTC = GTC_
    IOC = IOC_
    FOK = FOK_
    GTX = GTX_

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.value
        elif isinstance(other, TimeInForce):
            return other.value == self.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class OrderType(Enum):
    LIMIT = LIMIT_
    MARKET = MARKET_
    STOP_LIMIT = STOP_
    STOP_MARKET = STOP_MARKET_
    TAKE_PROFIT_LIMIT = TAKE_PROFIT_
    TAKE_PROFIT_MARKET = TAKE_PROFIT_MARKET_
    TRAILING_STOP_MARKET = TRAILING_STOP_MARKET_

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.value
        elif isinstance(other, OrderType):
            return other.value == self.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
