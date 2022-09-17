from __future__ import annotations

import logging
from functools import wraps

from trader.backtest import BacktestFuturesBroker

from trader.core.const import Mode
from trader.core.interface import FuturesBroker
from trader.core.model import Balance, Position, Order
from trader.core.util import(
    store_iterable_object_names,
    cache_array_return_annotated_funcs,
    sliced_iterable_getattribute_wrapper,
)

from trader.data.model import Candles
from trader.log import logger


def set_broker_callbacks(strategy: Strategy, broker: FuturesBroker):
    broker.on_new_orders = strategy.on_new_orders
    broker.on_filled_orders = strategy.on_filled_orders
    broker.on_cancel_orders = strategy.on_cancel_orders

    broker.on_position_close = strategy.on_position_close
    broker.on_position_open = strategy.on_position_open

    broker.on_balance_change = strategy.on_balance_change
    broker.on_balance_gain = strategy.on_balance_gain
    broker.on_balance_loss = strategy.on_balance_loss


def _strategy_init_wrapper(init):

    @wraps(init)
    def wrapper(self, *args, **kwargs):
        self._candles = kwargs.pop('_Strategy__candles')
        self._broker = kwargs.pop('_Strategy__broker')

        init(self, *args, **kwargs)

        store_iterable_object_names(self)
        cache_array_return_annotated_funcs(self)

        set_broker_callbacks(strategy=self, broker=self._broker)

        self.__class__.__getattribute__ = sliced_iterable_getattribute_wrapper(self.__class__.__getattribute__)

    return wrapper


class StrategyMeta(type):

    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        cls.__init__ = _strategy_init_wrapper(cls.__init__)
        return cls


class Strategy(metaclass=StrategyMeta):

    @property
    def logger(self) -> logging.Logger:
        return logger.backtest if self.mode is Mode.BACKTEST else logger.live

    @property
    def broker(self) -> FuturesBroker:
        return self._broker

    @property
    def candles(self) -> Candles:
        return self._candles

    @property
    def mode(self) -> Mode:
        return Mode.BACKTEST if isinstance(self._broker, BacktestFuturesBroker) else Mode.LIVE

    def __call__(self, candles: Candles):
        self._candles = candles
        position = self._broker.position

        self.on_new_candle()
        self.on_in_position(position) if position else self.on_not_in_position()

    def on_new_candle(self):
        """Called on every candle close."""
        ...

    def on_in_position(self, position: Position):
        """Called on every new candle if there is an open position."""
        ...

    def on_not_in_position(self):
        """Called on every new candle if there is no open position."""
        ...

    def on_position_open(self, position: Position):
        """Called on new position open."""
        ...

    def on_position_close(self, closed_position: Position):
        """Called on position close."""
        ...

    def on_balance_change(self, prev_balance: Balance, curr_balance: Balance):
        """Called on balance change."""
        ...

    def on_balance_gain(self, prev_balance: Balance, curr_balance: Balance):
        """Called on balance increase."""
        ...

    def on_balance_loss(self, prev_balance: Balance, curr_balance: Balance):
        """Called on balance decrease."""
        ...

    def on_position_profit(self, prev_balance: Balance, curr_balance: Balance):
        """Called on position closed in profit."""
        ...

    def on_position_loss(self, prev_balance: Balance, curr_balance: Balance):
        """Called on position closed in loss."""
        ...

    def on_new_orders(self, new_orders: list[Order]):
        """Called when new order is created."""
        ...

    def on_cancel_orders(self, canceled_order: list[Order]):
        """Called when an open order gets canceled."""
        ...

    def on_filled_orders(self, filled_orders: list[Order]):
        """Called when an open order gets filled."""
        ...
