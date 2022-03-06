from typing import Union

import numpy as np

from trader.core.enum import OHLCV, MAType
from trader.core.indicator import Indicator, Result
from trader.core.model import Candles
from trader.core.util.np import avg_line
from trader.core.util.trade import talib_ma, cross


class DoubleMAResult(Result):

    def __init__(self, slow_ma: np.ndarray, fast_ma: np.ndarray):
        self.slow_ma = slow_ma
        self.fast_ma = fast_ma

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
        return cross(self.fast_ma, ">", self.slow_ma)

    def bearish_cross(self) -> np.ndarray:
        """
        True where fast MA crosses below slow MA.

        Signals sell - Indicates downtrend

        :return: bool numpy array
        """
        return cross(self.fast_ma, "<", self.slow_ma)


class DoubleMAIndicator(Indicator):

    def __init__(
            self,
            fast_period: int,
            fast_type: Union[str, MAType],
            slow_period: int,
            slow_type: Union[str, MAType],
            fast_line=OHLCV.CLOSE_PRICE,
            slow_line=OHLCV.CLOSE_PRICE,
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

        fast_ma = talib_ma(
            type=self.fast_type,
            period=self.fast_period,
            data=avg_line(candles, self.fast_line),
        )
        slow_ma = talib_ma(
            type=self.slow_type,
            period=self.slow_period,
            data=avg_line(candles, self.slow_line),
        )

        return DoubleMAResult(
            slow_ma=slow_ma,
            fast_ma=fast_ma,
        )
