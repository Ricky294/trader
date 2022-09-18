import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class UltimateOscillator(Indicator):
    """Ultimate Oscillator - ULT OSC

    Momentum Indicators"""

    def __init__(self, candles: Candles, period1=7, period2=14, period3=28):
        self.period1 = period1
        self.period2 = period2
        self.period3 = period3
        super().__init__(candles)

    @property
    def ultosc(self):
        return self._current_slice(self._ultosc)

    def __call__(self, candles: Candles):
        self._ultosc = talib.ULTOSC(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            timeperiod1=self.period1,
            timeperiod2=self.period2,
            timeperiod3=self.period3,
        )
