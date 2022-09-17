from __future__ import annotations

from trader.backtest import BacktestFuturesBroker
from trader.core.strategy import Strategy, Engine
from trader.data.binance import get_store_candles

from trader.core.model import Position, Balance
from trader.core.const import Market

from util.performance import execute_measure_performance


class EmptyStrategy(Strategy):

    def __init__(self): ...

    def on_not_in_position(self): ...

    def on_in_position(self, position: Position): ...


if __name__ == '__main__':
    start_cash = 1000
    base_currency = 'BTC'
    quote_currency = 'USDT'
    symbol = base_currency + quote_currency

    candles = get_store_candles(
        symbol=symbol,
        interval='15m',
        market=Market.FUTURES,
    )

    strategy = EmptyStrategy

    broker = BacktestFuturesBroker(
        balances=[Balance(asset='USDT', available=start_cash)],
        symbols_set_leverage={symbol: 1},
    )

    engine = Engine(candles=candles, broker=broker, strategy=strategy)
    execute_measure_performance(engine.run)
