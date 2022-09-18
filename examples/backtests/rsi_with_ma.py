"""
200 EMA
RSI

Only trade RSI overbought if price is in downtrend (decreasing EMA)
Only trade RSI oversold if price is in uptrend (increasing EMA)

"""

from datetime import datetime

import plotly.graph_objs as go

from trader.backtest import BacktestFuturesBroker

from trader.core.indicator import MAIndicator, RSIIndicator
from trader.core.interface import FuturesBroker
from trader.core.model import Balance, Position
from trader.core.strategy import Strategy
from trader.core.const import MA, Side, Market

from trader.data.binance import get_store_candles
from trader.data.db import HDF5CandleStorage
from trader.data.model import Candles, Symbol

from trader.ui import CustomGraph
from trader.ui.const import Graph
import nputils as npu

from util.performance import measure_performance


class RSIMAStrategy(Strategy):

    def __init__(self, candles: Candles, broker: FuturesBroker):
        self.ema = MAIndicator(candles=candles, period=200, type=MA.EMA)
        self.rsi = RSIIndicator(candles=candles)
        self.rsi_oversold_line = self.rsi.rsi < 30
        self.rsi_overbought_line = self.rsi.rsi > 70
        self.increasing_ema_line = npu.increase(self.ema.ma)
        self.decreasing_ema_line = npu.decrease(self.ema.ma)

    def on_not_in_position(self):
        if self.rsi_oversold_line[-1] and self.increasing_ema_line[-1]:
            self.broker.enter_position(symbol=symbol, side=Side.BUY, amount=400)
        elif self.rsi_overbought_line[-1] and self.decreasing_ema_line[-1]:
            self.broker.enter_position(symbol=symbol, side=Side.SELL, amount=400)

    def on_in_position(self, position: Position):
        if position.side is Side.BUY and self.rsi_overbought_line[-1]:
            self.broker.close_position_market(symbol=symbol)
        elif position.side is Side.SELL and self.rsi_oversold_line[-1]:
            self.broker.close_position_market(symbol=symbol)


if __name__ == '__main__':
    start_cash = 1000
    symbol = Symbol('BTC', 'USDT')

    candles = get_store_candles(
        symbol=symbol,
        interval='1h',
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

    strategy = RSIMAStrategy(candles=candles, broker=broker)
    measure_performance(strategy.run)
    """
    strategy.run()

    strategy.plot(
        volume_type=None,
        side_labels=False,
        price_markers=False,
        custom_graphs=[
            CustomGraph(
                graph=Graph.CANDLESTICK,
                graph_object=go.Scattergl(
                    y=strategy.ema.ma,
                    name='EMA',
                    marker={'color': '#D10000'},
                ),
            ),
            CustomGraph(
                graph=Graph.NEW,
                graph_object=[
                    go.Scattergl(
                        y=strategy.rsi.rsi,
                        name='RSI',
                        marker={'color': '#a21ddb'},
                    ),
                    go.Scattergl(
                        y=[strategy.rsi.lower_limit],
                        name='RSI lower limit',
                        marker={'color': '#2a1ddb'},
                    ),
                    go.Scattergl(
                        y=[strategy.rsi.upper_limit],
                        name='RSI upper limit',
                        marker={'color': '#2a1ddb'},
                    ),
                ]
            ),
        ]
    )
    """
