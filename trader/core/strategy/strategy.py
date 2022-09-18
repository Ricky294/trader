from __future__ import annotations

import logging
from typing import Iterable

import websocket
from tqdm import tqdm

from trader.backtest import BacktestFuturesBroker

from trader.core.const import Environment, BrokerEvent
from trader.core.indicator import Indicator
from trader.core.interface import FuturesBroker
from trader.core.model import Order, Balance, Position, Balances, Positions, Orders

from trader.data.binance import candle_stream
from trader.data.model import Candles, Line, FuncLine, AttrLine

from trader.live.binance import BinanceFuturesBroker
import trader.log

from trader.settings import Settings

from trader.ui import UIApp, CustomGraph
from trader.ui.const import Volume, Candlestick

import util.format_util as fmt
from util.inspect_util import is_array_return_annotated_func
from util.iter_util import get_class_attrs
from util.observer import Observer


class StrategyException(Exception):

    def __init__(self):
        super(StrategyException, self).__init__()


class Strategy(Observer):

    def __new__(cls, candles: Candles, broker: FuturesBroker):
        self = super().__new__(cls)
        self._candles = candles
        self._i = len(candles) - 1

        self._lines = set()
        self._ind_refs = set()

        broker.publisher.attach(self)

        if isinstance(broker, BacktestFuturesBroker):
            broker._post_init(candles)

        self._broker = broker

        if Settings.event_logging:
            broker.publisher.attach(self.logger)

        return self

    def update(self, event: BrokerEvent, *args, **kwargs):
        # Matches all events.
        # For example if event is BrokerEvent.ON_IN_POSITION
        # then self.on_in_position method is called.
        getattr(self, str(event.value).lower())(*args, **kwargs)

    @property
    def candles(self) -> Candles:
        return self._candles[:self._i + 1]

    @property
    def broker(self) -> FuturesBroker:
        return self._broker

    @property
    def environment(self) -> Environment:
        if isinstance(self._broker, BacktestFuturesBroker):
            return Environment.BACKTEST
        elif isinstance(self._broker, BinanceFuturesBroker):
            return Environment.BINANCE
        raise ValueError(f'Unsupported broker: {self._broker}')

    @property
    def logger(self) -> logging.Logger:
        if self.environment is Environment.BACKTEST:
            return trader.log.backtest()
        elif self.environment is Environment.BINANCE:
            return trader.log.binance()
        raise ValueError(f'Unsupported environment: {self.environment}')

    def __save_wrapped_attrs(self):
        for attr_name, attr in get_class_attrs(self).items():
            if isinstance(attr, Line):
                self._lines.add(attr)

    def __wrap_line_attrs(self):
        for attr_name, attr in get_class_attrs(self).items():
            if attr_name.endswith('line') and not isinstance(attr, Line):
                if callable(attr):
                    wrapped_attr = FuncLine(attr)
                else:
                    wrapped_attr = AttrLine(attr)

                setattr(self, attr_name, wrapped_attr)
                self._lines.add(wrapped_attr)

    def __save_ind_refs(self):
        for attr_name, attr in vars(self).items():
            if isinstance(attr, Indicator):
                self._ind_refs.add(attr)

    def __wrap_ind_funcs(self):
        for ind in self._ind_refs:
            for attr_name, attr in get_class_attrs(ind).items():
                if is_array_return_annotated_func(attr):
                    setattr(ind, attr_name, FuncLine(attr, self._i))

    def run(self):
        trader.log.core().info(f'Running backtest on {type(self).__qualname__} strategy.')

        if self.environment is Environment.BACKTEST:
            self.__backtest_run()
        elif self.environment is Environment.BINANCE:
            self.__live_run()
        else:
            raise ValueError(f'Unsupported broker {type(self._broker).__name__}')

    def __live_run(self):

        def on_exception(ws: websocket.WebSocketApp, exc: Exception) -> None:
            self._broker.cancel_all(symbol=self._candles.symbol)

        if Settings.candle_stream_log:
            on_candle_callback = lambda *args, **kwargs: trader.log.binance().info(*args, **kwargs)
        else:
            on_candle_callback = lambda *args, **kwargs: ()

        candle_stream(
            candles=self._candles,
            on_candle=on_candle_callback,
            on_candle_close=self.broker.__call__,
            on_exception=on_exception,
            log_candles=Settings.candle_stream_log,
        )

    def __backtest_run(self):
        self.__save_wrapped_attrs()
        self.__wrap_line_attrs()
        self.__save_ind_refs()

        for i in tqdm(range(len(self._candles))):
            self._i = i

            for attr in self._lines:
                attr._i = i

            for attr in self._ind_refs:
                attr._i = i

            self.broker.__call__(self._candles[:self._i + 2])

        self.__backtest_log_results()

    def __backtest_log_results(self):
        number_of_opened_positions = self.broker.position_history.number_of_opened_positions
        number_of_closed_positions = self.broker.position_history.number_of_closed_positions
        number_of_wins = self.broker.position_history.number_of_wins
        win_rate = self.broker.position_history.win_rate

        trader.log.core().info(f'Finished backtesting on {len(self.candles)} candles.')
        trader.log.core().info(f'Entered {number_of_opened_positions} positions.')
        trader.log.core().info(
            f'Wins: {number_of_wins}, '
            f'Losses: {number_of_closed_positions - number_of_wins}, '
            f'Win rate: {fmt.num(win_rate, prec=2, perc=True)}'
        )
        trader.log.core().info(
            f'Balance: {self.broker.balance_history[0].simple_repr()} '
            f'-> {self.broker.balance_history[-1].simple_repr()}'
        )

    def plot(
            self,
            candlestick_type=Candlestick.AUTO,
            volume_type: Volume | None = Volume.AUTO,
            side_labels=True,
            price_markers=True,
            custom_graphs: Iterable[CustomGraph] = (),
            debug=True,
    ) -> None:
        self._ui_app = UIApp(
            candles=self.candles,
            positions=self._broker.position_history,
            orders=self._broker.order_history,
            balances=self._broker.balance_history,
        )

        self._ui_app.run(
            candlestick_type=candlestick_type,
            volume_type=volume_type,
            side_labels=side_labels,
            price_markers=price_markers,
            custom_graphs=custom_graphs,
            debug=debug,
        )

    def on_candle_close(self) -> None:
        """Called on every candle close."""
        ...

    # Position events

    def on_in_position(self, position: Position) -> None:
        """Called on candle close if a position is open."""
        ...

    def on_position_in_profit(self, position: Position) -> None:
        """Called on candle close if a position is open and in profit."""
        ...

    def on_position_in_loss(self, position: Position) -> None:
        """Called on candle close if a position is open and in loss."""
        ...

    def on_not_in_position(self) -> None:
        """Called on every candle close if no position is open."""
        ...

    def on_position_open(self, position: Position) -> None:
        """Called on new position open."""
        ...

    def on_position_close(self, closed_position: Position) -> None:
        """Called on position close."""
        ...

    def on_position_adjust(self, position: Position) -> None:
        """Called on position change."""
        ...

    def on_position_close_in_profit(self, closed_position: Position) -> None:
        """Called on position close in profit."""
        ...

    def on_position_close_in_loss(self, closed_position: Position) -> None:
        """Called on position close in loss."""
        ...

    # Balance events

    def on_balance_change(self, balance: Balance) -> None:
        """Called on balance change."""
        ...

    # Order events

    def on_orders_create(self, new_orders: list[Order]) -> None:
        """Called on new order creation."""
        ...

    def on_orders_cancel(self, canceled_order: list[Order]) -> None:
        """Called on open order cancel."""
        ...

    def on_orders_fill(self, filled_orders: list[Order]) -> None:
        """Called an open order fill."""
        ...

    def on_leverage_change(self, symbol: str, leverage: int) -> None:
        """Called on leverage set."""
        ...
