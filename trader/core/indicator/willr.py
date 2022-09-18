import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class WilliamsRIndicator(Indicator):
    """
    Williams' %R - WILL R

    Momentum Indicator
    """

    def __init__(self, candles: Candles, timeperiod=14):
        self.period = timeperiod
        super().__init__(candles)

    @property
    def willr(self):
        return self._current_slice(self._willr)

    def __call__(self, candles: Candles):
        self._willr = talib.WILLR(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            timeperiod=self.period,
        )
