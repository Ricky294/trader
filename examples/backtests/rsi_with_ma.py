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
from trader.core.model import Balance, Order, Position
from trader.core.strategy import Strategy, Engine
from trader.core.const import MA, Side, OrderType, Market

from trader.data.binance import get_store_candles
from trader.data.db import HDF5CandleStorage

from trader.ui import GraphWrapper
from trader.ui.const import Graph
import nputils as npu


class RSIMAStrategy(Strategy):

    def __init__(self):
        self.ema = MAIndicator(period=200, type=MA.EMA)
        self.rsi = RSIIndicator()
        self.rsi_oversold = self.rsi.rsi < 30
        self.rsi_overbought = self.rsi.rsi > 70
        self.increasing_ema = npu.increase(self.ema.ma)
        self.decreasing_ema = npu.decrease(self.ema.ma)

    def on_not_in_position(self):
        if self.rsi_oversold[-1] and self.increasing_ema[-1]:
            self.broker.create_order(Order(symbol=symbol, type=OrderType.MARKET, side=Side.BUY, amount=900))
        elif self.rsi_overbought[-1] and self.decreasing_ema[-1]:
            self.broker.create_order(Order(symbol=symbol, type=OrderType.MARKET, side=Side.SELL, amount=900))

    def on_in_position(self, position: Position):
        if position.side is Side.BUY and self.rsi_overbought[-1]:
            self.broker.close_position_market(symbol=symbol)
        elif position.side is Side.SELL and self.rsi_oversold[-1]:
            self.broker.close_position_market(symbol=symbol)


if __name__ == '__main__':
    start_cash = 1000
    base_currency = 'BTC'
    quote_currency = 'USDT'
    symbol = base_currency + quote_currency

    candles = get_store_candles(
        symbol=symbol,
        interval='5m',
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

    engine = Engine(candles=candles, broker=broker, strategy=RSIMAStrategy)
    engine.run()

    engine.plot(
        side_labels=False,
        price_markers=False,
        extra_graphs=[
            GraphWrapper(
                graph=Graph.CANDLESTICK,
                graph_object=go.Scattergl(
                    y=engine.strategy.ema.ma,
                    name='EMA',
                    marker={'color': '#D10000'},
                ),
            ),
            GraphWrapper(
                graph=Graph.NEW,
                graph_object=go.Scattergl(
                    y=engine.strategy.rsi.rsi,
                    name='RSI',
                    marker={'color': '#3EA055'},
                ),
            ),
        ]
    )
