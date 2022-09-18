from trader.core.const import Market
from trader.core.indicator import RSIIndicator
from trader.data.binance import get_store_candles

candles = get_store_candles(
    symbol='BTCUSDT',
    interval='1d',
    market=Market.FUTURES,
)

rsi = RSIIndicator(candles)
