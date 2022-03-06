from typing import Union

import numpy as np
import talib

from trader.core.enum import OHLCV, MAType
from trader.core.model import Candles
from trader.core.util.np import avg_line
from trader.core.util.trade import talib_ma
from trader.core.indicator import Indicator, Result


class KeltnerChannelsResult(Result):

    def __init__(self, upper: np.ndarray, middle: np.ndarray, lower: np.ndarray, candles: Candles):
        self.upper = upper
        self.middle = middle
        self.lower = lower
        self.__candles = candles

    def high_price_above_upper_band(self) -> np.ndarray:
        """
        True where high price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.__candles.high_prices() > self.upper

    def close_price_above_upper_band(self) -> np.ndarray:
        """
        True where close price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.__candles.close_prices() > self.upper

    def low_price_below_lower_band(self) -> np.ndarray:
        """
        True where low price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.__candles.low_prices() < self.lower

    def close_price_below_lower_band(self) -> np.ndarray:
        """
        True where close price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.__candles.close_prices() < self.lower


class KeltnerChannelsIndicator(Indicator):

    def __init__(
            self,
            line=OHLCV.CLOSE_PRICE,
            atr_period=10,
            ma_period=20,
            ma_type: Union[str, MAType] = MAType.EMA,
            multiplier=2.0,
    ):
        self.line = line
        self.atr_period = atr_period
        self.ma_period = ma_period
        self.ma_type = ma_type
        self.multiplier = multiplier

    def __call__(self, candles: Candles):
        """
        Calculates Keltner Channels

        :param candles: Input data for indicator.

        :return: KeltnerChannelsResult - upper, middle, lower
        """
        atr = talib.ATR(
            candles.high_prices(),
            candles.low_prices(),
            candles.close_prices(),
            timeperiod=self.atr_period,
        )

        middle = talib_ma(self.ma_type, self.ma_period, avg_line(candles, self.line))
        upper = middle + self.multiplier * atr
        lower = middle - self.multiplier * atr

        return KeltnerChannelsResult(
            upper=upper,
            middle=middle,
            lower=lower,
            candles=candles,
        )
