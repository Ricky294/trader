from __future__ import annotations

import logging
from typing import Callable

from trader.backtest.log import get_backtest_logger
from trader.backtest.model import BacktestPosition
from trader.backtest.util import (
    get_filled_orders,
    is_position_liquidated,
    calculate_liquidation_price,
)

from trader.config import BACKTEST_LOGGING
from trader.core.super_enum import OrderSide, TimeInForce, OrderType
from trader.core.exception import PositionError, BalanceError, LiquidationError
from trader.core.interface import FuturesBroker
from trader.core.model import MarketOrder, LimitOrder, Order, Balance
from trader.core.util.common import remove_none, log_method_return
from trader.core.util.trade import create_orders, calculate_fee

from trader.data.model import Candles


@log_method_return(logger=get_backtest_logger(), level=logging.INFO, log=BACKTEST_LOGGING)
class BacktestFuturesBroker(FuturesBroker, Callable):

    def __init__(
            self,
            balance: Balance,
            liquidation=False,
            maker_fee_rate=0.0,
            taker_fee_rate=0.0,
    ):
        """
        Maker fee is applied if the order goes into the order book (e.g. limit order)
        Taker fee is applied if the order fills immediately (e.g. market order)

        :param liquidation: If True position can get liquidated in case of huge position loss.
        """
        super().__init__()
        self.liquidation = liquidation

        self.start_balance = balance
        self.balances = [balance]

        self.maker_fee_rate = maker_fee_rate
        self.taker_fee_rate = taker_fee_rate

        self.positions: list[BacktestPosition] = []

        self.orders: list[Order] = []
        self.open_orders: list[Order] = []

        self.entry_fees: list[float] = []
        self.exit_fees: list[float] = []

        self._candles: Candles | None = None
        self._leverage: int | None = None
        self.position: BacktestPosition | None = None

    def _is_position_liquidated(self, candles: Candles):
        return (
            is_position_liquidated(
                side=self.position.side,
                leverage=self.position.leverage,
                average_entry_price=self.position.entry_price,
                maintenance_margin_rate=0,
                candles=candles,
            )
            if self.position
            else False
        )

    def _calculate_liquidation_price(self):
        return (
            calculate_liquidation_price(
                side=self.position.side,
                leverage=self.position.leverage,
                average_entry_price=self.position.entry_price,
                maintenance_margin_rate=0,
            ) if self.position
            else False
        )

    def _get_filled_orders(self, candles: Candles):
        return get_filled_orders(
            candles=candles,
            orders=self.open_orders,
        )

    def __call__(self, candles: Candles):
        self._candles = candles

        if self.liquidation and self._is_position_liquidated(candles):
            liquidation_price = self._calculate_liquidation_price()
            self.position.update(latest_price=liquidation_price)
            raise LiquidationError(f'{self.position} liquidated at price: {liquidation_price}.')

        if self.position:
            self.position.update(latest_price=candles.latest_close_price)

        filled_orders = self._get_filled_orders(candles)

        for order in filled_orders:
            if order.is_taker:
                order.price = candles.latest_open_price

            if not self.position:
                self.position = self._create_position(
                    time=candles.latest_time,
                    order=order,
                )
            else:
                self._close_position(
                    time=candles.latest_time,
                    order=order,
                )
            self.open_orders.remove(order)

    @property
    def _latest_balance(self):
        return self.balances[-1]

    def _calculate_fee(self, order: Order):
        fee_rate = self.taker_fee_rate if order.is_taker else self.maker_fee_rate
        return calculate_fee(quantity=order.quantity, price=order.price, fee_rate=fee_rate)

    def _create_position(self, time: float, order: Order):
        fee = self._calculate_fee(order)
        self.entry_fees.append(fee)

        self.balances.append(
            self._latest_balance.copy_init(time=time, free=self._latest_balance.available - fee)
        )

        return BacktestPosition(
            entry_time=time,
            symbol=order.symbol,
            entry_price=order.price,
            side=order.side,
            amount=order.amount,
            quantity=order.quantity,
            leverage=self._leverage,
        )

    def _close_position(self, time: float, order: Order):
        fee = self._calculate_fee(order)
        self.exit_fees.append(fee)

        self.position.close(
            time=time,
            price=order.price,
        )

        self.balances.append(
            Balance(
                time=time,
                asset=self._latest_balance.asset,
                available=self._latest_balance.available + self.position.profit - fee
            )
        )

        self.positions.append(self.position)
        self.position = None

    def finished(self):
        if self.position:
            self.positions.append(self.position)

    def cancel_orders(self, symbol: str):
        for order in self.open_orders:
            if order.symbol == symbol:
                self.open_orders.remove(order)

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
    ):
        if amount > self._latest_balance.available:
            raise BalanceError(
                f"You tried to enter a position with {amount} {asset}, "
                f"while your balance is only {self._latest_balance}."
            )

        if self.position:
            raise PositionError(
                f"Creating a {symbol} position is not allowed. "
                f"A {symbol} position is already opened."
            )
        self._leverage = leverage

        orders = create_orders(
            symbol=symbol,
            amount=amount,
            type=OrderType.MARKET if price is None else OrderType.LIMIT,
            side=side,
            leverage=leverage,
            price=self._candles.latest_open_price if price is None else price,
            profit_price=profit_price,
            stop_price=stop_price,
            trailing_stop_rate=trailing_stop_rate,
            trailing_stop_activation_price=trailing_stop_activation_price,
        )
        orders = remove_none(orders)
        self.orders.extend(orders)
        self.open_orders.extend(orders)

        return orders

    def create_order(self, order: Order):
        self.orders.append(order)
        self.open_orders.append(order)

    def __raise_error_if_not_in_position(self, msg: str):
        if not self.position:
            raise PositionError(msg)

    def close_position_market(self):
        self.__raise_error_if_not_in_position('No position to close!')

        order = MarketOrder(
            symbol=self.position.symbol,
            side=self.position.side.opposite(),
            amount=self.position.amount,
            quantity=self.position.quantity,
            price=self._candles.latest_open_price,
        )
        self.create_order(order)
        return order

    def close_position_limit(self, price: float, time_in_force=TimeInForce.GTC):
        self.__raise_error_if_not_in_position('No position to close!')

        order = LimitOrder(
            symbol=self.position.symbol,
            side=self.position.side.opposite(),
            amount=self.position.amount,
            quantity=self.position.quantity,
            price=price,
            time_in_force=time_in_force,
        )
        self.create_order(order)
        return order

    def get_balance(self, asset: str):
        if self._latest_balance.asset == asset:
            return self._latest_balance
        raise BalanceError(f"{asset} balance not found!")

    def get_open_orders(self, symbol: str):
        return self.open_orders

    def get_position(self, symbol: str):
        return self.position

    def set_leverage(self, symbol: str, leverage: int):
        self._leverage = leverage

    def get_leverage(self, symbol) -> int:
        return self._leverage
