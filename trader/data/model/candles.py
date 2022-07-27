from __future__ import annotations

from datetime import datetime
from enum import Enum

import numpy as np
import pandas as pd
import nputils as npu

from trader.data.candle_schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME
from trader.data.super_enum import Market
from trader.data.model import ABCCandles
from trader.data.util import blend_ohlc, to_heikin_ashi, interval_to_seconds


class ConfigParam(Enum):

    def __str__(self):
        return str(self.value)


class Orientation(ConfigParam):
    AUTO = 'AUTO'
    COLUMNAR = 'COLUMNAR'
    RECORD = 'RECORD'


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
            market: Market,
            meta: dict = None,
            schema=(OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME),
            orientation=Orientation.AUTO,
    ):
        super(Candles, self).__init__(
            candles=candles,
            symbol=symbol,
            interval=interval,
            market=market,
            meta=meta,
            schema=schema,
        )

    def roll_up(self, interval: str) -> Candles:
        """
        Creates a new Candles object by grouping and aggregating candles on a higher interval.

        `self.interval` = x and `interval` = y (where y > x and y / x is integer) it creates candle groups
        with size = y / x, and aggregates them as follows:
            - OPEN_TIME: First value in group.
            - OPEN_PRICE: First value in group.
            - HIGH_PRICE: Max value in group
            - LOW_PRICE: Min value in group.
            - CLOSE_PRICE: Last value in group.
            - VOLUME: Sum of group values.

        :param interval: Higher / aggregation timeframe.
        :return: New Candles object on a higher timeframe.
        :raises ValueError: If interval less than or equals with self.interval
        or interval divided by self.interval is not an integer.

        Example:
        --------

        :examples:
        >>> data = np.array([[1,  4,  7,  3,  6,  2],
        ...                  [2,  6,  9,  2,  8,  3],
        ...                  [3,  8, 10,  4,  5,  2],
        ...                  [4,  5,  6,  1,  4,  5],
        ...                  [5,  4, 12,  2,  6,  1],
        ...                  [6,  6,  8,  3,  7,  1]])

        >>> candles1h = Candles(candles=data, symbol="XYZ", interval="1h", market=Market.SPOT)
        >>> candles2h = candles1h.roll_up("2h")
        >>> candles2h.candles
        array([[ 1,  4,  9,  2,  8,  5],
               [ 3,  8, 10,  1,  4,  7],
               [ 5,  4, 12,  2,  7,  2]])

        >>> candles3h = candles1h.roll_up("3h")
        >>> candles3h.candles
        array([[ 1,  4, 10,  2,  5,  7],
               [ 4,  5, 12,  1,  7,  7]])

        >>> candles4h = candles1h.roll_up("4h")
        >>> candles4h.candles
        array([[ 1,  4, 10,  1,  4, 12]])
        """

        this_interval_in_sec = interval_to_seconds(self.interval)
        roll_up_interval_in_sec = interval_to_seconds(interval)

        dim2_size = roll_up_interval_in_sec / this_interval_in_sec
        if not dim2_size.is_integer() or dim2_size <= 1:
            raise ValueError(
                f"Unable to roll up {self.interval!r} (self) interval candles to {interval!r} (param).\n"
                "Param interval must be greater than self.interval "
                "and param interval divided by self.interval must be an integer."
            )

        dim2_size = int(dim2_size)
        dim1_size = int(self.times.size / dim2_size)

        def reduce_reshape(arr: np.ndarray):
            return npu.reduce_reshape(arr, dim2_size)

        def reshape(arr: np.ndarray):
            return arr.reshape(len(arr), 1)

        def aggregate_series():
            for name, data in self.to_dict().items():
                reduced_data = reduce_reshape(data)
                if name in [OPEN_TIME, OPEN_PRICE]:
                    yield reduced_data[:, 0]
                elif name == HIGH_PRICE:
                    yield np.max(reduced_data, axis=-1)
                elif name == LOW_PRICE:
                    yield np.min(reduced_data, axis=-1)
                elif name == CLOSE_PRICE:
                    yield reduced_data[:, -1]
                elif name == VOLUME:
                    yield np.sum(reduced_data, axis=-1)

        aggregated_candles = np.concatenate(
            tuple(map(reshape, aggregate_series())), axis=-1
        ).reshape(dim1_size, len(self.schema))

        return self.copy_init(aggregated_candles, interval=interval)

    @property
    def patterns(self):
        self._ohlc_not_none_check()
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

    def _ohlc_not_none_check(self) -> None:
        if any(val is None for val in (self.open_prices, self.high_prices, self.low_prices, self.close_prices)):
            raise ValueError("Open, high, low or close prices are missing.")

    def normalize(self, *x: str) -> Candles:
        """
        Creates and returns a new Candles object with normalized data defined by `x`.

        :param x: Series to normalize between 0 and 1.
        :return: New Candles object
        """

        if len(x) == 0:
            raise ValueError("At least one parameter is required!")

        x = [str(val) for val in x]

        data = np.array([
            npu.normalize(self.series(name))
            if name in x
            else self.series(name)
            for name in self.schema
        ]).T

        candles = self.copy_init(candles=data, meta=dict(self.meta, **{"normalized": True}))
        return candles

    def to_heikin_ashi(self):
        """
        Converts candles (open, high, low and close prices) to heikin ashi candles.

        Calculation formula:
            - ha open: (ha open[-1] + ha close[-1]) / 2
            - ha high: max(high, ha open[0], ha close[0])
            - ha low: min(low, ha open[0], ha close[0])
            - ha close: (open[0], high[0], low[0], close[0]) / 4

        Note: [0] - means current, [-1] - means previous

        :return: New Candles object (ohlc prices are altered based on the above formula).
        """

        o, h, l, c = to_heikin_ashi(
            open=self.open_prices,
            high=self.high_prices,
            low=self.low_prices,
            close=self.close_prices,
        )
        ohlc = {OPEN_PRICE: o, HIGH_PRICE: h, LOW_PRICE: l, CLOSE_PRICE: c}
        arrays = [ohlc[name] if name in ohlc else self.series(name) for name in self.schema]
        data = np.vstack(arrays).T

        candles = self.copy_init(data, meta=dict(self.meta, **{"heikin_ashi": True}))
        return candles

    def blend(self, period=2) -> Candles:
        self._ohlc_not_none_check()

        o, h, l, c = blend_ohlc(
            open=self.open_prices,
            high=self.high_prices,
            low=self.low_prices,
            close=self.close_prices,
            period=period,
        )

        ohlc = {OPEN_PRICE: o, HIGH_PRICE: h, LOW_PRICE: l, CLOSE_PRICE: c}
        arrays = [ohlc[name] if name in ohlc else self.series(name) for name in self.schema]
        data = np.vstack(arrays).T

        candles = self.copy_init(data, meta=dict(self.meta, **{"blended": True}))
        return candles

    def average(self, *series: str) -> np.ndarray:
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

    def between(self, start: float | datetime, end: float | datetime):
        """
        Creates a new Candles object, which only includes candles between `start` and `end` time.

        Formula: Include candle only if
            - open_time >= start
            - and open time <= end

        :param start: Filters out candles before this time.
        :param end: Filters out candles after this time.
        :return: new Candles object between start and end timeframe.
        """

        if isinstance(start, datetime):
            start = start.timestamp()
        if isinstance(end, datetime):
            end = end.timestamp()

        filtered_candles = self.candles[(self.times >= start) & (self.times <= end)]
        return self.copy_init(filtered_candles)

    @property
    def times(self) -> np.ndarray | None:
        try:
            return self.series(OPEN_TIME)
        except ValueError:
            return None

    @property
    def pd_open_times(self):
        return pd.to_datetime(self.times, unit="s")

    @property
    def latest_time(self):
        try:
            return int(self.times[-1])
        except TypeError:
            return None

    @property
    def open_prices(self) -> np.ndarray | None:
        try:
            return self.series(OPEN_PRICE)
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
            return self.series(HIGH_PRICE)
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
            return self.series(LOW_PRICE)
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
            return self.series(CLOSE_PRICE)
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
            return self.series(VOLUME)
        except ValueError:
            return None

    @property
    def latest_volume(self):
        try:
            return float(self.volumes[-1])
        except TypeError:
            return None
