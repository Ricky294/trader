import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class NormalizedAverageTrueRange(Indicator):

    def __init__(self, period=14):
        self.period = period

    def __call__(self, candles: Candles):
        self.natr = talib.NATR(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            timeperiod=self.period
        )