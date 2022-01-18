from abc import abstractmethod

from ..const.trade_actions import BUY, SELL


class Position:

    __slots__ = "symbol", "side", "quantity", "entry_price", "leverage"

    def __init__(
            self,
            symbol: str,
            quantity: float,
            entry_price: float,
            leverage: int,
    ):
        if quantity == 0:
            raise ValueError("Quantity must not be 0")

        self.symbol = symbol
        self.side = BUY if quantity > 0 else SELL
        self.quantity = quantity
        self.entry_price = entry_price
        self.leverage = leverage

    @abstractmethod
    def profit(self) -> float: ...
