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
from trader.core.enumerate import OrderSide, TimeInForce
from trader.core.exception import PositionError, BalanceError, LiquidationError
from trader.core.interface import FuturesBroker
from trader.core.model import MarketOrder, LimitOrder, Order, Balance
from trader.core.util.common import remove_none, log_method_return
from trader.core.util.trade import create_orders, opposite_side, calculate_quantity, calculate_fee

from trader.data.model import Candles


@log_method_return(logger=get_backtest_logger(), level=logging.INFO, log=BACKTEST_LOGGING)
class BacktestFuturesBroker(FuturesBroker, Callable):

    def __init__(
            self,
            balance: Balance,
            maker_fee_rate=0.0,
            taker_fee_rate=0.0,
    ):
        """
        Maker fee is applied if the order goes into the order book (e.g. limit order)
        Taker fee is applied if the order fills immediately (e.g. market order)
        """
        super().__init__()

        self.start_balance = balance
        self.balances = [balance]

        self.maker_fee_rate = maker_fee_rate
        self.taker_fee_rate = taker_fee_rate

        self.positions: list[BacktestPosition] = []

        self.orders: list[Order] = []
        self.open_orders: list[Order] = []

        self.entry_fees: list[float] = []
        self.exit_fees: list[float] = []

        self._leverage: int | None = None

        self.position: BacktestPosition | None = None

    def _is_position_liquidated(self, candles: Candles):
        return (
            False if self.position
            else is_position_liquidated(
                side=self.position.side,
                leverage=self.position.leverage,
                average_entry_price=self.position.entry_price,
                maintenance_margin_rate=0,
                candles=candles,
            )
        )

    def _calculate_liquidation_price(self):
        return (
            False if self.position
            else calculate_liquidation_price(
                side=self.position.side,
                leverage=self.position.leverage,
                average_entry_price=self.position.entry_price,
                maintenance_margin_rate=0,
            )
        )

    def _get_filled_orders(self, candles: Candles):
        return get_filled_orders(
            candles=candles,
            orders=self.open_orders,
        )

    def __call__(self, candles: Candles):
        # if self._is_position_liquidated(candles):
        #     liquidation_price = self._calculate_liquidation_price()
        #     self.position.update(latest_price=liquidation_price)
        #     raise LiquidationError(f'{self.position} liquidated at price: {liquidation_price}.')

        if self.position:
            self.position.update(latest_price=candles.latest_close_price)

        filled_orders = self._get_filled_orders(candles)

        for order in filled_orders:
            # order.type: STOP_MARKET, TAKE_PROFIT_MARKET, STOP_LIMIT or TAKE_PROFIT_LIMIT
            if order.stop_price is not None:
                price = order.stop_price
            # order.type: LIMIT
            elif order.price is not None:
                price = order.price
            # order.type: MARKET
            else:
                price = candles.latest_open_price

            if not self.position:
                self.position = self._create_position(
                    time=candles.latest_time,
                    price=price,
                    order=order,
                )
            else:
                self._close_position(
                    time=candles.latest_time,
                    price=price,
                    order=order,
                )
            self.open_orders.remove(order)

    @property
    def __latest_balance(self):
        return self.balances[-1]

    def _calculate_fee(self, order: Order, price: float):
        fee_rate = self.taker_fee_rate if order.is_taker else self.maker_fee_rate
        return calculate_fee(quantity=order.amount / price, price=price, fee_rate=fee_rate)

    def _create_position(self, time: int | float, price: float, order: Order):
        fee = self._calculate_fee(order, price)
        self.entry_fees.append(fee)

        self.balances.append(
            self.__latest_balance.copy_init(free=self.__latest_balance.free - fee)
        )

        return BacktestPosition(
            symbol=order.symbol,
            side=order.side,
            amount=order.amount,
            quantity=calculate_quantity(amount=order.amount, price=price, leverage=self._leverage),
            leverage=self._leverage,
            entry_time=time,
            entry_price=price,
        )

    def _close_position(self, time, price, order: Order):
        fee = self._calculate_fee(order, price)
        self.exit_fees.append(fee)

        self.position.close(
            time=time,
            price=price,
        )

        self.balances.append(
            Balance(
                time=time,
                asset=self.__latest_balance.asset,
                free=self.__latest_balance.free + self.position.profit - fee
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
            side: int | str | OrderSide,
            leverage: int,
            price: float = None,
            profit_price: float = None,
            stop_price: float = None,
            trailing_stop_rate: float = None,
            trailing_stop_activation_price: float = None,
    ):
        if amount > self.__latest_balance.free:
            raise BalanceError(
                f"You tried to enter a position with {amount} {asset}, "
                f"while your balance is only {self.__latest_balance}."
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
            side=side,
            order_price=price,
            order_profit_price=profit_price,
            order_stop_price=stop_price,
            order_trailing_stop_rate=trailing_stop_rate,
            order_trailing_stop_activation_price=trailing_stop_activation_price,
        )
        orders = remove_none(orders)
        self.orders.extend(orders)
        self.open_orders.extend(orders)

        return orders

    def create_order(self, order: Order):
        self.orders.append(order)
        self.open_orders.append(order)

    def create_close_order(self, price: float = None, time_in_force: str | TimeInForce = "GTC"):
        if not self.position:
            raise PositionError("Unable to create position closing order because there is no open position!")

        close_order = (
            MarketOrder(
                symbol=self.position.symbol,
                side=opposite_side(self.position.side),
                amount=self.position.amount,
                quantity=self.position.quantity,
                price=None,
            )
            if price is None
            else LimitOrder(
                symbol=self.position.symbol,
                side=opposite_side(self.position.side),
                amount=self.position.amount,
                quantity=self.position.quantity,
                price=price,
                time_in_force=time_in_force,
            )
        )
        self.orders.append(close_order)
        self.open_orders.append(close_order)

        return close_order

    def close_position_market(self):
        if not self.position:
            raise PositionError("No position to close.")

        return self.create_close_order()

    def close_position_limit(self, price: float, time_in_force: str | TimeInForce = "GTC"):
        if not self.in_position:
            raise PositionError("No position to close.")

        return self.create_close_order(price=price, time_in_force=time_in_force)

    def get_balance(self, asset: str):
        if self.__latest_balance.asset == asset:
            return self.__latest_balance
        raise BalanceError(f"{asset} balance not found!")

    def get_open_orders(self, symbol: str):
        return self.open_orders

    def get_position(self, symbol: str):
        return self.position

    def set_leverage(self, symbol: str, leverage: int):
        self._leverage = leverage

    def get_leverage(self, symbol) -> int:
        return self._leverage
