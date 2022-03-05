from abc import ABC, abstractmethod
from typing import List, Union, Optional

from ..enum import OrderSide, TimeInForce
from ..model import Balance, Order, Position


class FuturesTrader(ABC):

    @abstractmethod
    def cancel_orders(self, symbol: str) -> List[Order]: ...

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
    ) -> Optional[List[Order]]: ...

    @abstractmethod
    def close_position_market(self, symbol: str) -> Order: ...

    @abstractmethod
    def close_position_limit(self, symbol: str, price: float, time_in_force: Union[str, TimeInForce] = "GTC") -> Order: ...

    @abstractmethod
    def get_balance(self, asset: str) -> Optional[Balance]: ...

    @abstractmethod
    def get_open_orders(self, symbol: str) -> List[Order]: ...

    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]: ...

    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> None: ...
