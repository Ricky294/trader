import numpy as np
import talib

from trader.core.indicator import Indicator, Result
from trader.core.model import Candles
from trader.core.util.trade import cross


class DMIResult(Result):

    def __init__(self, adx: np.ndarray, plus_di: np.ndarray, minus_di: np.ndarray, volatility_limit: float):
        self.adx = adx
        self.plus_di = plus_di
        self.minus_di = minus_di
        self.volatility_limit = volatility_limit

    def ranging(self) -> np.ndarray:
        """
        True where ADX is above volatility limit.

        Indicates a ranging market.

        :return: bool numpy array
        """
        return self.adx < self.volatility_limit

    def trending(self) -> np.ndarray:
        """
        True where ADX is above volatility limit.

        Indicates a trending market.

        :return: bool numpy array
        """
        return self.adx > self.volatility_limit

    def uptrend(self) -> np.ndarray:
        """
        True where +DI is above -DI.

        Indicates upward pressure.

        :return: bool numpy array
        """
        return self.plus_di > self.minus_di

    def downtrend(self) -> np.ndarray:
        """
        True where -DI is above +DI.

        Indicates downward pressure.

        :return: bool numpy array
        """
        return self.minus_di > self.plus_di

    def non_volatile_uptrend(self) -> np.ndarray:
        """
        True where ADX is below volatility limit and +DI is above -DI.

        Indicates ranging upward movement.

        :return: bool numpy array
        """
        return (self.adx < self.volatility_limit) & (self.plus_di > self.minus_di)

    def non_volatile_downtrend(self) -> np.ndarray:
        """
        True where ADX is below volatility limit and -DI is above +DI.

        Indicates downward pressure.

        :return: bool numpy array
        """
        return (self.adx < self.volatility_limit) & (self.minus_di > self.plus_di)

    def volatile_uptrend(self) -> np.ndarray:
        """
        True where ADX is above volatility limit and +DI is above -DI.

        Indicates upward pressure.

        :return: bool numpy array
        """
        return (self.adx > self.volatility_limit) & (self.plus_di > self.minus_di)

    def volatile_downtrend(self) -> np.ndarray:
        """
        True where ADX is above volatility limit and -DI is above +DI.

        Indicates downward pressure.

        :return: bool numpy array
        """
        return (self.adx > self.volatility_limit) & (self.minus_di > self.plus_di)

    def cross(self) -> np.ndarray:
        """
        True where +DI crosses above -DI or +DI crosses below -DI.

        :return: bool numpy array
        """
        return self.bullish_cross() | self.bearish_cross()

    def bullish_cross(self) -> np.ndarray:
        """
        True where +DI crosses above -DI.

        Indicates upward pressure - Signals buy

        :return: bool numpy array
        """
        return cross(self.plus_di, ">", self.minus_di)

    def bearish_cross(self) -> np.ndarray:
        """
        True where -DI crosses above +DI.

        Indicates downward pressure - Signals sell

        :return: bool numpy array
        """
        return cross(self.minus_di, ">", self.plus_di)

    def bullish_cross_above_adx(self) -> np.ndarray:
        """
        True where +DI crosses above -DI above ADX.

        Indicates upward pressure - Signals buy

        :return: bool numpy array
        """
        return self.bullish_cross() & (self.adx < self.plus_di) & (self.adx < self.minus_di)

    def bearish_cross_above_adx(self) -> np.ndarray:
        """
        True where -DI crosses above +DI above ADX.

        Indicates downward pressure - Signals sell

        :return: bool numpy array
        """
        return self.bearish_cross() & (self.adx < self.plus_di) & (self.adx < self.minus_di)

    def bullish_cross_below_adx(self) -> np.ndarray:
        """
        True where +DI crosses above -DI below ADX.

        Indicates upward pressure - Signals buy

        :return: bool numpy array
        """
        return self.bullish_cross() & (self.adx > self.plus_di) & (self.adx > self.minus_di)

    def bearish_cross_below_adx(self) -> np.ndarray:
        """
        True where -DI crosses above +DI below ADX.

        Indicates downward pressure - Signals sell

        :return: bool numpy array
        """
        return self.bearish_cross() & (self.adx > self.plus_di) & (self.adx > self.minus_di)

    def volatile_bullish_cross(self) -> np.ndarray:
        """
        True where +DI crosses above -DI and ADX is above volatility limit.

        Indicates upward pressure - Signals buy

        :return: bool numpy array
        """
        return self.bullish_cross() & (self.adx > self.volatility_limit)

    def volatile_bearish_cross(self) -> np.ndarray:
        """
        True where -DI crosses above +DI and ADX is above volatility limit.

        Indicates downward pressure - Signals sell

        :return: bool numpy array
        """
        return self.bearish_cross() & (self.adx > self.volatility_limit)

    def non_volatile_bullish_cross(self) -> np.ndarray:
        """
        True where +DI crosses above -DI and ADX is below volatility limit.

        Indicates upward pressure - Signals buy

        :return: bool numpy array
        """
        return self.bullish_cross() & (self.adx < self.volatility_limit)

    def non_volatile_bearish_cross(self) -> np.ndarray:
        """
        True where -DI crosses above +DI and ADX is below volatility limit.

        Indicates downward pressure - Signals sell

        :return: bool numpy array
        """
        return self.bearish_cross() & (self.adx < self.volatility_limit)


class DMIIndicator(Indicator):

    def __init__(self, adx_period=14, plus_di_period=14, minus_di_period=14, volatlity_limit=25.0):
        self.adx_period = adx_period
        self.plus_di_period = plus_di_period
        self.minus_di_period = minus_di_period
        self.volatlity_limit = volatlity_limit

    def __call__(self, candles: Candles):
        """
        Calculates Directional Moving Index

        :param candles: Input data for indicator.

        :return: DMIResult - adx, minus_di, plus_di
        """

        adx = talib.ADX(
            candles.high_prices(),
            candles.low_prices(),
            candles.close_prices(),
            self.adx_period
        )

        plus_di = talib.PLUS_DI(
            candles.high_prices(),
            candles.low_prices(),
            candles.close_prices(),
            self.plus_di_period,
        )

        minus_di = talib.MINUS_DI(
            candles.high_prices(),
            candles.low_prices(),
            candles.close_prices(),
            self.minus_di_period
        )

        return DMIResult(
            adx=adx,
            minus_di=minus_di,
            plus_di=plus_di,
            volatility_limit=self.volatlity_limit,
        )
