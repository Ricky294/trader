from __future__ import annotations

import concurrent.futures
from abc import ABC, abstractmethod
from typing import Callable, Iterable

from tqdm import trange

from trader.backtest import BacktestFuturesBroker

from trader.config import MONEY_PRECISION
from trader.core.enumerate import Mode
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
    # Use this wrapper to pass candles to functions instead of saving candles as instance variable in __init__.
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
    def __call__(self, candles: Candles):
        ...

    def __binance_run(self, candles: Candles):
        candle_stream(candles=candles, on_candle_close=self.__call__, on_candle=lambda: ())

    def __backtest_run(self, candles: Candles):
        if not isinstance(self.broker, BacktestFuturesBroker):
            raise TraderError(f'Unsupported broker: {type(self.broker).__class__.__name__}')

        get_core_logger().info(f'Running backtest on {len(candles)} candles.')

        for _, candles in zip(trange(len(candles)), candles.replayer()):
            self.broker(candles)
            self.__call__(candles)

        self.broker.finished()

        get_core_logger().info(
            f'Finished backtesting. Entered {len(self.broker.positions)} positions. '
            f'Final balance: {self.broker.balances[-1].free:.{MONEY_PRECISION}f} {self.broker.balances[-1].asset}'
        )

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
