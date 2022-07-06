from __future__ import annotations

import copy
from typing import Callable

from trader.core.util.common import remove_none
from trader.data.model import Candles

from trader.core.model import OrderGroup, MarketOrder, LimitOrder, Order
from trader.core.exception import PositionError, BalanceError
from trader.core.enumerate import OrderSide, TimeInForce
from trader.core.interface import FuturesTrader
from trader.core.util.trade import create_orders, opposite_side

from trader.backtest.util import is_order_filled, get_filled_first
from trader.backtest.model import BacktestBalance, BacktestPosition


class BacktestFuturesTrader(FuturesTrader, Callable):

    def __init__(
            self,
            balance: BacktestBalance,
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
        self.order_group: OrderGroup | None = None
        self._leverage: int | None = None

        self.position: BacktestPosition | None = None

    @property
    def in_position(self):
        return self.position is not None

    @property
    def not_in_position(self):
        return self.position is None

    def __call__(self, candles: Candles):
        if self.order_group:
            if self.in_position:
                self.position.liquidation_check(
                    low_price=candles.latest_low_price,
                    high_price=candles.latest_high_price,
                    balance=self.balances[-1].free,
                )
                self.position.update(latest_price=candles.latest_close_price)
                self.__exit_logic(candles=candles)
            else:
                self.__entry_logic(candles=candles)

    def __create_position(self, time: int | float, price: float, order: Order):
        return BacktestPosition(
            symbol=order.symbol,
            side=order.side,
            money=order.money,
            quantity=order.quantity,
            leverage=self._leverage,
            entry_order_type=order.type,
            entry_time=int(time),
            entry_price=price,
            entry_fee=self.taker_fee_rate if order.is_taker else self.maker_fee_rate,
        )

    def __entry_logic(
            self,
            candles: Candles,
    ):

        if is_order_filled(
                high_price=candles.latest_high_price,
                low_price=candles.latest_low_price,
                order=self.order_group.entry_order
        ):
            # Calculate fee

            time = candles.latest_time
            price = candles.latest_open_price if self.order_group.entry_order.is_taker else self.order_group.entry_order.price

            self.position = self.__create_position(
                time=time,
                price=price,
                order=self.order_group.entry_order
            )
            self.order_group.entry_order = None

    def __exit_logic(
            self,
            candles: Candles,
    ):
        exit_order = get_filled_first(
            high_price=candles.latest_high_price,
            low_price=candles.latest_low_price,
            open_price=candles.latest_open_price,
            take_profit_order=self.order_group.profit_order,
            trailing_stop_order=self.order_group.trailing_order,
            stop_order=self.order_group.stop_order,
            exit_order=self.order_group.exit_order,
        )

        if exit_order is not None:
            if exit_order.is_taker:
                price = candles.latest_open_price
            elif exit_order.stop_price is not None:
                price = exit_order.stop_price
            elif exit_order.price is not None:
                price = exit_order.price
            else:
                price = candles.latest_close_price

            # Calculate fee

            self.position.close(
                time=candles.latest_time,
                price=price,
                fee=0
            )

            self.balances.append(BacktestBalance(
                time=candles.latest_time,
                asset=self.balances[-1].asset,
                free=self.balances[-1].free + self.position.profit)
            )
            self.positions.append(self.position)
            self.position = None
            self.order_group = None

    def cancel_orders(self, symbol: str):
        if self.order_group is None:
            return []

        orders = copy.deepcopy(self.order_group)
        self.order_group = None
        return orders

    def enter_position(
            self,
            candles: Candles,
            money: float,
            side: int | OrderSide,
            leverage: int,
            price: float = None,
            profit_price: float = None,
            stop_price: float = None,
            trailing_stop_rate: float = None,
            trailing_stop_activation_price: float = None,
    ):
        symbol = candles.symbol

        if money > self.balances[-1].free:
            raise BalanceError(
                f"You tried to enter a position with {money} {self.balances[-1].asset}, "
                f"while your balance is only {self.balances[-1]}."
            )

        if self.in_position:
            raise PositionError(
                f"Creating a {symbol} position is not allowed. "
                f"A {symbol} position is already opened."
            )
        self._leverage = leverage

        entry_orders = create_orders(
            symbol=symbol,
            money=money,
            side=side,
            current_price=candles.latest_close_price,
            order_price=price,
            order_profit_price=profit_price,
            order_stop_price=stop_price,
            order_trailing_stop_rate=trailing_stop_rate,
            order_trailing_stop_activation_price=trailing_stop_activation_price,
        )
        self.orders.extend(remove_none(entry_orders))
        self.order_group = OrderGroup(*entry_orders)

        return self.order_group

    def create_close_order(self, candles: Candles, close_price: float = None, time_in_force: str | TimeInForce = "GTC"):
        if not self.in_position:
            raise PositionError("Unable to create position closing order because there is no open position!")

        close_order = (
            MarketOrder(
                symbol=self.position.symbol,
                side=opposite_side(self.position.side),
                money=self.position.money,
                quantity=self.position.quantity,
                price=candles.latest_close_price,
            )
            if close_price is None
            else LimitOrder(
                symbol=self.position.symbol,
                side=opposite_side(self.position.side),
                money=self.position.money,
                quantity=self.position.quantity,
                price=close_price,
                time_in_force=time_in_force,
            )
        )
        self.orders.append(close_order)

        self.order_group.exit_order = close_order
        return close_order

    def close_position_market(self, candles: Candles):
        if self.not_in_position:
            raise PositionError("No position to close.")

        return self.create_close_order(candles)

    def close_position_limit(self, candles: Candles, price: float, time_in_force: str | TimeInForce = "GTC"):
        if self.not_in_position:
            raise PositionError("No position to close.")

        return self.create_close_order(candles=candles, close_price=price, time_in_force=time_in_force)

    def get_balance(self, asset: str):
        if self.balances[-1].asset == asset:
            return self.balances[-1]
        raise BalanceError(f"{asset} balance not found!")

    def get_open_orders(self, symbol: str):
        if self.order_group is None:
            return []

        return self.order_group

    def get_position(self, symbol: str):
        return self.position

    def set_leverage(self, symbol: str, leverage: int):
        self._leverage = leverage

    def get_leverage(self, symbol) -> int:
        return self._leverage
