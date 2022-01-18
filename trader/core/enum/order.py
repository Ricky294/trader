from enum import Enum
from ..const.trade_actions import BUY as TA_BUY, SELL as TA_SELL


class OrderSide(Enum):
    BUY = TA_BUY
    SELL = TA_SELL

    LONG = TA_BUY
    SHORT = TA_SELL

    @classmethod
    def from_quantity(cls, quantity: float):
        if quantity > 0:
            return cls.BUY
        elif quantity < 0:
            return cls.SELL
        else:
            raise ValueError("Quantity must not be 0.")

    def __str__(self):
        from ..util.trade import int_side_to_str
        return int_side_to_str(self.value)

    def __int__(self):
        return self.value


class TimeInForce(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTX = "GTX"

    def __str__(self):
        return self.value


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
