import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class Aroon(Indicator):
    """
    Aroon

    Momentum Indicator
    """

    def __init__(self, candles: Candles, period=14):
        self.period = period
        super().__init__(candles)

    @property
    def aroon_down(self):
        return self._current_slice(self._aroon_down)

    @property
    def aroon_up(self):
        return self._current_slice(self._aroon_up)

    def __call__(self, candles: Candles):
        self._aroon_down, self._aroon_up = talib.AROON(
            candles.high_prices,
            candles.low_prices,
            timeperiod=self.period,
        )
