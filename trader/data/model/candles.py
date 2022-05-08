from __future__ import annotations

import numpy as np
import nputils as npu
import pandas as pd

from trader.data.enum import Market, OHLCV
from trader.data.model import ABCCandles
from trader.data.util import blend_ohlc, to_heikin_ashi
from trader.data.schema import *


class MarketCycle:

    def __init__(self):
        ...

    def consolidation(self):
        ...

    def trending(self):
        ...

    def uptrend(self):
        ...

    def downtrend(self):
        ...


class Candles(ABCCandles):
    """
    Suitable to store TOHLCV candles.

    TOHLCV stands for:
        - Time
        - Open price
        - High price
        - Low price
        - Close price
        - Volume
    """

    def __init__(
            self,
            candles: np.ndarray,
            symbol: str,
            interval: str,
            market: str | Market,
            meta: dict = None,
            schema=(OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME),
    ):
        super(Candles, self).__init__(
            candles=candles,
            symbol=symbol,
            interval=interval,
            market=market,
            meta=meta,
            schema=schema,
        )

    @property
    def patterns(self):
        self.__ohlc_not_none_check()
        from trader.data.model import TALibCandlePatterns

        return TALibCandlePatterns(self.open_prices, self.high_prices, self.low_prices, self.close_prices)

    def bullish_fractals(self):
        """
        Bullish turning point. Lowest low in the middle and two higher lows on each side.

        :return: bool numpy array
        """
        return npu.peaks(self.high_prices, n=2)

    def bearish_fractals(self):
        """
        Bearish turning point. Highest high in the middle and two lower highs on each side.

        :return: bool numpy array
        """
        return npu.bottoms(self.low_prices, n=2)

    def average_price(self) -> np.ndarray:
        """
        Calculates the mean on open, high, low, close prices.

        Formula: (open + high + low + close) / 4

        :return: numeric numpy array
        """

        return (self.open_prices + self.high_prices + self.low_prices + self.close_prices) / 4

    def median_price(self) -> np.ndarray:
        """
        Calculates the mean on high and low prices.

        Formula: (high + low) / 2

        :return: numeric numpy array
        """
        return (self.high_prices + self.low_prices) / 2

    def midpoint_price_over_period(self, period=14) -> np.ndarray:
        """
        Calculates the average price of the highest high and the lowest low prices in `period`.

        Formula: (period's highest high + period's lowest low) / 2

        :return: numeric numpy array
        """
        highest_high = npu.max_over_period(self.high_prices, period=period)
        lowest_low = npu.min_over_period(self.low_prices, period=period)
        return (highest_high + lowest_low) / 2

    def typical_price(self) -> np.ndarray:
        """
        Calculates the mean on high, low and close prices.

        Formula: (high + low + close) / 3

        :return: numeric numpy array
        """
        return (self.high_prices + self.low_prices + self.close_prices) / 3

    def weighted_close_price(self) -> np.ndarray:
        """
        Calculates the mean on high, low and 2 * close prices.

        Formula: (high + low + close * 2) / 4

        :return: numeric numpy array
        """
        return (self.high_prices + self.low_prices + self.close_prices * 2) / 4

    def __ohlc_not_none_check(self) -> None:
        if any(val is None for val in (self.open_prices, self.high_prices, self.low_prices, self.close_prices)):
            raise ValueError("Open, high, low or close prices are missing.")

    def normalize(self, *x: str | OHLCV) -> Candles:
        """
        Creates and returns a new Candles object with normalized data defined by `x`.

        :param x: Series to normalize between 0 and 1.
        :return: New Candles object
        """

        if len(x) == 0:
            raise ValueError("At least one parameter is required!")

        x = [str(val) for val in x]

        data = np.array([
            npu.normalize(self.__getitem__(name))
            if name in x
            else self.__getitem__(name)
            for name in self.schema
        ]).T

        candles = self.copy_with_data(data, meta={"normalized": True})
        return candles

    def to_heikin_ashi(self):
        o, h, l, c = to_heikin_ashi(
            open=self.open_prices,
            high=self.high_prices,
            low=self.low_prices,
            close=self.close_prices,
        )
        ohlc = {OPEN_PRICE: o, HIGH_PRICE: h, LOW_PRICE: l, CLOSE_PRICE: c}
        arrays = [ohlc[name] if name in ohlc else self.__getitem__(name) for name in self.schema]
        data = np.vstack(arrays).T

        candles = self.copy_with_data(data, meta={"heikin_ashi": True})
        return candles

    def blend(self, period=2) -> Candles:
        self.__ohlc_not_none_check()

        o, h, l, c = blend_ohlc(
            open=self.open_prices,
            high=self.high_prices,
            low=self.low_prices,
            close=self.close_prices,
            period=period,
        )

        ohlc = {OPEN_PRICE: o, HIGH_PRICE: h, LOW_PRICE: l, CLOSE_PRICE: c}
        arrays = [ohlc[name] if name in ohlc else self.__getitem__(name) for name in self.schema]
        data = np.vstack(arrays).T

        candles = self.copy_with_data(data, meta={"blended": True})
        return candles

    def series(self, x: int | str | OHLCV, /) -> np.ndarray:
        """
        Get data series by index or name.

        For example: self.line(OPEN_PRICE) returns the open_price candle series.
        """
        if isinstance(x, int):
            return self.candles.T[x]

        return self.candles.T[self.schema.index(str(x))]

    def average(self, *series: int | str | OHLCV) -> np.ndarray:
        """
        Counts average of multiple data series by index or name.

        For example: self.avg_line(OPEN_PRICE, CLOSE_PRICE) counts the average on open and close prices.
        """
        if len(series) == 0:
            raise ValueError("At least one parameter is required!")

        return np.mean([self.series(s) for s in series], axis=0)

    def body_size(self) -> np.ndarray:
        return np.abs(self.open_prices - self.close_prices)

    def wick_distance(self) -> np.ndarray:
        return self.high_prices - self.low_prices

    def ath(self):
        """Returns all-time high."""
        return np.max(self.high_prices)

    def atl(self):
        """Returns all-time low."""
        return np.min(self.low_prices)

    def highest_highs_over_period(self, period: int):
        return npu.max_over_period(self.high_prices, period)

    def lowest_lows_over_period(self, period: int):
        return npu.min_over_period(self.low_prices, period)

    def highest_closes_over_period(self, period: int):
        return npu.max_over_period(self.close_prices, period)

    def lowest_closes_over_period(self, period: int):
        return npu.min_over_period(self.close_prices, period)

    def highest_opens_over_period(self, period: int):
        return npu.max_over_period(self.open_prices, period)

    def lowest_opens_over_period(self, period: int):
        return npu.min_over_period(self.open_prices, period)

    @property
    def open_times(self) -> np.ndarray | None:
        try:
            return self.__getitem__(OPEN_TIME)
        except ValueError:
            return None

    @property
    def pd_open_times(self):
        return pd.to_datetime(self.open_times, unit="s")

    @property
    def latest_open_time(self):
        try:
            return int(self.open_times[-1])
        except TypeError:
            return None

    @property
    def open_prices(self) -> np.ndarray | None:
        try:
            return self.__getitem__(OPEN_PRICE)
        except ValueError:
            return None

    @property
    def latest_open_price(self):
        try:
            return float(self.open_prices[-1])
        except TypeError:
            return None

    @property
    def high_prices(self) -> np.ndarray | None:
        try:
            return self.__getitem__(HIGH_PRICE)
        except ValueError:
            return None

    @property
    def latest_high_price(self):
        try:
            return float(self.high_prices[-1])
        except TypeError:
            return None

    @property
    def low_prices(self) -> np.ndarray | None:
        try:
            return self.__getitem__(LOW_PRICE)
        except ValueError:
            return None

    @property
    def latest_low_price(self):
        try:
            return float(self.low_prices[-1])
        except TypeError:
            return None

    @property
    def close_prices(self) -> np.ndarray | None:
        try:
            return self.__getitem__(CLOSE_PRICE)
        except ValueError:
            return None

    @property
    def latest_close_price(self):
        try:
            return float(self.close_prices[-1])
        except TypeError:
            return None

    @property
    def volumes(self) -> np.ndarray | None:
        try:
            return self.__getitem__(VOLUME)
        except ValueError:
            return None

    @property
    def latest_volume(self):
        try:
            return float(self.volumes[-1])
        except TypeError:
            return None
