import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class TrueRangeIndicator(Indicator):
    """
    True Range - TRANGE

    Volatility Indicators
    """

    @property
    def trange(self):
        return self._current_slice(self._trange)

    def __call__(self, candles: Candles):
        self._trange = talib.TRANGE(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
        )
