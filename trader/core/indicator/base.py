from abc import abstractmethod
from typing import Iterable

from trader.data.model import Candles


class Indicator:
    subclasses = []

    def __init_subclass__(cls, *args, **kwargs):
        cls.subclasses.append(cls)

    def __init__(self, candles: Candles):
        self._candles = candles
        self._i = len(self._candles) - 1
        self.__call__(candles)

    def __len__(self):
        return self._i

    @abstractmethod
    def __call__(self, candles: Candles): ...

    @property
    def candles(self):
        return self._current_slice(self._candles)

    def _current_slice(self, x: Iterable):
        return x[:self._i + 1]
