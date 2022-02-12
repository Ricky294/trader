from enum import Enum
from typing import Union

from ..const.trade_actions import BUY as TA_BUY, SELL as TA_SELL


class OrderSide(Enum):
    BUY = TA_BUY
    SELL = TA_SELL

    LONG = TA_BUY
    SHORT = TA_SELL

    @classmethod
    def from_value(cls, side: Union[str, int]):
        if isinstance(side, str):
            from ..util.trade import str_side_to_int
            side = str_side_to_int(side)

        if side == TA_BUY:
            return cls.BUY
        elif side == TA_SELL:
            return cls.SELL
        else:
            ValueError(f"Parameter 'side' must be {TA_BUY} or {TA_SELL}")

    @classmethod
    def from_quantity(cls, quantity: float):
        if quantity > 0:
            return cls.BUY
        elif quantity < 0:
            return cls.SELL
        else:
            raise ValueError("Quantity must not be 0.")

    def opposite(self):
        if self.value == TA_BUY:
            return self.SELL
        return self.BUY

    def __str__(self):
        from ..util.trade import int_side_to_str
        return int_side_to_str(self.value)

    def __int__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return (
                    (other in ("SELL", "SHORT") and self.value == TA_SELL)
                    or (other in ("BUY", "LONG") and self.value == TA_BUY)
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
