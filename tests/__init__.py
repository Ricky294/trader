import numpy as np

from trader.core.const import Market

from trader.data.candle_schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME
from trader.data.model import Candles


def generate_candles(
        candle_count: int,
        symbol='XYZ',
        interval='1h',
        market=Market.FUTURES,
        schema=(OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME)
):
    return Candles(
        symbol=symbol,
        interval=interval,
        market=market,
        candles=np.ones(shape=(candle_count, len(schema)), dtype=float),
    )
