from __future__ import annotations

from trader.data.model import Candles
from trader.data.enumerate import OHLCV

from trader.core.enumerate import MA
from trader.core.indicator import Indicator
from trader.core.util.vectorized.trade import talib_ma


class SingleMAIndicator(Indicator):
    """Single Moving Average"""

    def __init__(
            self,
            period: int,
            ma_type: str | MA,
            line=OHLCV.CLOSE_PRICE,
    ):
        self.period = period
        self.ma_type = ma_type
        self.line = line

    def __call__(self, candles: Candles):
        self.__candles = candles
        self.ma = talib_ma(candles.average(self.line), type=self.ma_type, period=self.period)

    def below_low_price(self):
        return self.ma < self.__candles.low_prices

    def below_close_price(self):
        return self.ma < self.__candles.close_prices

    def below_high_price(self):
        return self.ma < self.__candles.high_prices

    def below_open_price(self):
        return self.ma < self.__candles.open_prices

    def above_low_price(self):
        return self.ma > self.__candles.low_prices

    def above_close_price(self):
        return self.ma > self.__candles.close_prices

    def above_high_price(self):
        return self.ma > self.__candles.high_prices

    def above_open_price(self):
        return self.ma > self.__candles.open_prices
