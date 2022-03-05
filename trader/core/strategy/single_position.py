from abc import abstractmethod
from typing import Optional, Union

import numpy as np

from trader.core.interface import FuturesTrader
from trader.core.model import Position, Candles

from .base import Strategy


class SinglePositionStrategy(Strategy):

    def __init__(self, symbol: str, trader: FuturesTrader):
        super(SinglePositionStrategy, self).__init__(trader)
        self.symbol = symbol

    def __call__(self, candles: Union[Candles, np.ndarray]):
        if isinstance(candles, np.ndarray):
            candles = Candles.with_data(candles)

        position = self.trader.get_position(self.symbol)
        self.on_next(candles, position)

    def on_next(self, candles: Candles, position: Optional[Position]):
        if position is None:
            self.not_in_position(candles)
        else:
            self.in_position(candles, position)

    @abstractmethod
    def in_position(self, candles: Candles, position: Position): ...

    @abstractmethod
    def not_in_position(self, candles: Candles): ...
