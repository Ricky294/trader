from __future__ import annotations

from enum import Enum

from trader.core.const.trade_actions import (
    BUY as BUY_,
    SELL as SELL_,
)


class OrderSide(Enum):
    BUY = BUY_
    SELL = SELL_

    LONG = BUY_
    SHORT = SELL_

    @classmethod
    def from_value(cls, side: str | int):
        if isinstance(side, str):
            from ..util.trade import str_side_to_int
            side = str_side_to_int(side)

        if side == BUY_:
            return cls.BUY
        elif side == SELL_:
            return cls.SELL
        else:
            ValueError(f"Parameter 'side' must be {BUY_} or {SELL_}")

    @classmethod
    def from_quantity(cls, quantity: float):
        if quantity > 0:
            return cls.BUY
        elif quantity < 0:
            return cls.SELL
        else:
            raise ValueError("Quantity must not be 0.")

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
                    (other in ("SELL", "SHORT") and self.value == SELL_)
                    or (other in ("BUY", "LONG") and self.value == BUY_)
            )
        elif isinstance(other, int):
            return other == self.value
        elif isinstance(other, OrderSide):
            return other.value == self.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class TimeInForce(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTX = "GTX"

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
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP"
    STOP_MARKET = "STOP_MARKET"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"
    TRAILING_STOP_MARKET = "TRAILING_STOP_MARKET"

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
