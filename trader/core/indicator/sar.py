import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class ParabolicSAR(Indicator):

    def __init__(self, acceleration=0.02, maximum=0.2):
        self.acceleration = acceleration
        self.maximum = maximum

    def __call__(self, candles: Candles):
        self.sar = talib.SAR(
            candles.high_prices,
            candles.low_prices,
            acceleration=self.acceleration,
            maximum=self.maximum,
        )