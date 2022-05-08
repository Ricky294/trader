import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class TrueRangeIndicator(Indicator):

    def __call__(self, candles: Candles):
        self.trange = talib.TRANGE(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
        )
