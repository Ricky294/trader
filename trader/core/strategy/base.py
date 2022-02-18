import logging
from abc import ABC, abstractmethod
from typing import Callable, Union, List, Optional

import numpy as np

from ..interface import FuturesTrader
from ..model import Candles, Position, Order, Balance


class Strategy(Callable, ABC):

    def __init__(self, trader: FuturesTrader, **kwargs):
        self.trader = trader
        self.trader.on_entry_order = self.on_entry_order
        self.trader.on_close_order = self.on_close_order
        self.trader.on_cancel_orders = self.on_cancel_orders
        self.trader.on_get_position = self.on_get_position
        self.trader.on_get_balance = self.on_get_balance
        self.trader.on_set_leverage = self.on_set_leverage

        from trader.backtest import BacktestFuturesTrader
        self.logger = logging.getLogger(
            "trader.strategy.backtest"
            if isinstance(trader, BacktestFuturesTrader)
            else "trader.strategy.live"
        )

    def on_entry_order(self, symbol: str, orders: List[Order]): ...

    def on_close_order(self, symbol: str, order: Order): ...

    def on_cancel_orders(self, symbol: str, orders: List[Order]): ...

    def on_get_position(self, symbol: str, position: Optional[Position]): ...

    def on_set_leverage(self, symbol: str, leverage: int): ...

    def on_get_balance(self, asset: str, balance: Optional[Balance]): ...

    def __call__(self, candles: Union[Candles, np.ndarray]):
        if isinstance(candles, np.ndarray):
            candles = Candles.with_data(candles)

        self.on_next(candles)

    @abstractmethod
    def on_next(self, *args, **kwargs): ...
