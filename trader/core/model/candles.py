
from typing import Optional
import numpy as np

from ..const.candle_index import (
    OPEN_TIME_INDEX,
    OPEN_PRICE_INDEX,
    HIGH_PRICE_INDEX,
    LOW_PRICE_INDEX,
    CLOSE_PRICE_INDEX,
    VOLUME_INDEX,
)
from ..indicator import Indicators


class Candles:

    __slots__ = (
        "array",
        "latest",
        "latest_open_time",
        "latest_open_price",
        "latest_high_price",
        "latest_low_price",
        "latest_close_price",
        "latest_volume",
    )

    def indicator(self):
        return Indicators(self.array)

    def __init__(self):
        self.array: Optional[np.ndarray] = None
        self.latest: Optional[np.ndarray] = None
        self.latest_open_time: Optional[float] = None
        self.latest_open_price: Optional[float] = None
        self.latest_high_price: Optional[float] = None
        self.latest_low_price: Optional[float] = None
        self.latest_close_price: Optional[float] = None
        self.latest_volume: Optional[float] = None

    def update(self, candles: np.ndarray):
        self.array = candles
        self.latest = candles[-1]
        self.latest_open_time = float(self.latest[OPEN_TIME_INDEX])
        self.latest_open_price = float(self.latest[OPEN_PRICE_INDEX])
        self.latest_high_price = float(self.latest[HIGH_PRICE_INDEX])
        self.latest_low_price = float(self.latest[LOW_PRICE_INDEX])
        self.latest_close_price = float(self.latest[CLOSE_PRICE_INDEX])
        self.latest_volume = float(self.latest[VOLUME_INDEX])

    def open_times(self):
        return self.array.T[OPEN_TIME_INDEX]

    def open_prices(self):
        return self.array.T[OPEN_PRICE_INDEX]

    def high_prices(self):
        return self.array.T[HIGH_PRICE_INDEX]

    def low_prices(self):
        return self.array.T[LOW_PRICE_INDEX]

    def close_prices(self):
        return self.array.T[CLOSE_PRICE_INDEX]

    def volumes(self):
        return self.array.T[VOLUME_INDEX]

    def is_bullish(self):
        return self.latest_close_price > self.latest_open_price

    def is_bearish(self):
        return self.latest_close_price < self.latest_open_price

    def ath(self):
        """Returns all time high"""
        return self.high_prices().max()

    def atl(self):
        """Returns all time low"""
        return self.low_prices().min()
