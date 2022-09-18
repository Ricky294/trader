import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class AroonOscillator(Indicator):
    """
    Aroon Oscillator

    Momentum Indicator
    """

    def __init__(self, candles: Candles, period=14):
        self.period = period
        super().__init__(candles)

    @property
    def aroon(self):
        return self._current_slice(self._aroon)

    def __call__(self, candles: Candles):
        self._aroon = talib.AROONOSC(
            candles.high_prices,
            candles.low_prices,
            timeperiod=self.period,
        )
