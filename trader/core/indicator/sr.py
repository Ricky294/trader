import nputils as npu

from trader.data.model import Candles

from trader.core.indicator import Indicator


class SRIndicator(Indicator):
    """Support & Resistance"""

    def __init__(self, candles: Candles, period: int):
        self.period = period
        super().__init__(candles)

    @property
    def support(self):
        return self._current_slice(self._support)

    @property
    def resistance(self):
        return self._current_slice(self._resistance)

    def __call__(self, candles: Candles):
        self._support = npu.bottoms(candles.low_prices, self.period)
        self._resistance = npu.peaks(candles.high_prices, self.period)
