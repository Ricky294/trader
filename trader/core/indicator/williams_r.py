import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class WilliamsRIndicator(Indicator):

    def __init__(self, timeperiod=14):
        self.period = timeperiod

    def __call__(self, candles: Candles):
        self.willr = talib.WILLR(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            timeperiod=self.period,
        )
