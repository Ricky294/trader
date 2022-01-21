import copy
from typing import Callable, Optional, List, Union

import numpy as np

from ..core.model import Balance, LimitOrder, MarketOrder, StopMarketOrder, TakeProfitMarketOrder
from ..core.interface import FuturesTrader
from ..core.const.trade_actions import SELL, BUY
from ..core.const.candle_index import (
    OPEN_TIME_INDEX,
    OPEN_PRICE_INDEX,
    HIGH_PRICE_INDEX,
    LOW_PRICE_INDEX,
    CLOSE_PRICE_INDEX,
)
from ..core.util.common import interval_to_seconds
from ..core.util.trade import create_position, calculate_fee

from .position import BacktestPosition


class BacktestFuturesTrader(FuturesTrader, Callable):

    def __init__(
            self,
            symbol: str,
            interval: str,
            maker_fee_rate=0.0,
            taker_fee_rate=0.0,
            balance: Balance = Balance("USDT", total=1_000, available=1_000),
            leverage=1,
    ):
        """
        Maker fee is applied if the order goes into the order book (e.g. limit order)
        Taker fee is applied if the order fills immediately (e.g. market order)
        """

        super().__init__()
        self.total_fee_cost = .0
        self.symbol = symbol
        self.maker_fee_rate = maker_fee_rate
        self.taker_fee_rate = taker_fee_rate
        self.interval_in_seconds = interval_to_seconds(interval)

        self._leverage = leverage

        self.initial_balance = copy.deepcopy(balance)
        self.balance = balance

        self.positions: List[BacktestPosition] = []
        self.position: Optional[BacktestPosition] = None

        self.order: Union[Optional[LimitOrder], Optional[MarketOrder]] = None
        self.stop_order: Optional[StopMarketOrder] = None
        self.take_profit_order: Optional[TakeProfitMarketOrder] = None

        self.latest_open_time: int
        self.latest_high_price: float
        self.latest_low_price: float
        self.latest_close_price: float

    def _is_limit_buy_hit(self):
        return (
            self.order.side == BUY
            and self.low_price < self.order.price
        )

    def _is_limit_sell_hit(self):
        return (
            self.order.side == SELL
            and self.high_price > self.order.price
        )

    def _is_stop_loss_hit(self):
        if self.stop_order is None:
            return False

        return (
            self.low_price < self.stop_order.stop_price
            if self.position.side == BUY
            else self.high_price > self.stop_order.stop_price
        )

    def _is_take_profit_hit(self):
        if self.take_profit_order is None:
            return False

        return (
            self.high_price > self.take_profit_order.stop_price
            if self.position.side == BUY
            else self.low_price < self.take_profit_order.stop_price
        )

    def get_order(self):
        return self.order

    def get_take_profit_order(self):
        return self.take_profit_order

    def get_stop_loss_order(self):
        return self.stop_order

    def __apply_fee(self, price: float, quantity: float, is_taker: bool):
        fee = calculate_fee(
            price=price,
            quantity=quantity,
            fee_rate=self.taker_fee_rate if is_taker else self.maker_fee_rate,
            leverage=self._leverage
        )

        self.balance.total -= fee
        self.balance.available -= fee
        self.total_fee_cost += fee

    def __create_or_adjust_position(self, price: float, quantity: float, is_taker: bool):
        self.__apply_fee(price, quantity, is_taker)
        fee_reduced_quantity = quantity - (quantity * self.taker_fee_rate if is_taker else self.maker_fee_rate)

        if self.position is None:
            self.position = BacktestPosition(
                symbol=self.symbol,
                entry_time=self.open_time,
                entry_price=price,
                entry_quantity=fee_reduced_quantity,
                leverage=self._leverage,
            )
            self.balance.available -= price * abs(quantity)
        else:
            # It's not properly calculated...
            raise NotImplementedError
            self.position.adjust(
                time=self.open_time,
                price=price,
                quantity=quantity,
            )

            self.balance.total += self.position.profit()
            self.balance.available = self.balance.total
            self.positions.append(self.position)
            self.position = None

    def __call__(self, candles: np.ndarray):
        latest_candle = candles[-1]
        self.open_time = latest_candle[OPEN_TIME_INDEX]
        self.high_price = latest_candle[HIGH_PRICE_INDEX]
        self.low_price = latest_candle[LOW_PRICE_INDEX]
        self.close_price = latest_candle[CLOSE_PRICE_INDEX]
        self.open_price = latest_candle[OPEN_PRICE_INDEX]

        if self.position is not None:
            self.position(candles, balance=self.balance)

            take_profit_hit = self._is_take_profit_hit()
            stop_hit = self._is_stop_loss_hit()

            if take_profit_hit and stop_hit:
                high_distance = self.high_price - self.open_price
                low_distance = self.open_price - self.low_price

                take_profit_distance = abs(self.open_price - self.take_profit_order.stop_price)
                stop_loss_distance = abs(self.open_price - self.stop_order.stop_price)

                if high_distance / take_profit_distance > low_distance / stop_loss_distance:
                    stop_hit = False
                else:
                    take_profit_hit = False

            if take_profit_hit:
                self._close_position(self.take_profit_order.stop_price, is_taker=True)
                self.take_profit = None
                self.stop_order = None
            elif stop_hit:
                self._close_position(self.stop_order.stop_price, is_taker=True)
                self.take_profit = None
                self.stop_order = None

                if self.balance.total <= 0:
                    from trader.backtest import NotEnoughFundsError
                    raise NotEnoughFundsError(
                        f"You got liquidated! Final balance: {self.balance}"
                    )

        if self.order is not None:
            is_market_order = True if self.order.price is None else False

            self.__create_or_adjust_position(
                price=self.close_price if is_market_order else self.order.price,
                quantity=self.order.quantity,
                is_taker=is_market_order,
            )
            self.order = None

    def cancel_orders(self, symbol: str):
        self.order = None
        self.take_profit_order = None
        self.stop_order = None

    def cancel_order(self, symbol: str):
        self.order = None

    def cancel_take_profit_order(self, symbol: str):
        self.take_profit_order = None

    def cancel_stop_loss_orders(self, symbol: str):
        self.stop_order = None

    def create_position(
            self,
            symbol: str,
            quantity: float,
            entry_price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ):

        self.order, self.stop_order, self.take_profit_order = create_position(
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price
        )

    def _close_position(self, price: float, is_taker: bool):
        if self.position is not None:
            self.__apply_fee(price, self.position.quantity, is_taker=is_taker)

            self.position.close(
                time=self.open_time,
                price=price,
            )
            self.balance.total += self.position.profit()
            self.balance.available = self.balance.total
            self.positions.append(self.position)
            self.position = None

    def close_position(self, symbol: str):
        self._close_position(self.close_price, is_taker=True)

    def get_balances(self) -> List[Balance]:
        return [self.balance]

    def get_balance(self, asset: str) -> Balance:
        return self.balance

    def get_open_orders(self, symbol: str):
        open_orders = []
        if self.order is not None:
            open_orders.append(self.order)
        elif self.take_profit_order is not None:
            open_orders.append(self.take_profit_order)
        elif self.stop_order is not None:
            open_orders.append(self.stop_order)
        return open_orders

    def get_position(self, symbol: str) -> Optional[BacktestPosition]:
        return self.position

    def set_leverage(self, symbol: str, leverage: int):
        self._leverage = leverage

    def get_leverage(self, symbol) -> int:
        return self._leverage
