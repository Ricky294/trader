from datetime import datetime

import plotly.graph_objs as go

from trader.backtest import BacktestFuturesBroker

from trader.core.indicator import MAIndicator
from trader.core.interface import FuturesBroker
from trader.core.model import Balance, Position
from trader.core.strategy import Strategy
from trader.core.const import MA, Side, Market

from trader.data.binance import get_store_candles
from trader.data.db import HDF5CandleStorage
from trader.data.model import Candles, Symbol

from trader.trade import cross

from trader.ui import CustomGraph
from trader.ui.const import Graph
from util import performance


class MACrossStrategy(Strategy):

    def __init__(self, candles: Candles, broker: FuturesBroker):
        self.fast_ma = MAIndicator(candles=candles, period=15, type=MA.SMA)
        self.slow_ma = MAIndicator(candles=candles, period=30, type=MA.SMA)
        self.bullish_cross_line = cross(self.fast_ma.ma > self.slow_ma.ma)
        self.bearish_cross_line = cross(self.fast_ma.ma < self.slow_ma.ma)

    def on_not_in_position(self):
        if self.bullish_cross_line[-1]:
            self.broker.enter_position(symbol=symbol, side=Side.BUY, amount=100)
        elif self.bearish_cross_line[-1]:
            self.broker.enter_position(symbol=symbol, side=Side.SELL, amount=100)

    def on_in_position(self, position: Position):
        if self.bullish_cross_line[-1] or self.bearish_cross_line[-1]:
            self.broker.close_position_market(symbol=symbol)


if __name__ == '__main__':
    start_cash = 1000
    symbol = Symbol('BTC', 'USDT')

    candles = get_store_candles(
        symbol=symbol,
        interval='1d',
        market=Market.FUTURES,
        storage_type=HDF5CandleStorage,
    ).between(
        start=datetime(year=2020, month=1, day=1),
        end=datetime(year=2022, month=1, day=2)
    )

    broker = BacktestFuturesBroker(
        balances={symbol.quote: start_cash},
        symbol_leverage_pair={symbol: 1},
        maker_fee_percentage=0.02,
        taker_fee_percentage=0.04,
    )

    strategy = MACrossStrategy(candles=candles, broker=broker)
    strategy.run()
    strategy.plot(
        custom_graphs=[
            CustomGraph(
                graph=Graph.CANDLESTICK,
                graph_object=go.Scattergl(
                    x=candles.times,
                    y=strategy.slow_ma.ma,
                    name='Slow MA',
                    marker={'color': '#D10000'},
                ),
            ),
            CustomGraph(
                graph=Graph.CANDLESTICK,
                graph_object=go.Scattergl(
                    x=candles.times,
                    y=strategy.fast_ma.ma,
                    name='Fast MA',
                    marker={'color': '#3EA055'},
                ),
            ),
        ]
    )
