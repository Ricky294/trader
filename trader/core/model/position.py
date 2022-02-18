from abc import abstractmethod
from typing import Union
from ..enum import OrderSide
from ..util.trade import int_side_to_str
from ... import MONEY_PRECISION, PROFIT_PRECISION, PRICE_PRECISION


class Position:

    __slots__ = "symbol", "side", "_money", "entry_price", "entry_time", "leverage"

    def __init__(
            self,
            symbol: str,
            money: float,
            side: Union[int, OrderSide],
            entry_price: float,
            entry_time: int,
            leverage: int,
    ):
        self.symbol = symbol
        self.side = int(side)
        self._money = money
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.leverage = leverage

    @classmethod
    def from_quantity(
            cls,
            symbol: str,
            quantity: float,
            side: Union[int, OrderSide],
            entry_price: float,
            entry_time: int,
            leverage: int,
    ):
        return cls(
            symbol=symbol,
            side=side,
            money=entry_price * quantity,
            entry_price=entry_price,
            entry_time=entry_time,
            leverage=leverage
        )

    def money(self, leverage=False):
        return self._money * (self.leverage if leverage else 1)

    def quantity(self, leverage=False):
        return self._money / self.entry_price * (self.leverage if leverage else 1)

    @abstractmethod
    def profit(self, *args, **kwargs) -> float: ...

    def __str__(self):
        return (
            f"Position (money: {self._money:.{MONEY_PRECISION}f}, side: {int_side_to_str(self.side)}, "
            f"leverage: {self.leverage}, entry_price: {self.entry_price:.{PRICE_PRECISION}f}, "
            f"profit: {self.profit():.{PROFIT_PRECISION}f})"
        )
