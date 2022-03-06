from typing import Union

import numpy as np

from trader.core.enum import OHLCV, MAType
from trader.core.indicator import Indicator, Result
from trader.core.model import Candles
from trader.core.util.np import avg_line, slope
from trader.core.util.trade import talib_ma


class SingleMAResult(Result):

    def __init__(self, ma: np.ndarray, candles: Candles):
        self.ma = ma
        self.__candles = candles

    def below_low_price(self):
        return self.ma < self.__candles.low_prices()

    def below_close_price(self):
        return self.ma < self.__candles.close_prices()

    def below_high_price(self):
        return self.ma < self.__candles.high_prices()

    def below_open_price(self):
        return self.ma < self.__candles.open_prices()

    def above_low_price(self):
        return self.ma > self.__candles.low_prices()

    def above_close_price(self):
        return self.ma > self.__candles.close_prices()

    def above_high_price(self):
        return self.ma > self.__candles.high_prices()

    def above_open_price(self):
        return self.ma > self.__candles.open_prices()


class SingleMAIndicator(Indicator):

    def __init__(
            self,
            ma_period: int,
            ma_type: Union[str, MAType],
            ma_line=OHLCV.CLOSE_PRICE,
    ):
        self.ma_period = ma_period
        self.ma_type = ma_type
        self.ma_line = ma_line

    def __call__(self, candles: Candles) -> Result:
        ma = talib_ma(type=self.ma_type, period=self.ma_period, data=avg_line(candles, self.ma_line))

        return SingleMAResult(
            ma=ma,
        )

