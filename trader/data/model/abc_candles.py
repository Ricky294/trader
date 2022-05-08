from __future__ import annotations

import copy
from abc import abstractmethod, ABC

import numpy as np

from trader.data.database import HDF5CandleStorage, NPYCandleStorage, CandleStorage
from trader.data.enum import Market, OHLCV


class CandleIterable:
    """Iterates through all candles from start to end."""

    __slots__ = ("_candles", "_i")

    def __init__(self, candles: np.ndarray):
        self._candles = candles
        self._i = 0

    @property
    def i(self):
        """Current index."""
        return self._i

    def __next__(self):
        if self._i >= self._candles.shape[0]:
            raise StopIteration

        ret = self._candles[self._i]
        self._i += 1
        return ret


class CandleReplayer:
    """Iterates through all candles from start to end while keeping all the previous candles."""

    __slots__ = ("_original", "_replayed", "_i")

    def __init__(self, candles: ABCCandles, /):
        self._original = candles
        self._replayed = candles.copy_with_data(np.empty(candles.shape))
        self._i = 0

    @property
    def i(self):
        """Current index."""
        return self._i

    def __len__(self):
        return self._original.__len__()

    def __iter__(self):
        return self

    def __next__(self):
        if self._i >= self.__len__():
            raise StopIteration

        self._i += 1
        self._replayed.candles = self._original.candles[:self._i]
        return self._replayed


class ABCCandles(ABC):
    """
    Abstract class for candle containers.
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
                raise ValueError(f"Unsupported type: {type(key)}")
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
                raise ValueError(f"Unsupported type: {type(key)}")
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
        if candles.ndim != 2:
            raise ValueError("Data must have exactly two dimensions.")

        elif len(schema) != candles.shape[1]:
            raise ValueError("Different shape for data and schema.")

        self.candles = candles
        self.schema = schema
        self.symbol = symbol
        self.interval = interval
        self.market = market
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta

    def copy_with_data(self, data: np.ndarray, /, meta: dict = None):
        if meta is None:
            kwargs = self.meta
        else:
            kwargs = dict(self.meta, **meta)

        return type(self)(
            candles=data,
            symbol=copy.deepcopy(self.symbol),
            interval=copy.deepcopy(self.interval),
            market=copy.deepcopy(self.market),
            schema=copy.deepcopy(self.schema),
            meta=kwargs,
        )

    def __str__(self):
        return (
            f"Candles(symbol={self.symbol}, interval={self.interval}, "
            f"market={self.market}, schema={self.schema}, records={self.shape[0]})"
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
        return self.copy_with_data(self.candles[:n])

    def tail(self, n: int):
        """
        Creates a new ABCCandles with the last `n` number of candles.

        :param n: Number of candles to include to end.
        :return: ABCCandles
        """
        return self.copy_with_data(self.candles[-n:])

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
            raise ValueError(f"Unable to append data type: {type(other)}.")

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
            raise ValueError(f"Unable to append data type: {type(other)}.")
        return this

    def __getitem__(self, item):
        def to_index(val):
            if isinstance(val, OHLCV):
                return self.schema.index(str(val))
            if isinstance(val, str):
                return self.schema.index(val)
            return int(val)

        if isinstance(item, slice):
            start = to_index(item.start)
            stop = to_index(item.stop)
            step = to_index(item.step)
            return self.candles.T[start:stop:step]

        return self.candles.T[to_index(item)]

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
