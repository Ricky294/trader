import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class ChaikinOscillator(Indicator):
    """Chaikin A/D Oscillator"""

    def __init__(self, fast_period=3, slow_period=10):
        self.fast_period = fast_period
        self.slow_period = slow_period

    def __call__(self, candles: Candles):
        self.adosc = talib.ADOSC(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            candles.volumes,
            fastperiod=self.fast_period,
            slowperiod=self.slow_period,
        )
