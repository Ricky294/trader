from abc import ABC, abstractmethod
from typing import Callable

from trader.core.indicator import Result
from trader.core.model import Candles


class SLTPResult(Result):

    def __init__(self, take_profit_price: float, stop_loss_price: float):
        self.take_profit_price = take_profit_price
        self.stop_loss_price = stop_loss_price


class SLTPIndicator(ABC, Callable):

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    def __call__(self, candles: Candles) -> SLTPResult: ...
