import concurrent.futures
from typing import List, Optional

from ..backtest import BacktestFuturesTrader, Plot, run_backtest
from ..core.interface import TradingBot
from ..core.enum import CandlestickType
from ..core.strategy import Strategy


class BacktestBot(TradingBot):

    def add_strategy(self, strategy: Strategy):
        if not isinstance(strategy.trader, BacktestFuturesTrader):
            raise ValueError("Trader is not an instance of BacktestFuturesTrader!")
        self.strategy = strategy

    def _run(
            self,
            log_scale: bool = False,
            candlestick_type: CandlestickType = CandlestickType.LINE,
            extra_plots: List[Plot] = None
    ):
        run_backtest(
            strategy=self.strategy,
            candles=self.candles,
            log_scale=log_scale,
            candlestick_type=candlestick_type,
            extra_plots=extra_plots,
        )


class BacktestRunParams:

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
    params: BacktestRunParams = args[1]

    bot.run(**params.__dict__)


def backtest_multiple_bot(bots: List[BacktestBot], params_list: List[BacktestRunParams]):

    if len(bots) != len(params_list):
        raise ValueError("Length of 'bots' differs from the length of 'params_list'.")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(__run_bot_from_arg_list, [(bot, params) for bot, params in zip(bots, params_list)])
