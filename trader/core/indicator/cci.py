import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class CommodityChannelIndex(Indicator):
    """
    Commodity Channel Index - CCI

    Momentum Indicator
    """
    def __init__(self, candles: Candles, period=14):
        self.period = period
        super().__init__(candles)

    @property
    def cci(self):
        return self._current_slice(self._cci)

    def __call__(self, candles: Candles):
        self._cci = talib.CCI(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            timeperiod=self.period
        )
