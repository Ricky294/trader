from __future__ import annotations

import logging
from functools import wraps
from typing import Iterable

from tqdm import trange

import util.format as fmt

from trader.backtest import BacktestFuturesBroker

from trader.core.const import Mode
from trader.core.indicator import Indicator
from trader.core.interface import FuturesBroker
from trader.core.model import Balance, Position, Order
from trader.core.util import(
    store_iterable_object_names,
    cache_array_return_annotated_funcs,
    sliced_iterable_getattribute_wrapper,
)
from trader.data.binance import candle_stream

from trader.data.model import Candles
from trader.log import logger
from trader.ui import UIApp, GraphWrapper
from trader.ui.const import Volume, Candlestick


class StrategyException(Exception):

    def __init__(self):
        super(StrategyException, self).__init__()


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
        try:
            self._candles = kwargs.pop('candles')
            self._broker = kwargs.pop('broker')
        except KeyError as ke:
            raise KeyError('Missing "broker"/"candles" keyword argument(s) on init strategy!') from ke

        Indicator._candles = self._candles

        if 'object.' not in init.__qualname__:
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
        Indicator._candles = candles
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

    def run(self):
        if self.mode is Mode.LIVE:
            candle_stream(
                candles=self._candles,
                on_candle=lambda *args, **kwargs: (),
                on_candle_close=self.__call__,
            )
        elif self.mode is Mode.BACKTEST:
            for _, candles in zip(trange(len(self._candles)), self._candles.slice_iter()):
                self._broker(candles)
                self.__call__(candles)

            self._broker.finished()
            self.__log_results()
        else:
            raise ValueError(f'Unsupported broker instance: {self._broker.__class__.__name__}')

    def __log_results(self):
        number_of_positions = len(self._broker.positions)
        number_of_wins = 0
        for pos in self._broker.positions:
            if pos.profit > 0:
                number_of_wins += 1

        try:
            win_rate = fmt.num(number_of_wins / number_of_positions, prec=2, perc=True)
        except ZeroDivisionError:
            win_rate = 0

        logger.core.info(f'Finished backtesting on {len(self.candles)} candles.')
        logger.core.info(f'Entered {number_of_positions} positions.')
        logger.core.info(f'Wins: {number_of_wins}, '
                         f'Losses: {number_of_positions - number_of_wins}, '
                         f'Win rate: {win_rate}')
        logger.core.info(f'Balance: {self._broker.balances[0].value_str()} -> {self._broker.balances[-1].value_str()}')

    def plot(
            self,
            candlestick_type=Candlestick.AUTO,
            volume_type=Volume.AUTO,
            side_labels=True,
            price_markers=True,
            extra_graphs: Iterable[GraphWrapper] = ()
    ):
        self._ui_app = UIApp(
            candles=self.candles,
            positions=self._broker.positions,
            orders=self._broker.orders,
            balances=self._broker.balances,
            entry_fees=self._broker.entry_fees,
            exit_fees=self._broker.exit_fees,
        )

        self._ui_app.run(
            candlestick_type=candlestick_type,
            volume_type=volume_type,
            side_labels=side_labels,
            price_markers=price_markers,
            custom_graphs=extra_graphs
        )
