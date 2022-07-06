from __future__ import annotations

from abc import ABC, abstractmethod

from trader.core.enumerate import OrderSide, TimeInForce
from trader.core.model import Balance, Position, OrderGroup, MarketOrder, LimitOrder
from trader.data.model import Candles


class FuturesTrader(ABC):

    @abstractmethod
    def cancel_orders(self, symbol: str) -> OrderGroup:
        """
        Cancels all open orders on `symbol`.

        :return: Canceled orders.
        """
        pass

    @abstractmethod
    def enter_position(
            self,
            money: float,
            side: int | OrderSide,
            leverage: int,
            candles: Candles,
            price: float = None,
            profit_price: float = None,
            stop_price: float = None,
            trailing_stop_rate: float = None,
            trailing_stop_activation_price: float = None,
    ) -> OrderGroup:
        """
        Creates orders based on parameters.

        :param symbol: Symbol to create orders against.
        :param money: Amount of money for position.
        :param side: Buy or sell.
        :param leverage: Leverage is set before order creation.
        :param price: If None creates a market order, otherwise a limit order.
        :param profit_price: If not None, creates a take profit market order.
        :param stop_price: If not None, creates a stop loss market order.
        :return: Created orders.
        """
        pass

    def close_position(
            self,
            candles: Candles,
            price: float = None,
            time_in_force: str | TimeInForce = "GTC"
    ):
        if price:
            return self.close_position_limit(candles=candles, price=price, time_in_force=time_in_force)
        return self.close_position_market(candles=candles)

    @abstractmethod
    def close_position_market(self, candles: Candles) -> MarketOrder | None: ...

    @abstractmethod
    def close_position_limit(self, candles: Candles, price: float, time_in_force: str | TimeInForce = "GTC") -> LimitOrder: ...

    @abstractmethod
    def get_balance(self, asset: str) -> Balance | None: ...

    @abstractmethod
    def get_open_orders(self, symbol: str) -> OrderGroup: ...

    @abstractmethod
    def get_position(self, symbol: str) -> Position | None: ...

    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> None: ...

    @abstractmethod
    def get_leverage(self, symbol) -> int: ...
