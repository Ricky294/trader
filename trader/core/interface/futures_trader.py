from abc import ABC, abstractmethod
from typing import List, Union, Optional

from ..enum import OrderSide
from ..model import Balance, Order, Position


class FuturesTrader(ABC):

    def __init__(self):
        self.on_entry_order = lambda symbol, orders: ...
        self.on_close_order = lambda symbol, order: ...

        self.on_get_open_orders = lambda symbol, orders: ...
        self.on_get_position = lambda symbol, position: ...
        self.on_get_balance = lambda asset, balance: ...

        self.on_cancel_orders = lambda symbol, orders: ...
        self.on_set_leverage = lambda symbol, leverage: ...

    @abstractmethod
    def _cancel_orders(self, symbol: str) -> List[Order]: ...

    def cancel_orders(self, symbol: str) -> List[Order]:
        orders = self._cancel_orders(symbol)
        self.on_cancel_orders(symbol, orders)
        return orders

    @abstractmethod
    def get_latest_price(self, symbol: str) -> float: ...

    @abstractmethod
    def _create_position(
            self,
            symbol: str,
            money: float,
            side: Union[int, OrderSide],
            leverage: int,
            price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ) -> Optional[List[Order]]: ...

    def create_position(
            self,
            symbol: str,
            money: float,
            side: Union[int, OrderSide],
            leverage: int,
            price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ) -> Optional[List[Order]]:
        orders = self._create_position(
            symbol=symbol,
            money=money,
            side=side,
            leverage=leverage,
            price=price,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price,
        )
        self.on_entry_order(symbol, orders)
        return orders

    @abstractmethod
    def _close_position_market(self, symbol: str) -> Order: ...

    def close_position_market(self, symbol: str) -> Order:
        order = self._close_position_market(symbol)
        self.on_close_order(symbol, order)
        return order

    @abstractmethod
    def _close_position_limit(self, symbol: str, price: float) -> Order: ...

    def close_position_limit(self, symbol: str, price: float) -> Order:
        order = self._close_position_limit(symbol, price)
        self.on_close_order(symbol, order)
        return order

    @abstractmethod
    def _get_balance(self, asset: str) -> Optional[Balance]: ...

    def get_balance(self, asset: str) -> Optional[Balance]:
        balance = self._get_balance(asset)
        self.on_get_balance(asset, balance)
        return balance

    @abstractmethod
    def _get_open_orders(self, symbol: str) -> List[Order]: ...

    def get_open_orders(self, symbol: str) -> List[Order]:
        orders = self._get_open_orders(symbol)
        self.on_get_open_orders(symbol, orders)
        return orders

    @abstractmethod
    def _get_position(self, symbol: str) -> Optional[Position]: ...

    def get_position(self, symbol: str) -> Optional[Position]:
        position = self._get_position(symbol)
        self.on_get_position(symbol, position)
        return position

    @abstractmethod
    def _set_leverage(self, symbol: str, leverage: int) -> None: ...

    def set_leverage(self, symbol: str, leverage: int) -> None:
        self._set_leverage(symbol, leverage)
        self.on_set_leverage(symbol, leverage)
