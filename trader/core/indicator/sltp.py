from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from trader.data.model import Candles

from trader.core.super_enum import OrderSide


class SLTPIndicator(ABC, Callable):

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    def __call__(self, candles: Candles, side: OrderSide): ...
