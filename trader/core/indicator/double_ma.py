from __future__ import annotations

import numpy as np

from trader.data.model import Candles
from trader.data.candle_schema import CLOSE_PRICE

from trader.core.super_enum import MA
from trader.core.indicator import Indicator
from trader.core.util.vectorized.trade import talib_ma, cross


class DoubleMAIndicator(Indicator):
    """Double Moving Average"""

    color = {"fast_ma": "#00bcd4", "slow_ma": "#f23645"}

    def __init__(
            self,
            fast_period: int,
            slow_period: int,
            fast_type: MA,
            slow_type: MA,
            fast_line=CLOSE_PRICE,
            slow_line=CLOSE_PRICE,
    ):
        self.fast_period = fast_period
        self.fast_type = fast_type
        self.fast_line = fast_line

        self.slow_period = slow_period
        self.slow_type = slow_type
        self.slow_line = slow_line

    def __call__(self, candles: Candles):
        """
        Calculates a slow and a fast moving average.

        :param candles: Input data for calculating slow and fast MA.
        :return: IndicatorResult - slow_ma, fast_ma
        """

        self.fast_ma = talib_ma(
            candles.average(self.fast_line),
            type=self.fast_type,
            period=self.fast_period,
        )
        self.slow_ma = talib_ma(
            candles.average(self.slow_line),
            type=self.slow_type,
            period=self.slow_period,
        )

    def uptrend(self) -> np.ndarray:
        """
        True where fast MA is above slow MA

        Indicates uptrend

        :return: bool numpy array
        """
        return self.fast_ma > self.slow_ma

    def downtrend(self) -> np.ndarray:
        """
        True where fast MA is below slow MA

        Indicates downtrend

        :return: bool numpy array
        """
        return self.fast_ma < self.slow_ma

    def bullish_cross(self) -> np.ndarray:
        """
        True where fast MA crosses above slow MA.

        Signals buy - Indicates uptrend

        :return: bool numpy array
        """
        return cross(self.fast_ma > self.slow_ma)

    def bearish_cross(self) -> np.ndarray:
        """
        True where fast MA crosses below slow MA.

        Signals sell - Indicates downtrend

        :return: bool numpy array
        """
        return cross(self.fast_ma < self.slow_ma)


DoubleMAIndicator(
    fast_line=5,
)