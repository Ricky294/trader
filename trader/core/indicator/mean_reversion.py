from __future__ import annotations

import numpy as np

from trader_data.core.model import Candles
from trader_data.core.enum import OHLCV

from trader.core.enum import MA
from trader.core.indicator import Indicator
from trader.core.util.vectorized.trade import talib_ma, slope


class MeanReversionIndicator(Indicator):
    """Mean Reversion"""

    def __init__(
            self,
            ma_period: int,
            ma_type: str | MA,
            slope_period: int,
            slope_limit: float,
            ma_line=OHLCV.CLOSE_PRICE,
    ):
        self.ma_period = ma_period
        self.slope_period = slope_period
        self.slope_limit = abs(slope_limit)
        self.ma_type = ma_type
        self.ma_line = ma_line

    def __call__(self, candles: Candles):
        self.__candles = candles
        self.ma = talib_ma(candles.avg_line(self.ma_line), type=self.ma_type, period=self.ma_period)
        self.ma_slope = slope(self.ma, self.slope_period)

    def candle_wick_mean_reversion(self) -> np.ndarray:
        """
        True where moving average is greater than low price and less than high price,
        in other words mean is between high and low.

        :return: bool numpy array
        """

        return (self.ma > self.__candles.low_prices) & (self.ma < self.__candles.high_prices)

    def candle_body_mean_reversion(self) -> np.ndarray:
        """
        True where moving average is greater than low price and less than high price,
        in other words mean is between high and low.

        :return: bool numpy array
        """

        return (self.ma > self.__candles.low_prices) & (self.ma < self.__candles.high_prices)

    def uptrend_candle_body_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is greater than the slope limit
        and moving average is above close price.

        Signals buy

        :return: bool numpy array
        """
        return (self.ma_slope > self.slope_limit) & (self.ma > self.__candles.close_prices)

    def uptrend_candle_wick_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is greater than the slope limit
        and moving average is above low price.

        Signals buy

        :return: bool numpy array
        """
        return (self.ma_slope > self.slope_limit) & (self.ma > self.__candles.low_prices)

    def uptrend_candle_wick_only_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is greater than the slope limit
        and moving average is above low price but not above close price.

        Signals buy

        :return: bool numpy array
        """
        return self.uptrend_candle_wick_mean_reversion() & (self.ma < self.__candles.close_prices)

    def downtrend_candle_body_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is less than the slope limit
        and moving average is below close or open price.

        Signals sell

        :return: bool numpy array
        """
        return (self.ma_slope < -self.slope_limit) & (self.ma < self.__candles.close_prices)

    def downtrend_candle_wick_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is less than the slope limit
        and moving average is below high price.

        Signals sell

        :return: bool numpy array
        """
        return (self.ma_slope < -self.slope_limit) & (self.ma < self.__candles.high_prices)

    def downtrend_candle_wick_only_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is less than the slope limit
        and moving average is below high price but not below close price.

        Signals sell

        :return: bool numpy array
        """
        return self.downtrend_candle_wick_mean_reversion() & (self.ma > self.__candles.close_prices)
