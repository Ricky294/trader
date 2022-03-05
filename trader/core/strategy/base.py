import logging
from abc import ABC, abstractmethod
from typing import Callable, Union, List, Optional

import numpy as np

from ..enum import OrderSide, TimeInForce
from ..interface import FuturesTrader
from ..model import Candles, Position, Order, Balance


class Strategy(FuturesTrader, Callable, ABC):

    def __init__(self, trader: FuturesTrader, **kwargs):
        from trader.backtest import BacktestFuturesTrader
        self.trader = trader

        is_backtest = isinstance(trader, BacktestFuturesTrader)

        self.logger = logging.getLogger(
            "trader.strategy.backtest"
            if is_backtest
            else "trader.strategy.live"
        )

    def on_entry_order(self, symbol: str, orders: List[Order]): ...

    def on_close_order(self, symbol: str, order: Order): ...

    def on_cancel_orders(self, symbol: str, orders: List[Order]): ...

    def on_get_position(self, symbol: str, position: Optional[Position]): ...

    def on_set_leverage(self, symbol: str, leverage: int): ...

    def on_get_balance(self, asset: str, balance: Optional[Balance]): ...

    def on_get_open_orders(self, symbol: str, orders: List[Order]): ...

    def create_position(
            self,
            symbol: str,
            money: float,
            side: Union[int, OrderSide],
            leverage: int,
            price: Optional[float] = None,
            take_profit_price: Optional[float] = None,
            stop_loss_price: Optional[float] = None
    ):
        orders = self.trader.create_position(
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

    def cancel_orders(self, symbol: str) -> List[Order]:
        orders = self.trader.cancel_orders(symbol)
        self.on_cancel_orders(symbol=symbol, orders=orders)
        return orders

    def get_open_orders(self, symbol: str) -> List[Order]:
        orders = self.trader.get_open_orders(symbol)
        self.on_get_open_orders(symbol, orders)
        return orders

    def set_leverage(self, symbol: str, leverage: int) -> None:
        self.trader.set_leverage(symbol=symbol, leverage=leverage)
        self.on_set_leverage(symbol=symbol, leverage=leverage)

    def close_position_limit(self, symbol: str, price, time_in_force: TimeInForce = "GTC") -> Order:
        order = self.trader.close_position_limit(symbol=symbol, price=price, time_in_force=time_in_force)
        self.on_close_order(symbol, order)
        return order

    def close_position_market(self, symbol: str) -> Order:
        order = self.trader.close_position_market(symbol=symbol)
        self.on_close_order(symbol, order)
        return order

    def get_position(self, symbol: str) -> Optional[Position]:
        position = self.trader.get_position(symbol)
        self.on_get_position(symbol, position)
        return position

    def get_latest_price(self, symbol: str) -> float:
        return self.trader.get_latest_price(symbol)

    def get_balance(self, asset: str) -> Optional[Balance]:
        balance = self.trader.get_balance(asset)
        self.on_get_balance(asset, balance)
        return balance

    def __call__(self, candles: Union[Candles, np.ndarray]):
        if isinstance(candles, np.ndarray):
            candles = Candles.with_data(candles)

        self.on_next(candles)

    @abstractmethod
    def on_next(self, *args, **kwargs): ...
