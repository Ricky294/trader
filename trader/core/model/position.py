from __future__ import annotations

from datetime import datetime
from abc import abstractmethod, ABC

import pandas as pd

import trader.core.model as core_model
from trader.core.enumerate import OrderSide
from trader.core.exception import PositionError
from trader.core.util.trade import side_to_buy_sell
from trader.config import MONEY_PRECISION, PROFIT_PRECISION, PRICE_PRECISION, FEE_PRECISION


class Position(ABC):

    __slots__ = (
        "symbol", "side", "money", "leverage",
        "entry_time", "entry_price", "entry_fee",
        "exit_time", "exit_price", "exit_fee",
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
            entry_time=entry_time,
            entry_price=entry_price,
            entry_fee=entry_fee,
        )

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
            entry_price=order.price,
            entry_fee=entry_fee,
        )

    def __init__(
            self,
            symbol: str,
            money: float,
            quantity: float,
            side: int | OrderSide,
            leverage: int,
            entry_time: int,
            entry_price: float,
            entry_fee: float,
    ):
        self.symbol = symbol
        self.side = int(side)
        self.money = money
        self.quantity = quantity
        self.leverage = leverage
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.entry_fee = entry_fee
        self.exit_time = None
        self.exit_price = None
        self.exit_fee = None

    def set_exit(self, time: int, price: float, fee: float):
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
        """Converts exit timestamp to pandas datetime object."""
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
            f"Position (entry: {self.dt_entry_time}, symbol: {self.symbol}, side: {side_to_buy_sell(self.side)}, "
            f"money: {self.money:.{MONEY_PRECISION}f}, fee: {self.entry_fee:.{FEE_PRECISION}f}, "
            f"price: {self.entry_price:.{PRICE_PRECISION}f}, "
            f"leverage: {self.leverage}, profit: {self.profit:.{PROFIT_PRECISION}f}, "
            f"exit time: {self.dt_exit_time}, exit price: {self.exit_price:.{PRICE_PRECISION}}, exit fee: {self.exit_fee:.{FEE_PRECISION}})"
        )

    def to_list(self):
        return [
            self.symbol, self.entry_time, self.entry_price, self.money, self.quantity, self.side, self.entry_fee,
            self.leverage, self.exit_time, self.exit_price, self.exit_fee, self.profit,
        ]

    def to_dict(self, time_format="ts"):
        """
        Converts position to dictionary.

        time_format options:
            - ts = timestamp in seconds
            - pd = pandas datetime
            - dt = builtin datetime

        :param time_format: Formats entry and exit time.
        :return: dict
        :raises ValueError: If `format` is not "ts", "pd" or "dt"
        """

        if time_format == "ts":
            entry_time = self.entry_time
            exit_time = self.exit_time
        elif time_format == "pd":
            entry_time = self.pd_entry_time
            exit_time = self.pd_exit_time
        elif time_format == "dt":
            entry_time = self.dt_entry_time
            exit_time = self.dt_exit_time
        else:
            raise ValueError("Format param must be 'ts', 'pd' or 'dt'.")

        return {
            "Symbol": self.symbol, "Entry time": entry_time, "Entry price": self.entry_price, "Money": self.money,
            "Quantity": self.quantity, "Side": self.side, "Entry fee": self.entry_fee, "Leverage": self.leverage,
            "Exit time": exit_time, "Exit price": self.exit_price, "Exit fee": self.exit_fee, "Profit": self.profit,
        }
