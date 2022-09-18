from __future__ import annotations

import numpy as np
import talib

from trader.data.model import Candles
from trader.data.candle_schema import CLOSE_PRICE
from trader.core.const.ma import MA
from trader.trade import talib_ma
from trader.core.indicator import Indicator


class KeltnerChannelsIndicator(Indicator):
    """
    Keltner Channels
    """

    def __init__(
            self,
            candles: Candles,
            line=CLOSE_PRICE,
            atr_period=10,
            ma_period=20,
            ma_type: MA = MA.EMA,
            multiplier=2.0,
    ):
        self.line = line
        self.atr_period = atr_period
        self.ma_period = ma_period
        self.ma_type = ma_type
        self.multiplier = multiplier
        super().__init__(candles)

    @property
    def middle(self):
        return self._current_slice(self._middle)

    @property
    def upper(self):
        return self._current_slice(self._upper)

    @property
    def lower(self):
        return self._current_slice(self._lower)

    def __call__(self, candles: Candles):
        """
        Calculates Keltner Channels

        :param candles: Input data for indicator.

        :return: KeltnerChannelsResult - upper, middle, lower
        """
        self._candles = candles
        self._atr = talib.ATR(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            timeperiod=self.atr_period,
        )

        self._middle = talib_ma(candles.average(self.line), self.ma_type, self.ma_period)
        self._upper: np.ndarray = self._middle + self.multiplier * self._atr
        self._lower: np.ndarray = self._middle - self.multiplier * self._atr

    def high_price_above_upper_band(self) -> np.ndarray:
        """
        True where high price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.candles.high_prices > self.upper

    def close_price_above_upper_band(self) -> np.ndarray:
        """
        True where close price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.candles.close_prices > self.upper

    def low_price_below_lower_band(self) -> np.ndarray:
        """
        True where low price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.candles.low_prices < self.lower

    def close_price_below_lower_band(self) -> np.ndarray:
        """
        True where close price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.candles.close_prices < self.lower
