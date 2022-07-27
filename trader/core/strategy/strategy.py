from __future__ import annotations

import concurrent.futures
from abc import ABC, abstractmethod
from typing import Callable, Iterable

from tqdm import trange

from trader.backtest import BacktestFuturesBroker

import trader.core.util.format as fmt
from trader.core.model import Balance, Position, Order
from trader.core.super_enum import Mode
from trader.core.exception import TraderError
from trader.core.indicator import Indicator
from trader.core.interface import FuturesBroker
from trader.core.log import get_core_logger

from trader.data.binance import candle_stream
from trader.data.model import Candles

from trader.live.binance import BinanceFuturesBroker

from trader.ui import UIApp, CustomGraph
from trader.ui.enumerate import Candlestick, Volume


def _call_with_candles(func: Callable, candles: Candles):
    # This wrapper is to pass candles to function instead of saving it as an instance variable in __init__.
    def wrapper(*args, **kwargs):
        return func(candles, *args, **kwargs)

    return wrapper


class Strategy(Callable, ABC):

    def __init__(self, candles: Candles, broker: FuturesBroker, asset: str):
        self.broker = broker
        self.asset = asset

        self.plot = _call_with_candles(self.__plot, candles)
        if isinstance(broker, BacktestFuturesBroker):
            self.mode = Mode.BACKTEST
            self.run = _call_with_candles(self.__backtest_run, candles)
        elif isinstance(broker, BinanceFuturesBroker):
            self.mode = Mode.LIVE
            self.run = _call_with_candles(self.__binance_run, candles)
        else:
            raise TraderError(f'Unsupported broker: {type(broker).__class__.__name__}.')

    @abstractmethod
    def __call__(
            self,
            candles: Candles,
            balance: Balance,
            open_orders: list[Order],
            position: Position | None,
            leverage: int,
            *args,
            **kwargs,
    ): ...

    def _get_call_kwargs(self, candles: Candles):
        balance = self.broker.get_balance(self.asset)
        position = self.broker.get_position(symbol=candles.symbol)
        open_orders = self.broker.get_open_orders(symbol=candles.symbol)
        leverage = self.broker.get_leverage(symbol=candles.symbol)
        return dict(candles=candles, balance=balance, open_orders=open_orders, position=position, leverage=leverage)

    def __binance_run(self, candles: Candles):
        self.broker: BinanceFuturesBroker
        candle_stream(
            candles=candles,
            on_candle=lambda: (),
            on_candle_close=self.__call__,
            on_candle_close_kwargs=self._get_call_kwargs
        )

    def __backtest_run(self, candles: Candles):
        self.broker: BacktestFuturesBroker

        def log(msg: str):
            get_core_logger().info(msg)

        log(f'Running backtest on {len(candles)} candles.')

        for _, candles in zip(trange(len(candles)), candles.replayer()):
            self.broker(candles)
            self.__call__(**self._get_call_kwargs(candles))

        self.broker.finished()

        number_of_positions = len(self.broker.positions)
        number_of_wins = 0
        for pos in self.broker.positions:
            if pos.profit > 0:
                number_of_wins += 1

        log(f'Finished backtesting on {len(candles)} candles.')
        log(f'Entered {number_of_positions} positions.')
        log(f'Wins: {number_of_wins}, '
            f'Losses: {number_of_positions - number_of_wins}, '
            f'Win rate: {fmt.num(number_of_wins / number_of_positions, prec=2, perc=True)}')
        log(f'Balance: {self.broker.balances[0].value_str()} -> {self.broker.balances[-1].value_str()}')

    def __plot(
            self,
            candles: Candles,
            candlestick_type: Candlestick = Candlestick.LINE,
            volume_type: Volume = Volume.LINE,
            custom_graphs: Iterable[CustomGraph | Indicator] = ()
    ):

        if not isinstance(self.broker, BacktestFuturesBroker):
            raise TraderError(f'Strategy can be plotted only if broker is instance of BacktestFuturesBroker.')

        UIApp(
            candles=candles,
            positions=self.broker.positions,
            orders=self.broker.orders,
            balances=self.broker.balances,
            entry_fees=self.broker.entry_fees,
            exit_fees=self.broker.exit_fees,
        ).run(
            candlestick_type=candlestick_type,
            volume_type=volume_type,
            custom_graphs=custom_graphs
        )


class BacktestRunParams:

    def __init__(
            self,
            enable_logging=False,
    ):
        self.enable_logging = enable_logging


class BacktestPlotParams:

    def __init__(
            self,
            log_scale: bool = False,
            candlestick_type: Candlestick = Candlestick.LINE,
            extra_plots: Iterable[CustomGraph] = (),
    ):
        self.log_scale = log_scale
        self.candlestick_type = candlestick_type
        self.extra_plots = extra_plots


def __run_bot_from_arg_list(args):
    strategy: Strategy = args[0]
    plot_params: BacktestPlotParams = args[2]

    strategy.run()
    strategy.plot(**plot_params.__dict__)


def backtest_multiple_strategies(
        strategies: list[Strategy],
        plot_params: list[BacktestPlotParams],
):
    if len(strategies) != len(plot_params):
        raise ValueError('Parameter lists has different lengths.')

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(
            __run_bot_from_arg_list,
            [(strategy, plot_p) for strategy, plot_p in zip(strategies, plot_params)]
        )
