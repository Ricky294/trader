from __future__ import annotations

from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable

from trader.core.const import Side, TimeInForce, BrokerEvent
from trader.core.exception import LeverageError, PositionError
from trader.core.model import Balance, Position, Order, Balances, Positions, Orders

from trader.data.model import Percentage, Candles, Symbol

from trader.settings import Settings
from util.observer import Subject


def leverage_constraint(set_leverage: Callable):
    """
    Prevents to set leverage above Settings.leverage_max or below 1.
    """

    @wraps(set_leverage)
    def wrapper(symbol: str, leverage: int):
        if leverage > Settings.leverage_max:
            raise LeverageError(
                f'Trying to set {symbol} leverage to {leverage} while the maximum value is {Settings.leverage_max}.'
            )
        elif leverage < 1:
            raise LeverageError(
                f'Trying to set {symbol} leverage to {leverage}, but it cannot be smaller than 1.'
            )
        return set_leverage(symbol=symbol, leverage=leverage)

    return wrapper


class FuturesBroker(ABC):

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.set_leverage = leverage_constraint(obj.set_leverage)
        return obj

    def __init__(
            self,
    ):
        self.publisher = Subject()

        self.balance_history = Balances()
        self.position_history = Positions()
        self.order_history = Orders()

    @abstractmethod
    def __call__(self, candles: Candles):
        ...

    def _on_candle_close(self, position: Position | None):
        self.publisher.notify(BrokerEvent.ON_CANDLE_CLOSE)

        if position and position.is_open:
            self.publisher.notify(BrokerEvent.ON_IN_POSITION, position)
            if position.profit >= .0:
                self.publisher.notify(BrokerEvent.ON_POSITION_IN_PROFIT, position)
            else:
                self.publisher.notify(BrokerEvent.ON_POSITION_IN_LOSS, position)
        else:
            self.publisher.notify(BrokerEvent.ON_NOT_IN_POSITION)

    def _on_position_change(self, position: Position):
        self.position_history.append(position)
        self.publisher.notify(position.event(), position)

    def _on_orders_create(self, orders: list[Order]):
        if orders:
            self.order_history.extend(orders)
            self.publisher.notify(BrokerEvent.ON_ORDERS_CREATE, orders)

    def _on_orders_fill(self, orders: list[Order]):
        if orders:
            self.order_history.extend(orders)
            self.publisher.notify(BrokerEvent.ON_ORDERS_FILL, orders)

    def _on_orders_cancel(self, orders: list[Order]):
        if orders:
            self.order_history.extend(orders)
            self.publisher.notify(BrokerEvent.ON_ORDERS_CANCEL, orders)

    def _on_balance_change(self, new_balance: Balance):
        self.balance_history.append(new_balance)
        self.publisher.notify(BrokerEvent.ON_BALANCE_CHANGE, new_balance)

    def _on_leverage_change(self, symbol: Symbol, leverage: int):
        self.publisher.notify(BrokerEvent.ON_LEVERAGE_CHANGE, symbol, leverage)

    @abstractmethod
    def cancel_orders(self, symbol: Symbol) -> list[Order]:
        ...

    @abstractmethod
    def enter_position(
            self,
            symbol: Symbol,
            amount:  float | Percentage,
            side: Side,
            entry_price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ) -> list[Order]:
        """
        Creates a limit/market order and optionally stop loss and take profit market orders based on parameters.

        :param symbol: Symbol to open position for.
        :param amount: Position entry size.
        :param side: Position side - Buy/Sell - Long/Short.
        :param entry_price: Creates a market order if None, else a limit order (Optional).
        :param take_profit_price: Creates take profit market order if defined (Optional).
        :param stop_loss_price: Creates a stop loss market order if defined (Optional).
        :return: Created orders.

        :raises SymbolError: If symbol is invalid.
        :raises InvalidOrder: If take_profit_price or stop_loss_price is incorrect.
        :raises BalanceError: If asset is invalid or if the available balance is insufficient.
        :raises PositionError: If symbol position is already opened.
        """
        ...

    def close_position(
            self,
            symbol: Symbol,
            price: float = None,
            time_in_force=TimeInForce.GTC
    ) -> Order:
        """
        Creates a market or limit order to close current open `symbol` position.

        * price is None -> market order
        * price is number -> limit order

        :raises SymbolError: If symbol is invalid.
        :raises PositionError: If there is no open position for symbol.
        :raises InvalidPrice: If price is invalid.
        :raises TimeInForceError: If time in force is not supported.
        """

        if price:
            return self.close_position_limit(symbol=symbol, price=price, time_in_force=time_in_force)
        return self.close_position_market(symbol=symbol)

    def _get_open_position_or_raise_error(
            self,
            symbol: Symbol,
    ) -> Position:
        """
        Creates a market order to close current open `symbol` position.

        :raises SymbolError: If symbol is invalid.
        :raises PositionError: If there is no open position for symbol.
        """
        position = self.get_position(symbol=symbol)

        if position:
            return position

        raise PositionError(f'No open {symbol} position to close!')

    @abstractmethod
    def close_position_market(self, symbol: Symbol) -> Order:
        """
        Creates a limit order to close current open `symbol` position.

        :raises SymbolError: If symbol is invalid.
        :raises PositionError: If there is no open position for symbol.
        """
        ...

    @abstractmethod
    def close_position_limit(self, symbol: Symbol, price: float, time_in_force=TimeInForce.GTC) -> Order:
        """
        Creates a limit order to close current open `symbol` position.

        :raises SymbolError: If symbol is invalid.
        :raises PositionError: If there is no open position for symbol.
        :raises InvalidPrice: If price is invalid.
        :raises TimeInForceError: If time in force is not supported.
        """
        ...

    @abstractmethod
    def get_balance(self, symbol: Symbol) -> Balance:
        """Returns quote currency balance.

        :raises BalanceError: If no balance found for asset.
        """
        ...

    @abstractmethod
    def get_open_orders(self, symbol: Symbol) -> list[Order]:
        """
        Returns all open orders for `symbol`.

        :raise SymbolError: If symbol is invalid.
        """
        ...

    @abstractmethod
    def get_position(self, symbol: Symbol) -> Position | None:
        """Returns Position object if there is an open position.

        Returns None if there is no open position.

        :raise SymbolError: If symbol is invalid.
        """
        ...

    @abstractmethod
    def set_leverage(self, symbol: Symbol, leverage: int) -> None:
        """
        Changes `leverage` on `symbol`.

        :raise SymbolError: If symbol is invalid.
        :raise LeverageError: If leverage is invalid.
        """
        ...

    @abstractmethod
    def get_leverage(self, symbol: Symbol) -> int:
        """
        Returns leverage for `symbol`.

        :raise SymbolError: If symbol is invalid.
        """
        ...

    def cancel_all(self, symbol: Symbol):
        """
        Closes position and cancels all orders on `symbol`.

        :raises SymbolError: If symbol is invalid.
        """
        self.cancel_orders(symbol=symbol)

        position = self.get_position(symbol=symbol)

        if position and position.is_open:
            self.close_position(symbol=symbol)
