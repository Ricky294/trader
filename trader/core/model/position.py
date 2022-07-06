from __future__ import annotations

from datetime import datetime
from abc import abstractmethod, ABC

import pandas as pd

import trader.core.model as core_model
from trader.core.enumerate import OrderSide, OrderType, SideFormat, TimeFormat
from trader.core.exception import PositionError
from trader.core.util.trade import side_to_int, side_to_long_short, format_side, format_time
from trader.config import MONEY_PRECISION, PROFIT_PRECISION, PRICE_PRECISION, FEE_PRECISION, QUANTITY_PRECISION


class Position(ABC):

    __slots__ = (
        "symbol",
        "side",
        "money",
        "quantity",
        "leverage",
        "entry_order_type",
        "entry_time",
        "entry_price",
        "entry_fee",
        "exit_order_type",
        "exit_time",
        "exit_price",
        "exit_fee",
    )

    @classmethod
    def from_market_order(
            cls,
            order: core_model.MarketOrder,
            leverage: int,
            entry_time: int,
            entry_price: float,
            entry_fee: float,
    ):

        return cls(
            symbol=order.symbol,
            money=order.money,
            quantity=order.quantity,
            side=order.side,
            leverage=leverage,
            entry_order_type=order.type,
            entry_time=entry_time,
            entry_price=entry_price,
            entry_fee=entry_fee,
        )

    @property
    def is_entry_order_taker(self):
        return 'MARKET' in self.entry_order_type

    @property
    def is_exit_order_taker(self):
        return 'MARKET' in self.exit_order_type

    @classmethod
    def from_limit_order(
            cls,
            order: core_model.LimitOrder,
            leverage: int,
            entry_time: int,
            entry_fee: float,
    ):

        return cls(
            symbol=order.symbol,
            money=order.money,
            quantity=order.quantity,
            side=order.side,
            leverage=leverage,
            entry_time=entry_time,
            entry_order_type=order.type,
            entry_price=order.price,
            entry_fee=entry_fee,
        )

    def __init__(
            self,
            symbol: str,
            money: float,
            quantity: float,
            side: int | str | OrderSide,
            leverage: int,
            entry_order_type: str | OrderType,
            entry_time: int,
            entry_price: float,
            entry_fee: float,
    ):
        self.symbol = symbol
        self.side = side_to_int(side)
        self.money = money
        self.quantity = quantity
        self.leverage = leverage
        self.entry_order_type = str(entry_order_type)
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.entry_fee = entry_fee
        self.exit_time = None
        self.exit_price = None
        self.exit_fee = None

    def close(self, time: int, price: float, fee: float):
        if self.exit_time:
            raise PositionError("Position already closed!")

        self.exit_time = time
        self.exit_price = price
        self.exit_fee = fee

    def is_closed(self):
        return self.exit_time is not None

    @property
    def dt_entry_time(self):
        """Converts entry timestamp to datetime object."""
        return datetime.fromtimestamp(self.entry_time)

    @property
    def pd_entry_time(self):
        """Converts entry timestamp to pandas datetime object."""
        return pd.to_datetime(self.entry_time, unit="s")

    @property
    def dt_exit_time(self):
        """Converts exit timestamp to datetime object."""
        return datetime.fromtimestamp(self.exit_time)

    @property
    def pd_exit_time(self):
        """
        Converts exit timestamp to pandas datetime object.

        :examples:

        >>> p1 = Position(symbol='XYZ', money=100, quantity=1, side='BUY', leverage=1,
        ...               entry_order_type='MARKET', entry_time=1623300000, entry_price=100, entry_fee=0)
        >>> p1.close(1623300000, 200, 0)
        >>> p1.pd_exit_time()
        """
        return pd.to_datetime(self.exit_time, unit="s")

    @property
    @abstractmethod
    def profit(self): ...

    def __eq__(self, other):
        return (
                isinstance(other, type(self))
                and (self.symbol, self.entry_time, self.side)
                == (other.symbol, other.entry_time, other.side)
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.symbol, self.entry_time, self.side))

    def __str__(self):
        return (
            f"Position(symbol: {self.symbol}"
            f", time: {self.pd_entry_time}"
            f", price: {self.entry_price:.{PRICE_PRECISION}f}"
            f", fee: {self.entry_fee:.{FEE_PRECISION}f}"
            f", side: {side_to_long_short(self.side)}"
            f", money: {self.money:.{MONEY_PRECISION}f}"
            f', quantity: {self.quantity:.{QUANTITY_PRECISION}f}'
            f", exit time: {self.pd_exit_time}"
            f", exit price: {self.exit_price:.{PRICE_PRECISION}}"
            f", exit fee: {self.exit_fee:.{FEE_PRECISION}}"
            f", profit: {self.profit:.{PROFIT_PRECISION}f}"
            f', leverage: {self.leverage})'
        )

    def to_list(self, time_format=TimeFormat.TIMESTAMP, side_format=SideFormat.NUM):
        """
        Converts position to list.

        Data by indexes:
            - 0:  symbol - str
            - 1:  entry time - int | datetime | pd.Timestamp
            - 2:  entry price - float
            - 3:  entry fee - float
            - 4:  side - int | str
            - 5:  money - float
            - 6:  quantity - float
            - 7:  leverage - int
            - 8:  exit time - int | datetime | pd.Timestamp
            - 9:  exit price - float
            - 10: exit fee - float
            - 11: profit - float

        :param time_format: Formats position entry and exit time.
        :param side_format: Formats position side.
        :return: list
        """

        return [
            self.symbol,
            format_time(self.entry_time, time_format),
            self.entry_price,
            self.entry_fee,
            format_side(self.side, side_format),
            self.money,
            self.quantity,
            self.leverage,
            format_time(self.exit_time, time_format),
            self.exit_price,
            self.exit_fee,
            self.profit,
        ]

    def to_dict(
            self,
            time_format: TimeFormat,
            side_format: SideFormat,
    ):
        """
        Converts position to dictionary.

        time_format options:
            - ts = timestamp in seconds
            - pd = pandas datetime
            - dt = builtin datetime

        :param time_format: Formats entry and exit time.
        :param side_format: Formats position side.
        :return: dict
        :raises ValueError: If `format` is not "ts", "pd" or "dt"
        """

        return {
            "symbol": self.symbol,
            "entry_time": format_time(self.entry_time, time_format),
            "entry_price": self.entry_price,
            "entry_fee": self.entry_fee,
            "side": format_side(self.side, side_format),
            "money": self.money,
            "quantity": self.quantity,
            "leverage": self.leverage,
            "exit_time": format_time(self.exit_time, time_format),
            "exit_price": self.exit_price,
            "exit_fee": self.exit_fee,
            "profit": self.profit,
        }


if __name__ == '__main__':
    import doctest
    p1 = Position(
        symbol="XYZ", money=100, quantity=1, side="BUY", leverage=1,
        entry_order_type=OrderType.MARKET, entry_time=1623300000, entry_price=100, entry_fee=0
    )
    doctest.testmod(extraglobs={'p1': p1})
