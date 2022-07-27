from typing import Final

OPEN_TIME: Final = 'OPEN_TIME'
OPEN_PRICE: Final = 'OPEN_PRICE'
HIGH_PRICE: Final = 'HIGH_PRICE'
LOW_PRICE: Final = 'LOW_PRICE'
CLOSE_PRICE: Final = 'CLOSE_PRICE'
VOLUME: Final = 'VOLUME'

OHLC_LONG: Final = (OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE)
OHLCV_LONG: Final = (OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME)
TOHLCV_LONG: Final = (OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME)

TOHLCV_LONG_TO_INDEX: Final = {
    OPEN_TIME: 0,
    OPEN_PRICE: 1,
    HIGH_PRICE: 2,
    LOW_PRICE: 3,
    CLOSE_PRICE: 4,
    VOLUME: 5,
}

TOHLCV_LONG_TO_SHORT: Final = {
    OPEN_TIME: 't',
    OPEN_PRICE: 'o',
    HIGH_PRICE: 'h',
    LOW_PRICE: 'l',
    CLOSE_PRICE: 'c',
    VOLUME: 'v',
}

TOHLCV_SHORT_TO_LONG: Final = {
    't': OPEN_TIME,
    'o': OPEN_PRICE,
    'h': HIGH_PRICE,
    'l': LOW_PRICE,
    'c': CLOSE_PRICE,
    'v': VOLUME,
}
