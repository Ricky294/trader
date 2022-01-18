from abc import ABC, abstractmethod
from typing import List

from ..model import Balance, Order, SymbolInfo, Position


class FuturesTrader(ABC):

    @abstractmethod
    def cancel_orders(self, symbol: str) -> None: ...

    @abstractmethod
    def create_position(
            self,
            symbol: str,
            quantity: float,
            price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ) -> None: ...

    @abstractmethod
    def close_position(self, symbol: str) -> None: ...

    @abstractmethod
    def get_balances(self) -> List[Balance]: ...

    @abstractmethod
    def get_balance(self, asset: str) -> Balance: ...

    @abstractmethod
    def get_open_orders(self, symbol: str) -> List[Order]: ...

    @abstractmethod
    def get_symbol_info(self, symbol: str) -> SymbolInfo: ...

    @abstractmethod
    def get_position(self, symbol: str) -> Position: ...

    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> None: ...

    @abstractmethod
    def get_leverage(self, symbol) -> int: ...
