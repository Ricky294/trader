import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class BalanceOfPower(Indicator):
    """
    Balance Of Power - BOP

    Momentum Indicator
    """

    @property
    def bop(self):
        return self._current_slice(self._bop)

    def __call__(self, candles: Candles):
        self._bop = talib.BOP(
            candles.open_prices,
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
        )
