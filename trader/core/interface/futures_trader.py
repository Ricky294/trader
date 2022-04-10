from __future__ import annotations

from abc import ABC, abstractmethod

from ..enum import OrderSide, TimeInForce
from ..model import Balance, Order, Position


class FuturesTrader(ABC):

    @abstractmethod
    def cancel_orders(self, symbol: str) -> list[Order]: ...

    @abstractmethod
    def get_latest_price(self, symbol: str) -> float: ...

    @abstractmethod
    def create_position(
            self,
            symbol: str,
            money: float,
            side: int | OrderSide,
            leverage: int,
            price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ) -> list[Order]: ...

    def close_position(self, symbol: str, price: float = None, time_in_force: str | TimeInForce = "GTC") -> Order | None:
        if price is None:
            return self.close_position_market(symbol)
        return self.close_position_limit(symbol=symbol, price=price, time_in_force=time_in_force)

    @abstractmethod
    def close_position_market(self, symbol: str) -> Order | None: ...

    @abstractmethod
    def close_position_limit(self, symbol: str, price: float, time_in_force: str | TimeInForce = "GTC") -> Order | None: ...

    @abstractmethod
    def get_balance(self, asset: str) -> Balance | None: ...

    @abstractmethod
    def get_open_orders(self, symbol: str) -> list[Order]: ...

    @abstractmethod
    def get_position(self, symbol: str) -> Position | None: ...

    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> None: ...
