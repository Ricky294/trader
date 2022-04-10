
from trader_data.core.model import Candles

from trader.core.indicator import Indicator
from trader.core.util.vectorized.trade import support, resistance


class SRIndicator(Indicator):
    """Support & Resistance"""

    def __init__(self, period: int):
        self.period = period

    def __call__(self, candles: Candles):
        self.support = support(candles.high_prices, self.period)
        self.resistance = resistance(candles.low_prices, self.period)
