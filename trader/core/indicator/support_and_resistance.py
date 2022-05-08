import nputils as npu

from trader.data.model import Candles

from trader.core.indicator import Indicator


class SRIndicator(Indicator):
    """Support & Resistance"""

    def __init__(self, period: int):
        self.period = period

    def __call__(self, candles: Candles):
        self.support = npu.bottoms(candles.low_prices, self.period)
        self.resistance = npu.peaks(candles.high_prices, self.period)
