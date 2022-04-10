from __future__ import annotations

import numpy as np
import talib

from trader_data.core.model import Candles
from trader_data.core.enum import OHLCV

from trader.core.enum import MA
from trader.core.util.vectorized.trade import talib_ma
from trader.core.indicator import Indicator


class KeltnerChannelsIndicator(Indicator):
    """Keltner Channels"""

    def __init__(
            self,
            line=OHLCV.CLOSE_PRICE,
            atr_period=10,
            ma_period=20,
            ma_type: str | MA = MA.EMA,
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
        self.__candles = candles
        self.atr = talib.ATR(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            timeperiod=self.atr_period,
        )

        self.middle = talib_ma(candles.avg_line(self.line), self.ma_type, self.ma_period)
        self.upper: np.ndarray = self.middle + self.multiplier * self.atr
        self.lower: np.ndarray = self.middle - self.multiplier * self.atr

    def high_price_above_upper_band(self) -> np.ndarray:
        """
        True where high price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.__candles.high_prices > self.upper

    def close_price_above_upper_band(self) -> np.ndarray:
        """
        True where close price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.__candles.close_prices > self.upper

    def low_price_below_lower_band(self) -> np.ndarray:
        """
        True where low price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.__candles.low_prices < self.lower

    def close_price_below_lower_band(self) -> np.ndarray:
        """
        True where close price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.__candles.close_prices < self.lower
