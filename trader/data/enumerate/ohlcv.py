from enum import Enum

from trader.data.schema import (
    OPEN_PRICE as O,
    HIGH_PRICE as H,
    LOW_PRICE as L,
    CLOSE_PRICE as C,
    VOLUME as V,
)


class OHLCV(Enum):
    OPEN_PRICE = O
    HIGH_PRICE = H
    LOW_PRICE = L
    CLOSE_PRICE = C
    VOLUME = V

    def __str__(self):
        return self.value
