import numpy as np
import talib

from trader.core.enum import OHLCV
from trader.core.model import Candles
from trader.core.util.np import avg_line
from trader.core.util.trade import cross
from trader.core.indicator import Indicator, Result


class RSIResult(Result):

    def __init__(
            self,
            rsi: np.ndarray,
            upper_limit: float,
            lower_limit: float
    ):
        self.rsi = rsi
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    def above50(self) -> np.ndarray:
        """
        True where RSI is above 50.

        :return: bool numpy array
        """
        return self.rsi > 50.0

    def below50(self) -> np.ndarray:
        """
        True where RSI is below 50.

        :return: bool numpy array
        """
        return self.rsi < 50.0

    def cross_above50(self) -> np.ndarray:
        """
        True where RSI crosses above 50.

        :return: bool numpy array
        """
        return cross(self.rsi, ">", 50.0)

    def cross_below50(self) -> np.ndarray:
        """
        True where RSI crosses below 50.

        :return: bool numpy array
        """
        return cross(self.rsi, "<", 50.0)

    def overbought(self) -> np.ndarray:
        """
        True where RSI is greater than upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.rsi > self.upper_limit

    def oversold(self) -> np.ndarray:
        """
        True where RSI is lower than lower limit.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.rsi < self.lower_limit

    def cross_to_oversold(self) -> np.ndarray:
        """
        True where RSI crosses below lower limit.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return cross(self.rsi, "<", self.lower_limit)

    def cross_from_oversold(self) -> np.ndarray:
        """
        True where RSI crosses above lower limit.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return cross(self.rsi, ">", self.lower_limit)

    def cross_to_overbought(self) -> np.ndarray:
        """
        True where RSI crosses above upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return cross(self.rsi, ">", self.upper_limit)

    def cross_from_overbought(self) -> np.ndarray:
        """
        True where RSI crosses below upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return cross(self.rsi, "<", self.upper_limit)

    def overbought_reversal(self) -> np.ndarray:
        """
        True where RSI is above upper limit and current value is less than previous.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.overbought() & (self.rsi[-1] < self.rsi[-2])

    def oversold_reversal(self) -> np.ndarray:
        """
        True where RSI is below lower limit and current value is greater than previous.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.oversold() & (self.rsi[-1] > self.rsi[-2])


class RSIIndicator(Indicator):

    def __init__(
            self,
            line=OHLCV.CLOSE_PRICE,
            period=14,
            upper_limit=70.0,
            lower_limit=30.0,
    ):
        self.line = line
        self.period = period
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    def __call__(self, candles: Candles):
        """
        Calculates Relative Strength Index

        :param candles: Input data for indicator.

        :return: RSIResult - rsi
        """
        rsi = talib.RSI(avg_line(candles, self.line), timeperiod=self.period)

        return RSIResult(
            rsi=rsi,
            upper_limit=self.upper_limit,
            lower_limit=self.lower_limit,
        )
