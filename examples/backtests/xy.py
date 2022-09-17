from __future__ import annotations

from mysecrets import BINANCE_SECRETS_PATH
from trader.core.const import Side, OrderType
from trader.core.strategy import Strategy, Engine
from trader.data.binance import get_store_candles

from trader.core.model import Position, Order
from trader.core.const import Market
from trader.live.binance import BinanceFuturesBroker
from util.file import read_config


class RSIStrategy(Strategy):

    def on_not_in_position(self):
        self.broker.create_order(Order(symbol=symbol, type=OrderType.MARKET, side=Side.LONG, quantity=0.001))

    def on_in_position(self, position: Position):
        self.broker.close_position_market(symbol)


if __name__ == '__main__':

    base_currency = 'BTC'
    quote_currency = 'USDT'
    symbol = base_currency+quote_currency

    secret_keys = read_config(BINANCE_SECRETS_PATH)

    candles = get_store_candles(
        symbol=symbol,
        interval='1m',
        market=Market.FUTURES,
    )

    broker = BinanceFuturesBroker(
        assets=['USDT'],
        symbols_set_leverage={symbol: 1},
        **secret_keys
    )

    engine = Engine(candles=candles, broker=broker, strategy=RSIStrategy)

    engine.run()
