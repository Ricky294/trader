from __future__ import annotations

from mysecrets import BINANCE_SECRETS_PATH

from trader.core.const import Side, Market
from trader.core.model import Position
from trader.core.strategy import Strategy

from trader.data.binance import get_store_candles
from trader.data.model import Symbol

from trader.live.binance import BinanceFuturesBroker

from util.file_util import read_config


class RSIStrategy(Strategy):

    def __init__(self, *args, **kwargs):
        # self.broker.set_leverage(symbol=symbol, leverage=1)
        ...

    def on_not_in_position(self):
        self.broker.enter_position(symbol=symbol, side=Side.LONG, amount=100)

    def on_in_position(self, position: Position):
        self.broker.close_position_market(position.symbol)


if __name__ == '__main__':
    symbol = Symbol('BTC', 'USDT')

    secret_keys = read_config(BINANCE_SECRETS_PATH)

    candles = get_store_candles(
        symbol=symbol,
        interval='1m',
        market=Market.FUTURES,
    )

    broker = BinanceFuturesBroker(
        symbol_leverage_pair={symbol: 10},
        **secret_keys
    )

    engine = RSIStrategy(candles=candles, broker=broker)
    engine.run()
