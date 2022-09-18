import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class NormalizedAverageTrueRange(Indicator):
    """
    Normalized Average True Range - NATR

    Volatility Indicator
    """
    def __init__(self, candles: Candles, period=14):
        self.period = period
        super().__init__(candles)

    @property
    def natr(self):
        return self._current_slice(self._natr)

    def __call__(self, candles: Candles):
        self._natr = talib.NATR(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            timeperiod=self.period
        )
