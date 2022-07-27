from __future__ import annotations

from datetime import datetime

import pandas as pd

import trader.core.model as core_model
from trader.core.super_enum import OrderSide
from trader.core.exception import PositionError

from trader.data.model import Model


class Position(Model):

    @classmethod
    def from_market_order(
            cls,
            order: core_model.MarketOrder,
            leverage: int,
            entry_time: int,
            entry_price: float,
            position_id=None,
    ):
        return cls(
            position_id=position_id,
            symbol=order.symbol,
            amount=order.amount,
            quantity=order.quantity,
            side=order.side,
            leverage=leverage,
            entry_time=entry_time,
            entry_price=entry_price,
        )

    @classmethod
    def from_limit_order(
            cls,
            order: core_model.LimitOrder,
            leverage: int,
            entry_time: int,
            position_id=None,
    ):
        return cls(
            position_id=position_id,
            symbol=order.symbol,
            amount=order.amount,
            quantity=order.quantity,
            side=order.side,
            leverage=leverage,
            entry_time=entry_time,
            entry_price=order.price,
        )

    def __init__(
            self,
            symbol: str,
            amount: float,
            quantity: float,
            side: OrderSide,
            leverage: int,
            entry_time: float,
            entry_price: float,
            position_id=None,
    ):
        super(Position, self).__init__(entry_time)
        self.position_id = position_id
        self.symbol = symbol
        self.side = side
        self.amount = amount
        self.quantity = quantity
        self.leverage = leverage
        self.entry_price = entry_price
        self.exit_time = None
        self.exit_price = None
        self.closed = False

    def close(self, time: float, price: float):
        if self.closed:
            raise PositionError("Position already closed!")

        self.exit_time = time
        self.exit_price = price
        self.closed = True

    @property
    def dt_entry_time(self):
        """Converts entry timestamp to datetime object."""
        return datetime.fromtimestamp(self.time)

    @property
    def pd_entry_time(self):
        """Converts entry timestamp to pandas datetime object."""
        return pd.to_datetime(self.time, unit="s")

    @property
    def dt_exit_time(self):
        """Converts exit timestamp to datetime object."""
        return datetime.fromtimestamp(self.exit_time)

    @property
    def pd_exit_time(self):
        """
        Converts exit timestamp to pandas datetime object.

        :examples:

        >>> p1 = Position(symbol='XYZ', amount=100, quantity=1, side=OrderSide.LONG, leverage=1,
        ...               entry_time=1623300000, entry_price=100)
        >>> p1.close(1623300000, 200)
        >>> p1.pd_exit_time()
        """
        return pd.to_datetime(self.exit_time, unit="s")

    @property
    def profit(self):
        return NotImplementedError


if __name__ == '__main__':
    import doctest
    p1 = Position(
        symbol="XYZ", amount=100, quantity=1, side=OrderSide.LONG, leverage=1,
        entry_time=1623300000, entry_price=100
    )
    print(p1.__str__())
    doctest.testmod(extraglobs={'p1': p1})
