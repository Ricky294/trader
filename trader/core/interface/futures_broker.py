from __future__ import annotations

from abc import ABC, abstractmethod

from trader.core.super_enum import OrderSide, TimeInForce
from trader.core.model import Balance, Position, MarketOrder, LimitOrder, Order


class FuturesBroker(ABC):

    @abstractmethod
    def cancel_orders(self, symbol: str) -> list[Order]:
        """
        Cancels all open orders on `symbol`.

        :return: Canceled orders.
        """
        pass

    @abstractmethod
    def enter_position(
            self,
            symbol: str,
            amount: float,
            asset: str,
            side: OrderSide,
            leverage: int,
            price: float = None,
            profit_price: float = None,
            stop_price: float = None,
            trailing_stop_rate: float = None,
            trailing_stop_activation_price: float = None,
    ) -> list[Order]:
        """
        Creates orders based on parameters.

        :param candles: Latest candles object.
        :param amount: Amount of amount for position.
        :param side: Buy or sell.
        :param leverage: Leverage is set before order creation.
        :param price: If None creates a market order, otherwise a limit order.
        :param profit_price: If not None, creates a take profit market order.
        :param stop_price: If not None, creates a stop loss market order.
        :return: Created orders.
        """
        ...

    def close_position(
            self,
            price: float = None,
            time_in_force=TimeInForce.GTC
    ):
        if price:
            return self.close_position_limit(price=price, time_in_force=time_in_force)
        return self.close_position_market()

    @abstractmethod
    def close_position_market(self) -> MarketOrder | None: ...

    @abstractmethod
    def close_position_limit(self, price: float, time_in_force=TimeInForce.GTC) -> LimitOrder: ...

    @abstractmethod
    def get_balance(self, asset: str) -> Balance | None: ...

    @abstractmethod
    def get_open_orders(self, symbol: str) -> list[Order]: ...

    @abstractmethod
    def get_position(self, symbol: str) -> Position | None: ...

    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> None: ...

    @abstractmethod
    def get_leverage(self, symbol) -> int: ...
