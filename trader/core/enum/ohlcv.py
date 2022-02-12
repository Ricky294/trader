from enum import Enum

from trader.core.const.candle_index import (
    OPEN_PRICE_INDEX,
    HIGH_PRICE_INDEX,
    LOW_PRICE_INDEX,
    CLOSE_PRICE_INDEX,
    VOLUME_INDEX,
)


class OHLCV(Enum):
    OPEN_PRICE = OPEN_PRICE_INDEX
    HIGH_PRICE = HIGH_PRICE_INDEX
    LOW_PRICE = LOW_PRICE_INDEX
    CLOSE_PRICE = CLOSE_PRICE_INDEX
    VOLUME = VOLUME_INDEX

    def __int__(self):
        return self.value
