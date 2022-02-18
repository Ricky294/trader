import concurrent.futures
from typing import List, Optional, Type, Iterable

from trader.core.enum import CandlestickType
from trader.core.indicator import Indicator
from trader.core.interface import TradingBot
from trader.core.strategy import Strategy

from .backtester import plot_backtest_results, run_backtest
from .futures_trader import BacktestFuturesTrader
from .plot import Plot


class BacktestBot(TradingBot):

    def add_strategy(self, strategy: Strategy):
        if not isinstance(strategy.trader, BacktestFuturesTrader):
            raise ValueError("Trader is not an instance of BacktestFuturesTrader!")
        self.strategy = strategy

    def create_strategy_with_optimized_indicators(
            self,
            strategy: Type[Strategy],
            symbol: str,
            trader: BacktestFuturesTrader,
            **kwargs,
    ):
        if self.candles is None:
            raise ValueError("Missing data (self.candles is None). Unable to optimize without precalculated data!")

        from . import OptimizedIndicator

        optimized_kwargs = {}
        for key, val in kwargs.items():
            if isinstance(val, Indicator):
                optimized_kwargs[key] = OptimizedIndicator(candles=self.candles, indicator=val)
            elif val and isinstance(val, Iterable) and all(isinstance(ind, Indicator) for ind in val):
                optimized_kwargs[key] = [OptimizedIndicator(candles=self.candles, indicator=v) for v in val]
            else:
                optimized_kwargs[key] = val

        self.strategy = strategy(
            symbol=symbol,
            trader=trader,
            **optimized_kwargs,
        )

    def run(
            self,
            enable_logging=False,
    ):
        self._check_strategy_and_candles()
        self._setup_logger(enable_logging)
        run_backtest(
            strategy=self.strategy,
            candles=self.candles,
        )

    def plot(
            self,
            log_scale=False,
            candlestick_type=CandlestickType.LINE,
            extra_plots: List[Plot] = None,
    ):
        plot_backtest_results(
            candles=self.candles,
            trader=self.strategy.trader,
            start_cash=self.strategy.trader.start_balance.free,
            log_scale=log_scale,
            candlestick_type=candlestick_type,
            extra_plots=extra_plots,
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
            candlestick_type: CandlestickType = CandlestickType.LINE,
            extra_plots: Optional[List[Plot]] = None,
    ):
        self.log_scale = log_scale
        self.candlestick_type = candlestick_type
        self.extra_plots = extra_plots


def __run_bot_from_arg_list(args):
    bot: BacktestBot = args[0]
    run_params: BacktestRunParams = args[1]
    plot_params: BacktestPlotParams = args[2]

    bot.run(**run_params.__dict__)
    bot.plot(**plot_params.__dict__)


def backtest_multiple_bot(
        bots: List[BacktestBot],
        run_params: List[BacktestRunParams],
        plot_params: List[BacktestPlotParams],
):

    if len(bots) != len(run_params) != len(plot_params):
        raise ValueError("Parameter lists has different lengths.")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(
            __run_bot_from_arg_list,
            [(bot, run_p, plot_p) for bot, run_p, plot_p in zip(bots, run_params, plot_params)]
        )
