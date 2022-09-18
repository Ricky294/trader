import talib

from trader.data.model import Candles

from trader.core.indicator import Indicator


class DXIndicator(Indicator):
    """
    Directional Movement Index - DX

    Momentum Indicator
    """

    def __init__(self, candles: Candles, period=14):
        self.period = period
        super().__init__(candles)

    @property
    def dx(self):
        return self._current_slice(self._dx)

    def __call__(self, candles: Candles):
        self._dx = talib.DX(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            self.period
        )
