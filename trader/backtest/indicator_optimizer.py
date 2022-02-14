from trader.core.indicator import Indicator
from trader.core.model import Candles


class OptimizedIndicator(Indicator):

    __slots__ = "__indicator"

    def __init__(self, indicator: Indicator, candles: Candles):
        super().__init__(*(key for key in indicator.__dict__.keys()))
        indicator(candles)
        self.__indicator = indicator

    def __call__(self, candles: Candles):
        self.buy_signal = self.__indicator.buy_signal[:candles.shape[0]]
        self.sell_signal = self.__indicator.sell_signal[:candles.shape[0]]
        for key in self.__dict__.keys():
            self.__dict__[key] = self.__indicator.__dict__[key][:candles.shape[0]]
