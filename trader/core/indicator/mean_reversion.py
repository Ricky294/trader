from typing import Union

import numpy as np

from trader.core.enum import OHLCV, MAType
from trader.core.indicator import Indicator, Result
from trader.core.model import Candles
from trader.core.util.np import avg_line, slope
from trader.core.util.trade import talib_ma


class MeanReversionResult(Result):

    def __init__(self, ma: np.ndarray, ma_slope: np.ndarray, slope_limit: float, candles: Candles):
        self.ma = ma
        self.ma_slope = ma_slope
        self.slope_limit = slope_limit
        self.__candles = candles

    def candle_wick_mean_reversion(self) -> np.ndarray:
        """
        True where moving average is greater than low price and less than high price,
        in other words mean is between high and low.

        :return: bool numpy array
        """

        return (self.ma > self.__candles.low_prices()) & (self.ma < self.__candles.high_prices())

    def candle_body_mean_reversion(self) -> np.ndarray:
        """
        True where moving average is greater than low price and less than high price,
        in other words mean is between high and low.

        :return: bool numpy array
        """

        return (self.ma > self.__candles.low_prices()) & (self.ma < self.__candles.high_prices())

    def uptrend_candle_body_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is greater than the slope limit
        and moving average is above close price.

        Signals buy

        :return: bool numpy array
        """
        return (self.ma_slope > self.slope_limit) & (self.ma > self.__candles.close_prices())

    def uptrend_candle_wick_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is greater than the slope limit
        and moving average is above low price.

        Signals buy

        :return: bool numpy array
        """
        return (self.ma_slope > self.slope_limit) & (self.ma > self.__candles.low_prices())

    def uptrend_candle_wick_only_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is greater than the slope limit
        and moving average is above low price but not above close price.

        Signals buy

        :return: bool numpy array
        """
        return self.uptrend_candle_wick_mean_reversion() & (self.ma < self.__candles.close_prices())

    def downtrend_candle_body_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is less than the slope limit
        and moving average is below close or open price.

        Signals sell

        :return: bool numpy array
        """
        return (self.ma_slope < -self.slope_limit) & (self.ma < self.__candles.close_prices())

    def downtrend_candle_wick_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is less than the slope limit
        and moving average is below high price.

        Signals sell

        :return: bool numpy array
        """
        return (self.ma_slope < -self.slope_limit) & (self.ma < self.__candles.high_prices())

    def downtrend_candle_wick_only_mean_reversion(self) -> np.ndarray:
        """
        True where the moving average slope is less than the slope limit
        and moving average is below high price but not below close price.

        Signals sell

        :return: bool numpy array
        """
        return self.downtrend_candle_wick_mean_reversion() & (self.ma > self.__candles.close_prices())


class MeanReversionIndicator(Indicator):

    def __init__(
            self,
            ma_period: int,
            ma_type: Union[str, MAType],
            slope_period: int,
            slope_limit: float,
            ma_line=OHLCV.CLOSE_PRICE,
    ):
        self.ma_period = ma_period
        self.slope_period = slope_period
        self.slope_limit = abs(slope_limit)
        self.ma_type = ma_type
        self.ma_line = ma_line

    def __call__(self, candles: Candles) -> Result:
        ma = talib_ma(type=self.ma_type, period=self.ma_period, data=avg_line(candles, self.ma_line))
        ma_slope = slope(ma, self.slope_period)

        return MeanReversionResult(
            ma=ma,
            ma_slope=ma_slope,
            slope_limit=self.slope_limit,
            candles=candles
        )
