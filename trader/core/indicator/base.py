from abc import ABC, abstractmethod
from typing import Callable

from trader.core.indicator.result import IndicatorResult
from trader.core.model import Candles
from trader.core.util.common import Storable


class Indicator(Storable, ABC, Callable):

    @abstractmethod
    def __call__(self, candles: Candles) -> IndicatorResult: ...
