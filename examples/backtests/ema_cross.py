from datetime import datetime

import plotly.graph_objs as go

from trader.backtest import BacktestFuturesBroker

from trader.core.indicator import MAIndicator
from trader.core.interface import FuturesBroker
from trader.core.model import Balance, Order, Position
from trader.core.strategy import Strategy
from trader.core.const import MA, Side, OrderType, Market

from trader.data.binance import get_store_candles
from trader.data.db import HDF5CandleStorage
from trader.data.model import Candles

from trader.trade import cross

from trader.ui import GraphWrapper
from trader.ui.const import Graph


class MACrossStrategy(Strategy):

    def __init__(self):
        self.fast_ma = MAIndicator(period=10, type=MA.SMA)
        self.slow_ma = MAIndicator(period=50, type=MA.SMA)
        self.bearish_cross = cross(self.fast_ma.ma < self.slow_ma.ma)
        self.bullish_cross = cross(self.fast_ma.ma > self.slow_ma.ma)

    def on_not_in_position(self):
        if self.bullish_cross[-1]:
            self.broker.create_order(Order(symbol=symbol, type=OrderType.MARKET, side=Side.BUY, amount=100))
        elif self.bearish_cross[-1]:
            self.broker.create_order(Order(symbol=symbol, type=OrderType.MARKET, side=Side.SELL, amount=100))

    def on_in_position(self, position: Position):
        if self.bullish_cross[-1] or self.bearish_cross[-1]:
            self.broker.close_position_market(symbol=symbol)


if __name__ == '__main__':
    start_cash = 1000
    base_currency = 'BTC'
    quote_currency = 'USDT'
    symbol = base_currency + quote_currency

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
        balances=[Balance(time=candles.times[0], asset=quote_currency, available=start_cash)],
        symbols_set_leverage={symbol: 1},
        maker_fee_rate=0.0002,
        taker_fee_rate=0.0004,
        liquidation=False,
    )

    strategy = MACrossStrategy(candles=candles, broker=broker)
    strategy.run()
    strategy.plot(
        extra_graphs=[
            GraphWrapper(
                graph=Graph.CANDLESTICK,
                graph_object=go.Scattergl(
                    x=candles.pd_open_times,
                    y=strategy.slow_ma.ma,
                    name='Slow MA',
                    marker={'color': '#D10000'},
                ),
            ),
            GraphWrapper(
                graph=Graph.CANDLESTICK,
                graph_object=go.Scattergl(
                    x=candles.pd_open_times,
                    y=strategy.fast_ma.ma,
                    name='Fast MA',
                    marker={'color': '#3EA055'},
                ),
            ),
        ]
    )
