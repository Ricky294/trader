import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class UltimateOscillator(Indicator):

    def __init__(self, period1=7, period2=14, period3=28):
        self.period1 = period1
        self.period2 = period2
        self.period3 = period3

    def __call__(self, candles: Candles):
        self.ultosc = talib.ULTOSC(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            timeperiod1=self.period1,
            timeperiod2=self.period2,
            timeperiod3=self.period3,
        )
