from __future__ import annotations

import copy
from typing import Callable

from trader.data.model import Candles

from trader.core.model import Orders, MarketOrder, LimitOrder
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

        self.start_balance = copy.deepcopy(balance)
        self.balance = balance

        self.maker_fee_rate = maker_fee_rate
        self.taker_fee_rate = taker_fee_rate

        self.positions: list[BacktestPosition] = []

        self.orders: Orders | None = None
        self._leverage: int | None = None

        self.position: BacktestPosition | None = None

    @property
    def in_position(self):
        return self.position is not None

    @property
    def not_in_position(self):
        return self.position is None

    def __call__(self, candles: Candles):
        if self.orders:
            if self.in_position:
                self.position.liquidation_check(
                    low_price=candles.latest_low_price,
                    high_price=candles.latest_high_price,
                    balance=self.balance.free,
                )
                self.position.update_profit(close_price=candles.latest_close_price)
                self.__exit_logic(candles=candles)
            else:
                self.__entry_logic(candles=candles)

    def __entry_logic(
            self,
            candles: Candles,
    ):
        if is_order_filled(
                high_price=candles.latest_high_price,
                low_price=candles.latest_low_price,
                order=self.orders.entry_order
        ):
            # Calculate fee

            self.position = BacktestPosition(
                symbol=self.orders.entry_order.symbol,
                side=self.orders.entry_order.side,
                money=self.orders.entry_order.money,
                leverage=self._leverage,
                entry_time=int(candles.latest_open_time),
                entry_price=candles.latest_close_price if self.orders.entry_order.is_taker else self.orders.entry_order.price,
                entry_fee=self.taker_fee_rate if self.orders.entry_order.is_taker else self.maker_fee_rate,
            )
            self.orders.entry_order = None

    def __exit_logic(
            self,
            candles: Candles,
    ):
        exit_order = get_filled_first(
            high_price=candles.latest_high_price,
            low_price=candles.latest_low_price,
            open_price=candles.latest_open_price,
            take_profit_order=self.orders.profit_order,
            trailing_stop_order=self.orders.trailing_order,
            stop_order=self.orders.stop_order,
            exit_order=self.orders.exit_order,
        )

        if exit_order is not None:
            if exit_order.stop_price is not None:
                price = exit_order.stop_price
            elif exit_order.price is not None:
                price = exit_order.price
            else:
                price = candles.latest_close_price

            # Calculate fee

            self.position.set_exit(
                time=candles.latest_open_time,
                price=price,
                fee=0
            )

            self.positions.append(self.position)
            self.position = None
            self.orders = None

    def cancel_orders(self, symbol: str):
        if self.orders is None:
            return []

        orders = copy.deepcopy(self.orders)
        self.orders = None
        return orders

    def create_position(
            self,
            symbol: str,
            money: float,
            side: int | OrderSide,
            leverage: int,
            price: float = None,
            profit_price: float = None,
            stop_price: float = None,
            trailing_stop_rate: float = None,
            trailing_stop_activation_price: float = None,
    ):
        if money > self.balance.free:
            raise BalanceError(
                f"You tried to enter a position with {money} {self.balance.asset}, "
                f"while your balance is only {self.balance}."
            )

        if self.in_position:
            raise PositionError(
                f"Creating a {symbol} position is not allowed. "
                f"A {symbol} position is already opened."
            )
        self._leverage = leverage
        self.orders = Orders(
            *create_orders(
                symbol=symbol,
                money=money,
                side=side,
                price=price,
                profit_price=profit_price,
                stop_price=stop_price,
                trailing_stop_rate=trailing_stop_rate,
                trailing_stop_activation_price=trailing_stop_activation_price,
            )
        )

        return self.orders

    def create_close_order(self, price: float = None):
        if not self.in_position:
            raise PositionError("Unable to create position closing order because there is no open position!")

        self.orders.exit_order = (
            MarketOrder(
                symbol=self.position.symbol,
                side=opposite_side(self.position.side),
                money=self.position.money,
            )
            if price is None
            else LimitOrder(
                symbol=self.position.symbol,
                side=opposite_side(self.position.side),
                money=self.position.money,
                price=price,
            )
        )
        return self.orders.exit_order

    def close_position_market(self, symbol: str):
        if self.not_in_position:
            raise PositionError("No position to close.")

        return self.create_close_order()

    def close_position_limit(self, symbol: str, price: float, time_in_force: str | TimeInForce = "GTC"):
        if self.not_in_position:
            raise PositionError("No position to close.")

        return self.create_close_order(price)

    def get_balance(self, asset: str):
        if self.balance.asset == asset:
            return self.balance
        raise BalanceError(f"{asset} balance not found!")

    def get_open_orders(self, symbol: str):
        if self.orders is None:
            return []

        return self.orders

    def get_position(self, symbol: str):
        return self.position

    def set_leverage(self, symbol: str, leverage: int):
        self._leverage = leverage

    def get_leverage(self, symbol) -> int:
        return self._leverage
