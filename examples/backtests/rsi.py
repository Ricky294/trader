from __future__ import annotations

import plotly.graph_objs as go

from trader.core.const import Side, OrderType
from trader.core.strategy import Strategy, Engine
from trader.data.binance import get_store_candles

from trader.backtest import BacktestFuturesBroker

from trader.core.model import Balance, Position, Order
from trader.core.indicator import RSIIndicator
from trader.core.const import Market

from trader.ui import GraphWrapper
from trader.ui.const import Candlestick, Volume, Graph


class RSIStrategy(Strategy):

    def __init__(self):
        self.rsi_ind = RSIIndicator()
        self.rsi_buy_signal = self.rsi_ind.rsi < 30
        self.rsi_sell_signal = self.rsi_ind.rsi > 70

    def on_not_in_position(self):
        if self.rsi_buy_signal[-1]:
            self.broker.create_order(Order(symbol=symbol, type=OrderType.MARKET, side=Side.LONG, amount=50.0))
        elif self.rsi_sell_signal[-1]:
            self.broker.create_order(Order(symbol=symbol, type=OrderType.MARKET, side=Side.SELL, amount=50.0))

    def on_in_position(self, position: Position):
        if (position.side is Side.SHORT and self.rsi_buy_signal[-1]) or (position.side is Side.LONG and self.rsi_sell_signal[-1]):
            self.broker.close_position_market(symbol)


if __name__ == '__main__':
    start_cash = 1000
    base_currency = 'BTC'
    quote_currency = 'USDT'
    symbol = base_currency+quote_currency

    candles = get_store_candles(
        symbol=symbol,
        interval='12h',
        market=Market.FUTURES,
    )

    broker = BacktestFuturesBroker(
        balances=[Balance(available=start_cash, asset=quote_currency)],
        symbols_set_leverage={symbol: 1}
    )

    engine = Engine(candles=candles, broker=broker, strategy=RSIStrategy)

    engine.run()
    engine.plot(
        candlestick_type=Candlestick.AUTO,
        volume_type=Volume.AUTO,
        side_labels=False,
        price_markers=False,
        extra_graphs=[
            GraphWrapper(
                graph=Graph.NEW,
                graph_object=[
                    go.Scattergl(
                        y=engine.strategy.rsi_ind.rsi,
                        name='RSI',
                        marker={'color': '#a21ddb'},
                    ),
                    go.Scattergl(
                        y=[engine.strategy.rsi_ind.lower_limit],
                        name='RSI lower limit',
                        marker={'color': '#2a1ddb'},
                    ),
                    go.Scattergl(
                        y=[engine.strategy.rsi_ind.upper_limit],
                        name='RSI upper limit',
                        marker={'color': '#2a1ddb'},
                    )
                ]
            )
        ],
    )
