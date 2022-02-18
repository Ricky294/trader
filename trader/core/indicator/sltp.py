from abc import ABC, abstractmethod
from typing import Callable, Tuple

import numpy as np
from trader.core.model import Candles

from trader.core.util.common import Storable


class SLTPIndicator(ABC, Callable, Storable):
    @abstractmethod
    def __init__(self, *args, **data): ...

    @abstractmethod
    def __call__(self, candles: Candles, side: int) -> Tuple[float, float]: ...
