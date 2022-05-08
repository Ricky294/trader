import talib

from trader.data.model import Candles

from trader.core.indicator import Indicator


class DXIndicator(Indicator):
    """Directional Movement Index"""

    def __init__(self, period=14):
        self.period = period

    def __call__(self, candles: Candles):
        self.adx = talib.ADX(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            self.period
        )
