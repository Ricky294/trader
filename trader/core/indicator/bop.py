import talib
from trader.data.model import Candles

from trader.core.indicator import Indicator


class BalanceOfPower(Indicator):

    def __call__(self, candles: Candles):
        self.bop = talib.BOP(
            candles.open_prices,
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
        )
