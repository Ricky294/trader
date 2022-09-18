import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class ParabolicSAR(Indicator):
    """
    Parabolic SAR - SAR

    Overlap Studies
    """

    def __init__(self, candles: Candles, acceleration=0.02, maximum=0.2):
        self.acceleration = acceleration
        self.maximum = maximum
        super().__init__(candles)

    @property
    def sar(self):
        return self._current_slice(self._sar)

    def __call__(self, candles: Candles):
        self._sar = talib.SAR(
            candles.high_prices,
            candles.low_prices,
            acceleration=self.acceleration,
            maximum=self.maximum,
        )
