from typing import Iterable, Type

from tqdm import trange

import util.format as fmt

from trader.backtest import BacktestFuturesBroker
from trader.core.indicator import Indicator

from trader.core.interface import FuturesBroker
from trader.core.strategy import Strategy

from trader.data.binance import candle_stream
from trader.data.model import Candles

from trader.live.binance import BinanceFuturesBroker
from trader.log import logger

from trader.ui import UIApp, GraphWrapper
from trader.ui.const import Candlestick, Volume


class Engine:

    def __init__(
            self,
            candles: Candles,
            broker: FuturesBroker,
            strategy: Type[Strategy],
            *strategy_args,
            **strategy_kwargs,
    ):
        Indicator._candles = candles

        self._strategy = strategy(
            *strategy_args,
            _Strategy__candles=candles,
            _Strategy__broker=broker,
            **strategy_kwargs
        )
        self._candles = candles
        self._broker = broker
        self._logger = logger.core
        self._ui_app = None

    @property
    def strategy(self):
        return self._strategy

    @property
    def candles(self):
        return self._candles

    @property
    def broker(self):
        return self._broker

    def run(self):
        if isinstance(self._broker, BinanceFuturesBroker):
            candle_stream(
                candles=self._candles,
                on_candle=lambda *args, **kwargs: (),
                on_candle_close=self._strategy.__call__,
            )
        elif isinstance(self._broker, BacktestFuturesBroker):
            for _, candles in zip(trange(len(self._candles)), self._candles.slice_iter()):
                self._broker(candles)
                self._strategy(candles)

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

        self._logger.info(f'Finished backtesting on {len(self._strategy.candles)} candles.')
        self._logger.info(f'Entered {number_of_positions} positions.')
        self._logger.info(f'Wins: {number_of_wins}, '
                          f'Losses: {number_of_positions - number_of_wins}, '
                          f'Win rate: {win_rate}')
        self._logger.info(f'Balance: {self._broker.balances[0].value_str()} -> {self._broker.balances[-1].value_str()}')

    def plot(
            self,
            candlestick_type=Candlestick.AUTO,
            volume_type=Volume.AUTO,
            side_labels=True,
            price_markers=True,
            extra_graphs: Iterable[GraphWrapper] = ()
    ):
        self._ui_app = UIApp(
            candles=self._strategy.candles,
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
