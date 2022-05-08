from abc import ABC, abstractmethod
from typing import Callable

from trader.data.model import Candles


class Indicator(ABC, Callable):

    @abstractmethod
    def __call__(self, candles: Candles): ...
