from __future__ import annotations

import copy
from abc import abstractmethod, ABC
from typing import Iterator, Iterable

import numpy as np

from trader.data.database import HDF5CandleStorage, NPYCandleStorage, CandleStorage
from trader.data.enumerate import Market, OHLCV
from trader.data.typing import Series


class CandleIterable(Iterator):
    """Iterates through all candles from start to end."""

    __slots__ = ('_candles', '_i')

    def __init__(self, candles: np.ndarray):
        self._candles = candles
        self._i = 0

    @property
    def i(self):
        """Current index."""
        return self._i

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i >= self._candles.shape[0]:
            raise StopIteration

        ret = self._candles[self._i]
        self._i += 1
        return ret


class CandleReplayer(Iterator):
    """Iterates through all candles from start to end while keeping all the previous candles."""

    __slots__ = ('_original', '_replayed', '_i')

    def __init__(self, candles: ABCCandles, /):
        self._original = candles
        self._replayed = candles.copy_init(np.empty(candles.shape))
        self._i = 0

    @property
    def i(self):
        """Current index."""
        return self._i

    def __len__(self):
        return self._original.__len__()

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i >= self.__len__():
            raise StopIteration

        self._i += 1
        self._replayed.candles = self._original.candles[:self._i]
        return self._replayed


class ABCCandles(ABC):
    """
    Abstract class for storing candle data.
    """

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
            symbol: str,
            interval: str,
            market: str | Market,
            meta: dict,
            schema: tuple[str, ...] | list[str],
    ):
        """
        Initializes `self` object.

        :param candles: Must be a two-dimensional numpy array. Each nested array represents a candle object.
        :param symbol: Candle symbol (e.g. S&P500, BTCUSDT).
        :param interval: Candle interval (e.g. '15m', '1h', '1d').
        :param market: Where candles are from (e.g. 'FUTURES', 'SPOT').
        :param meta: Additional metadata for this object.
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
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta

    def copy_init(
            self,
            candles: np.ndarray = None,
            symbol: str = None,
            interval: str = None,
            market: str | Market = None,
            meta: dict = None,
            schema: tuple[str, ...] | list[str] = None,
    ):
        """
        Copy constructor - creates a copy of `self`.

        Creates a new Candles object by copying all attributes from `self`
        where parameter is None else it copies the parameter.

        :return: new ABCCandles object
        """

        return type(self)(
            candles=copy.deepcopy(self.candles) if candles is None else candles,
            symbol=copy.deepcopy(self.symbol) if symbol is None else symbol,
            interval=copy.deepcopy(self.interval) if interval is None else interval,
            market=copy.deepcopy(self.market) if market is None else market,
            schema=copy.deepcopy(self.schema) if schema is None else schema,
            meta=copy.deepcopy(self.meta) if meta is None else meta,
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
        storage = HDF5CandleStorage(dir_path=dir_path, symbol=self.symbol, interval=self.interval, market=self.market)
        storage.append(self.candles)

    def save_to_npy(self, dir_path: str):
        storage = NPYCandleStorage(dir_path=dir_path, symbol=self.symbol, interval=self.interval, market=self.market)
        storage.append(self.candles)

    def concatenate(self, other: ABCCandles | np.ndarray, /):
        """
        Appends `other` at the end of `self` in place.

        Same as using the '+=' operator (__iadd__).

        Similar method(s):
            - append

        :param other: Candle object to append at the end of self.
        :return: None
        """

        if isinstance(other, ABCCandles):
            self.candles = np.vstack((self.candles, other.candles))
        elif isinstance(other, np.ndarray):
            self.candles = np.vstack((self.candles, other))
        else:
            raise TypeError(f'Unable to append data type: {type(other)}.')

    def append(self, other: ABCCandles | np.ndarray, /):
        """
        Returns a new Candles object by appending `other` at the end of `self`.

        Same as using the '+' operator (__add__).

        Similar method(s):
            - concatenate

        :param other: Candle object to append at the end of self.
        :return: Candles object
        """

        this = copy.deepcopy(self)
        if isinstance(other, ABCCandles):
            this.candles = np.vstack((self.candles, other.candles))
        elif isinstance(other, np.ndarray):
            this.candles = np.vstack((self.candles, other))
        else:
            raise ValueError(f'Unable to append data type: {type(other)}.')
        return this

    def to_dict(self):
        return {schema: self.series(schema) for schema in self.schema}

    def series_to_index(self, ser: Series, /):
        return self.schema.index(str(ser)) if isinstance(ser, (str, OHLCV)) else int(ser)

    def series(self, item: Series | Iterable[Series], /) -> np.ndarray:
        """
        Returns 1 or 2 dimensional numpy array based on the type of `item`:
            - 1D - Series = int | str | OHLCV
            - 2D - Iterable[Series] = Iterable[int | str | OHLCV]

        :param item: Filter for Candle series (series to keep in numpy array).
        :return: numpy array
        """

        if isinstance(item, (int, str, OHLCV)):   # Series type
            return self.candles.T[self.series_to_index(item)]
        else:   # Iterable[Series]
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

    def __len__(self):
        return len(self.candles)

    def __iter__(self):
        return CandleIterable(self.candles)

    def replayer(self):
        return CandleReplayer(self)

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
