import numpy as np
import talib

from trader.core.indicator import Indicator, Result
from trader.core.model import Candles
from trader.core.util.trade import cross


class MFIResult(Result):

    def __init__(
            self,
            mfi: np.ndarray,
            upper_limit: float,
            lower_limit: float,
    ):
        self.mfi = mfi
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    def overbought(self) -> np.ndarray:
        """
        True where MFI is greater than upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.mfi > self.upper_limit

    def oversold(self) -> np.ndarray:
        """
        True where MFI is lower than lower limit.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.mfi < self.lower_limit

    def cross_to_oversold(self) -> np.ndarray:
        """
        True where MFI crosses below lower limit.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return cross(self.mfi, "<", self.lower_limit)

    def cross_from_oversold(self) -> np.ndarray:
        """
        True where MFI crosses above lower limit.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return cross(self.mfi, ">", self.lower_limit)

    def cross_to_overbought(self) -> np.ndarray:
        """
        True where MFI crosses above upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return cross(self.mfi, ">", self.upper_limit)

    def cross_from_overbought(self) -> np.ndarray:
        """
        True where MFI crosses below upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return cross(self.mfi, "<", self.upper_limit)

    def overbought_reversal(self) -> np.ndarray:
        """
        True where MFI is above upper limit and current value is less than previous.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.overbought() & (self.mfi[-1] < self.mfi[-2])

    def oversold_reversal(self) -> np.ndarray:
        """
        True where MFI is below lower limit and current value is greater than previous.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.oversold() & (self.mfi[-1] > self.mfi[-2])


class MFIIndicator(Indicator):

    def __init__(
            self,
            period=14,
            upper_limit=80.0,
            lower_limit=20.0,
    ):
        self.period = period
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    def __call__(self, candles: Candles):
        """
        Calculates Money Flow Index (volume-weighted MFI)

        :param candles: Input data for MFI indicator
        :return: MFIResult - mfi
        """
        self._mfi = talib.MFI(
            candles.high_prices(),
            candles.low_prices(),
            candles.close_prices(),
            candles.volumes(),
            timeperiod=self.period,
        )

        return MFIResult(
            mfi=self._mfi,
            lower_limit=self.lower_limit,
            upper_limit=self.upper_limit,
        )
