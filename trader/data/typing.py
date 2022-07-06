from typing import TypeVar

from trader.core.enumerate import OrderSide
from trader.data.enumerate import OHLCV

Series = TypeVar('Series', int, str, OHLCV)
Side = TypeVar('Side', int, str, OrderSide)
