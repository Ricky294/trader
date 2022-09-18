from __future__ import annotations

import plotly.graph_objs as go

from trader.backtest import BacktestFuturesBroker
from trader.core.const import Side, Market
from trader.core.indicator import RSIIndicator
from trader.core.interface import FuturesBroker
from trader.core.model import Position
from trader.core.strategy import Strategy

from trader.data.binance import get_store_candles
from trader.data.model import Candles, Percentage, Symbol

from trader.ui import CustomGraph
from trader.ui.const import Candlestick, Volume, Graph


class RSIStrategy(Strategy):

    def __init__(self, candles: Candles, broker: FuturesBroker):
        self.rsi_ind = RSIIndicator(candles)

        self.buy_signal_line = self.rsi_ind.rsi > 70
        self.sell_signal_line = self.rsi_ind.rsi < 30

    def on_not_in_position(self):
        if self.buy_signal_line[-1]:
            self.broker.enter_position(symbol=symbol, side=Side.LONG, amount=Percentage(50))
        elif self.sell_signal_line[-1]:
            self.broker.enter_position(symbol=symbol, side=Side.SELL, amount=Percentage(50))

    def on_in_position(self, position: Position):
        if (position.side is Side.SHORT and self.buy_signal_line[-1]) \
                or (position.side is Side.LONG and self.sell_signal_line[-1]):
            self.broker.close_position_market(symbol)


if __name__ == '__main__':
    start_cash = 1000
    symbol = Symbol('BTC', 'USDT')

    candles = get_store_candles(
        symbol=symbol,
        interval='1d',
        market=Market.FUTURES,
    )

    broker = BacktestFuturesBroker(
        balances={symbol.quote: start_cash},
        symbol_leverage_pair={symbol: 1},
        taker_fee_percentage=.2,
        maker_fee_percentage=.4,
    )

    strategy = RSIStrategy(candles=candles, broker=broker)

    strategy.run()
    strategy.plot(
        candlestick_type=Candlestick.AUTO,
        volume_type=Volume.AUTO,
        #side_labels=False,
        #price_markers=False,
        custom_graphs=[
            CustomGraph(
                graph=Graph.NEW,
                graph_object=[
                    go.Scattergl(
                        y=strategy.rsi_ind.rsi,
                        name='RSI',
                        marker={'color': '#a21ddb'},
                    ),
                    go.Scattergl(
                        y=[strategy.rsi_ind.lower_limit],
                        name='RSI lower limit',
                        marker={'color': '#2a1ddb'},
                    ),
                    go.Scattergl(
                        y=[strategy.rsi_ind.upper_limit],
                        name='RSI upper limit',
                        marker={'color': '#2a1ddb'},
                    )
                ]
            )
        ],
    )
