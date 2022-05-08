import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class Aroon(Indicator):

    def __init__(self, period=14):
        self.period = period

    def __call__(self, candles: Candles):
        self.aroon_down, self.aroon_up = talib.AROON(
            candles.high_prices,
            candles.low_prices,
            timeperiod=self.period,
        )
