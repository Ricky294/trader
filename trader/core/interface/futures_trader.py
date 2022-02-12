from abc import ABC, abstractmethod
from typing import List, Union

from ..enum import OrderSide
from ..model import Balance, Order, Position


class FuturesTrader(ABC):

    @abstractmethod
    def cancel_orders(self, symbol: str) -> None: ...

    @abstractmethod
    def get_latest_price(self, symbol: str) -> float: ...

    @abstractmethod
    def create_position(
            self,
            symbol: str,
            money: float,
            side: Union[int, OrderSide],
            leverage: int,
            price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ) -> None: ...

    @abstractmethod
    def close_position_market(self, symbol: str) -> None: ...

    @abstractmethod
    def close_position_limit(self, symbol: str, price: float) -> None: ...

    @abstractmethod
    def get_balance(self, asset: str) -> Balance: ...

    @abstractmethod
    def get_open_orders(self, symbol: str) -> List[Order]: ...

    @abstractmethod
    def get_position(self, symbol: str) -> Position: ...

    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> None: ...

    @abstractmethod
    def get_leverage(self, symbol) -> int: ...
