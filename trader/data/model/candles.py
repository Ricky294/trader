from __future__ import annotations

import copy
from abc import abstractmethod, ABC
from datetime import datetime

import numpy as np
import nputils as npu
import talib as ta

from trader.data.model import Symbol
from trader.data.db import CandleStorage, HDF5CandleStorage, NPYCandleStorage
from trader.data.candle_schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME

from trader.core.const import Market
from trader.data.candle_util import blend_ohlc, to_heikin_ashi

from util.interval import interval_to_seconds
from util.iter_util import SliceIterator


class BaseCandles(ABC):
    """
    Abstract class for storing candle data.
    """

    __slots__ = 'candles', 'schema', 'symbol', 'interval', 'market', 'tags'

    @staticmethod
    def __index_name_schema(schema: dict):
        ret = {}
        for key, value in schema.items():
            if isinstance(key, int):
                ret[key] = value
            elif isinstance(key, str):
                ret[value] = key
            else:
                raise ValueError(f'Unsupported type: {type(key)}')
        return ret

    @staticmethod
    def __name_index_schema(schema: dict):
        ret = {}
        for key, value in schema.items():
            if isinstance(key, int):
                ret[value] = key
            elif isinstance(key, str):
                ret[key] = value
            else:
                raise ValueError(f'Unsupported type: {type(key)}')
        return ret

    @abstractmethod
    def __init__(
            self,
            candles: np.ndarray,
            symbol: Symbol,
            interval: str,
            market: Market,
            tags: dict[str, str | bool | int | float],
            schema: tuple[str, ...] | list[str],
    ):
        """
        Initializes `self` object.

        :param candles: Must be a two-dimensional numpy array. Each nested array represents a candle object.
        :param symbol: Candle symbol (e.g. S&P500, BTCUSDT).
        :param interval: Candle interval (e.g. '15m', '1h', '1d').
        :param market: Where candles are from (e.g. 'FUTURES', 'SPOT').
        :param tags: Additional metadata for this object.
        :param schema: Array like object, which describes candle schema.
        :raises ValueError: If candles number of dimension is not exactly 2
        or if schema length not equals with candle schema length.
        """

        if candles.ndim != 2:
            raise ValueError(f'Data must have exactly two dimensions but it has {candles.ndim}!')

        elif len(schema) != candles.shape[1]:
            raise ValueError(
                'Different shape for data and schema. '
                f'Schema defines {len(schema)} values while second dimension of candles data has {candles.shape[1]} values.'
            )

        self.candles = candles
        self.schema = schema
        self.symbol = symbol
        self.interval = interval
        self.market = market
        if tags:
            self.tags = tags
        else:
            self.tags = {}

    def copy_init(
            self,
            candles: np.ndarray = None,
            symbol: str = None,
            interval: str = None,
            market: Market = None,
            tags: dict = None,
            schema: tuple[str, ...] | list[str] = None,
    ):
        """
        Copy constructor - creates a copy of `self`.

        Creates a new Candles object by copying all attributes from `self`
        where parameter is None else it copies the parameter.

        :return: new ABCCandles object
        """

        return type(self)(
            candles=self.candles if candles is None else candles,
            symbol=self.symbol if symbol is None else symbol,
            interval=self.interval if interval is None else interval,
            market=self.market if market is None else market,
            schema=self.schema if schema is None else schema,
            tags={key: val for key, val in self.tags.items()} if tags is None else tags,
        )

    def pop(self):
        """
        Removes the latest candle from this object and returns it.

        :return: latest candle - 1D numpy array
        """
        latest_candle: np.ndarray = self.candles[-1]
        self.candles = self.candles[:-1]
        return latest_candle

    def __str__(self):
        return (
            f'Candles(symbol={self.symbol}, interval={self.interval}, '
            f'market={self.market}, schema={self.schema}, candle_count={self.shape[0]})'
        )

    def __iadd__(self, other):
        self.concatenate(other)
        return self

    def __add__(self, other):
        return self.append(other)

    def head(self, n: int):
        """
        Creates a new ABCCandles with the first `n` number of candles.

        :param n: Number of candles to include from start.
        :return: ABCCandles
        """
        return self.copy_init(self.candles[:n])

    def tail(self, n: int):
        """
        Creates a new ABCCandles with the last `n` number of candles.

        :param n: Number of candles to include to end.
        :return: ABCCandles
        """
        return self.copy_init(self.candles[-n:])

    def save_to_hdf5(self, dir_path: str):
        storage = HDF5CandleStorage(dir_path=dir_path, symbol=self.symbol.pair, interval=self.interval, market=self.market)
        storage.append(self.candles)

    def save_to_npy(self, dir_path: str):
        storage = NPYCandleStorage(dir_path=dir_path, symbol=self.symbol.pair, interval=self.interval, market=self.market)
        storage.append(self.candles)

    def concatenate(self, other: BaseCandles | np.ndarray, /):
        """
        Appends `other` at the end of `self` in place.

        Same as using the '+=' operator (__iadd__).

        Similar method(s):
            - append

        :param other: Candle object to append at the end of self.
        :return: None
        """

        if isinstance(other, BaseCandles):
            self.candles = np.vstack((self.candles, other.candles))
        elif isinstance(other, np.ndarray):
            self.candles = np.vstack((self.candles, other))
        else:
            raise TypeError(f'Unable to append data type: {type(other)}.')

    def append(self, other: BaseCandles | np.ndarray, /):
        """
        Returns a new Candles object by appending `other` at the end of `self`.

        Same as using the '+' operator (__add__).

        Similar method(s):
            - concatenate

        :param other: Candle object to append at the end of self.
        :return: Candles object
        """

        this = copy.deepcopy(self)
        if isinstance(other, BaseCandles):
            this.candles = np.vstack((self.candles, other.candles))
        elif isinstance(other, np.ndarray):
            this.candles = np.vstack((self.candles, other))
        else:
            raise ValueError(f'Unable to append data type: {type(other)}.')
        return this

    def to_dict(self):
        return {schema: self.series(schema) for schema in self.schema}

    def series_to_index(self, ser: str, /):
        return self.schema.index(ser)

    def series(self, item: str | tuple[str] | list[str], /) -> np.ndarray:
        """
        Returns 1 or 2 dimensional numpy array based on the type of `item`:
            - 1D - Series = int | str | OHLCV
            - 2D - Iterable[Series] = Iterable[int | str | OHLCV]

        :param item: Filter for Candle series (series to keep in numpy array).
        :return: numpy array
        """

        if isinstance(item, str):
            return self.candles.T[self.series_to_index(item)]
        else:
            indexes = [self.series_to_index(e) for e in item]
            candle_series = np.vstack([self.candles.T[index] for index in indexes])
            return candle_series

    def __getitem__(self, index: int | slice):
        """
        Filters on candles by a single index or an index slice.

        Note: If you would like to filter on series instead of candles, use series method.

        :param index: Defines which candles to include in the new Candles object
        :return: new Candles object
        """

        if isinstance(index, slice):
            # TODO:
            # Not that straight forward.
            # If item step is not exactly 1, then interval is different and data aggregation is needed.
            return self.copy_init(self.candles[index.start:index.stop:index.step])

        return self.copy_init(self.candles[index])

    @property
    def last_index(self):
        return len(self) - 1

    def __len__(self):
        return len(self.candles)

    def __iter__(self):
        return self.candles.__iter__()

    def slice_iterator(self, start_index=0):
        return SliceIterator(copy.deepcopy(self), start_index=start_index)

    def save(self, storage: CandleStorage):
        storage.append(self.candles)

    @property
    def last_candle(self) -> np.ndarray:
        return self.candles[-1]

    @property
    def size(self):
        """Number of elements in candles array."""
        return self.candles.size

    @property
    def shape(self):
        return self.candles.shape


class Candles(BaseCandles):
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
            symbol: Symbol,
            interval: str,
            market: Market,
            tags: dict = None,
            schema=(OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME),
    ):
        super(Candles, self).__init__(
            candles=candles,
            symbol=symbol,
            interval=interval,
            market=market,
            tags=tags,
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
        dim1_size = int(self.timestamps.size / dim2_size)

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
        from trader.data.model import CandlePatterns

        return CandlePatterns(self.open_prices, self.high_prices, self.low_prices, self.close_prices)

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

        candles = self.copy_init(candles=data, tags=dict(self.tags, **{"normalized": True}))
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

        candles = self.copy_init(data, tags=dict(self.tags, **{"heikin_ashi": True}))
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

        candles = self.copy_init(data, tags=dict(self.tags, **{"blended": True}))
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

        filtered_candles = self.candles[(self.timestamps >= start) & (self.timestamps <= end)]
        return self.copy_init(filtered_candles)

    @property
    def latest_ohlc(self) -> tuple[float, float, float, float]:
        """
        Returns a tuple containing the latest open, high, low, and close prices.

        Returns:
            tuple[float, float, float, float]: A tuple in the format (open, high, low, close).
        """
        return self.latest_open_price, self.latest_high_price, self.latest_low_price, self.latest_close_price

    @property
    def timestamps(self) -> np.ndarray | None:
        try:
            return self.series(OPEN_TIME)
        except ValueError:
            return None

    @property
    def times(self) -> np.ndarray[datetime]:
        if self.timestamps is not None:
            return np.array([datetime.fromtimestamp(ts) for ts in self.timestamps])

    @property
    def latest_time(self) -> datetime | None:
        try:
            return datetime.fromtimestamp(self.timestamps[-1])
        except TypeError:
            return None

    @property
    def latest_timestamp(self) -> float | None:
        try:
            return self.timestamps[-1]
        except TypeError:
            return None

    @property
    def open_prices(self) -> np.ndarray | None:
        try:
            return self.series(OPEN_PRICE)
        except ValueError:
            return None

    @property
    def latest_open_price(self) -> float | None:
        try:
            return self.open_prices[-1]
        except TypeError:
            return None

    @property
    def high_prices(self) -> np.ndarray | None:
        try:
            return self.series(HIGH_PRICE)
        except ValueError:
            return None

    @property
    def latest_high_price(self) -> float | None:
        try:
            return self.high_prices[-1]
        except TypeError:
            return None

    @property
    def low_prices(self) -> np.ndarray | None:
        try:
            return self.series(LOW_PRICE)
        except ValueError:
            return None

    @property
    def latest_low_price(self) -> float | None:
        try:
            return self.low_prices[-1]
        except TypeError:
            return None

    @property
    def close_prices(self) -> np.ndarray | None:
        try:
            return self.series(CLOSE_PRICE)
        except ValueError:
            return None

    @property
    def latest_close_price(self) -> float | None:
        try:
            return self.close_prices[-1]
        except TypeError:
            return None

    @property
    def volumes(self) -> np.ndarray | None:
        try:
            return self.series(VOLUME)
        except ValueError:
            return None

    @property
    def latest_volume(self) -> float | None:
        try:
            return self.volumes[-1]
        except TypeError:
            return None


class CandlePatterns:

    def __init__(self, open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
        self.ohlc = open, high, low, close
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def bullish_candles(self) -> np.ndarray:
        """
        Returns True where `close` price is greater than `open` price.

        :return: bool numpy array
        """
        return self.close > self.open

    def bearish_candles(self) -> np.ndarray:
        """
        Returns True where `close` price is less than `open` price.

        :return: bool numpy array
        """
        return self.close < self.open

    def consecutive_bullish_candles(self, n: int):
        """
        Returns True where `close` price is greater than `open` price
        after at least `n` consecutive times.

        :param n: True, where at least n number of consecutive candles are bullish.
        :return: bool numpy array
        """
        is_bullish = self.bullish_candles()
        bullish_win = np.lib.stride_tricks.sliding_window_view(is_bullish, n)

        return np.concatenate((np.full(n - 1, False), np.all(bullish_win, axis=-1)))

    def consecutive_bearish_candles(self, n: int):
        """
        Returns True where `close` price is less than `open` price
        after at least `n` consecutive times.

        :param n: True, where at least n number of consecutive candles are bearish.
        :return: bool numpy array
        """
        is_bullish = self.bearish_candles()
        bullish_win = np.lib.stride_tricks.sliding_window_view(is_bullish, n)

        return np.concatenate((np.full(n - 1, False), np.all(bullish_win, axis=-1)))

    # ---- Candlestick patterns ---- #
    def two_crows(self) -> np.ndarray:
        return ta.CDL2CROWS(*self.ohlc)

    def three_line_strike(self) -> np.ndarray:
        return ta.CDL3LINESTRIKE(*self.ohlc)

    def three_black_crows(self) -> np.ndarray:
        return ta.CDL3BLACKCROWS(*self.ohlc)

    def three_inside(self) -> np.ndarray:
        return ta.CDL3INSIDE(*self.ohlc)

    def three_outside_up_down(self) -> np.ndarray:
        return ta.CDL3OUTSIDE(*self.ohlc)

    def three_stars_in_south(self) -> np.ndarray:
        return ta.CDL3STARSINSOUTH(*self.ohlc)

    def three_white_soldiers(self) -> np.ndarray:
        return ta.CDL3WHITESOLDIERS(*self.ohlc)

    def abandoned_baby(self, penetration=0.3) -> np.ndarray:
        return ta.CDLABANDONEDBABY(*self.ohlc, penetration=penetration)

    def advance_block(self) -> np.ndarray:
        return ta.CDLADVANCEBLOCK(*self.ohlc)

    def breakaway(self) -> np.ndarray:
        return ta.CDLBREAKAWAY(*self.ohlc)

    def closing_marubozu(self) -> np.ndarray:
        return ta.CDLCLOSINGMARUBOZU(*self.ohlc)

    def belt_hold(self) -> np.ndarray:
        return ta.CDLBELTHOLD(*self.ohlc)

    def conceal_baby_swallow(self) -> np.ndarray:
        return ta.CDLCONCEALBABYSWALL(*self.ohlc)

    def counter_attack(self) -> np.ndarray:
        return ta.CDLCOUNTERATTACK(*self.ohlc)

    def dark_cloud_cover(self, penetration=0.5) -> np.ndarray:
        return ta.CDLDARKCLOUDCOVER(*self.ohlc, penetration=penetration)

    def doji(self) -> np.ndarray:
        return ta.CDLDOJI(*self.ohlc)

    def doji_star(self) -> np.ndarray:
        return ta.CDLDOJISTAR(*self.ohlc)

    def dragonfly_doji(self) -> np.ndarray:
        return ta.CDLDRAGONFLYDOJI(*self.ohlc)

    def engulfing(self) -> np.ndarray:
        return ta.CDLENGULFING(*self.ohlc)

    def evening_doji_star(self, penetration=0.3) -> np.ndarray:
        return ta.CDLEVENINGDOJISTAR(*self.ohlc, penetration=penetration)

    def evening_star(self, penetration=0.3) -> np.ndarray:
        return ta.CDLEVENINGSTAR(*self.ohlc, penetration=penetration)

    def gap_side_side_white(self) -> np.ndarray:
        return ta.CDLGAPSIDESIDEWHITE(*self.ohlc)

    def gravestone_doji(self) -> np.ndarray:
        return ta.CDLGRAVESTONEDOJI(*self.ohlc)

    def hammer(self) -> np.ndarray:
        return ta.CDLHAMMER(*self.ohlc)

    def hanging_man(self) -> np.ndarray:
        return ta.CDLHANGINGMAN(*self.ohlc)

    def harami(self) -> np.ndarray:
        return ta.CDLHARAMI(*self.ohlc)

    def harami_cross(self) -> np.ndarray:
        return ta.CDLHARAMICROSS(*self.ohlc)

    def high_wave(self) -> np.ndarray:
        return ta.CDLHIGHWAVE(*self.ohlc)

    def hikkake(self) -> np.ndarray:
        return ta.CDLHIKKAKE(*self.ohlc)

    def hikakke_modified(self) -> np.ndarray:
        return ta.CDLHIKKAKEMOD(*self.ohlc)

    def homing_pigeon(self) -> np.ndarray:
        return ta.CDLHOMINGPIGEON(*self.ohlc)

    def identical_three_crows(self) -> np.ndarray:
        return ta.CDLIDENTICAL3CROWS(*self.ohlc)

    def in_neck(self) -> np.ndarray:
        return ta.CDLINNECK(*self.ohlc)

    def inverted_hammer(self) -> np.ndarray:
        return ta.CDLINVERTEDHAMMER(*self.ohlc)

    def kicking(self) -> np.ndarray:
        return ta.CDLKICKING(*self.ohlc)

    def kicking_by_length(self) -> np.ndarray:
        return ta.CDLKICKINGBYLENGTH(*self.ohlc)

    def ladder_bottom(self) -> np.ndarray:
        return ta.CDLLADDERBOTTOM(*self.ohlc)

    def long_legged_doji(self) -> np.ndarray:
        return ta.CDLLONGLEGGEDDOJI(*self.ohlc)

    def long_line(self) -> np.ndarray:
        return ta.CDLLONGLINE(*self.ohlc)

    def marubozu(self) -> np.ndarray:
        return ta.CDLMARUBOZU(*self.ohlc)

    def matching_low(self) -> np.ndarray:
        return ta.CDLMATCHINGLOW(*self.ohlc)

    def mat_hold(self, penetration=0.5) -> np.ndarray:
        return ta.CDLMATHOLD(*self.ohlc, penetration=penetration)

    def morning_doji_star(self, penetration=0.3) -> np.ndarray:
        return ta.CDLMORNINGDOJISTAR(*self.ohlc, penetration=penetration)

    def morning_star(self, penetration=0.3) -> np.ndarray:
        return ta.CDLMORNINGSTAR(*self.ohlc, penetration=penetration)

    def on_neck(self) -> np.ndarray:
        return ta.CDLONNECK(*self.ohlc)

    def piercing(self) -> np.ndarray:
        return ta.CDLPIERCING(*self.ohlc)

    def rickshaw_man(self) -> np.ndarray:
        return ta.CDLRICKSHAWMAN(*self.ohlc)

    def rising_falling_three_methods(self) -> np.ndarray:
        return ta.CDLRISEFALL3METHODS(*self.ohlc)

    def separating_lines(self) -> np.ndarray:
        return ta.CDLSEPARATINGLINES(*self.ohlc)

    def shooting_star(self) -> np.ndarray:
        return ta.CDLSHOOTINGSTAR(*self.ohlc)

    def short_line(self) -> np.ndarray:
        return ta.CDLSHORTLINE(*self.ohlc)

    def spinning_top(self) -> np.ndarray:
        return ta.CDLSPINNINGTOP(*self.ohlc)

    def stalled_pattern(self) -> np.ndarray:
        return ta.CDLSTALLEDPATTERN(*self.ohlc)

    def stick_sandwich(self) -> np.ndarray:
        return ta.CDLSTICKSANDWICH(*self.ohlc)

    def takuri(self) -> np.ndarray:
        return ta.CDLTAKURI(*self.ohlc)

    def tasuki_gap(self) -> np.ndarray:
        return ta.CDLTASUKIGAP(*self.ohlc)

    def thrusting(self) -> np.ndarray:
        return ta.CDLTHRUSTING(*self.ohlc)

    def tristar(self) -> np.ndarray:
        return ta.CDLTRISTAR(*self.ohlc)

    def unique_three_river(self) -> np.ndarray:
        return ta.CDLUNIQUE3RIVER(*self.ohlc)

    def upside_gap_two_crows(self) -> np.ndarray:
        return ta.CDLUPSIDEGAP2CROWS(*self.ohlc)

    def upside_downside_gap_three_methods(self) -> np.ndarray:
        return ta.CDLXSIDEGAP3METHODS(*self.ohlc)


if __name__ == "__main__":
    import doctest

    flags = doctest.REPORT_NDIFF | doctest.FAIL_FAST
    doctest.testmod(verbose=True)
