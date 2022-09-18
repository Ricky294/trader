from __future__ import annotations

from trader.backtest import BacktestFuturesBroker
from trader.core.strategy import Strategy
from trader.data.binance import get_store_candles

from trader.core.model import Position, Balance
from trader.core.const import Market
from trader.data.model import Symbol

from util.performance import measure_performance


class EmptyStrategy(Strategy):

    def on_not_in_position(self): ...

    def on_in_position(self, position: Position): ...


if __name__ == '__main__':
    start_cash = 1000
    symbol = Symbol('BTC', 'USDT')

    candles = get_store_candles(
        symbol=symbol,
        interval='15m',
        market=Market.FUTURES,
    )

    broker = BacktestFuturesBroker(
        balances={symbol.quote: start_cash},
        symbol_leverage_pair={symbol: 1},
    )

    engine = EmptyStrategy(candles=candles, broker=broker)
    measure_performance(engine.run)
