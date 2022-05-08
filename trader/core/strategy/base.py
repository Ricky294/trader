from __future__ import annotations

import concurrent.futures
from abc import ABC, abstractmethod
from typing import Callable, Iterable

from tqdm import trange
from trader.data.binance import candle_stream
from trader.data.model import Candles

from trader.config import MONEY_PRECISION
from trader.backtest import BacktestFuturesTrader, get_backtest_logger
from trader.core.enumerate import TimeInForce, OrderSide, Mode
from trader.core.exception import TraderException
from trader.core.indicator import Indicator
from trader.core.interface import FuturesTrader
from trader.core.log import get_core_logger
from trader.live.log import get_live_logger
from trader.live.binance import BinanceFuturesTrader

from trader.ui import UIApp, CustomGraph
from trader.ui.enumerate import Candlestick, Volume


class Strategy(Callable, ABC):

    def __init__(self, trader: FuturesTrader, candles: Candles):
        self.trader = trader
        self.candles = candles
        if isinstance(trader, BacktestFuturesTrader):
            self.mode = Mode.BACKTEST
            self.run = self.__backtest_run
            self.logger = get_backtest_logger()
        elif isinstance(trader, BinanceFuturesTrader):
            self.mode = Mode.LIVE
            self.run = self.__binance_run
            self.logger = get_live_logger()
        else:
            raise TraderException(f"Unsupported trader: {type(trader)}.")

    @abstractmethod
    def __call__(self, candles: Candles): ...

    def __binance_run(self):
        candle_stream(candles=self.candles, on_candle_close=self.__call__, on_candle=lambda: ())

    def __backtest_run(self):
        if not isinstance(self.trader, BacktestFuturesTrader):
            raise TraderException(f"Unsupported trader type: {type(self.trader)}")

        get_core_logger().info(f"Running backtest on {len(self.candles)} candles.")

        for _, data in zip(trange(len(self.candles)), self.candles.replayer()):
            self.__call__(data)
            self.trader(data)

        get_core_logger().info(
            f"Finished backtesting. Entered {len(self.trader.positions)} positions. "
            f"Final balance: {self.trader.balance.free:.{MONEY_PRECISION}f} {self.trader.balance.asset}"
        )

    def plot_results(
            self,
            candlestick_type: Candlestick = Candlestick.LINE,
            volume_type: Volume = Volume.LINE,
            custom_graphs: Iterable[CustomGraph | Indicator] = ()
    ):

        if not isinstance(self.trader, BacktestFuturesTrader):
            raise TraderException("Strategy can be plotted only if trader is instance of BacktestFuturesTrader")

        UIApp(
            candles=self.candles,
            positions=self.trader.positions,
            start_cash=self.trader.start_balance.free
        ).run_ui_app(
            candlestick_type=candlestick_type,
            volume_type=volume_type,
            custom_graphs=custom_graphs
        )

    def create_position(
            self,
            symbol: str,
            money: float,
            side: int | OrderSide,
            leverage: int,
            price: float | None = None,
            profit_price: float | None = None,
            stop_price: float | None = None
    ):
        orders = self.trader.create_position(
            symbol=symbol,
            money=money,
            side=side,
            leverage=leverage,
            price=price,
            profit_price=profit_price,
            stop_price=stop_price,
        )
        return orders

    def cancel_orders(self, symbol: str):
        orders = self.trader.cancel_orders(symbol)
        return orders

    def get_open_orders(self, symbol: str):
        orders = self.trader.get_open_orders(symbol)
        return orders

    def set_leverage(self, symbol: str, leverage: int):
        self.trader.set_leverage(symbol=symbol, leverage=leverage)

    def close_position(self, symbol: str, price: float = None, time_in_force: str | TimeInForce = "GTC"):
        self.trader.close_position(symbol=symbol, price=price, time_in_force=time_in_force)

    def close_position_limit(self, symbol: str, price: float, time_in_force: str | TimeInForce = "GTC"):
        order = self.trader.close_position_limit(symbol=symbol, price=price, time_in_force=time_in_force)
        return order

    def close_position_market(self, symbol: str):
        order = self.trader.close_position_market(symbol=symbol)
        return order

    def get_position(self, symbol: str):
        position = self.trader.get_position(symbol)
        return position

    def get_balance(self, asset: str):
        balance = self.trader.get_balance(asset)
        return balance


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
    strategy.plot_results(**plot_params.__dict__)


def backtest_multiple_strategies(
        strategies: list[Strategy],
        plot_params: list[BacktestPlotParams],
):
    if len(strategies) != len(plot_params):
        raise ValueError("Parameter lists has different lengths.")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(
            __run_bot_from_arg_list,
            [(strategy, plot_p) for strategy, plot_p in zip(strategies, plot_params)]
        )
